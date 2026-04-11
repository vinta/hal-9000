#!/bin/bash
# Install HAL 9000 statusline into Claude Code
set -e

REMOTE_URL="https://raw.githubusercontent.com/vinta/hal-9000/main/dotfiles/.claude/statusline/hal-statusline.py"
DEST="$HOME/.claude/statusline/hal-statusline.py"
SETTINGS="$HOME/.claude/settings.json"

if ! command -v python3 &>/dev/null; then
  echo "Error: python3 is required but not installed." >&2
  exit 1
fi

if ! command -v curl &>/dev/null; then
  echo "Error: curl is required but not installed." >&2
  exit 1
fi

# Download statusline script from GitHub
mkdir -p "$(dirname "$DEST")"
curl -fsSL "$REMOTE_URL" -o "$DEST"
echo "Downloaded statusline to $DEST"

# Write statusLine into settings.json
STATUSLINE_CMD="python3 $DEST"
python3 - "$SETTINGS" "$STATUSLINE_CMD" <<'PYEOF'
import json, sys
from pathlib import Path

path = Path(sys.argv[1])
cmd = sys.argv[2]

d = {}
if path.exists():
    with path.open() as f:
        try:
            d = json.load(f)
        except Exception:
            d = {}

d["statusLine"] = {"type": "command", "command": cmd}

with path.open("w") as f:
    json.dump(d, f, indent=2)
    f.write("\n")
PYEOF

echo "HAL 9000 statusline installed. Restart Claude Code to activate."
