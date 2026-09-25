#!/usr/bin/env python3
"""
Check that the nextest `no-trybuild` and `trybuild-only` profiles split the
test set cleanly.

Every Test Suite leg runs `no-trybuild`; the Trybuild job runs
`trybuild-only` (`make test-trybuild`). If the two filters drift apart, a
compile-fail suite runs twice, or nowhere at all. Two rules:

1. `no-trybuild`'s default-filter is exactly `not (<trybuild-only filter>)`.
2. Every `binary(=NAME)` in the trybuild-only filter is in the test target
   list passed as arguments (the Makefile's TRYBUILD_TEST_TARGETS). That list
   limits what the Trybuild job builds; a binary missing from it is never
   built there, so its suites would silently run nowhere.

Usage:
  check_trybuild_profiles.py TARGET [TARGET ...]

Exit codes:
  0 - The profiles are consistent
  1 - They are not (details on stderr)
"""

import re
import sys
import tomllib
from pathlib import Path

NEXTEST_TOML = Path(__file__).resolve().parents[2] / ".config" / "nextest.toml"


def main(targets: list[str]) -> int:
    profiles = tomllib.loads(NEXTEST_TOML.read_text())["profile"]
    only = profiles["trybuild-only"]["default-filter"]
    excluded = profiles["no-trybuild"]["default-filter"]
    errors = []

    if excluded != f"not ({only})":
        errors.append(
            "no-trybuild's default-filter is not `not (<trybuild-only filter>)`:\n"
            f"  no-trybuild:   {excluded}\n"
            f"  trybuild-only: {only}"
        )

    missing = sorted(set(re.findall(r"binary\(=([^)]+)\)", only)) - set(targets))
    if missing:
        errors.append(
            "binary(=...) names in trybuild-only that TRYBUILD_TEST_TARGETS "
            f"does not build: {', '.join(missing)}"
        )

    for error in errors:
        print(f"error: {error}", file=sys.stderr)
    if errors:
        print(f"(profiles are in {NEXTEST_TOML})", file=sys.stderr)
        return 1
    print("nextest trybuild profiles are consistent")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
