#!/usr/bin/env bash
# Which files trigger this is controlled by the "if" permission-rule filter in settings.json, not here.
set -Eeuo pipefail

# Linter diagnostics land on stdout, but PostToolUse only shows stderr to Claude, so re-emit them there with exit 2.
if ! output=$(make "$1" 2>&1); then
  echo "$output" >&2
  exit 2
fi
