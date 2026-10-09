#!/usr/bin/env python3
"""Reject structural/protected-source changes against the recorded starter commit."""

from __future__ import annotations

import ast
import json
from pathlib import Path
import re
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
ALLOWLIST = {"src/search.py", "src/searchAgents.py"}


def git(root: Path, *arguments: str) -> bytes:
    return subprocess.run(["git", *arguments], cwd=root, check=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout


def parse_changes(raw: bytes) -> list[tuple[str, str, str, str]]:
    fields = raw.split(b"\0")
    records = []
    while fields and fields[-1] == b"":
        fields.pop()
    if len(fields) % 2:
        raise ValueError("malformed Git raw change records")
    for offset in range(0, len(fields), 2):
        header = fields[offset].decode("ascii").split()
        if len(header) != 5 or not header[0].startswith(":"):
            raise ValueError("malformed Git raw change header")
        records.append((header[4], fields[offset + 1].decode("utf-8", "surrogateescape"),
                        header[0][1:], header[1]))
    return records


def rejected_changes(records: list[tuple[str, str, str, str]]) -> list[str]:
    return [
        f"{status}: {name} ({old_mode} -> {new_mode})"
        for status, name, old_mode, new_mode in records
        if status != "M" or name not in ALLOWLIST
        or old_mode != new_mode or new_mode not in {"100644", "100755"}
    ]


def check(root: Path, policy: dict) -> list[str]:
    if (policy.get("schema") != 1
            or len(policy.get("editableFiles", [])) != 2
            or set(policy.get("editableFiles", [])) != ALLOWLIST
            or not re.fullmatch(r"[a-f0-9]{40}", policy.get("baselineCommit", ""))):
        raise ValueError("source policy must retain exactly the two-file edit boundary and a commit SHA")
    baseline = policy["baselineCommit"]
    git(root, "cat-file", "-e", f"{baseline}^{{commit}}")
    names = git(root, "ls-tree", "-r", "-z", "--name-only", baseline, "--", "src").split(b"\0")
    expected = {name.decode("utf-8", "surrogateescape") for name in names if name}
    if not ALLOWLIST.issubset(expected):
        raise ValueError("baseline does not contain both assignment implementation files")
    errors = rejected_changes(parse_changes(
        git(root, "diff", "--raw", "-z", "--no-renames", baseline, "--", "src")
    ))
    source = root / "src"
    if not source.is_dir() or source.is_symlink() or getattr(source, "is_junction", lambda: False)():
        return errors + ["src must be an existing regular directory"]
    current = set()
    for path in source.rglob("*"):
        name = path.relative_to(root).as_posix()
        if (path.is_symlink() or getattr(path, "is_junction", lambda: False)()
                or not path.resolve().is_relative_to(root.resolve())):
            errors.append(f"links and junctions are prohibited: {name}")
            continue
        if path.is_file():
            current.add(name)
            if path.suffix == ".py":
                try:
                    ast.parse(path.read_bytes(), filename=name)
                except (SyntaxError, ValueError) as error:
                    errors.append(f"invalid Python source: {name}: {error}")
    errors.extend(f"unexpected source file: {name}" for name in sorted(current - expected))
    errors.extend(f"missing source file: {name}" for name in sorted(expected - current))
    return errors


def main() -> int:
    try:
        policy = json.loads((ROOT / ".github/policies/source-policy.json").read_text(encoding="utf-8"))
        errors = check(ROOT, policy)
    except (OSError, ValueError, TypeError, subprocess.CalledProcessError) as error:
        print(f"FAIL: source boundary could not be verified: {error}")
        return 1
    for error in errors:
        print(f"FAIL: {error}")
    if errors:
        return 1
    print("PASS: existing two-file source boundary, protected starter files and Python syntax")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
