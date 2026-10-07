#!/usr/bin/env python3
"""Unit tests for ci_prebuild.py, the integration job's background prebuild.

    python3 -m unittest discover -s tools/scripts/tests
"""

from __future__ import annotations

import re
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

import ci_prebuild  # noqa: E402


def job_text(workflow, job):
    """The lines of one job, from its key to the next job key."""
    text = workflow.read_text(encoding="utf-8")
    start = text.index(f"\n  {job}:\n")
    end = re.search(r"\n  [\w-]+:\n", text[start + 1:])
    return text[start:start + 1 + end.start()] if end else text[start:]

WORKFLOW = """\
name: CI
jobs:
  test:
    steps:
      - name: Not this job
        run: make test-other
  integration:
    steps:
      - uses: actions/checkout@v4
  # A comment at job-key depth does not end the job.
      - name: First
        run: make test-macros
      - name: Not a single make target
        run: make test-a test-b
      - name: Not make
        run: cargo test -p foo
      - name: Second
        run:   make test-users-info-pg
  coverage:
    steps:
      - run: make coverage
"""


class TestMakeTargets(unittest.TestCase):
    def targets(self, job):
        with tempfile.NamedTemporaryFile("w", suffix=".yml", delete=False) as f:
            f.write(WORKFLOW)
        try:
            return ci_prebuild.make_targets(f.name, job)
        finally:
            Path(f.name).unlink()

    def test_only_the_jobs_own_single_make_steps_in_order(self):
        self.assertEqual(self.targets("integration"), ["test-macros", "test-users-info-pg"])

    def test_other_jobs_are_separate(self):
        self.assertEqual(self.targets("test"), ["test-other"])
        self.assertEqual(self.targets("coverage"), ["coverage"])

    def test_unknown_job_has_no_steps(self):
        self.assertEqual(self.targets("missing"), [])

    def test_the_real_integration_job(self):
        workflow = HERE.parents[2] / ".github" / "workflows" / "ci.yml"
        targets = ci_prebuild.make_targets(str(workflow), "integration")
        steps = re.findall(r"^\s+run:\s*make\s+(test-[\w.-]+)\s*$", job_text(workflow, "integration"), re.M)
        self.assertGreater(len(targets), 10)
        self.assertEqual(targets, steps)


class TestCargoCommands(unittest.TestCase):
    def test_nextest_and_test_become_test_no_run(self):
        script = (
            "cargo nextest run -p a --features x --no-fail-fast\n"
            "cargo test -p b --test api -- --test-threads 1\n"
        )
        self.assertEqual(ci_prebuild.cargo_commands(script), [
            ["cargo", "test", "--no-run", "-p", "a", "--features", "x"],
            ["cargo", "test", "--no-run", "-p", "b", "--test", "api"],
        ])

    def test_build_keeps_build(self):
        self.assertEqual(ci_prebuild.cargo_commands("cargo build --workspace --all-features\n"),
                         [["cargo", "build", "--workspace", "--all-features"]])

    def test_only_options_that_select_what_to_build_are_kept(self):
        script = "cargo nextest run -j 4 --profile ci -F=a,b --lib --exclude c -p=d\n"
        self.assertEqual(ci_prebuild.cargo_commands(script), [
            ["cargo", "test", "--no-run", "-F=a,b", "--lib", "--exclude", "c", "-p=d"],
        ])

    def test_continued_lines_and_shell_operators(self):
        script = (
            "echo start && RUST_LOG=info cargo test \\\n"
            "  -p a --features integration; cargo build -p b | tee log\n"
        )
        self.assertEqual(ci_prebuild.cargo_commands(script), [
            ["cargo", "test", "--no-run", "-p", "a", "--features", "integration"],
            ["cargo", "build", "-p", "b"],
        ])

    def test_duplicates_and_other_subcommands_are_dropped(self):
        script = "cargo test -p a\ncargo test -p a\ncargo clippy -p a\ncargo fmt\necho cargo\n"
        self.assertEqual(ci_prebuild.cargo_commands(script), [["cargo", "test", "--no-run", "-p", "a"]])

    def test_unbalanced_quotes_are_skipped(self):
        self.assertEqual(ci_prebuild.cargo_commands("cargo test -p 'a\n"), [])


if __name__ == "__main__":
    unittest.main()
