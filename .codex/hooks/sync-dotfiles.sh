#!/usr/bin/env bash
# PostToolUse hook: runs "hal sync" when copy-mode source files or the manifest change.
# Symlinked files propagate instantly and don't need this.

set -euo pipefail

REPO_ROOT="/usr/local/hal-9000"
MANIFEST="$REPO_ROOT/dotfiles/hal_dotfiles.json"

hook_input=$(cat)
session_cwd=$(jq -r '.cwd // empty' <<<"$hook_input")
changed_paths=$(jq -r '.tool_input.command // empty' <<<"$hook_input" | sed -nE 's/^\*\*\* (Add|Update|Delete) File: (.*)$/\2/p; s/^\*\*\* Move to: (.*)$/\1/p')
copy_sources=$(jq -r '.copies[].src' "$MANIFEST" | sed "s|{{REPO_ROOT}}|$REPO_ROOT|g")

while IFS= read -r file_path; do
  [[ -z "$file_path" ]] && continue

  if [[ "$file_path" != /* && -n "$session_cwd" ]]; then
    file_path="$session_cwd/${file_path#./}"
  fi

  if [[ "$file_path" == "$MANIFEST" ]] || grep -qxF "$file_path" <<<"$copy_sources"; then
    cd "$REPO_ROOT" && bin/hal sync
    exit 0
  fi
done <<<"$changed_paths"
