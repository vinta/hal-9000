#!/usr/bin/env bash
# PostToolUse hook: runs "hal sync" when copy-mode source files or the manifest change.
# Symlinked files propagate instantly and don't need this.

set -euo pipefail

REPO_ROOT="/usr/local/hal-9000"
MANIFEST="$REPO_ROOT/dotfiles/hal_dotfiles.json"

file_path=$(jq -r '.tool_input.file_path // .tool_response.filePath' <&0)

# Fast path: manifest itself changed
if [[ "$file_path" == */hal_dotfiles.json ]]; then
  cd "$REPO_ROOT" && bin/hal sync
  exit 0
fi

# Check if the file is a copy-mode source (these don't auto-propagate like symlinks)
copy_sources=$(jq -r '.copies[].src' "$MANIFEST" | sed "s|{{REPO_ROOT}}|$REPO_ROOT|g")
if echo "$copy_sources" | grep -qxF "$file_path"; then
  cd "$REPO_ROOT" && bin/hal sync
fi
