#!/usr/bin/env bash
# PostToolUse hook: run a lint target and surface failures on stderr so Claude sees why and can fix it.
# Which files trigger this is controlled by the "if" permission-rule filter in settings.json, not here.
set -Eeuo pipefail

REPO_ROOT="/usr/local/hal-9000"
target="$1"

cd "$REPO_ROOT"
if ! output=$(make "$target" 2>&1); then
  echo "$output" >&2
  exit 2
fi
