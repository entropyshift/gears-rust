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
    def test_splits_steps_in_order(self):
        self.assertEqual(iw.plan(["a", "b", "c", "d"], 2), [["a", "b"], ["c", "d"]])

    def test_odd_count_gives_the_extra_suite_to_the_last_wave(self):
        self.assertEqual(iw.plan(["a", "b", "c", "d", "e"], 2), [["a", "b"], ["c", "d", "e"]])

    def test_every_suite_in_exactly_one_wave(self):
        suites = [f"s{i}" for i in range(17)]
        waves = iw.plan(suites, 3)
        self.assertEqual([s for w in waves for s in w], suites)
        self.assertEqual([len(w) for w in waves], [5, 6, 6])

    def test_fewer_suites_than_waves(self):
        self.assertEqual(iw.plan(["x"], 2), [[], ["x"]])

    def test_new_step_at_the_end_moves_at_most_one_suite(self):
        before = iw.plan(["a", "b", "c", "d"], 2)
        after = iw.plan(["a", "b", "c", "d", "e"], 2)
        moved = [s for w in range(2) for s in before[w] if s not in after[w]]
        self.assertLessEqual(len(moved), 1)


class TestDecide(unittest.TestCase):
    SUITES = ["test-a", "test-b"]  # test-a -> wave 1, test-b -> wave 2

    def test_decide_runs_own_wave(self):
        self.assertEqual(iw.decide(["test-a"], "1/2", self.SUITES), "run")

    def test_decide_skips_other_wave(self):
        self.assertEqual(
            iw.decide(["test-b"], "1/2", self.SUITES),
            "skip: test-b runs in wave 2/2",
        )

    def test_decide_runs_unknown_goal(self):
        self.assertEqual(iw.decide(["install-tools"], "1/2", self.SUITES), "run")

    def test_decide_runs_with_flags(self):
        self.assertEqual(iw.decide(["-n", "test-b"], "1/2", self.SUITES), "run")

    def test_decide_runs_with_several_goals(self):
        self.assertEqual(iw.decide(["test-a", "test-b"], "1/2", self.SUITES), "run")

    def test_decide_ignores_variable_assignments(self):
        self.assertEqual(
            iw.decide(["test-b", "X=1"], "1/2", self.SUITES),
            "skip: test-b runs in wave 2/2",
        )

    def test_bad_wave_raises(self):
        for spec in ("", "3/2", "0/2", "a/b", "1"):
            with self.assertRaises(ValueError):
                iw.parse_wave(spec)


class TestPlanMarkdown(unittest.TestCase):
    def test_lists_each_suite_with_its_wave(self):
        steps = [("Step A", "test-a"), ("Step B", "test-b")]
        self.assertEqual(
            iw.plan_markdown(steps, 2),
            "### Integration waves\n\n"
            "| Wave | Suite | Step |\n|---|---|---|\n"
            "| 1/2 | `test-a` | Step A |\n"
            "| 2/2 | `test-b` | Step B |\n",
        )


WRAPPER = HERE.parent.parent / "ci" / "wave-bin" / "make"


@unittest.skipIf(sys.platform == "win32", "bash wrapper, Linux CI only")
class TestWrapper(unittest.TestCase):
    def run_wrapper(self, args, wave, ci_yml=CI_YML):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            (d / "ci.yml").write_text(ci_yml, encoding="utf-8")
            fake = d / "fake-make"
            fake.write_text('#!/usr/bin/env bash\necho "REAL $*"\n', encoding="utf-8")
            fake.chmod(0o755)
            env = dict(os.environ, REAL_MAKE=str(fake),
                       INTEGRATION_WAVES_CI_YML=str(d / "ci.yml"))
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
