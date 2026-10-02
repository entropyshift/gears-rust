#!/usr/bin/env python3
"""Unit tests for integration_waves.py.

    python3 -m unittest discover -s tools/scripts/tests
"""

from __future__ import annotations

import os
import subprocess
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


class TestStepSeconds(unittest.TestCase):
    # In each wave the first suite that really runs also builds the shared
    # base (~5 min), so its time is left out; other-wave steps take ~1 s.
    JOBS = [
        {
            "name": "Integration tests (wave 1/2)",
            "steps": [
                {"name": "Checkout", "started_at": "2026-10-03T09:59:00Z", "completed_at": "2026-10-03T10:00:00Z"},
                {"name": "Test G", "started_at": "2026-10-03T09:59:59Z", "completed_at": "2026-10-03T10:00:00Z"},
                {"name": "Test F", "started_at": "2026-10-03T10:00:00Z", "completed_at": "2026-10-03T10:10:00Z"},
                {"name": "Test A", "started_at": "2026-10-03T10:10:00Z", "completed_at": "2026-10-03T10:15:00Z"},
                {"name": "Test B", "started_at": "2026-10-03T10:15:00Z", "completed_at": "2026-10-03T10:15:01Z"},
            ],
        },
        {
            "name": "Integration tests (wave 2/2)",
            "steps": [
                {"name": "Test G", "started_at": "2026-10-03T10:00:00Z", "completed_at": "2026-10-03T10:08:20Z"},
                {"name": "Test F", "started_at": "2026-10-03T10:08:20Z", "completed_at": "2026-10-03T10:08:21Z"},
                {"name": "Test A", "started_at": "2026-10-03T10:08:21Z", "completed_at": "2026-10-03T10:08:22Z"},
                {"name": "Test B", "started_at": "2026-10-03T10:08:22Z", "completed_at": "2026-10-03T10:10:22Z"},
                {"name": "Test C", "started_at": None, "completed_at": None},
            ],
        },
        {"name": "Test Suite (ubuntu-latest, 1/2)", "steps": [
            {"name": "Test A", "started_at": "2026-10-03T10:00:00Z", "completed_at": "2026-10-03T11:00:00Z"},
        ]},
    ]
    NAMES = {"Test A": "test-a", "Test B": "test-b", "Test C": "test-c", "Test F": "test-f", "Test G": "test-g"}

    def test_takes_the_wave_that_ran_it(self):
        seconds = iw.step_seconds(self.JOBS, self.NAMES)
        self.assertEqual((seconds["test-a"], seconds["test-b"]), (300.0, 120.0))

    def test_skips_first_suite_that_ran_in_each_wave(self):
        seconds = iw.step_seconds(self.JOBS, self.NAMES)
        self.assertNotIn("test-f", seconds)
        self.assertNotIn("test-g", seconds)

    def test_write_keeps_old_values_for_missing_suites(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "t.toml"
            p.write_text("test-a = 1\ntest-z = 9\n", encoding="utf-8")
            iw.write_timings({"test-a": 300.4, "test-b": 120.0}, "123", p)
            self.assertEqual(iw.load_timings(p), {"test-a": 300.0, "test-b": 120.0, "test-z": 9.0})
            self.assertIn("run 123", p.read_text(encoding="utf-8"))


WRAPPER = HERE.parent.parent / "ci" / "wave-bin" / "make"


@unittest.skipIf(sys.platform == "win32", "bash wrapper, Linux CI only")
class TestWrapper(unittest.TestCase):
    def run_wrapper(self, args, wave, ci_yml=CI_YML):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            (d / "ci.yml").write_text(ci_yml, encoding="utf-8")
            (d / "t.toml").write_text("test-macros = 100\ntest-users-info-pg = 50\n", encoding="utf-8")
            fake = d / "fake-make"
            fake.write_text('#!/usr/bin/env bash\necho "REAL $*"\n', encoding="utf-8")
            fake.chmod(0o755)
            env = dict(os.environ, REAL_MAKE=str(fake),
                       INTEGRATION_WAVES_CI_YML=str(d / "ci.yml"),
                       INTEGRATION_WAVES_TIMINGS=str(d / "t.toml"))
            if wave is None:
                env.pop("CI_WAVE", None)
            else:
                env["CI_WAVE"] = wave
            r = subprocess.run(["bash", str(WRAPPER), *args], env=env,
                               capture_output=True, text=True, encoding="utf-8")
            return r.returncode, r.stdout

    def test_wrapper_runs_own_wave(self):
        self.assertEqual(self.run_wrapper(["test-macros"], "1/2"), (0, "REAL test-macros\n"))

    def test_wrapper_skips_other_wave(self):
        code, out = self.run_wrapper(["test-users-info-pg"], "1/2")
        self.assertEqual(code, 0)
        self.assertIn("runs in wave 2/2", out)
        self.assertNotIn("REAL", out)

    def test_wrapper_runs_setup_calls(self):
        self.assertEqual(self.run_wrapper(["install-tools"], "2/2"), (0, "REAL install-tools\n"))

    def test_wrapper_runs_without_ci_wave(self):
        self.assertEqual(self.run_wrapper(["test-users-info-pg"], None), (0, "REAL test-users-info-pg\n"))

    def test_wrapper_runs_when_script_fails(self):
        # A malformed CI_WAVE makes the script exit 1; the step must still run.
        self.assertEqual(self.run_wrapper(["test-users-info-pg"], "9/2"), (0, "REAL test-users-info-pg\n"))


if __name__ == "__main__":
    unittest.main()
