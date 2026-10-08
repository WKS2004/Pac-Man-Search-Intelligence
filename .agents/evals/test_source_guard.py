#!/usr/bin/env python3
"""Recovery regression cases on isolated temporary source trees only."""

import contextlib
import copy
import importlib.util
import io
import json
import os
from pathlib import Path
import stat
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "source_guard.py"
SPEC = importlib.util.spec_from_file_location("pacman_source_guard", SCRIPT)
guard = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(guard)


class RecoveryCases(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="pacman-guard-test-")
        self.root = Path(self.temporary.name).resolve()
        # Verify that recursive fixture cleanup is confined to system temp.
        self.assertTrue(self.root.is_relative_to(Path(tempfile.gettempdir()).resolve()))
        self.addCleanup(self.temporary.cleanup)
        (self.root / "src").mkdir()
        (self.root / "src" / "layouts").mkdir()
        for name, data in {
            "search.py": b"original search\r\n",
            "searchAgents.py": b"original agents\n",
            "util.py": b"pre-existing USER edit\r\n\x00",
            "untracked.txt": b"pre-existing untracked USER file\n",
            "layouts/maze.lay": b"original maze\n",
        }.items():
            (self.root / "src" / name).write_bytes(data)
        self.snapshot = guard.capture(self.root)

    def owned(self, *names):
        current = guard.inventory(self.root)
        return {name: guard.fingerprint(current.get(name)) for name in names}

    def assert_restored(self, result):
        self.assertTrue(result["rejected"])
        self.assertFalse(result["unresolved"], result)
        self.assertFalse(result["errors"], result)
        self.assertEqual(guard.check(self.root, self.snapshot)["rejected"], {})

    def test_clean_read_only_tree(self):
        result = guard.check(self.root, self.snapshot)
        self.assertEqual(result, {"rejected": {}, "restored": [], "unresolved": [], "errors": []})

    def test_protected_overwrite_restores_preexisting_user_bytes_and_metadata(self):
        path = self.root / "src/util.py"
        path.write_bytes(b"agent overwrite")
        self.assert_restored(guard.check(self.root, self.snapshot, owned=self.owned("src/util.py")))
        self.assertEqual(path.read_bytes(), b"pre-existing USER edit\r\n\x00")
        self.assertEqual(path.stat().st_mtime_ns, self.snapshot["entries"]["src/util.py"]["mtime_ns"])

    def test_both_allowed_edits_survive_only_with_authorization(self):
        for name in ("search.py", "searchAgents.py"):
            (self.root / "src" / name).write_bytes(b"authorized implementation")
        self.assertFalse(guard.check(self.root, self.snapshot, authorized=True)["rejected"])
        result = guard.check(self.root, self.snapshot,
                             owned=self.owned("src/search.py", "src/searchAgents.py"))
        self.assert_restored(result)

    def test_allowed_file_deletion_is_rejected_even_when_authorized(self):
        (self.root / "src/search.py").unlink()
        result = guard.check(self.root, self.snapshot, authorized=True,
                             owned=self.owned("src/search.py"))
        self.assert_restored(result)

    def test_deleted_nested_directory_and_files_are_recreated(self):
        (self.root / "src/layouts/maze.lay").unlink()
        (self.root / "src/layouts").rmdir()
        result = guard.check(self.root, self.snapshot,
                             owned=self.owned("src/layouts", "src/layouts/maze.lay"))
        self.assert_restored(result)

    def test_agent_created_file_and_directory_are_removed(self):
        (self.root / "src/cache").mkdir()
        (self.root / "src/cache/output.txt").write_bytes(b"generated side effect")
        result = guard.check(self.root, self.snapshot, authorized=True,
                             owned=self.owned("src/cache", "src/cache/output.txt"))
        self.assert_restored(result)

    def test_rename_recovers_both_paths(self):
        (self.root / "src/untracked.txt").rename(self.root / "src/renamed.txt")
        result = guard.check(self.root, self.snapshot,
                             owned=self.owned("src/untracked.txt", "src/renamed.txt"))
        self.assert_restored(result)

    def test_unknown_concurrent_user_edit_is_never_restored(self):
        path = self.root / "src/util.py"
        path.write_bytes(b"user concurrent change")
        result = guard.check(self.root, self.snapshot)
        self.assertEqual(result["unresolved"], ["src/util.py"])
        self.assertFalse(result["restored"])
        self.assertEqual(path.read_bytes(), b"user concurrent change")

    def test_stale_agent_fingerprint_preserves_newer_user_edit(self):
        path = self.root / "src/util.py"
        path.write_bytes(b"agent violation")
        owned = self.owned("src/util.py")
        path.write_bytes(b"newer USER edit")
        result = guard.check(self.root, self.snapshot, owned=owned)
        self.assertEqual(result["unresolved"], ["src/util.py"])
        self.assertFalse(result["restored"])
        self.assertEqual(path.read_bytes(), b"newer USER edit")

    def test_unknown_contents_prevent_directory_deletion(self):
        (self.root / "src/new").mkdir()
        (self.root / "src/new/user.txt").write_bytes(b"user added this")
        result = guard.check(self.root, self.snapshot, owned=self.owned("src/new"))
        self.assertTrue(result["unresolved"])
        self.assertTrue(result["errors"])
        self.assertEqual((self.root / "src/new/user.txt").read_bytes(), b"user added this")

    def test_type_replacement_recovers_original_file(self):
        path = self.root / "src/util.py"
        path.unlink()
        path.mkdir()
        result = guard.check(self.root, self.snapshot, owned=self.owned("src/util.py"))
        self.assert_restored(result)

    def test_metadata_only_change_is_rejected_and_restored(self):
        path = self.root / "src/util.py"
        old = path.stat()
        os.utime(path, ns=(old.st_atime_ns, old.st_mtime_ns + 10_000_000))
        self.assert_restored(guard.check(self.root, self.snapshot, owned=self.owned("src/util.py")))

    def test_agent_readonly_permission_change_is_restored(self):
        path = self.root / "src/util.py"
        os.chmod(path, stat.S_IRUSR)
        self.assert_restored(guard.check(self.root, self.snapshot, owned=self.owned("src/util.py")))

    def test_agent_created_readonly_file_is_removed(self):
        path = self.root / "src/generated.txt"
        path.write_bytes(b"agent output")
        os.chmod(path, stat.S_IRUSR)
        self.assert_restored(guard.check(self.root, self.snapshot, owned=self.owned("src/generated.txt")))

    def test_tampered_snapshot_and_path_escape_are_rejected(self):
        corrupt = copy.deepcopy(self.snapshot)
        corrupt["entries"]["src/util.py"]["data"] = "Y29ycnVwdA=="
        with self.assertRaises(ValueError):
            guard.check(self.root, corrupt)
        for name in ("src/../outside", "src\\util.py", "src/C:bad", "/src/util.py"):
            with self.assertRaises(ValueError):
                guard.safe_path(self.root, name)

    def test_recovered_violation_still_returns_failure_from_cli(self):
        baseline_path = self.root / "snapshot.json"
        baseline_path.write_text(json.dumps(self.snapshot), encoding="utf-8")
        (self.root / "src/util.py").write_bytes(b"agent violation")
        token = self.owned("src/util.py")["src/util.py"]
        arguments = [str(SCRIPT), "check", str(baseline_path), "--owned", f"src/util.py={token}"]
        with patch.object(guard, "ROOT", self.root), patch.object(sys, "argv", arguments):
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(guard.main(), 1)
        self.assertFalse(guard.check(self.root, self.snapshot)["rejected"])

    def test_cli_snapshot_can_use_persistent_temporary_storage(self):
        arguments = [str(SCRIPT), "snapshot", "--directory", str(self.root)]
        output = io.StringIO()
        with patch.object(guard, "ROOT", self.root), patch.object(sys, "argv", arguments):
            with contextlib.redirect_stdout(output):
                self.assertEqual(guard.main(), 0)
        snapshot_path = Path(output.getvalue().strip())
        self.assertEqual(snapshot_path.parent, self.root)
        saved = json.loads(snapshot_path.read_text(encoding="utf-8"))
        self.assertFalse(guard.check(self.root, saved)["rejected"])

    def test_cli_cannot_store_snapshot_inside_source(self):
        arguments = [str(SCRIPT), "snapshot", "--directory", str(self.root / "src")]
        with patch.object(guard, "ROOT", self.root), patch.object(sys, "argv", arguments):
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(guard.main(), 2)
        self.assertFalse(guard.check(self.root, self.snapshot)["rejected"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
