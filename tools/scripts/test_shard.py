#!/usr/bin/env python3
"""
Print the cargo arguments for one shard of the `make test-no-macros` package set.

CI splits a slow OS leg across runners (`make test-no-macros TEST_SHARD=1/2`).
Every workspace member except the EXCLUDED ones lands in exactly one shard, so
together the shards run the same tests as one `--workspace` run.

A package subset unifies features differently from `--workspace`: a member can
lose a feature that only another member turns on, and with it every test
behind `#[cfg(feature = ...)]`. Run 36229001448 lost six that way
(cf-gears-oagw-sdk without `axum`, cf-gears-toolkit-utils without `schemars`).
So each shard also passes `--features` for its own members, set to the
features `cargo metadata` resolves for them across the whole workspace, which
keeps their `cfg(feature)` surface identical to a `--workspace` run.

Packages are weighted by the size of their Rust sources (tests included),
plus EXTRA_WEIGHT_SHARE for packages whose test run is unusually expensive.
Source size tracks the cost that matters, compiling and linking test binaries,
closely: against the macOS cargo timings of CI run 36195700995 it correlates
at 0.96. New crates are placed automatically.

The split must also be stable. A package that changes shard changes its
neighbours, and so the feature sets its dependencies build with, and every
such crate misses the sccache cache on that shard. The first version filled
the lightest shard largest-first; after merging 24 upstream commits, 10
packages swapped between the macOS shards (CI run 36236536073) and one shard's
build went from ~16 to 27 min. In a simulation with +-3% size drift that
scheme moved a median of 50 packages. Now only the few HEAVY packages (at
least HEAVY_SHARE of the total, placed first, largest into the lightest
shard) are balanced that way, since their order rarely changes; the rest are
split into name-ordered runs, each shard taking the next names until it
reaches its share. Drift then moves a package or two at a boundary: median 1,
at most 2 in the same simulation, with shards balanced to within 0.2%.

Usage:
  test_shard.py INDEX/COUNT [--all-members]      e.g. 1/2

--all-members shards every workspace member, EXCLUDED ones included. The
coverage job uses it: it measures the whole workspace (`--workspace`), unlike
`make test-no-macros`, which leaves the EXCLUDED macro crates to its own target.

Exit codes:
  0 - Arguments printed on stdout
  1 - Bad arguments, or `cargo metadata` / `rustc -vV` failed
"""

import json
import os
import subprocess
import sys
from pathlib import Path

# Keep in sync with the `--exclude` list of `test-no-macros` in the Makefile.
EXCLUDED = {"cf-gears-toolkit-macros-tests", "cf-gears-toolkit-db-macros"}

# Test *execution* cost that source size cannot see, as a share of the whole
# set's source weight. cf-gears-bss-pricing runs ~3,500 tests averaging ~0.6 s
# (2,131 test-seconds on Windows in CI run 36225208693, against 54 s for the
# next package), so by source size alone its shard spent 616 s running tests
# against 92 s for the other. 0.25 is the value that evened out a simulation of
# that run's build and test times (~19 / ~19 min instead of ~23 / ~15). Revisit
# when a shard's test phase drifts well away from the other's.
EXTRA_WEIGHT_SHARE = {"cf-gears-bss-pricing": 0.25}

# Packages at least this share of the total weight are placed individually
# before the name-ordered split; see the module docstring.
HEAVY_SHARE = 0.05


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


def run(*cmd: str) -> str:
    # Explicit UTF-8: cargo emits UTF-8, and on Windows `text=True` alone
    # decodes with the ANSI code page, which fails on crate descriptions in
    # the full metadata (CI run 36232565886).
    return subprocess.run(
        cmd, check=True, capture_output=True, text=True, encoding="utf-8"
    ).stdout


def cargo_json(*args: str) -> dict:
    return json.loads(run("cargo", *args))


def host_triple() -> str:
    out = run("rustc", "-vV")
    return next(line.split(": ", 1)[1] for line in out.splitlines() if line.startswith("host: "))


def workspace_features(names: list[str]) -> list[str]:
    """`pkg/feature` for every non-default feature the whole workspace enables on `names`."""
    metadata = cargo_json(
        "metadata", "--format-version", "1", "--filter-platform", host_triple()
    )
    by_id = {p["id"]: p["name"] for p in metadata["packages"]}
    wanted = set(names) & {by_id[i] for i in metadata["workspace_members"]}
    return sorted(
        f"{by_id[node['id']]}/{feature}"
        for node in metadata["resolve"]["nodes"]
        if by_id[node["id"]] in wanted and node["id"] in metadata["workspace_members"]
        for feature in node["features"]
        if feature != "default"
    )


def shard_packages(index: int, count: int, excluded: set[str]) -> list[str]:
    metadata = cargo_json("metadata", "--no-deps", "--format-version", "1")
    members = set(metadata["workspace_members"])
    weights = {
        p["name"]: source_bytes(Path(p["manifest_path"]).parent)
        for p in metadata["packages"]
        if p["id"] in members and p["name"] not in excluded
    }
    total = sum(weights.values())
    for name, share in EXTRA_WEIGHT_SHARE.items():
        if name in weights:
            weights[name] += int(share * total)
    shards: list[list] = [[0, []] for _ in range(count)]
    heavy = sorted(
        (n for n in weights if weights[n] >= HEAVY_SHARE * total),
        key=lambda n: (-weights[n], n),
    )
    for name in heavy:
        lightest = min(shards, key=lambda s: s[0])
        lightest[0] += weights[name]
        lightest[1].append(name)
    # The rest in name order: each shard takes the next names while that
    # brings it closer to its share, then the next shard continues.
    target = sum(weights.values()) / count
    k = 0
    for name in sorted(n for n in weights if n not in heavy):
        if k < count - 1 and shards[k][0] + weights[name] / 2 > target:
            k += 1
        shards[k][0] += weights[name]
        shards[k][1].append(name)
    return sorted(shards[index - 1][1])


def main(argv: list[str]) -> int:
    try:
        flags = [a for a in argv if a.startswith("--")]
        positional = [a for a in argv if not a.startswith("--")]
        if set(flags) - {"--all-members"} or len(positional) != 1:
            raise ValueError
        index, count = (int(x) for x in positional[0].split("/"))
        if not 1 <= index <= count:
            raise ValueError
    except ValueError:
        print("usage: test_shard.py INDEX/COUNT [--all-members] (e.g. 1/2)", file=sys.stderr)
        return 1
    excluded = set() if "--all-members" in flags else EXCLUDED
    try:
        packages = shard_packages(index, count, excluded)
        features = workspace_features(packages)
    except subprocess.CalledProcessError as e:
        print(f"{' '.join(e.cmd)} failed:\n{e.stderr}", file=sys.stderr)
        return 1
    args = [f"-p {p}" for p in packages]
    if features:
        args.append("--features " + ",".join(features))
    print(" ".join(args))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
