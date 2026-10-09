#!/usr/bin/env python3
"""Check that crates with one test binary load every test file.

A crate that builds its integration tests as one binary keeps them in
`tests/integration/`. Cargo builds `tests/integration/main.rs` as the test
target and does not build the files next to it on their own, so a file there
that main.rs does not load is never compiled and never run. This check fails
instead.

Exit codes:
  0 - every test file is loaded
  1 - a crate has a test file its tests/integration/main.rs does not load
"""

import re
import subprocess
import sys
from pathlib import Path

ROOT_FILE = "main.rs"


def problems(folder: Path) -> list[str]:
    """What is wrong with one tests/integration/ folder."""
    root = (folder / ROOT_FILE).read_text(encoding="utf-8")
    loaded = set(re.findall(r'#\[path\s*=\s*"([^"/]+\.rs)"\]', root))
    loaded |= {f"{m}.rs" for m in re.findall(r"^\s*(?:pub(?:\([a-z]+\))?\s+)?mod\s+(\w+)\s*;", root, re.M)}
    return [
        f"{path} is not loaded by {folder / ROOT_FILE}"
        for path in sorted(folder.glob("*.rs"))
        if path.name != ROOT_FILE and path.name not in loaded
    ]


def main() -> int:
    repo = Path(__file__).resolve().parents[2]
    listed = subprocess.run(
        ["git", "ls-files", "-z", "--", f":(glob)**/tests/integration/{ROOT_FILE}"],
        cwd=repo, capture_output=True, check=True, text=True,
    ).stdout
    found = []
    for rel in filter(None, listed.split("\0")):
        found += problems(repo / Path(rel).parent)
    for line in found:
        print(f"error: {line}")
    if found:
        print(f"Add a `mod <file>;` line to the crate's tests/integration/{ROOT_FILE}.")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
