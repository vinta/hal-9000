#!/bin/bash
# Install HAL 9000 statusline into Claude Code
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SRC="$REPO_ROOT/dotfiles/.claude/statusline/hal-statusline.py"
DEST="$HOME/.claude/statusline/hal-statusline.py"
SETTINGS="$HOME/.claude/settings.json"

if [ ! -f "$SRC" ]; then
  echo "Error: source not found: $SRC" >&2
  exit 1
fi

if ! command -v python3 &>/dev/null; then
  echo "Error: python3 is required but not installed." >&2
  exit 1
fi

# Symlink the statusline script
mkdir -p "$(dirname "$DEST")"
if [ -L "$DEST" ]; then
  CURRENT_TARGET=$(readlink "$DEST")
  if [ "$CURRENT_TARGET" = "$SRC" ]; then
    echo "Symlink already points to $SRC"
  else
    echo "Updating symlink: $CURRENT_TARGET -> $SRC"
    ln -sf "$SRC" "$DEST"
  fi
elif [ -f "$DEST" ]; then
  echo "Replacing existing file with symlink"
  ln -sf "$SRC" "$DEST"
else
  ln -sf "$SRC" "$DEST"
  echo "Symlinked $DEST -> $SRC"
fi

# Check for existing statusLine config
STATUSLINE_CMD="python3 $DEST"
EXISTING=$(python3 -c "
import json, os
path = os.path.expanduser('$SETTINGS')
if os.path.exists(path):
    try:
        d = json.load(open(path))
        sl = d.get('statusLine', {})
        cmd = sl.get('command', '')
        if cmd and cmd != '$STATUSLINE_CMD':
            print(cmd)
    except: pass
" 2>/dev/null)

if [ -n "$EXISTING" ]; then
  echo "Another statusline is already configured:"
  echo "  $EXISTING"
  printf "Replace it with HAL 9000 statusline? [Y/n] "
  read -r ans
  if [ "$ans" = "n" ] || [ "$ans" = "N" ]; then
    echo "Skipped. Existing statusline kept."
    exit 0
  fi
fi

# Write statusLine into settings.json
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
