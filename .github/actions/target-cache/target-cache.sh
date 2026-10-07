#!/usr/bin/env bash
# Restore or save target/debug in S3-compatible storage. Called by the
# restore/ and save/ actions next to this file.
#
# Most of a warm build is compiling and linking test binaries, which sccache
# never caches. With main's target/ and the mtimes fixed by target_cache.py,
# cargo rebuilds only what changed since main built it.
#
# Objects: gears-rust/target/<name>/<OS>.<commit>.<run>-<attempt>.tar.zst and
# <OS>.manifest.json (blob of every tracked file at the commit that was built,
# and the archive's name). The manifest is uploaded last and names its own
# archive, so two runs saving at once never pair one run's manifest with the
# other's archive. Each run writes a new archive, so a failed upload never
# replaces a good one. A save keeps its own archive and the previous one, which
# a run that read the previous manifest may still be downloading, and deletes
# any other archive older than three hours. The restore is skipped when most
# test binaries would be rebuilt anyway, and saving runs skip it when Cargo.lock
# changed, so the archive does not grow. Never fails the job.

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
s3rm() { aws s3 rm ${endpoint_arg[@]+"${endpoint_arg[@]}"} --only-show-errors "$@"; }
# Download, quiet when the object does not exist. Any other error (no access,
# wrong endpoint, no aws) is a warning, so a broken cache does not stay silent.
s3err="$RUNNER_TEMP/target-cache-s3.err"
fetch() {
  s3 "$@" 2>"$s3err" && return 0
  grep -qE '\(404\)|NoSuchKey|does not exist' "$s3err" \
    || echo "::warning::target cache: $(tr '\n' ' ' < "$s3err")"
  return 1
}
# No newline: on Windows it would be \r\n, and bash keeps the \r.
field() { python3 -c 'import json,sys; print(json.load(open(sys.argv[1])).get(sys.argv[2], ""), end="")' "$1" "$2"; }
helper="$(dirname "${BASH_SOURCE[0]}")/target_cache.py"
remote="s3://$S3_BUCKET/$PREFIX"
manifest="$RUNNER_TEMP/target-cache-manifest.json"
trybuild_dir=target/tests/trybuild

if [[ "$MODE" == "restore" ]]; then
  fetch "$remote.manifest.json" "$manifest" || { echo "No target cache to restore"; exit 0; }
  decision="$(python3 "$helper" plan "$manifest")" || decision="restore: could not plan, restoring anyway"
  echo "$decision"
  [[ "$decision" == restore* ]] || exit 0
  archive="$(field "$manifest" archive)"
  [[ -n "$archive" ]] || { echo "Manifest names no archive; building from scratch"; exit 0; }
  mkdir -p target
  start=$SECONDS
  if ! s3 "s3://$S3_BUCKET/$archive" - | zstd -d -q | tar -xf - -C target; then
    # A partial tree could hold truncated files that cargo trusts.
    echo "::warning::target cache restore failed; building from scratch"
    rm -rf target/debug
    exit 0
  fi
  # The mtime fix below also makes trybuild's copies of workspace crates look
  # unchanged, which is only right if that archive is from the same commit.
  built="$(field "$manifest" commit)"
  if [[ -d "$trybuild_dir" && "$(cat "$trybuild_dir/.cache-commit" 2>/dev/null)" != "$built" ]]; then
    echo "trybuild cache is from another commit than target/; dropping it"
    rm -rf "$trybuild_dir"
  fi
  python3 "$helper" mtimes "$manifest" || {
    echo "::warning::could not fix mtimes; building from scratch"
    rm -rf target/debug
    exit 0
  }
  echo "::notice::target cache restored in $((SECONDS - start))s ($(du -sh target/debug | cut -f1)); ${decision#restore: }"
else
  [[ -d target/debug ]] || { echo "No target/debug to save"; exit 0; }
  start=$SECONDS
  previous="$RUNNER_TEMP/target-cache-previous.json"
  fetch "$remote.manifest.json" "$previous" || : > "$previous"
  ARCHIVE="$PREFIX.$(git rev-parse HEAD).$GITHUB_RUN_ID-$GITHUB_RUN_ATTEMPT.tar.zst" \
    python3 "$helper" manifest "$manifest" \
    || { echo "::warning::could not write the manifest"; exit 0; }
  archive="$(field "$manifest" archive)"
  items=(debug)
  [[ -f target/.rustc_info.json ]] && items+=(.rustc_info.json)
  if tar -cf - -C target --exclude=debug/incremental "${items[@]}" | zstd -q -T0 -1 | s3 - "s3://$S3_BUCKET/$archive" \
    && s3 "$manifest" "$remote.manifest.json"; then
    echo "::notice::target cache saved in $((SECONDS - start))s ($(du -sh target/debug | cut -f1) before compression)"
    # Not deleted here: a run that read the previous manifest may still be
    # downloading it. The next save deletes it.
    old="$( [[ -s "$previous" ]] && field "$previous" archive )"
    listing="$RUNNER_TEMP/target-cache-listing.json"
    if aws s3api list-objects-v2 ${endpoint_arg[@]+"${endpoint_arg[@]}"} \
      --bucket "$S3_BUCKET" --prefix "$PREFIX." --output json > "$listing"; then
      python3 "$helper" prune "$listing" "$archive" ${old:+"$old"} | while read -r key; do
        key="${key%$'\r'}"
        if s3rm "s3://$S3_BUCKET/$key"; then
          echo "Deleted the stale target archive $key"
        else
          echo "::warning::could not delete the stale target archive $key"
        fi
      done
    else
      echo "::warning::could not list the target archives"
    fi
  else
    echo "::warning::could not save the target cache"
    # A part that did get uploaded is named by no manifest.
    s3rm "s3://$S3_BUCKET/$archive" 2>/dev/null || true
  fi
fi
