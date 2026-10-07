#!/usr/bin/env python3
"""Unit tests for .github/actions/target-cache/target_cache.py.

    python3 -m unittest discover -s tools/scripts/tests
"""

from __future__ import annotations

import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / ".github" / "actions" / "target-cache"))

import target_cache as tc  # noqa: E402

DAY = 24 * 3600
HOUR = 3600


def lock(*pkgs):
    return "".join(f'[[package]]\nname = "{n}"\nversion = "{v}"\n\n' for n, v in pkgs)


class TestLockChanges(unittest.TestCase):
    def test_added_removed_and_changed_packages(self):
        old = lock(("a", "1.0.0"), ("b", "1.0.0"), ("c", "1.0.0"))
        new = lock(("a", "1.0.0"), ("b", "1.1.0"), ("d", "1.0.0"))
        self.assertEqual(tc.lock_changes(old, new), {"b", "c", "d"})

    def test_same_lock_has_no_changes(self):
        text = lock(("a", "1.0.0"))
        self.assertEqual(tc.lock_changes(text, text), set())

    def test_unreadable_lock_is_none(self):
        self.assertIsNone(tc.lock_changes("[[package]\n", lock(("a", "1.0.0"))))


class TestRootChanges(unittest.TestCase):
    BASE = """\
[workspace]
members = ["a"]
resolver = "2"

[workspace.dependencies]
serde = "1"
tokio = "1"
"""

    def test_changed_workspace_dependency_names(self):
        new = self.BASE.replace('tokio = "1"', 'tokio = "1.40"\nrand = "0.9"')
        self.assertEqual(tc.root_changes(self.BASE, new), {"tokio", "rand"})

    def test_members_do_not_count(self):
        new = self.BASE.replace('members = ["a"]', 'members = ["a", "b"]')
        self.assertEqual(tc.root_changes(self.BASE, new), set())

    def test_other_settings_are_none(self):
        new = self.BASE.replace('resolver = "2"', 'resolver = "3"')
        self.assertIsNone(tc.root_changes(self.BASE, new))
        self.assertIsNone(tc.root_changes(self.BASE, self.BASE + "\n[profile.dev]\nopt-level = 1\n"))


class TestAncestors(unittest.TestCase):
    def test_every_directory_up_to_the_root(self):
        self.assertEqual(tc.ancestors("a/b/c.rs"), {".", "a", "a/b"})
        self.assertEqual(tc.ancestors("top.rs"), {"."})


class TestStaleArchives(unittest.TestCase):
    NOW = 1_800_000_000

    def obj(self, key, age):
        stamp = time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime(self.NOW - age))
        return {"Key": key, "LastModified": stamp}

    def test_old_archives_but_the_kept_ones(self):
        listing = {"Contents": [
            self.obj("t/Linux.aaa.1-1.tar.zst", 3 * DAY),   # kept: named by the new manifest
            self.obj("t/Linux.ddd.0-1.tar.zst", 5 * DAY),   # kept: previous, may be downloading
            self.obj("t/Linux.bbb.2-1.tar.zst", 2 * DAY),   # orphan
            self.obj("t/Linux.tar.zst", 9 * DAY),           # old format
            self.obj("t/Linux.ccc.3-1.tar.zst", 2 * HOUR),  # may be a save in progress
            self.obj("t/Linux.eee.4-1.tar.zst", 4 * HOUR),  # orphan, past the prune age
            self.obj("t/Linux.manifest.json", 9 * DAY),     # not an archive
        ]}
        keep = {"t/Linux.aaa.1-1.tar.zst", "t/Linux.ddd.0-1.tar.zst"}
        self.assertEqual(tc.stale_archives(listing, keep, self.NOW),
                         ["t/Linux.bbb.2-1.tar.zst", "t/Linux.tar.zst", "t/Linux.eee.4-1.tar.zst"])

    def test_empty_listing(self):
        self.assertEqual(tc.stale_archives({}, {"k"}, self.NOW), [])
        self.assertEqual(tc.stale_archives({"Contents": None}, {"k"}, self.NOW), [])

    def test_prune_keeps_every_named_archive(self):
        listing = {"Contents": [
            self.obj("t/Linux.new.2-1.tar.zst", 2 * DAY),
            self.obj("t/Linux.old.1-1.tar.zst", 3 * DAY),
            self.obj("t/Linux.older.0-1.tar.zst", 4 * DAY),
        ]}
        with tempfile.TemporaryDirectory() as d:
            path = Path(d, "listing.json")
            path.write_text(json.dumps(listing))
            out = io.StringIO()
            with contextlib.redirect_stdout(out), mock.patch.object(tc.time, "time", return_value=self.NOW):
                tc.prune(str(path), "t/Linux.new.2-1.tar.zst", "t/Linux.old.1-1.tar.zst")
            self.assertEqual(out.getvalue(), "t/Linux.older.0-1.tar.zst\n")

    def test_prune_reads_an_empty_listing_file(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d, "listing.json")
            path.write_text("\n")
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                tc.prune(str(path), "k")
            self.assertEqual(out.getvalue(), "")


class GitRepoTest(unittest.TestCase):
    """Runs each test in a fresh git repository."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.cwd = os.getcwd()
        os.chdir(self.tmp.name)
        self.addCleanup(os.chdir, self.cwd)
        self.git("init", "-q")

    def git(self, *args):
        subprocess.run(
            ["git", "-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false", *args],
            check=True, capture_output=True,
        )

    def write(self, path, text):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(text)

    def commit(self, files):
        for path, text in files.items():
            self.write(path, text)
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "c")

    def manifest(self, **env):
        path = os.path.join(self.tmp.name, "manifest.json")
        with mock.patch.dict(os.environ, env), contextlib.redirect_stdout(io.StringIO()):
            tc.write_manifest(path)
        return path


def mtime(path):
    return os.stat(path).st_mtime_ns


def set_all(paths, stamp):
    for path in paths:
        os.utime(path, (stamp, stamp))


class TestSetMtimes(GitRepoTest):
    def set_mtimes(self, manifest):
        with contextlib.redirect_stdout(io.StringIO()):
            tc.set_mtimes(manifest)

    def test_unchanged_files_get_the_recorded_mtime_and_changed_files_get_now(self):
        self.commit({"a/x.rs": "1", "a/y.rs": "1", "b/z.rs": "1", "c/gone.rs": "1"})
        set_all(("a/x.rs", "a/y.rs", "b/z.rs", "c/gone.rs", "a", "b", "c", "."), 1_000_000_000)
        manifest = self.manifest()
        Path("c/gone.rs").unlink()
        self.commit({"a/x.rs": "2", "d/new.rs": "1"})
        # A checkout made before the restore: older than the restored outputs.
        set_all(("a/x.rs", "a/y.rs", "b/z.rs", "d/new.rs", "a", "b", "c", "d", "."), time.time() - 600)

        start = time.time_ns() - 10**9
        self.set_mtimes(manifest)

        for path in ("a/y.rs", "b/z.rs", "b"):
            self.assertEqual(mtime(path), 1_000_000_000 * 10**9, path)
        # Changed, added, and the directories above them and above a removed file.
        for path in ("a/x.rs", "d/new.rs", "a", "c", "d", "."):
            self.assertGreaterEqual(mtime(path), start, path)

    def test_a_change_keeps_its_time_in_later_caches(self):
        # Run A builds every variant; run B changes x.rs but builds only some
        # variants, so the archive keeps A's outputs for the rest. Run C must
        # still see x.rs as newer than A's outputs.
        self.commit({"a/x.rs": "1"})
        set_all(("a/x.rs", "a", "."), 1_000_000_000)
        manifest_a = self.manifest()
        a_outputs = 1_000_000_100 * 10**9
        self.commit({"a/x.rs": "2"})
        self.set_mtimes(manifest_a)
        changed_in_b = {p: mtime(p) for p in ("a/x.rs", "a")}
        self.assertGreater(min(changed_in_b.values()), a_outputs)
        manifest_b = self.manifest()
        self.commit({"docs.md": "new"})
        set_all(("a/x.rs", "a", "."), time.time() + 600)

        self.set_mtimes(manifest_b)

        self.assertEqual({p: mtime(p) for p in changed_in_b}, changed_in_b)

    def test_a_path_with_no_recorded_mtime_gets_now(self):
        self.commit({"a/x.rs": "1"})
        manifest = self.manifest()
        with open(manifest) as f:
            m = json.load(f)
        del m["mtimes"]
        with open(manifest, "w") as f:
            json.dump(m, f)
        set_all(("a/x.rs", "a", "."), 1_000_000_000)

        start = time.time_ns() - 10**9
        self.set_mtimes(manifest)

        for path in ("a/x.rs", "a", "."):
            self.assertGreaterEqual(mtime(path), start, path)


class TestPlan(GitRepoTest):
    def setUp(self):
        super().setUp()
        self.commit({"Cargo.lock": lock(("a", "1.0.0")), "rust-toolchain.toml": "1", "src/a.rs": "1"})

    def plan(self, manifest, **env):
        with mock.patch.dict(os.environ, {"KEY": "k", "SAVES": "false", **env}):
            return tc.plan(manifest)

    def test_other_key_skips(self):
        manifest = self.manifest(KEY="old")
        self.assertTrue(self.plan(manifest).startswith("skip: toolchain"))

    def test_no_change_restores(self):
        manifest = self.manifest(KEY="k")
        self.assertEqual(self.plan(manifest), "restore: no file changed since the cache")

    def test_lock_change_skips_only_when_the_run_saves(self):
        manifest = self.manifest(KEY="k")
        self.commit({"Cargo.lock": lock(("a", "1.1.0"))})
        self.assertTrue(self.plan(manifest, SAVES="true").startswith("skip: Cargo.lock changed"))

    def test_toolchain_change_skips(self):
        manifest = self.manifest(KEY="k")
        self.commit({"rust-toolchain.toml": "2"})
        self.assertEqual(self.plan(manifest), "skip: toolchain or cargo config changed")


class TestPlanAffected(GitRepoTest):
    """`plan` past the key checks, with a fake `cargo metadata`: b uses a, c stands alone."""

    def setUp(self):
        super().setUp()
        self.commit({
            "Cargo.lock": lock(("a", "1.0.0"), ("b", "1.0.0"), ("c", "1.0.0")),
            "rust-toolchain.toml": "1",
            **{f"{p}/Cargo.toml": "" for p in "abc"},
            **{f"{p}/src/lib.rs": "1" for p in "abc"},
        })
        self.cargo_calls = []

    def metadata(self):
        root = os.getcwd()
        pkg = lambda n: {"id": n, "name": n, "manifest_path": os.path.join(root, n, "Cargo.toml"),
                         "targets": [{"kind": ["lib"]}, {"kind": ["test"]}]}
        return {
            "packages": [pkg(n) for n in "abc"],
            "workspace_members": list("abc"),
            "resolve": {"nodes": [{"id": "a", "deps": []}, {"id": "b", "deps": [{"pkg": "a"}]},
                                  {"id": "c", "deps": []}]},
        }

    def plan(self, manifest):
        real = subprocess.run

        def run(cmd, *args, **kwargs):
            if cmd[0] == "cargo":
                self.cargo_calls.append(cmd)
                return subprocess.CompletedProcess(cmd, 0, json.dumps(self.metadata()).encode(), b"")
            return real(cmd, *args, **kwargs)

        with mock.patch.dict(os.environ, {"KEY": "k", "SAVES": "false"}), \
                mock.patch.object(tc.subprocess, "run", side_effect=run):
            return tc.plan(manifest)

    def test_a_change_also_rebuilds_its_dependents(self):
        manifest = self.manifest(KEY="k")
        self.commit({"a/src/lib.rs": "2"})
        # a and b: 4 of 6 test binaries, above the 60% limit.
        self.assertEqual(self.plan(manifest), "skip: about 67% of 6 test binaries need a rebuild")

    def test_a_leaf_change_restores(self):
        manifest = self.manifest(KEY="k")
        self.commit({"c/src/lib.rs": "2"})
        self.assertEqual(self.plan(manifest), "restore: about 33% of 6 test binaries need a rebuild")

    def test_a_lock_change_seeds_the_changed_packages(self):
        manifest = self.manifest(KEY="k")
        self.commit({"Cargo.lock": lock(("a", "1.0.0"), ("b", "1.0.0"), ("c", "1.1.0"))})
        self.assertEqual(self.plan(manifest), "restore: about 33% of 6 test binaries need a rebuild")

    def test_a_file_outside_the_packages_rebuilds_nothing(self):
        manifest = self.manifest(KEY="k")
        self.commit({"docs/x.md": "new"})
        self.assertEqual(self.plan(manifest), "restore: about 0% of 6 test binaries need a rebuild")

    def test_metadata_never_rewrites_the_lockfile(self):
        manifest = self.manifest(KEY="k")
        self.commit({"c/src/lib.rs": "2"})
        self.plan(manifest)
        self.assertIn("--locked", self.cargo_calls[0])


class TestWriteManifest(GitRepoTest):
    def test_records_commit_archive_and_blobs(self):
        self.commit({"Cargo.lock": "lock", "Cargo.toml": "toml", "src/a.rs": "1"})
        self.write("src/a.rs", "changed in the job")
        os.utime("Cargo.lock", ns=(1_000_000_000_700_000_000, 1_000_000_000_700_000_000))
        with open(self.manifest(KEY="k", ARCHIVE="t/Linux.c.1-1.tar.zst")) as f:
            m = json.load(f)
        self.assertEqual(m["key"], "k")
        self.assertEqual(m["archive"], "t/Linux.c.1-1.tar.zst")
        self.assertEqual(m["cargo_lock"], "lock")
        self.assertEqual(m["root_manifest"], "toml")
        # A file the job changed has no committed blob to match.
        self.assertEqual(sorted(m["files"]), ["Cargo.lock", "Cargo.toml"])
        # The exact mtimes of those files and the directories above them.
        self.assertEqual(sorted(m["mtimes"]), [".", "Cargo.lock", "Cargo.toml"])
        self.assertEqual(m["mtimes"]["Cargo.lock"], 1_000_000_000_700_000_000)


if __name__ == "__main__":
    unittest.main()
