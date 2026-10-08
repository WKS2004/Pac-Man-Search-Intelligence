#!/usr/bin/env python3
"""Explicit source integrity gate and provenance-checked recovery, not a watcher."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat
import sys
import tempfile

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
ALLOWLIST = {"src/search.py", "src/searchAgents.py"}


def fingerprint(entry: dict | None) -> str:
    if entry is None:
        return "missing"
    if entry["kind"] == "directory":
        return "directory"
    state = {key: entry[key] for key in ("kind", "sha256", "mode", "mtime_ns")}
    return hashlib.sha256(json.dumps(state, sort_keys=True).encode()).hexdigest()


def safe_path(root: Path, name: str) -> Path:
    parts = PurePosixPath(name).parts
    if (
        not parts or parts[0] != "src" or ".." in parts
        or "\\" in name or ":" in name or PurePosixPath(name).as_posix() != name
    ):
        raise ValueError(f"unsafe source path: {name!r}")
    destination = root.joinpath(*parts)
    for candidate in (destination, *destination.parents):
        if candidate == root:
            break
        if candidate.is_symlink() or getattr(candidate, "is_junction", lambda: False)():
            raise ValueError(f"links/junctions cannot be guarded: {candidate}")
        # Also catches junctions on interpreters without Path.is_junction().
        if not candidate.resolve().is_relative_to(root):
            raise ValueError(f"source path escapes repository: {name}")
    return destination


def read_entry(path: Path, include_data: bool = False) -> dict | None:
    try:
        before = path.stat()
    except FileNotFoundError:
        return None
    if stat.S_ISDIR(before.st_mode):
        return {"kind": "directory"}
    if not stat.S_ISREG(before.st_mode):
        raise ValueError(f"unsupported source entry: {path}")
    data = path.read_bytes()
    after = path.stat()
    if (before.st_mtime_ns, before.st_size, before.st_mode) != (
        after.st_mtime_ns, after.st_size, after.st_mode,
    ):
        raise ValueError(f"source changed while reading: {path}")
    result = {
        "kind": "file", "sha256": hashlib.sha256(data).hexdigest(),
        "mode": stat.S_IMODE(after.st_mode), "mtime_ns": after.st_mtime_ns,
        "atime_ns": before.st_atime_ns,
    }
    if include_data:
        result["data"] = base64.b64encode(data).decode("ascii")
    return result


def inventory(root: Path, include_data: bool = False) -> dict:
    source = safe_path(root, "src")
    if not source.exists():
        return {}
    if not source.is_dir():
        raise ValueError("src must remain a directory")
    paths = [source]
    for directory, folders, files in os.walk(source, followlinks=False):
        for name in folders + files:
            path = Path(directory) / name
            safe_path(root, path.relative_to(root).as_posix())
            paths.append(path)
    entries = {}
    for path in paths:
        name = path.relative_to(root).as_posix()
        entry = read_entry(safe_path(root, name), include_data)
        if entry is None:
            raise ValueError(f"source disappeared while reading: {name}")
        entries[name] = entry
    return entries


def capture(root: Path) -> dict:
    root = root.resolve(strict=True)
    entries = inventory(root, include_data=True)
    if not entries:
        raise ValueError("cannot snapshot missing src")
    # A second pass detects intervening writes while capturing the tree.
    if {p: fingerprint(e) for p, e in entries.items()} != {
        p: fingerprint(e) for p, e in inventory(root).items()
    }:
        raise ValueError("source changed during snapshot; do not proceed")
    return {"schema": 1, "root": str(root), "entries": entries}


def validate_snapshot(root: Path, snapshot: dict) -> None:
    if snapshot.get("schema") != 1 or snapshot.get("root") != str(root.resolve()):
        raise ValueError("snapshot belongs to another repository or schema")
    entries = snapshot.get("entries")
    if not isinstance(entries, dict) or entries.get("src") != {"kind": "directory"}:
        raise ValueError("snapshot must contain the source directory")
    for name, entry in entries.items():
        safe_path(root, name)
        if entry.get("kind") not in {"file", "directory"}:
            raise ValueError(f"invalid snapshot entry: {name}")
        if name != "src" and entries.get(PurePosixPath(name).parent.as_posix()) != {
            "kind": "directory",
        }:
            raise ValueError(f"snapshot lacks parent directory: {name}")
        if entry["kind"] == "file":
            data = base64.b64decode(entry["data"], validate=True)
            if hashlib.sha256(data).hexdigest() != entry["sha256"]:
                raise ValueError(f"snapshot bytes fail integrity check: {name}")
            if not all(isinstance(entry[key], int) for key in ("mode", "mtime_ns", "atime_ns")):
                raise ValueError(f"invalid file metadata: {name}")


def violations(snapshot: dict, current: dict, authorized: bool = False) -> list[str]:
    original = snapshot["entries"]
    rejected = []
    for name in sorted(original.keys() | current.keys()):
        old, new = original.get(name), current.get(name)
        if fingerprint(old) == fingerprint(new):
            continue
        if (authorized and name in ALLOWLIST and old and new
                and old["kind"] == new["kind"] == "file"
                and old["mode"] == new["mode"]):
            continue
        rejected.append(name)
    return rejected


def check(root: Path, snapshot: dict, authorized: bool = False,
          owned: dict[str, str] | None = None) -> dict:
    """Ownership is attested from agent action evidence, never inferred from a diff."""
    root = root.resolve(strict=True)
    validate_snapshot(root, snapshot)
    current = inventory(root)
    rejected = violations(snapshot, current, authorized)
    original = snapshot["entries"]
    owned = owned or {}
    eligible = {name for name in rejected if owned.get(name) == fingerprint(current.get(name))}
    restored, errors = [], []

    def still_owned(name: str) -> Path:
        path = safe_path(root, name)
        if fingerprint(read_entry(path)) != owned[name]:
            raise ValueError(f"concurrent change; refusing recovery: {name}")
        return path

    # Remove new entries and type replacements from the leaves upward. rmdir
    # never recursively deletes; unexpected/user-owned contents block recovery.
    for name in sorted(eligible, key=lambda p: (p.count("/"), p), reverse=True):
        old, new = original.get(name), current.get(name)
        if new is None or (old and old["kind"] == new["kind"]):
            continue
        try:
            path = still_owned(name)
            if new["kind"] == "directory":
                path.rmdir()
            else:
                os.chmod(path, current[name]["mode"] | stat.S_IWUSR)
                path.unlink()
            if old is None:
                restored.append(name)
        except (OSError, ValueError) as error:
            errors.append(str(error))

    # Recreate only baseline directories whose disappearance is agent-owned.
    for name in sorted(eligible, key=lambda p: (p.count("/"), p)):
        old = original.get(name)
        if not old or old["kind"] != "directory":
            continue
        try:
            path = safe_path(root, name)
            if path.exists():
                raise ValueError(f"unexpected entry blocks directory recovery: {name}")
            # A replacement already removed above must still be absent.
            if current.get(name) is None:
                still_owned(name)
            path.mkdir()
            restored.append(name)
        except (OSError, ValueError) as error:
            errors.append(str(error))

    for name in sorted(eligible):
        old = original.get(name)
        if not old or old["kind"] != "file":
            continue
        try:
            path = safe_path(root, name)
            if current.get(name) and current[name]["kind"] != "file":
                if path.exists():
                    raise ValueError(f"unexpected entry blocks file recovery: {name}")
            else:
                still_owned(name)
            if not path.parent.is_dir():
                raise ValueError(f"unrestored parent blocks file recovery: {name}")
            data = base64.b64decode(old["data"], validate=True)
            if path.exists():
                os.chmod(path, old["mode"] | stat.S_IWUSR)
            try:
                path.write_bytes(data)
            finally:
                if path.is_file():
                    os.chmod(path, old["mode"])
            os.utime(path, ns=(old["atime_ns"], old["mtime_ns"]))
            if fingerprint(read_entry(path)) != fingerprint(old):
                raise ValueError(f"recovery verification failed: {name}")
            restored.append(name)
        except (OSError, ValueError) as error:
            errors.append(str(error))

    remaining = violations(snapshot, inventory(root), authorized)
    return {
        "rejected": {name: fingerprint(current.get(name)) for name in rejected},
        "restored": restored, "unresolved": remaining, "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    snapshotter = commands.add_parser("snapshot", help="capture source to private temporary storage")
    snapshotter.add_argument("--directory", type=Path,
                             help="existing persistent temporary directory, outside source/reference trees")
    checker = commands.add_parser("check", help="reject differences and restore attested agent changes")
    checker.add_argument("snapshot", type=Path)
    checker.add_argument("--authorized-source-edit", action="store_true")
    checker.add_argument("--owned", action="append", default=[], metavar="PATH=FINGERPRINT")
    args = parser.parse_args()
    try:
        if args.command == "snapshot":
            snapshot = capture(ROOT)
            directory = args.directory.resolve(strict=True) if args.directory else None
            reference = Path(r"D:\WKS\Projects\BLUEVERSE").resolve()
            if directory and (not directory.is_dir()
                              or directory.is_relative_to((ROOT / "src").resolve())
                              or directory.is_relative_to(reference)):
                raise ValueError("snapshot directory must be outside source and BLUEVERSE")
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", prefix="pacman-source-",
                                             suffix=".json", delete=False, dir=directory) as output:
                json.dump(snapshot, output)
                print(output.name)
            return 0
        owned = {}
        for item in args.owned:
            name, separator, token = item.partition("=")
            if not separator or not token or name in owned:
                raise ValueError("--owned needs a unique PATH=FINGERPRINT from agent evidence")
            safe_path(ROOT, name)
            owned[name] = token
        snapshot = json.loads(args.snapshot.read_text(encoding="utf-8"))
        result = check(ROOT, snapshot, args.authorized_source_edit, owned)
        print(json.dumps(result, indent=2))
        # Recovery never turns the violating operation into a passing operation.
        return 1 if result["rejected"] or result["errors"] or result["unresolved"] else 0
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"REJECTED: source integrity gate failed: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
