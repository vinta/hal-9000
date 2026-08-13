#!/usr/bin/env bash
set -euo pipefail

if jq -r '.tool_input.command // ""' | grep -Eq '^\*\*\* Update File: (.*/)?dotfiles/hal_dotfiles\.json$'; then
  cd "$(dirname "$0")/../.."
  bin/hal sync
fi
