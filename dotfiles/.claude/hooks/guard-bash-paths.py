from __future__ import annotations

import json
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


def check(command: str) -> str | None:
    normalized = command.replace("${HOME}", HOME).replace("$HOME", HOME).replace("~", HOME)
    for prefix in DENIED_PREFIXES:
        if prefix in normalized:
            return prefix
    if HOME in normalized:
        lower = normalized.lower()
        for substr in DENIED_SUBSTRINGS:
            if substr in lower:
                return f"~/*{substr}*"
    return None


data = json.load(sys.stdin)
command = data.get("tool_input", {}).get("command", "")
blocked = check(command)
if blocked:
    json.dump(
        {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": f"Blocked: Bash access to denied path ({blocked})",
            }
        },
        sys.stdout,
    )
