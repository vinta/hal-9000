from __future__ import annotations

import json
import re
import sys
from typing import TypedDict

COMMITTER_AGENT_TYPES = {"committer", "hal-skills:committer"}

# Read-only inspection plus staging/committing. Deliberately absent:
# - apply: hand-built patches can stage content that was never in the working tree
# - checkout / reset: can discard the author's uncommitted work
# - mv: renames files on disk (the author renames; the committer only stages)
ALLOWED_GIT_SUBCOMMANDS = {
    "add",
    "branch",
    "commit",
    "diff",
    "log",
    "ls-files",
    "restore",
    "rev-parse",
    "rm",
    "show",
    "stash",
    "status",
}

SINGLE_QUOTED = re.compile(r"'[^']*'")
DOUBLE_QUOTED = re.compile(r"\"(?:\\.|[^\"\\])*\"")
SEGMENT_SEPARATOR = re.compile(r"&&|;|\n")

# These expand even inside double quotes, so they must be checked before
# double-quoted spans are stripped. Only single quotes make them literal.
EXPANSION_SYNTAX = [
    ("`", "backticks"),
    ("$(", "command substitution"),
]

REDIRECTION_SYNTAX = [
    (">", "redirection"),
    ("<", "redirection/heredoc"),
]


class ToolInput(TypedDict, total=False):
    command: str


class HookInput(TypedDict, total=False):
    tool_name: str
    tool_input: ToolInput
    agent_type: str


DENIED_FLAGS = {
    "add": ({"-f", "--force"}, "`git add -f` bypasses .gitignore — skip the file and mention it in your summary"),
    "commit": ({"--amend", "--no-verify", "-n"}, "`git commit` must not amend or skip hooks"),
    "branch": (
        {"-d", "-D", "-m", "-M", "-c", "-C", "-f", "--force", "--delete", "--move", "--copy"},
        "`git branch` is allowed read-only",
    ),
}


def check_git_segment(tokens: list[str]) -> str | None:
    subcommand = tokens[1] if len(tokens) > 1 else ""
    if subcommand == "apply":
        return "`git apply` can stage content that was never in the working tree — stage whole files with `git add <file>` instead"
    if subcommand not in ALLOWED_GIT_SUBCOMMANDS:
        return f"`git {subcommand}` is not in the committer allowlist"
    flags = set(tokens[2:])
    if subcommand == "restore" and ("--staged" not in flags or flags & {"--worktree", "-W"}):
        return "`git restore` may only unstage (`--staged`) — restoring the working tree discards the author's changes"
    if subcommand == "rm" and "--cached" not in flags:
        return "`git rm` without `--cached` deletes files from disk — stage deletions with `git add <file>` instead"
    denied_flags, reason = DENIED_FLAGS.get(subcommand, (set(), ""))
    if flags & denied_flags:
        return reason
    return None


def check_segment(segment: str) -> str | None:
    tokens = segment.split()
    if not tokens:
        return None
    if "|" in segment or "&" in segment:
        return "pipes and background execution are not allowed"
    if tokens[0] in {"cd", "pwd"}:
        return None
    if tokens[0] != "git":
        return f"`{tokens[0]}` is not a git command — the committer only inspects, stages, and commits"
    return check_git_segment(tokens)


def check(command: str) -> str | None:
    no_single = SINGLE_QUOTED.sub("''", command)
    for needle, label in EXPANSION_SYNTAX:
        if needle in no_single:
            return f"{label} is not allowed"
    stripped = DOUBLE_QUOTED.sub("''", no_single)
    for needle, label in REDIRECTION_SYNTAX:
        if needle in stripped:
            return f"{label} is not allowed"
    for segment in SEGMENT_SEPARATOR.split(stripped):
        reason = check_segment(segment)
        if reason:
            return reason
    return None


def main() -> None:
    data: HookInput = json.load(sys.stdin)
    if data.get("agent_type", "") not in COMMITTER_AGENT_TYPES:
        return
    command = data.get("tool_input", {}).get("command", "")
    reason = check(command)
    if reason:
        json.dump(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": f"committer guard: {reason}",
                }
            },
            sys.stdout,
        )


if __name__ == "__main__":
    main()
