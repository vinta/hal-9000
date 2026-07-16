"""
PreToolUse guard blocking Bash access to sensitive paths.

This is a cheap text-level first filter, not a real security boundary. It inspects the Bash command string, so it cannot see inside script files (`python3 leak.py`)
or resolve command substitution (`$(...)`, backticks): closing those would require executing the command, defeating a pre-execution guard.

Treat it as one layer among several (settings.json deny rules, the auto-mode intent classifier, OS-level filesystem permissions), of which only the OS layer is a hard guarantee.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HOME = str(Path.home())

DENIED_PREFIXES = [
    f"{HOME}/{d}"
    for d in [
        ".aws",
        ".config",
        ".docker",
        ".dropbox",
        ".gnupg",
        ".gsutil",
        ".kube",
        ".npmrc",
        ".orbstack",
        ".pypirc",
        ".ssh",
        "Dropbox",
        "Library",
    ]
] + ["/etc/"]

DENIED_SUBSTRINGS = ["credential"]

# Matches simple `VAR=value` assignments so `D=Dropbox; ls ~/$D` can be resolved
# before the path check. Not a real shell parser: command substitution like
# `$(...)` still isn't resolved, since doing that safely would require running
# the command first, which defeats a pre-execution guard.
ASSIGNMENT_RE = re.compile(r"""(?:^|[;&\n])\s*([A-Za-z_][A-Za-z0-9_]*)=("[^"]*"|'[^']*'|\S*)""")


def expand_local_assignments(command: str) -> str:
    env: dict[str, str] = {}
    for match in ASSIGNMENT_RE.finditer(command):
        name, value = match.group(1), match.group(2)
        if len(value) >= 2 and value[0] in "'\"" and value[-1] == value[0]:  # noqa: PLR2004 magic-value-comparison
            value = value[1:-1]
        env[name] = value

    expanded = command
    for name, value in env.items():
        expanded = re.sub(rf"\$\{{{name}\}}|\${name}\b", value, expanded)
    return expanded


def check(command: str) -> str | None:
    expanded = expand_local_assignments(command)
    normalized = expanded.replace("${HOME}", HOME).replace("$HOME", HOME).replace("~", HOME)
    # Drop quotes and backslashes the shell would collapse at runtime, so
    # `~/Drop"box"` and `~/Drop\box` still resolve to the denied path.
    stripped = re.sub(r"""["'\\]""", "", normalized)
    lower = stripped.lower()
    for prefix in DENIED_PREFIXES:
        # Anchor at a path boundary so `.config` does not match `.configuration`.
        if re.search(re.escape(prefix.lower()) + r"(?![\w.\-])", lower):
            return prefix
    if HOME.lower() in lower:
        for substr in DENIED_SUBSTRINGS:
            if substr in lower:
                return f"~/*{substr}*"
    return None


if __name__ == "__main__":
    data = json.load(sys.stdin)
    command = data.get("tool_input", {}).get("command", "")
    blocked = check(command)
    if blocked:
        json.dump(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": f"[guard-bash-paths hook] Blocked Bash access to denied path: {blocked}",
                }
            },
            sys.stdout,
        )
