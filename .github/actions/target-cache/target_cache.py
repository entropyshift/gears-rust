#!/usr/bin/env python3
"""Helpers for the target/ cache. See target-cache.sh next to this file.

cargo decides what to rebuild by file mtimes. A fresh checkout gives every
file a new mtime, so a restored target/ would be rebuilt in full. The
manifest records the blob and mtime of every tracked file, and the mtime of
every directory above them, at the commit the cache was built from. `mtimes`
gives each file whose blob is the same as in the manifest its recorded mtime
back. Changed and new files get the current time, so cargo rebuilds exactly
what changed. Their checkout time is not enough: a run that saved after this
checkout restores outputs newer than it. Plain `git restore-mtime` is not
safe here: a PR with an older version of a file than the cache would get a
stale build.

Why the recorded mtime and not one old time for all: the archive also keeps outputs that
the saving run did not build, such as a test binary for a feature set it did
not use. Such an output may be older than a later change to its sources. The
recorded mtime is the time of that change, so cargo rebuilds the output when
a later run needs it again.

`plan` only decides whether a restore is worth its download time. It never
affects correctness: cargo still checks every unit.

  manifest OUT    write the manifest for the current checkout
  plan MANIFEST   print "restore ..." or "skip ..."
  mtimes MANIFEST set the recorded mtimes on unchanged tracked files
  prune LISTING KEEP...
                  print the archives in an S3 listing to delete
"""

import collections
import json
import os
import subprocess
import sys
import time
import tomllib
from datetime import datetime

# Skip the restore when more of the test binaries than this must be rebuilt.
MAX_REBUILD_SHARE = 0.6
# Changes here can change how every crate is built.
FULL_REBUILD_FILES = ("rust-toolchain.toml", ".cargo/")
# An archive that is neither current nor the previous one is left from an
# older, failed or overlapping save once it is this old. A younger one may
# belong to a save still in progress. Short, because main saves several times
# a day and each archive set is tens of GB.
PRUNE_AGE = 3 * 3600


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, check=True).stdout.decode()


def tracked_files():
    """path -> blob for tracked files, minus any the job changed."""
    files = {}
    for rec in git("ls-files", "-s", "-z").split("\0"):
        if not rec:
            continue
        meta, path = rec.split("\t", 1)
        mode, blob, _stage = meta.split()
        if mode != "160000":  # not a submodule
            files[path] = blob
    for path in git("diff", "--name-only", "-z").split("\0"):
        files.pop(path, None)
    return files


def read(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except OSError:
        return ""


def mtimes_of(files):
    """path -> mtime in ns for the files and every directory above them.

    Exact, not rounded to whole seconds like the outputs in the archive: for
    a build script that prints no `rerun-if` lines, cargo keeps the newest
    package file's exact mtime in the fingerprint, and any other value reruns
    the script and rebuilds the crate and everything that depends on it.
    """
    paths = set(files).union(*(ancestors(p) for p in files))
    return {p: os.lstat(p).st_mtime_ns for p in paths if os.path.lexists(p)}


def write_manifest(out):
    files = tracked_files()
    manifest = {
        "key": os.environ.get("KEY", ""),
        "commit": git("rev-parse", "HEAD").strip(),
        "archive": os.environ.get("ARCHIVE", ""),
        "files": files,
        "mtimes": mtimes_of(files),
        "cargo_lock": read("Cargo.lock"),
        "root_manifest": read("Cargo.toml"),
    }
    with open(out, "w", encoding="utf-8") as f:
        json.dump(manifest, f)
    print(f"manifest: {len(manifest['files'])} files at {manifest['commit'][:9]}")


def lock_changes(old, new):
    """Names of packages added, removed or changed in Cargo.lock."""
    def pkgs(text):
        try:
            data = tomllib.loads(text)
        except tomllib.TOMLDecodeError:
            return None
        return {(p["name"], p.get("version"), p.get("source")) for p in data.get("package", [])}

    a, b = pkgs(old), pkgs(new)
    if a is None or b is None:
        return None
    return {name for name, _, _ in a ^ b}


def root_changes(old, new):
    """Changed [workspace.dependencies] names, or None if anything else changed."""
    try:
        a, b = tomllib.loads(old), tomllib.loads(new)
    except tomllib.TOMLDecodeError:
        return None
    deps_a = a.get("workspace", {}).pop("dependencies", {})
    deps_b = b.get("workspace", {}).pop("dependencies", {})
    for doc in (a, b):
        doc.get("workspace", {}).pop("members", None)
        doc.get("workspace", {}).pop("exclude", None)
    if a != b:
        return None
    return {k for k in deps_a.keys() | deps_b.keys() if deps_a.get(k) != deps_b.get(k)}


def plan(manifest_path):
    with open(manifest_path, encoding="utf-8") as f:
        m = json.load(f)
    if m.get("key") != os.environ.get("KEY", ""):
        return "skip: toolchain, RUSTFLAGS or OS differ from the cache"
    cur = tracked_files()
    old = m["files"]
    if os.environ.get("SAVES") == "true" and old.get("Cargo.lock") != cur.get("Cargo.lock"):
        return "skip: Cargo.lock changed; building clean so the saved cache does not grow"
    changed = {p for p in cur.keys() | old.keys() if cur.get(p) != old.get(p)}
    if not changed:
        return "restore: no file changed since the cache"
    if any(p == f or (f.endswith("/") and p.startswith(f)) for p in changed for f in FULL_REBUILD_FILES):
        return "skip: toolchain or cargo config changed"

    meta = json.loads(subprocess.run(
        # --locked: never rewrite Cargo.lock, which would change its blob.
        ["cargo", "metadata", "--format-version", "1", "--locked"], capture_output=True, check=True,
    ).stdout)
    pkgs = {p["id"]: p for p in meta["packages"]}
    ws = set(meta["workspace_members"])
    by_name = collections.defaultdict(set)
    for pid, p in pkgs.items():
        by_name[p["name"]].add(pid)
    cwd = os.getcwd()
    dirs = {
        pid: os.path.relpath(os.path.dirname(pkgs[pid]["manifest_path"]), cwd).replace("\\", "/") + "/"
        for pid in ws
    }
    units = {
        pid: sum(
            1 for t in pkgs[pid]["targets"]
            if t["kind"][0] == "test" or (t["kind"][0] in ("lib", "proc-macro", "bin") and t.get("test", True))
        )
        for pid in ws
    }
    rdeps = collections.defaultdict(set)
    for node in meta["resolve"]["nodes"]:
        for dep in node["deps"]:
            rdeps[dep["pkg"]].add(node["id"])

    seeds = set()
    for path in changed:
        owner = max((pid for pid in ws if path.startswith(dirs[pid])), key=lambda pid: len(dirs[pid]), default=None)
        if owner:
            seeds.add(owner)
    if "Cargo.lock" in changed:
        names = lock_changes(m.get("cargo_lock", ""), read("Cargo.lock"))
        if names is None:
            return "skip: could not compare Cargo.lock"
        seeds |= {pid for n in names for pid in by_name.get(n, ())}
    if "Cargo.toml" in changed:
        names = root_changes(m.get("root_manifest", ""), read("Cargo.toml"))
        if names is None:
            return "skip: workspace settings in Cargo.toml changed"
        seeds |= {pid for n in names for pid in by_name.get(n, ())}

    affected, todo = set(seeds), list(seeds)
    while todo:
        for parent in rdeps[todo.pop()]:
            if parent not in affected:
                affected.add(parent)
                todo.append(parent)
    total = sum(units.values())
    share = sum(units[p] for p in affected if p in ws) / total
    verdict = "restore" if share <= MAX_REBUILD_SHARE else "skip"
    return f"{verdict}: about {share:.0%} of {total} test binaries need a rebuild"


def ancestors(path):
    parts = path.split("/")[:-1]
    return {"/".join(parts[:i]) or "." for i in range(len(parts) + 1)}


def set_mtimes(manifest_path):
    with open(manifest_path, encoding="utf-8") as f:
        m = json.load(f)
    old, recorded = m["files"], m.get("mtimes", {})
    cur = tracked_files()
    changed = {p for p in cur.keys() | old.keys() if cur.get(p) != old.get(p)}
    same = 0

    def restore(path):
        """Set the recorded mtime; the current time if none was recorded."""
        stamp = recorded.get(path)
        if stamp is None:
            os.utime(path, None)
            return False
        os.utime(path, ns=(stamp, stamp))
        return True

    for path in cur:
        if os.path.isfile(path) and not os.path.islink(path):
            if path in changed:
                os.utime(path, None)
            else:
                same += restore(path)
    # `rerun-if-changed=<dir>` makes cargo check directory mtimes too, and a
    # checkout creates every directory anew. The directories above a changed,
    # added or removed file get the current time: a removed file leaves no
    # other trace.
    keep = set().union(*(ancestors(p) for p in changed)) if changed else set()
    dirs = set().union(*(ancestors(p) for p in cur)) - keep
    for d in dirs:
        if os.path.isdir(d):
            restore(d)
    for d in keep:
        if os.path.isdir(d):
            os.utime(d, None)
    print(f"mtimes: {same} unchanged files and {len(dirs)} directories set as recorded; "
          f"{len(changed)} changed, added or removed files")


def stale_archives(listing, keep, now):
    """Archives in an `s3api list-objects-v2` listing to delete: all not in `keep`, once old."""
    stale = []
    for obj in listing.get("Contents") or []:
        key = obj["Key"]
        modified = datetime.fromisoformat(obj["LastModified"].replace("Z", "+00:00")).timestamp()
        if key.endswith(".tar.zst") and key not in keep and now - modified > PRUNE_AGE:
            stale.append(key)
    return stale


def prune(listing_path, *keep):
    text = read(listing_path).strip()
    for key in stale_archives(json.loads(text) if text else {}, set(keep), time.time()):
        print(key)


def main():
    cmd, arg = sys.argv[1], sys.argv[2]
    if cmd == "manifest":
        write_manifest(arg)
    elif cmd == "plan":
        print(plan(arg))
    elif cmd == "mtimes":
        set_mtimes(arg)
    elif cmd == "prune":
        prune(arg, *sys.argv[3:])
    else:
        sys.exit(f"unknown command {cmd}")


if __name__ == "__main__":
    main()
