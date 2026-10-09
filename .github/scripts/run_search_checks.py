#!/usr/bin/env python3
"""Grade unchanged Q1-Q7 tests, interpret scores, and reject/undo runner side effects."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
QUESTIONS = tuple(f"q{number}" for number in range(1, 8))
SPEC = importlib.util.spec_from_file_location("source_guard", ROOT / ".agents/scripts/source_guard.py")
GUARD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GUARD)


class SourceIntegrityError(RuntimeError):
    """The source gate failed; another question must not run."""


class OutputSafetyError(RuntimeError):
    """A report destination cannot be used without risking existing files."""


def output_path(root: Path, path: Path) -> Path:
    destination = path.resolve()
    protected = ((root / "src").resolve(), Path(r"D:\WKS\Projects\BLUEVERSE").resolve())
    if any(destination.is_relative_to(directory) for directory in protected):
        raise OutputSafetyError(f"report destination is protected: {path}")
    return destination


def write_report(root: Path, path: Path, contents: str) -> None:
    output_path(root, path)
    try:
        # Exclusive creation rejects pre-existing regular files, hard links and
        # symbolic links instead of overwriting their potentially protected target.
        with path.open("x", encoding="utf-8") as stream:
            stream.write(contents)
    except OSError as error:
        raise OutputSafetyError(f"cannot safely create report {path}: {error}") from error


def append_step_summary(root: Path, path: Path, contents: str) -> None:
    output_path(root, path)
    try:
        with path.open("a", encoding="utf-8") as stream:
            metadata = os.fstat(stream.fileno())
            if not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1:
                raise OutputSafetyError("step summary must be a regular file without hard-link aliases")
            stream.write(contents)
    except OSError as error:
        raise OutputSafetyError(f"cannot safely append step summary: {error}") from error


def score_result(output: str, question: str, maximum: int, returncode: int) -> dict:
    # Only the final table counts; earlier test messages/header scores are insufficient.
    table = output.rsplit("Provisional grades", 1)
    rows = re.findall(r"(?m)^Question (q\d+): (\d+)/(\d+)[ \t]*(.*)$", table[-1]) if len(table) == 2 else []
    grades = {name: (int(score), int(total), suffix.strip()) for name, score, total, suffix in rows}
    target = grades.get(question)
    passed = (
        returncode == 0 and len(grades) == len(rows) and bool(target)
        and target[0] == target[1] == maximum and maximum > 0
        and all(score == total and total > 0 and not suffix
                for score, total, suffix in grades.values())
    )
    return {
        "question": question, "passed": bool(passed), "returncode": returncode,
        "score": target[0] if target else None, "maximum": maximum,
        "reportedMaximum": target[1] if target else None,
        "dependencyScores": {name: {"score": row[0], "maximum": row[1], "note": row[2]}
                             for name, row in grades.items() if name != question},
        "reason": "full marks" if passed else "missing/incomplete grades, failed dependency, timeout or nonzero exit",
    }


def run_question(root: Path, question: str, results: Path, timeout: int) -> dict:
    config = (root / "src/test_cases" / question / "CONFIG").read_text(encoding="utf-8")
    match = re.search(r'(?m)^max_points:\s*"?(\d+)"?\s*$', config)
    if not match or int(match.group(1)) <= 0:
        raise ValueError(f"missing positive max_points for {question}")
    try:
        snapshot = GUARD.capture(root)
    except (OSError, ValueError) as error:
        raise SourceIntegrityError(f"cannot establish source baseline: {error}") from error
    output, returncode, report_error = "", -1, None
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8")
    try:
        try:
            completed = subprocess.run(
                [sys.executable, "-B", "autograder.py", "-q", question, "--no-graphics"],
                cwd=root / "src", env=environment, stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT, timeout=timeout,
            )
            output = completed.stdout.decode("utf-8", errors="replace")
            returncode = completed.returncode
        except subprocess.TimeoutExpired as error:
            partial = error.stdout or b""
            output = partial.decode("utf-8", errors="replace") if isinstance(partial, bytes) else partial
            output += f"\nCI timeout: {question} exceeded {timeout} seconds.\n"
        try:
            write_report(root, results / f"{question}.log", output)
        except OutputSafetyError as error:
            report_error = str(error)
    finally:
        # Each CI job owns an isolated checkout. No other command runs concurrently
        # here, so these differences are attributable to this grader subprocess.
        try:
            current = GUARD.inventory(root)
            changed = GUARD.violations(snapshot, current)
            owned = {name: GUARD.fingerprint(current.get(name)) for name in changed}
            integrity = GUARD.check(root, snapshot, owned=owned)
        except (OSError, ValueError, KeyError) as error:
            raise SourceIntegrityError(f"source recovery gate failed: {error}") from error
    result = score_result(output, question, int(match.group(1)), returncode)
    result["sourceIntegrity"] = integrity
    if integrity["rejected"] or integrity["unresolved"] or integrity["errors"]:
        result["passed"] = False
        result["reason"] = "grader changed source; operation rejected, recovery attempted"
    if report_error:
        result["passed"] = False
        result["outputError"] = report_error
        result["reason"] = report_error
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-dir", required=True, type=Path)
    parser.add_argument("--timeout", type=int, default=120)
    args = parser.parse_args()
    try:
        results = args.results_dir.resolve()
        summary_path = Path(os.environ['GITHUB_STEP_SUMMARY']).resolve() if os.environ.get('GITHUB_STEP_SUMMARY') else None
        protected = ((ROOT / 'src').resolve(), Path(r'D:\WKS\Projects\BLUEVERSE').resolve())
        if (args.timeout <= 0 or results.is_relative_to((ROOT / "src").resolve())
                or results.is_relative_to(protected[1])
                or (summary_path and any(summary_path.is_relative_to(path) for path in protected))):
            raise ValueError("results must stay outside src/BLUEVERSE; timeout must be positive")
        reports = [results / f"{question}.log" for question in QUESTIONS]
        reports += [results / "scores.json", results / "summary.md"]
        if any(path.exists() or path.is_symlink() for path in reports):
            raise OutputSafetyError("results directory already contains report paths; use a fresh directory")
        results.mkdir(parents=True, exist_ok=True)
        records = []
        for question in QUESTIONS:
            try:
                result = run_question(ROOT, question, results, args.timeout)
            except SourceIntegrityError as error:
                records.append({"question": question, "passed": False, "score": None,
                                "maximum": None, "reason": str(error)})
                print(f"FAIL: {error}; refusing to run further questions.")
                break
            except (OSError, ValueError, KeyError) as error:
                result = {"question": question, "passed": False, "score": None,
                          "maximum": None, "reason": str(error)}
            records.append(result)
            print(f"{'PASS' if result['passed'] else 'FAIL'}: {question} "
                  f"{result['score']}/{result['maximum']} - {result['reason']}")
            if (result.get("outputError") or result.get("sourceIntegrity", {}).get("unresolved")
                    or result.get("sourceIntegrity", {}).get("errors")):
                print("Unsafe report output or unresolved source changes; refusing further questions.")
                break
        write_report(ROOT, results / "scores.json", json.dumps(records, indent=2))
        summary = "# Pac-Man Q1-Q7\n\n| Question | Score | Result |\n| --- | --- | --- |\n"
        for result in records:
            summary += f"| {result['question']} | {result['score']}/{result['maximum']} | {'PASS' if result['passed'] else 'FAIL'} |\n"
        summary += "\nScores are supplied autograder points, not PDF marks. Q8 is excluded.\n"
        write_report(ROOT, results / "summary.md", summary)
        if summary_path:
            append_step_summary(ROOT, summary_path, summary)
        return 0 if len(records) == len(QUESTIONS) and all(r["passed"] for r in records) else 1
    except (OSError, ValueError, OutputSafetyError) as error:
        print(f"FAIL: search verification could not complete: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
