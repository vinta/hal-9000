#!/usr/bin/env bash
# PostToolUse hook: runs "hal sync" when the manifest changes, so new entries are linked right away.
# Edits to already-managed files propagate instantly through their symlinks and don't need this.

set -euo pipefail

REPO_ROOT="/usr/local/hal-9000"

file_path=$(jq -r '.tool_input.file_path // .tool_response.filePath' <&0)

if [[ "$file_path" == */hal_dotfiles.json ]]; then
  cd "$REPO_ROOT" && bin/hal sync
fi
