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

import json
import os
import re
import statistics
import subprocess
import sys
import tomllib
from datetime import datetime
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


TIMINGS_HEADER = """\
# Seconds per suite of the CI `integration` job, used by
# tools/scripts/integration_waves.py to balance the waves.
# Refresh: python3 tools/scripts/integration_waves.py timings <run-id>
# A suite missing here counts as the median. Stale values only make the waves
# less even; they never fail a build. Last refreshed from run {run_id}.
"""


def _when(stamp: str) -> datetime:
    return datetime.fromisoformat(stamp.replace("Z", "+00:00"))


# A step of another wave passes in about a second; a suite that really runs
# takes far longer than this.
RAN_SECONDS = 10.0


def step_seconds(jobs: list[dict], names: dict[str, str]) -> dict[str, float]:
    """Step time per suite, from the wave that ran it (other waves skip it in ~1 s).

    The first suite that really runs in each wave also builds the shared base
    (about 5 min in run 36699651834). Every wave pays that once, whatever its
    suites, so it is left out: that suite keeps its old time.
    """
    out: dict[str, float] = {}
    for job in jobs:
        if not job.get("name", "").startswith("Integration tests"):
            continue
        first_seen = False
        for step in job.get("steps") or []:
            target = names.get(step.get("name", ""))
            start, end = step.get("started_at"), step.get("completed_at")
            if not target or not start or not end:
                continue
            seconds = (_when(end) - _when(start)).total_seconds()
            if seconds < RAN_SECONDS:
                continue  # skipped: the suite runs in another wave
            if not first_seen:
                first_seen = True
                continue
            out[target] = max(out.get(target, 0.0), seconds)
    return out


def write_timings(seconds: dict[str, float], run_id: str, path: Path = TIMINGS) -> None:
    merged = load_timings(path)
    merged.update({k: float(round(v)) for k, v in seconds.items()})
    body = "".join(f"{k} = {merged[k]:.0f}\n" for k in sorted(merged))
    path.write_text(TIMINGS_HEADER.format(run_id=run_id) + body, encoding="utf-8")


def timings_main(rest: list[str], steps: list[tuple[str, str]]) -> int:
    repo = "constructorfabric/gears-rust"
    args = list(rest)
    if "--repo" in args:
        i = args.index("--repo")
        repo = args[i + 1]
        del args[i : i + 2]
    if len(args) != 1 or not args[0].isdigit():
        print("usage: integration_waves.py timings RUN_ID [--repo OWNER/NAME]", file=sys.stderr)
        return 1
    run_id = args[0]
    try:
        out = subprocess.run(
            ["gh", "api", "--paginate", f"repos/{repo}/actions/runs/{run_id}/jobs?per_page=100",
             "--jq", ".jobs[]"],
            check=True, capture_output=True, text=True, encoding="utf-8",
        ).stdout
    except (OSError, subprocess.CalledProcessError) as e:
        print(f"gh api failed: {getattr(e, 'stderr', e)}", file=sys.stderr)
        return 1
    jobs = [json.loads(line) for line in out.splitlines() if line.strip()]
    seconds = step_seconds(jobs, {n: t for n, t in steps})
    if not seconds:
        print(f"run {run_id}: no integration suite steps found", file=sys.stderr)
        return 1
    write_timings(seconds, run_id)
    for k in sorted(seconds):
        print(f"{k} = {seconds[k]:.0f}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
