#!/usr/bin/env bash
# Restore or save target/tests/trybuild in S3-compatible storage. Called by
# the restore/ and save/ actions next to this file.
# trybuild builds its own copy of the dependencies on every run, and its
# proc-macros and build scripts are never in sccache.
#
# One archive per name and OS: gears-rust/trybuild/<name>/<OS>.tar.zst, and
# <OS>.key with the Cargo.lock + rust-toolchain.toml hash it was built with.
# A save uploads to a temporary name and moves the archive into place only
# when the upload worked, so a failed upload never replaces a good archive.
# A stale archive is safe: cargo rebuilds what changed. Runs that save skip a
# restore when the key changed, so the archive does not grow. Never fails the job.
set -uo pipefail
# aws.exe on Windows: MSYS must not rewrite the s3:// URL.
[[ "$RUNNER_OS" == "Windows" ]] && export MSYS_NO_PATHCONV=1
endpoint_arg=()
if [[ -n "$S3_ENDPOINT" ]]; then
  endpoint_arg=(--endpoint-url "$S3_ENDPOINT")
  # Path-style addressing for custom endpoints, like sccache.
  export AWS_CONFIG_FILE="$RUNNER_TEMP/aws-config"
  printf '[default]\ns3 =\n    addressing_style = path\n' > "$AWS_CONFIG_FILE"
fi
s3() { aws s3 cp ${endpoint_arg[@]+"${endpoint_arg[@]}"} --only-show-errors "$@"; }
# No tags: R2 does not implement GetObjectTagging, which a move copies by default.
s3mv() { aws s3 mv ${endpoint_arg[@]+"${endpoint_arg[@]}"} --only-show-errors --copy-props none "$@"; }
s3rm() { aws s3 rm ${endpoint_arg[@]+"${endpoint_arg[@]}"} --only-show-errors "$@"; }
# Download, quiet when the object does not exist. Any other error (no access,
# wrong endpoint, no aws) is a warning, so a broken cache does not stay silent.
s3err="$RUNNER_TEMP/trybuild-cache-s3.err"
fetch() {
  s3 "$@" 2>"$s3err" && return 0
  grep -qE '\(404\)|NoSuchKey|does not exist' "$s3err" \
    || echo "::warning::trybuild cache: $(tr '\n' ' ' < "$s3err")"
  return 1
}
remote="s3://$S3_BUCKET/$PREFIX"
dir=target/tests/trybuild

if [[ "$MODE" == "restore" ]]; then
  key_file="$RUNNER_TEMP/trybuild-cache.key"
  fetch "$remote.key" "$key_file" || { echo "No trybuild archive to restore"; exit 0; }
  stored_key="$(cat "$key_file")"
  if [[ "$SAVES" == "true" && "$stored_key" != "$KEY" ]]; then
    echo "Cargo.lock or toolchain changed: building trybuild from scratch, to save a clean archive"
    exit 0
  fi
  mkdir -p target/tests
  start=$SECONDS
  if s3 "$remote.tar.zst" - | zstd -d -q | tar -xf - -C target/tests; then
    # trybuild builds the workspace crates by path, and cargo trusts them
    # while their sources are older than its outputs. The archive's outputs
    # can be newer than this checkout when it was saved after it, so give
    # every tracked file the current time. The target/ cache, when it
    # restores, sets the unchanged ones old again for the same commit.
    git ls-files -z | xargs -0 touch -c
    echo "::notice::trybuild cache restored in $((SECONDS - start))s ($(du -sh "$dir" | cut -f1)), key $([[ "$stored_key" == "$KEY" ]] && echo current || echo older)"
  else
    # A partial tree could hold truncated files that cargo trusts.
    echo "::warning::trybuild cache restore failed; building from scratch"
    rm -rf "$dir"
  fi
else
  [[ -d "$dir" ]] || { echo "No $dir to save"; exit 0; }
  start=$SECONDS
  # The target/ cache checks this before it fixes mtimes.
  git rev-parse HEAD > "$dir/.cache-commit"
  # Upload the key last, so a failed upload never pairs a new key
  # with an old archive.
  partial="$remote.$GITHUB_RUN_ID-$GITHUB_RUN_ATTEMPT.partial"
  if tar -cf - -C target/tests trybuild | zstd -q -T0 -3 | s3 - "$partial" \
    && s3mv "$partial" "$remote.tar.zst" \
    && printf '%s' "$KEY" | s3 - "$remote.key"; then
    echo "::notice::trybuild cache saved in $((SECONDS - start))s ($(du -sh "$dir" | cut -f1) before compression)"
  else
    echo "::warning::could not save the trybuild cache"
    s3rm "$partial" 2>/dev/null || true
  fi
fi
