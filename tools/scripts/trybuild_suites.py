#!/usr/bin/env python3
"""
Find the trybuild / compile-fail tests, so CI can run them in their own job.

Every test leg skips these tests (`make test-no-macros` with
TRYBUILD_SPLIT=skip) and the Trybuild job runs only them (`make
test-trybuild`), on the same three OSes. They are long serial rustc
sessions: on Ubuntu ~1,090 s of the test legs' time (run 36070999177).

Contributors do nothing: a test function whose body calls `TestCases::new`
(trybuild) is found here, and the filter both jobs use is built from the
same list, so the two are exact complements. HEAVY names the few tests that
are compile-heavy without trybuild. A test this scan misses runs in the test
legs, as it would without the split.

Usage:
  trybuild_suites.py filter  [--exclude PKG]...   print the nextest filterset of these tests
  trybuild_suites.py targets [--exclude PKG]...   print cargo args that build only their binaries

Exit codes:
  0 - Printed on stdout
  1 - Bad arguments, `cargo metadata` failed, or a HEAVY test is gone
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

# Compile-heavy tests that do not use trybuild: each spawns a nested
# `cargo test` build under a different GTS_ID_PREFIX. The three in-process
# Layer-1 tests in the same binary stay in the test legs.
# (package, test binary, test function)
HEAVY = [
    ("cf-gears-toolkit-gts", "prefix_customization", "default_prefix_is_gts_dot"),
    ("cf-gears-toolkit-gts", "prefix_customization", "custom_prefix_acme_dot"),
    ("cf-gears-toolkit-gts", "prefix_customization", "custom_prefix_myco_dot"),
    ("cf-gears-toolkit-gts", "prefix_customization", "invalid_prefix_fails_to_compile"),
]

TESTCASES = re.compile(r"\bTestCases::new\b")
FN = re.compile(r"\bfn\s+([A-Za-z_][A-Za-z0-9_]*)\s*[<(]")


def trybuild_fns(source: str) -> list[str]:
    """Names of the functions whose body calls trybuild's `TestCases::new`."""
    if "trybuild" not in source:
        return []
    names: list[str] = []
    for m in TESTCASES.finditer(source):
        fns = FN.findall(source, 0, m.start())
        if fns and fns[-1] not in names:
            names.append(fns[-1])
    return names


def _root(src: Path) -> Path:
    # `tests/foo.rs` owns `tests/foo/`; `tests/foo/main.rs` and `src/lib.rs`
    # own their directory.
    return src.parent if src.name in ("main.rs", "lib.rs") else src.with_suffix("")


def test_binary(file: Path, targets: list[dict]) -> str | None:
    """Test binary holding `file`: its name, "" for lib unit tests, None if none."""
    for kinds, result in ((("test",), None), (("lib", "proc-macro"), "")):
        for t in targets:
            if not set(t["kind"]) & set(kinds):
                continue
            src = Path(t["src_path"])
            if file == src or _root(src) in file.parents:
                return t["name"] if result is None else result
    return None


def rust_files(package_dir: Path):
    """*.rs files of a package, not descending into nested packages or target/."""
    for root, dirs, files in os.walk(package_dir):
        root_path = Path(root)
        if root_path != package_dir and (root_path / "Cargo.toml").exists():
            dirs[:] = []
            continue
        dirs[:] = sorted(d for d in dirs if d != "target")
        for f in sorted(files):
            if f.endswith(".rs"):
                yield root_path / f


def scan(metadata: dict, excluded: set[str], heavy=HEAVY) -> list[tuple[str, str, str]]:
    members = set(metadata["workspace_members"])
    found: set[tuple[str, str, str]] = set()
    fns_by_package: dict[str, set[str]] = {}
    for p in metadata["packages"]:
        if p["id"] not in members or p["name"] in excluded:
            continue
        all_fns = fns_by_package.setdefault(p["name"], set())
        for file in rust_files(Path(p["manifest_path"]).parent):
            text = file.read_text(encoding="utf-8", errors="replace")
            all_fns.update(FN.findall(text))
            for fn in trybuild_fns(text):
                binary = test_binary(file, p["targets"])
                if binary is not None:
                    found.add((p["name"], binary, fn))
    for package, binary, fn in heavy:
        if package in excluded:
            continue
        if fn not in fns_by_package.get(package, set()):
            raise LookupError(
                f"HEAVY test {package}::{binary}::{fn} is not in the source any more; "
                "remove it from HEAVY in tools/scripts/trybuild_suites.py"
            )
        found.add((package, binary, fn))
    return sorted(found)


def filterset(tests: list[tuple[str, str, str]]) -> str:
    terms = []
    for package, binary, fn in tests:
        binary_id = f"{package}::{binary}" if binary else package
        terms.append(f"(binary_id(={binary_id}) & test(/(^|::){fn}$/))")
    return " | ".join(terms)


def target_args(tests: list[tuple[str, str, str]]) -> list[str]:
    args = ["--lib"] if any(b == "" for _, b, _ in tests) else []
    for binary in sorted({b for _, b, _ in tests if b}):
        args += ["--test", binary]
    return args


def cargo_metadata() -> dict:
    # Explicit UTF-8, as in test_shard.py: on Windows `text=True` alone decodes
    # with the ANSI code page.
    out = subprocess.run(
        ["cargo", "metadata", "--no-deps", "--format-version", "1"],
        check=True, capture_output=True, text=True, encoding="utf-8",
    ).stdout
    return json.loads(out)


def main(argv: list[str]) -> int:
    try:
        cmd, excluded = argv[0], set()
        args = iter(argv[1:])
        for arg in args:
            if arg != "--exclude":
                raise ValueError
            excluded.add(next(args))
        if cmd not in ("filter", "targets"):
            raise ValueError
    except (IndexError, ValueError, StopIteration):
        print("usage: trybuild_suites.py filter|targets [--exclude PKG]...", file=sys.stderr)
        return 1
    try:
        tests = scan(cargo_metadata(), excluded)
    except subprocess.CalledProcessError as e:
        print(f"{' '.join(e.cmd)} failed:\n{e.stderr}", file=sys.stderr)
        return 1
    except LookupError as e:
        print(e, file=sys.stderr)
        return 1
    if not tests:
        print("trybuild_suites.py: no trybuild tests found", file=sys.stderr)
        return 1
    print(filterset(tests) if cmd == "filter" else " ".join(target_args(tests)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
