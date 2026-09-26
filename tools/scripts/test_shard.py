#!/usr/bin/env python3
"""
Print the `-p` arguments for one shard of the `make test-no-macros` package set.

CI splits a slow OS leg across runners (`make test-no-macros TEST_SHARD=1/2`).
Every workspace member except the EXCLUDED ones lands in exactly one shard, so
together the shards run the same tests as one `--workspace` run.

Packages are balanced by the size of their Rust sources (tests included),
largest first, each into the currently lightest shard. Source size tracks the
cost that matters, compiling and linking test binaries, closely: against the
macOS cargo timings of CI run 36195700995 it correlates at 0.96, and the
resulting two shards differ by ~6%. New crates are placed automatically.

Usage:
  test_shard.py INDEX/COUNT        e.g. 1/2

Exit codes:
  0 - Arguments printed on stdout
  1 - Bad arguments, or `cargo metadata` failed
"""

import json
import os
import subprocess
import sys
from pathlib import Path

# Keep in sync with the `--exclude` list of `test-no-macros` in the Makefile.
EXCLUDED = {"cf-gears-toolkit-macros-tests", "cf-gears-toolkit-db-macros"}


def source_bytes(package_dir: Path) -> int:
    """Total size of *.rs files in a package, not descending into nested packages."""
    total = 0
    for root, dirs, files in os.walk(package_dir):
        root_path = Path(root)
        if root_path != package_dir and (root_path / "Cargo.toml").exists():
            dirs[:] = []
            continue
        dirs[:] = [d for d in dirs if d != "target"]
        total += sum((root_path / f).stat().st_size for f in files if f.endswith(".rs"))
    return total


def shard_packages(index: int, count: int) -> list[str]:
    metadata = json.loads(
        subprocess.run(
            ["cargo", "metadata", "--no-deps", "--format-version", "1"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout
    )
    members = set(metadata["workspace_members"])
    weights = {
        p["name"]: source_bytes(Path(p["manifest_path"]).parent)
        for p in metadata["packages"]
        if p["id"] in members and p["name"] not in EXCLUDED
    }
    shards: list[list] = [[0, []] for _ in range(count)]
    for name in sorted(weights, key=lambda n: (-weights[n], n)):
        lightest = min(shards, key=lambda s: s[0])
        lightest[0] += weights[name]
        lightest[1].append(name)
    return sorted(shards[index - 1][1])


def main(argv: list[str]) -> int:
    try:
        index, count = (int(x) for x in argv[0].split("/"))
        if not 1 <= index <= count:
            raise ValueError
    except (IndexError, ValueError):
        print("usage: test_shard.py INDEX/COUNT (e.g. 1/2)", file=sys.stderr)
        return 1
    try:
        packages = shard_packages(index, count)
    except subprocess.CalledProcessError as e:
        print(f"cargo metadata failed:\n{e.stderr}", file=sys.stderr)
        return 1
    print(" ".join(f"-p {p}" for p in packages))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
