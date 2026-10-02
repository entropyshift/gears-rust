#!/usr/bin/env python3
"""Unit tests for integration_waves.py.

    python3 -m unittest discover -s tools/scripts/tests
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

import integration_waves as iw  # noqa: E402

CI_YML = """\
name: CI
on:
  push:
jobs:
  test:
    steps:
      - name: Unit
        run: make test-no-macros
  integration:
    name: Integration tests
    steps:
      - name: Setup
        run: make install-tools
      - name: UI tests for toolkit macros libraries
        run: make test-macros
      - name: "Test users_info with Postgres (integration)"
        env:
          FOO: "1"
        run: make test-users-info-pg
      - name: Not a suite
        run: |
          make test-multi-line
      - name: Duplicate
        run: make test-macros
  test-fips:
    steps:
      - name: FIPS
        run: make test-fips
"""


class TestSuiteSteps(unittest.TestCase):
    def test_reads_only_the_integration_job(self):
        self.assertEqual(
            iw.suite_steps(CI_YML),
            [
                ("UI tests for toolkit macros libraries", "test-macros"),
                ("Test users_info with Postgres (integration)", "test-users-info-pg"),
            ],
        )

    def test_unknown_job_has_no_suites(self):
        self.assertEqual(iw.suite_steps(CI_YML, job="nope"), [])


class TestPlan(unittest.TestCase):
    def test_longest_first_into_lightest_wave(self):
        suites = ["a", "b", "c", "d"]
        timings = {"a": 10, "b": 400, "c": 300, "d": 100}
        # b -> wave 1 (400), c -> wave 2 (300), d -> wave 2 (400), a -> wave 1 (410)
        self.assertEqual(iw.plan(suites, timings, 2), [["a", "b"], ["c", "d"]])

    def test_every_suite_in_exactly_one_wave(self):
        suites = [f"s{i}" for i in range(17)]
        timings = {s: (i * 37) % 101 for i, s in enumerate(suites)}
        waves = iw.plan(suites, timings, 3)
        flat = [s for w in waves for s in w]
        self.assertEqual(sorted(flat), sorted(suites))

    def test_new_suite_gets_median(self):
        suites = ["a", "b", "c", "new"]
        timings = {"a": 100, "b": 50, "c": 10}
        # median 50: a -> 1, new/b tie at 50 break by name: b -> 2, new -> 2, c -> 1
        self.assertEqual(iw.plan(suites, timings, 2), [["a", "c"], ["b", "new"]])

    def test_no_timings_at_all(self):
        self.assertEqual(iw.plan(["x", "y"], {}, 2), [["x"], ["y"]])

    def test_same_input_same_plan(self):
        suites = ["a", "b", "c"]
        timings = {"a": 5, "b": 5, "c": 5}
        self.assertEqual(iw.plan(suites, timings, 2), iw.plan(list(suites), dict(timings), 2))


class TestDecide(unittest.TestCase):
    SUITES = ["test-a", "test-b"]
    TIMINGS = {"test-a": 100, "test-b": 50}  # test-a -> wave 1, test-b -> wave 2

    def test_decide_runs_own_wave(self):
        self.assertEqual(iw.decide(["test-a"], "1/2", self.SUITES, self.TIMINGS), "run")

    def test_decide_skips_other_wave(self):
        self.assertEqual(
            iw.decide(["test-b"], "1/2", self.SUITES, self.TIMINGS),
            "skip: test-b runs in wave 2/2",
        )

    def test_decide_runs_unknown_goal(self):
        self.assertEqual(iw.decide(["install-tools"], "1/2", self.SUITES, self.TIMINGS), "run")

    def test_decide_runs_with_flags(self):
        self.assertEqual(iw.decide(["-n", "test-b"], "1/2", self.SUITES, self.TIMINGS), "run")

    def test_decide_runs_with_several_goals(self):
        self.assertEqual(iw.decide(["test-a", "test-b"], "1/2", self.SUITES, self.TIMINGS), "run")

    def test_decide_ignores_variable_assignments(self):
        self.assertEqual(
            iw.decide(["test-b", "X=1"], "1/2", self.SUITES, self.TIMINGS),
            "skip: test-b runs in wave 2/2",
        )

    def test_bad_wave_raises(self):
        for spec in ("", "3/2", "0/2", "a/b", "1"):
            with self.assertRaises(ValueError):
                iw.parse_wave(spec)


class TestTimings(unittest.TestCase):
    def test_load_missing_file_is_empty(self):
        self.assertEqual(iw.load_timings(Path("/nonexistent/timings.toml")), {})

    def test_load_reads_seconds(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "t.toml"
            p.write_text("# comment\ntest-a = 515\ntest-b = 41.5\n", encoding="utf-8")
            self.assertEqual(iw.load_timings(p), {"test-a": 515.0, "test-b": 41.5})


if __name__ == "__main__":
    unittest.main()
