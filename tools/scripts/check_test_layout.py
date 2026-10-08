#!/usr/bin/env python3
"""Check that crates with one test binary load every test file.

A crate that builds its integration tests as one binary has
`tests/integration.rs` and sets `autotests = false` in Cargo.toml, so cargo
compiles only that file. A `tests/*.rs` file it does not load is never
compiled and never run. This check fails instead. A file the crate declares
as a `[[test]]` of its own (`path = "tests/<file>.rs"`) is fine too.

Exit codes:
  0 - every test file is loaded
  1 - a crate has a test file its tests/integration.rs does not load, or
      builds its tests/*.rs files as binaries of their own as well
"""

import re
import subprocess
import sys
from pathlib import Path

ROOT_FILE = "integration.rs"


def problems(crate: Path) -> list[str]:
    """What is wrong with one crate that has tests/integration.rs."""
    tests = crate / "tests"
    root = (tests / ROOT_FILE).read_text(encoding="utf-8")
    loaded = set(re.findall(r'#\[path\s*=\s*"([^"/]+\.rs)"\]', root))
    loaded |= {f"{m}.rs" for m in re.findall(r"^(?:pub(?:\([a-z]+\))?\s+)?mod\s+(\w+)\s*;", root, re.M)}
    manifest = (crate / "Cargo.toml").read_text(encoding="utf-8")
    loaded |= set(re.findall(r'^path\s*=\s*"tests/([^"/]+\.rs)"', manifest, re.M))
    found = []
    for path in sorted(tests.glob("*.rs")):
        if path.name != ROOT_FILE and path.name not in loaded:
            found.append(f"{path} is not loaded by {tests / ROOT_FILE}")
    if not re.search(r"^autotests\s*=\s*false\s*$", manifest, re.M):
        found.append(f"{crate / 'Cargo.toml'} needs `autotests = false`")
    return found


def main() -> int:
    repo = Path(__file__).resolve().parents[2]
    listed = subprocess.run(
        ["git", "ls-files", "-z", "--", f":(glob)**/tests/{ROOT_FILE}"],
        cwd=repo, capture_output=True, check=True, text=True,
    ).stdout
    found = []
    for rel in filter(None, listed.split("\0")):
        found += problems(repo / Path(rel).parent.parent)
    for line in found:
        print(f"error: {line}")
    if found:
        print(f"Add a `#[path = \"<file>.rs\"] mod <file>;` line to the crate's tests/{ROOT_FILE}.")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
