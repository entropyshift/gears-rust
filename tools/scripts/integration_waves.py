#!/usr/bin/env python3
"""
Spread the suites of the CI `integration` job over waves.

Contributors add an integration suite as they always have: a `make test-foo`
target and a step with `run: make test-foo` in the `integration` job of
ci.yml. That job runs as a matrix of waves (CI_WAVE=1/2, 2/2). A `make`
wrapper on the job's PATH (tools/ci/wave-bin/make) asks this script whether a
step's suite belongs to its wave; a step of another wave passes at once.

The suite list is read from the job's `run: make test-*` lines, so a new step
needs no other edit. Suites go longest first into the lightest wave, with
times from .config/ci-suite-timings.toml; a suite with no time yet counts as
the median. Ties break by name, so every wave job computes the same plan.

Each suite is its own cargo call, so its features and its sccache keys do not
depend on its wave. Grouping related suites was measured and not worth it:
after a wave's first suite builds the shared base, every suite builds in
22-75 s, related or not (CI run 36699651834).

Usage:
  integration_waves.py plan [COUNT]       print the plan as markdown (COUNT from CI_WAVE if omitted)
  integration_waves.py decide ARG...      print "run" or "skip: ..." for `make ARG...` (CI_WAVE from env)
  integration_waves.py timings RUN_ID [--repo OWNER/NAME]
                                          rewrite the timings file from a CI run's step times

Exit codes:
  0 - Done
  1 - Bad arguments, bad CI_WAVE, or ci.yml / gh failed
"""

from __future__ import annotations

import os
import re
import statistics
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CI_YML = Path(os.environ.get("INTEGRATION_WAVES_CI_YML", ROOT / ".github" / "workflows" / "ci.yml"))
TIMINGS = Path(os.environ.get("INTEGRATION_WAVES_TIMINGS", ROOT / ".config" / "ci-suite-timings.toml"))
JOB = "integration"

# Used only when no suite in the job has a time yet.
DEFAULT_SECONDS = 60.0

JOB_KEY = re.compile(r"^  ([A-Za-z0-9_-]+):\s*$")
STEP_NAME = re.compile(r"^\s*- name:\s*(.+?)\s*$")
MAKE_RUN = re.compile(r"^\s*run:\s*make\s+(test-[A-Za-z0-9_-]+)\s*$")


def suite_steps(ci_yml: str, job: str = JOB) -> list[tuple[str, str]]:
    """(step name, make target) of each one-line `run: make test-*` step of `job`.

    A plain line scan, not a YAML parse: job keys sit at two spaces under
    `jobs:`, and a suite step is a single-line `run: make test-foo`. Multi-line
    `run: |` steps are not suites; the wrapper runs them in every wave.
    """
    steps: list[tuple[str, str]] = []
    seen: set[str] = set()
    inside, name = False, None
    for line in ci_yml.splitlines():
        key = JOB_KEY.match(line)
        if key:
            inside = key.group(1) == job
            name = None
            continue
        if not inside:
            continue
        if m := STEP_NAME.match(line):
            name = m.group(1).strip("\"'")
        elif (m := MAKE_RUN.match(line)) and m.group(1) not in seen:
            seen.add(m.group(1))
            steps.append((name or m.group(1), m.group(1)))
    return steps


def load_timings(path: Path = TIMINGS) -> dict[str, float]:
    if not path.exists():
        return {}
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    return {k: float(v) for k, v in data.items()}


def plan(suites: list[str], timings: dict[str, float], count: int) -> list[list[str]]:
    """Suites per wave, each wave in `suites` order (the order the steps run)."""
    known = [timings[s] for s in suites if s in timings]
    default = statistics.median(known) if known else DEFAULT_SECONDS
    cost = {s: timings.get(s, default) for s in suites}
    loads = [0.0] * count
    wave_of: dict[str, int] = {}
    for s in sorted(cost, key=lambda s: (-cost[s], s)):
        w = min(range(count), key=lambda i: (loads[i], i))
        loads[w] += cost[s]
        wave_of[s] = w
    order = list(dict.fromkeys(suites))
    return [[s for s in order if wave_of[s] == w] for w in range(count)]


def parse_wave(spec: str) -> tuple[int, int]:
    parts = spec.split("/")
    if len(parts) != 2:
        raise ValueError(f"bad wave {spec!r}, expected INDEX/COUNT")
    index, count = int(parts[0]), int(parts[1])
    if not 1 <= index <= count:
        raise ValueError(f"bad wave {spec!r}, expected 1 <= INDEX <= COUNT")
    return index, count


def decide(args: list[str], wave: str, suites: list[str], timings: dict[str, float]) -> str:
    """"run", unless `make ARGS` is exactly one suite that belongs to another wave."""
    if any(a.startswith("-") for a in args):
        return "run"
    goals = [a for a in args if "=" not in a]
    if len(goals) != 1 or goals[0] not in suites:
        return "run"
    index, count = parse_wave(wave)
    for i, members in enumerate(plan(suites, timings, count), start=1):
        if goals[0] in members and i != index:
            return f"skip: {goals[0]} runs in wave {i}/{count}"
    return "run"


def plan_markdown(steps: list[tuple[str, str]], timings: dict[str, float], count: int) -> str:
    suites = [t for _, t in steps]
    names = {t: n for n, t in steps}
    known = [timings[s] for s in suites if s in timings]
    default = statistics.median(known) if known else DEFAULT_SECONDS
    lines = ["### Integration waves", "", "| Wave | Suite | Step | Expected s |", "|---|---|---|---|"]
    for i, members in enumerate(plan(suites, timings, count), start=1):
        for s in members:
            t = timings.get(s)
            shown = f"{t:.0f}" if t is not None else f"{default:.0f} (median, not measured)"
            lines.append(f"| {i}/{count} | `{s}` | {names[s]} | {shown} |")
    return "\n".join(lines) + "\n"


def main(argv: list[str]) -> int:
    if not argv or argv[0] not in ("plan", "decide", "timings"):
        print(__doc__.split("Usage:")[1].split("Exit codes:")[0].rstrip(), file=sys.stderr)
        return 1
    cmd, rest = argv[0], argv[1:]
    try:
        steps = suite_steps(CI_YML.read_text(encoding="utf-8"))
        suites = [t for _, t in steps]
        if cmd == "decide":
            wave = os.environ.get("CI_WAVE", "")
            print(decide(rest, wave, suites, load_timings()) if wave else "run")
        elif cmd == "plan":
            count = int(rest[0]) if rest else parse_wave(os.environ.get("CI_WAVE", ""))[1]
            print(plan_markdown(steps, load_timings(), count), end="")
        else:
            return timings_main(rest, steps)
    except (OSError, ValueError, tomllib.TOMLDecodeError) as e:
        print(f"integration_waves.py: {e}", file=sys.stderr)
        return 1
    return 0


def timings_main(rest: list[str], steps: list[tuple[str, str]]) -> int:
    # Added in Task 2.
    print("timings: not implemented yet", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
