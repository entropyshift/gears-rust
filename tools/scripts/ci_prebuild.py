#!/usr/bin/env python3
"""Build a CI job's test binaries ahead of its steps, one step at a time.

The integration job runs its `make test-*` steps one after another, and each
step first builds, then runs its tests. Started in the background before the
first step, this builds every step's binaries in step order. A step then finds
its binaries ready and runs its tests while the next step's binaries build.
Two cargo commands never build at once in one target dir (cargo's lock), so
the order matches the steps.

The steps come from the workflow file, so a new `make test-*` step needs no
change here. Each make target's cargo commands come from `make -n`; only the
options that select what to build are kept. Never fails: a command that
fails here just leaves the build to its step.

  ci_prebuild.py <workflow.yml> <job>          print the build commands
  ci_prebuild.py <workflow.yml> <job> --run    run them
"""

import re
import shlex
import subprocess
import sys
import time

# Options that change what cargo builds; everything else is dropped.
WITH_VALUE = {"-p", "--package", "-F", "--features", "--test", "--example", "--exclude", "--bin"}
FLAGS = {"--lib", "--bins", "--tests", "--examples", "--all-features", "--no-default-features", "--workspace"}
SEPARATORS = {";", "&&", "||", "|", "&", "}", "{", "(", ")", "--"}


def make_targets(workflow, job):
    """`make <target>` steps of the job, in order."""
    targets, in_job = [], False
    with open(workflow, encoding="utf-8") as f:
        for line in f:
            # A job key, two spaces in. Not a comment or a blank line.
            if re.match(r"^  [^\s#]", line):
                in_job = line.strip() == f"{job}:"
            elif in_job:
                m = re.match(r"^\s+(?:-\s+)?run:\s*make\s+([\w.-]+)\s*$", line)
                if m:
                    targets.append(m.group(1))
    return targets


def build_commands(target):
    """`cargo test --no-run ...` / `cargo build ...` for one make target."""
    return cargo_commands(subprocess.run(["make", "-n", target], capture_output=True, text=True).stdout)


def cargo_commands(script):
    """Build commands for the cargo test, nextest and build calls in a shell script."""
    text = script.replace("\\\n", " ")
    cmds = []
    for line in text.splitlines():
        if "cargo" not in line:
            continue
        lexer = shlex.shlex(line, posix=True, punctuation_chars=";&|(){}")
        lexer.whitespace_split = True
        try:
            tokens = list(lexer)
        except ValueError:
            continue
        for i, tok in enumerate(tokens):
            if tok != "cargo" or i + 1 >= len(tokens):
                continue
            sub = tokens[i + 1]
            if sub == "nextest" and tokens[i + 2:i + 3] == ["run"]:
                kind, j = ["test", "--no-run"], i + 3
            elif sub == "test":
                kind, j = ["test", "--no-run"], i + 2
            elif sub == "build":
                kind, j = ["build"], i + 2
            else:
                continue
            opts = []
            while j < len(tokens) and tokens[j] not in SEPARATORS:
                tok = tokens[j]
                name = tok.split("=", 1)[0]
                if name in WITH_VALUE and "=" not in tok and j + 1 < len(tokens):
                    opts += [tok, tokens[j + 1]]
                    j += 2
                    continue
                if name in WITH_VALUE or tok in FLAGS:
                    opts.append(tok)
                j += 1
            cmd = ["cargo", *kind, *opts]
            if cmd not in cmds:
                cmds.append(cmd)
    return cmds


def main():
    workflow, job = sys.argv[1], sys.argv[2]
    run = "--run" in sys.argv[3:]
    seen = []
    for target in make_targets(workflow, job):
        for cmd in build_commands(target):
            if cmd in seen:
                continue
            seen.append(cmd)
            line = shlex.join(cmd)
            if not run:
                print(f"{target}: {line}")
                continue
            start = time.monotonic()
            rc = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode
            print(f"{time.monotonic() - start:6.0f}s rc={rc} {target}: {line}", flush=True)


if __name__ == "__main__":
    main()
