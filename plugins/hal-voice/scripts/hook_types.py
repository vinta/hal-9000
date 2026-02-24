"""Typed definitions for Claude Code hook input payloads.

Each hook event delivers JSON on stdin with common fields plus event-specific
fields. These TypedDicts document the exact shape of each payload per the
official hooks reference: https://code.claude.com/docs/en/hooks

The MATCHER_FIELD mapping tracks which input field each event's hooks.json
``matcher`` regex is tested against.
"""

from __future__ import annotations

from typing import Literal, NotRequired, TypedDict

# ---------------------------------------------------------------------------
# Common fields present in every hook event
# ---------------------------------------------------------------------------

PermissionMode = Literal["default", "plan", "acceptEdits", "dontAsk", "bypassPermissions"]


class CommonInput(TypedDict):
    session_id: str
    transcript_path: str
    cwd: str
    permission_mode: PermissionMode
    hook_event_name: str


# ---------------------------------------------------------------------------
# Per-event input types
# ---------------------------------------------------------------------------

SessionStartSource = Literal["startup", "resume", "clear", "compact"]


class SessionStartInput(CommonInput):
    source: SessionStartSource
    model: str
    agent_type: NotRequired[str]


SessionEndReason = Literal["clear", "logout", "prompt_input_exit", "bypass_permissions_disabled", "other"]


class SessionEndInput(CommonInput):
    reason: SessionEndReason


class UserPromptSubmitInput(CommonInput):
    prompt: str


class PreToolUseInput(CommonInput):
    tool_name: str
    tool_input: dict
    tool_use_id: str


class PostToolUseInput(CommonInput):
    tool_name: str
    tool_input: dict
    tool_response: dict
    tool_use_id: str


class PostToolUseFailureInput(CommonInput):
    tool_name: str
    tool_input: dict
    tool_use_id: str
    error: str
    is_interrupt: NotRequired[bool]


class PermissionRequestInput(CommonInput):
    tool_name: str
    tool_input: dict
    permission_suggestions: NotRequired[list[dict]]


NotificationType = Literal["permission_prompt", "idle_prompt", "auth_success", "elicitation_dialog"]


class NotificationInput(CommonInput):
    message: str
    title: NotRequired[str]
    notification_type: NotificationType


class SubagentStartInput(CommonInput):
    agent_id: str
    agent_type: str


class SubagentStopInput(CommonInput):
    stop_hook_active: bool
    agent_id: str
    agent_type: str
    agent_transcript_path: str
    last_assistant_message: str


class StopInput(CommonInput):
    stop_hook_active: bool
    last_assistant_message: str


class TeammateIdleInput(CommonInput):
    teammate_name: str
    team_name: str


class TaskCompletedInput(CommonInput):
    task_id: str
    task_subject: str
    task_description: NotRequired[str]
    teammate_name: NotRequired[str]
    team_name: NotRequired[str]


ConfigChangeSource = Literal["user_settings", "project_settings", "local_settings", "policy_settings", "skills"]


class ConfigChangeInput(CommonInput):
    source: ConfigChangeSource
    file_path: NotRequired[str]


class WorktreeCreateInput(CommonInput):
    name: str


class WorktreeRemoveInput(CommonInput):
    worktree_path: str


PreCompactTrigger = Literal["manual", "auto"]


class PreCompactInput(CommonInput):
    trigger: PreCompactTrigger
    custom_instructions: str


# ---------------------------------------------------------------------------
# Matcher field mapping
# ---------------------------------------------------------------------------
# Maps hook_event_name -> the hook_input field that the hooks.json ``matcher``
# regex is tested against. Events not listed have no matcher support.

MATCHER_FIELD: dict[str, str] = {
    "SessionStart": "source",
    "SessionEnd": "reason",
    "PreToolUse": "tool_name",
    "PostToolUse": "tool_name",
    "PostToolUseFailure": "tool_name",
    "PermissionRequest": "tool_name",
    "Notification": "notification_type",
    "SubagentStart": "agent_type",
    "SubagentStop": "agent_type",
    "PreCompact": "trigger",
    "ConfigChange": "source",
}
