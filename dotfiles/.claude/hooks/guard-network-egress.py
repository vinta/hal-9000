#!/usr/bin/env python3
"""
PreToolUse guard forcing a prompt on Bash commands that send local data out over the network.

Claude Code's auto-mode classifier reads the command text but never the tool results that produced it, so a request body assembled from earlier command output
(`curl -d "$PAYLOAD"`) reaches the classifier with the payload already invisible. This guard covers that gap from the other side: it matches the shape of the
request rather than its contents, and asks instead of denying, because uploading a locally generated file to one's own API is ordinary work.

Matching is text-level and runs per subcommand, on the subcommands whose first word is a network tool. That keeps `ssh host "curl -T dump.sql ..."` in scope,
since the quoted inner command travels with the `ssh` subcommand, while a commit message or a script that merely mentions `-d` or `-T` stays out of it. The
same limits as guard-bash-paths apply: it cannot see inside a script file the command executes, and it does not resolve command substitution.
"""

from __future__ import annotations

import json
import re
import sys

NETWORK_TOOLS = frozenset({"curl", "wget", "http", "httpie", "nc", "ncat", "scp", "rsync", "ssh"})

# Shell operators that separate one command from the next, matching the set Claude Code itself recognizes when it matches permission rules per subcommand.
SUBCOMMAND_SEPARATOR_RE = re.compile(r"&&|\|\||;|\||&|\n")

# A leading `VAR=value` assignment, plus the wrappers that run their argument as the actual command, so the real binary can be found.
COMMAND_PREFIX_RE = re.compile(r"^(?:[A-Za-z_][A-Za-z0-9_]*=\S*\s+|(?:timeout|time|nice|nohup|stdbuf|command|builtin|noglob|sudo|xargs)\s+)+")

# The tools that move a file as itself, rather than sending a request that happens to have a body.
TRANSFER_TOOLS = frozenset({"scp", "rsync"})

URL_RE = re.compile(r"\bhttps?://([^/\s\"'`)]+)")
LOCAL_HOST_RE = re.compile(r"(?:localhost|127\.0\.0\.1|0\.0\.0\.0|\[::1\]|host\.docker\.internal)(?::\d+)?$")

# Each entry is (regex, what the shape does) and is only consulted once the command is known to reach the network.
EGRESS_SHAPES = [
    (re.compile(r"(?:^|\s)(?:-d|--data|--data-binary|--data-raw|--data-urlencode)\s*@"), "uploads a local file as the request body"),
    (re.compile(r"(?:^|\s)(?:-F|--form)\s*\S*=@"), "attaches a local file as a multipart form field"),
    (re.compile(r"(?:^|\s)(?:-T|--upload-file)\s"), "uploads a local file"),
    (re.compile(r"--post-file="), "uploads a local file as the request body"),
    (re.compile(r"(?:-d|--data|--data-binary|--data-raw|--data-urlencode|--form|-F)\s*[\"']?\$\(\s*(?:cat|head|tail|base64)\b"), "puts file contents into the request body"),
    (re.compile(r"(?:-d|--data|--data-binary|--data-raw|--data-urlencode|--form|-F)\s*[\"']?`\s*(?:cat|head|tail|base64)\b"), "puts file contents into the request body"),
]

# Local secret material worth a prompt whenever it appears in a command that also reaches the network. Paths that guard-bash-paths.py already denies outright
# (~/.aws, ~/.ssh, ~/*credential*, and the rest) are deliberately absent: this list covers what that guard does not, chiefly project-local files.
SECRET_FILES_RE = re.compile(r"(?:^|[\s/\"'=@])(?:\.env(?:\.[\w.-]+)?|\.envrc|\.netrc|\.npmrc|\.pypirc|id_rsa|id_ed25519|[\w.-]+\.(?:pem|p12|pfx|key))\b")


def is_local_only(command: str) -> bool:
    urls = URL_RE.findall(command)
    return bool(urls) and all(LOCAL_HOST_RE.match(host) for host in urls)


def network_tool(subcommand: str) -> str | None:
    binary = COMMAND_PREFIX_RE.sub("", subcommand.lstrip(" (\"'`")).split(" ", 1)[0]
    binary = binary.rsplit("/", 1)[-1]
    return binary if binary in NETWORK_TOOLS else None


def check_subcommand(subcommand: str, tool: str) -> str | None:
    # A request that never leaves the machine carries nothing out, and local dev servers are authenticated with the same project secrets as remote ones.
    if is_local_only(subcommand):
        return None
    for pattern, description in EGRESS_SHAPES:
        if pattern.search(subcommand):
            return f"the command {description}"
    # A secret file read for a header value goes to the API that issued it, which is routine. A secret file handed to scp, or posted as a request body, is
    # the file itself leaving the machine.
    if tool in TRANSFER_TOOLS or re.search(r"@\S*\.env", subcommand):
        secret = SECRET_FILES_RE.search(subcommand)
        if secret:
            named = secret.group().strip("\"'=@/ ")
            return f"the command sends local secret material ({named})"
    return None


def check(command: str) -> str | None:
    for subcommand in SUBCOMMAND_SEPARATOR_RE.split(command):
        tool = network_tool(subcommand)
        if not tool:
            continue
        reason = check_subcommand(subcommand, tool)
        if reason:
            return reason
    return None


if __name__ == "__main__":
    data = json.load(sys.stdin)
    command = data.get("tool_input", {}).get("command", "")
    reason = check(command)
    if reason:
        json.dump(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "ask",
                    "permissionDecisionReason": f"[guard-network-egress hook] Confirm this send: {reason}.",
                }
            },
            sys.stdout,
        )
