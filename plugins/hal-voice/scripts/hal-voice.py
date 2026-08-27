#!/usr/bin/env python3
from __future__ import annotations

import contextlib
import fcntl
import json
import logging
import os
import platform
import random
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, Literal, TypedDict


class CommonInput(TypedDict):
    session_id: str
    transcript_path: str
    cwd: str
    hook_event_name: Literal[
        "ConfigChange",
        "CwdChanged",
        "DirectoryAdded",
        "Elicitation",
        "ElicitationResult",
        "FileChanged",
        "InstructionsLoaded",
        "MessageDisplay",
        "Notification",
        "PermissionDenied",
        "PermissionRequest",
        "PostCompact",
        "PostToolBatch",
        "PostToolUse",
        "PostToolUseFailure",
        "PreCompact",
        "PreToolUse",
        "SessionEnd",
        "SessionStart",
        "Setup",
        "Stop",
        "StopFailure",
        "SubagentStart",
        "SubagentStop",
        "TaskCompleted",
        "TaskCreated",
        "TeammateIdle",
        "UserPromptExpansion",
        "UserPromptSubmit",
        "WorktreeCreate",
        "WorktreeRemove",
    ]


class HookInput(CommonInput, total=False):
    # Common to most events, but not guaranteed on any of them
    permission_mode: Literal["default", "plan", "acceptEdits", "auto", "dontAsk", "bypassPermissions"]
    prompt_id: str
    effort: dict[str, Any]
    # SessionStart, ConfigChange, DirectoryAdded
    source: str
    # SessionStart
    model: str
    session_title: str
    # SessionStart, SubagentStart, SubagentStop
    agent_type: str
    # SessionEnd, PermissionDenied
    reason: str
    # UserPromptSubmit, UserPromptExpansion
    prompt: str
    # UserPromptExpansion
    expansion_type: str
    command_name: str
    command_args: str
    command_source: str
    # MessageDisplay
    turn_id: str
    message_id: str
    index: int
    final: bool
    delta: str
    # PreToolUse, PostToolUse, PostToolUseFailure, PermissionRequest, PermissionDenied
    tool_name: str
    tool_input: dict[str, Any]
    tool_use_id: str
    # PostToolUse
    tool_response: dict[str, Any]
    # PostToolUse, PostToolUseFailure
    duration_ms: int
    # PostToolUseFailure, StopFailure
    error: str
    # PostToolUseFailure
    is_interrupt: bool
    # PostToolBatch
    tool_calls: list[dict[str, Any]]
    # PermissionRequest
    permission_suggestions: list[dict[str, Any]]
    # Notification, Elicitation
    message: str
    # Notification
    title: str
    notification_type: str
    # SubagentStart, SubagentStop
    agent_id: str
    child_session_id: str
    # SubagentStop, Stop, StopFailure
    last_assistant_message: str
    # SubagentStop, Stop
    stop_hook_active: bool
    background_tasks: list[dict[str, Any]]
    session_crons: list[dict[str, Any]]
    # SubagentStop
    agent_transcript_path: str
    # StopFailure
    error_details: str
    # TeammateIdle, TaskCreated, TaskCompleted
    teammate_name: str
    team_name: str
    # TaskCreated, TaskCompleted
    task_id: str
    task_subject: str
    task_description: str
    # ConfigChange, InstructionsLoaded, FileChanged
    file_path: str
    # InstructionsLoaded
    memory_type: str
    load_reason: str
    globs: list[str]
    trigger_file_path: str
    parent_file_path: str
    # CwdChanged
    old_cwd: str
    new_cwd: str
    # DirectoryAdded
    directory: str
    # FileChanged
    event: str
    # WorktreeCreate
    name: str
    # WorktreeRemove
    worktree_path: str
    # Setup, PreCompact, PostCompact
    trigger: str
    # PreCompact
    custom_instructions: str
    # PostCompact
    compact_summary: str
    # Elicitation, ElicitationResult
    mcp_server_name: str
    mode: str
    elicitation_id: str
    # Elicitation
    url: str
    requested_schema: dict[str, Any]
    # ElicitationResult
    action: str
    content: dict[str, Any]


class Config(TypedDict):
    enabled: bool
    entrypoints: list[str]
    volume: float
    debounce_seconds: float
    replay_suppression_seconds: float
    suppress_subagent_complete: bool


class State(TypedDict):
    last_played: dict[str, str]
    last_stop_time: float
    last_prompt_time: float
    session_start_times: dict[str, float]
    subagent_sessions: dict[str, float]
    sound_pid: int | None


class CommonRule(TypedDict):
    detection: str
    clips: list[str]


class Rule(CommonRule, total=False):
    # Required when detection is "matcher"
    matcher: str
    # Required when detection is "regex"
    pattern: str
    # Required when detection is "elapsed"
    min_seconds: float
    # Optional on any detection, always as a pair: local "HH:MM" clock times, inclusive of `after` and exclusive of `before`
    after: str
    before: str


# Keyed by hook event, optionally suffixed with ":<tool_name>"
Manifest = dict[str, list[Rule]]


PLUGIN_ROOT = Path(os.environ.get("CLAUDE_PLUGIN_ROOT", Path(__file__).resolve().parent.parent))
HOOKS_PATH = PLUGIN_ROOT / "hooks" / "hooks.json"
MANIFEST_PATH = PLUGIN_ROOT / "manifest.json"
CONFIG_PATH = PLUGIN_ROOT / "config.json"
STATE_PATH = Path("/tmp/hal-voice-state.json")  # noqa: S108 hardcoded-temp-file
LOCK_PATH = Path("/tmp/hal-voice.lock")  # noqa: S108 hardcoded-temp-file
# `gettempdir()` honours `$TMPDIR`, which on macOS is a per-user directory, so the log never collides with another user's on a shared machine
LOG_PATH = Path(tempfile.gettempdir()) / "hal-voice.log"
LOG_MAX_BYTES = 1024 * 1024

DEFAULT_CONFIG: Config = {
    "enabled": True,
    "entrypoints": ["cli"],
    "volume": 0.5,
    "debounce_seconds": 5,
    "replay_suppression_seconds": 3,
    "suppress_subagent_complete": True,
}

DEFAULT_STATE: State = {
    "last_played": {},
    "last_stop_time": 0.0,
    "last_prompt_time": 0.0,
    "session_start_times": {},
    "subagent_sessions": {},
    "sound_pid": None,
}

logger = logging.getLogger("hal-voice")
logger.setLevel(logging.DEBUG)
logger.propagate = False

if not logger.handlers:
    file_handler = RotatingFileHandler(LOG_PATH, maxBytes=LOG_MAX_BYTES, backupCount=1)
    file_handler.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
    logger.addHandler(file_handler)


def _is_main_agent_only(hook_event: str) -> bool:
    try:
        hooks_config = json.loads(HOOKS_PATH.read_text())
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return False
    return any(rule.get("main_agent_only") for rule in hooks_config.get("hooks", {}).get(hook_event, []))


def current_entrypoint() -> str:
    # Every surface but the terminal CLI exports its own value: `claude-desktop`, `claude-vscode`, `remote*`. Claude Code itself treats an unset variable as the CLI
    return os.environ.get("CLAUDE_CODE_ENTRYPOINT") or "cli"


def load_config(config_path: Path) -> Config:
    config = DEFAULT_CONFIG.copy()
    with contextlib.suppress(FileNotFoundError, json.JSONDecodeError, OSError):
        config.update(json.loads(config_path.read_text()))
    return config


def load_state(state_path: Path) -> State:
    try:
        data = json.loads(state_path.read_text())
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        data = {}
    return {
        "last_played": data.get("last_played", DEFAULT_STATE["last_played"]),
        "last_stop_time": data.get("last_stop_time", DEFAULT_STATE["last_stop_time"]),
        "last_prompt_time": data.get("last_prompt_time", DEFAULT_STATE["last_prompt_time"]),
        "session_start_times": data.get("session_start_times", DEFAULT_STATE["session_start_times"]),
        "subagent_sessions": data.get("subagent_sessions", DEFAULT_STATE["subagent_sessions"]),
        "sound_pid": data.get("sound_pid", DEFAULT_STATE["sound_pid"]),
    }


def save_state(state_path: Path, state: State) -> None:
    try:
        state_path.write_text(json.dumps(state))
    except OSError:
        logger.exception("failed to write state")


_MATCHER_FIELD: dict[str, str] = {
    "SessionStart": "source",
    "Setup": "trigger",
    "SessionEnd": "reason",
    "PreToolUse": "tool_name",
    "PostToolUse": "tool_name",
    "PostToolUseFailure": "tool_name",
    "PermissionRequest": "tool_name",
    "PermissionDenied": "tool_name",
    "Notification": "notification_type",
    "SubagentStart": "agent_type",
    "SubagentStop": "agent_type",
    "StopFailure": "error",
    "PreCompact": "trigger",
    "PostCompact": "trigger",
    "ConfigChange": "source",
    "DirectoryAdded": "source",
    "InstructionsLoaded": "load_reason",
    "UserPromptExpansion": "command_name",
    "Elicitation": "mcp_server_name",
    "ElicitationResult": "mcp_server_name",
    # Claude Code matches FileChanged on a filename watch list, not a field regex; hal-voice matches its own manifest rules against the changed path
    "FileChanged": "file_path",
}


def _detect_regex(rule: Rule, hook_input: HookInput) -> bool:
    event = hook_input.get("hook_event_name", "")
    text = hook_input.get("prompt", "") if event == "UserPromptSubmit" else hook_input.get("last_assistant_message", "")
    if not text:
        return False
    return bool(re.search(rule["pattern"], text, re.IGNORECASE))


def _detect_matcher(rule: Rule, hook_input: HookInput) -> bool:
    field = _MATCHER_FIELD.get(hook_input.get("hook_event_name", ""))
    if not field:
        return False
    text = hook_input.get(field, "")
    return bool(re.search(rule.get("matcher", ""), text, re.IGNORECASE))


def _detect_elapsed(rule: Rule, state: State) -> bool:
    last_prompt = state.get("last_prompt_time", 0.0)
    if last_prompt == 0.0:
        return False
    return (time.time() - last_prompt) >= rule["min_seconds"]


def _minutes_since_midnight(clock: str) -> int:
    hour, minute = clock.split(":")
    return int(hour) * 60 + int(minute)


def _within_window(after: str, before: str) -> bool:
    now = time.localtime()
    minutes = now.tm_hour * 60 + now.tm_min
    start = _minutes_since_midnight(after)
    end = _minutes_since_midnight(before)
    if start <= end:
        return start <= minutes < end
    # The window wraps past midnight, so it is the two open-ended halves
    return minutes >= start or minutes < end


def evaluate_detection(rule: Rule, hook_input: HookInput, state: State) -> bool:
    if "after" in rule and not _within_window(rule["after"], rule["before"]):
        return False

    detection = rule["detection"]

    if detection == "always":
        return True
    if detection == "regex":
        return _detect_regex(rule, hook_input)
    if detection == "matcher":
        return _detect_matcher(rule, hook_input)
    if detection == "elapsed":
        return _detect_elapsed(rule, state)

    logger.error("unknown detection type: %s", detection)
    return False


def pick_clip(clips: list[str], last_played: str | None) -> str:
    if len(clips) == 1:
        return clips[0]
    candidates = [c for c in clips if c != last_played]
    return random.choice(candidates)  # noqa: S311 standard-pseudo-random


def should_debounce(state: State, config: Config, *, now: float) -> bool:
    last = state.get("last_stop_time", 0.0)
    if last == 0.0:
        return False
    return (now - last) < config["debounce_seconds"]


def should_suppress_replay(state: State, config: Config, *, session_id: str, now: float) -> bool:
    start_time = state.get("session_start_times", {}).get(session_id)
    if start_time is None:
        return False
    return (now - start_time) < config["replay_suppression_seconds"]


def should_suppress_subagent(state: State, config: Config, *, session_id: str) -> bool:
    if not config.get("suppress_subagent_complete", True):
        return False
    return session_id in state.get("subagent_sessions", {})


def match_manifest(manifest: Manifest, hook_event: str, tool_name: str, hook_input: HookInput, state: State) -> tuple[str, str] | None:
    for key, rules in manifest.items():
        parts = key.split(":", 1)
        key_event = parts[0]
        key_tool = parts[1] if len(parts) > 1 else None

        if key_event != hook_event:
            continue
        if key_tool is not None and key_tool != tool_name:
            continue

        for rule in rules:
            if not rule.get("clips"):
                continue
            if evaluate_detection(rule, hook_input, state):
                last = state.get("last_played", {}).get(key)
                return (key, pick_clip(rule["clips"], last))

    return None


def cleanup_old_sessions(state: State, *, now: float, max_age: float = 86400) -> None:
    state["session_start_times"] = {k: v for k, v in state["session_start_times"].items() if (now - v) < max_age}
    state["subagent_sessions"] = {k: v for k, v in state["subagent_sessions"].items() if (now - v) < max_age}


def _find_audio_player() -> list[str]:
    ffplay = ("ffplay", ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet"])

    candidates = {
        "Darwin": [("afplay", ["afplay"])],
        "Linux": [("paplay", ["paplay"]), ("aplay", ["aplay"]), ffplay],
        "Windows": [ffplay],
    }.get(platform.system(), [])

    for name, cmd in candidates:
        if shutil.which(name):
            return cmd
    return []


def kill_previous_sound(state: State) -> None:
    pid = state.get("sound_pid")
    if pid is None:
        return
    with contextlib.suppress(ProcessLookupError, PermissionError):
        os.kill(pid, signal.SIGTERM)
    state["sound_pid"] = None


def play_sound(clip_path: Path, volume: float) -> int | None:
    if not clip_path.is_file():
        logger.error("audio not found: %s", clip_path)
        return None

    player = _find_audio_player()
    if not player:
        logger.error("no audio player found")
        return None

    volume_args = ["-v", str(volume)] if player[0] == "afplay" else []
    cmd = [*player, *volume_args, str(clip_path)]

    logger.info("playing %s via %s", clip_path.name, player[0])
    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)  # noqa: S603 subprocess-without-shell-equals-true
    return proc.pid


def _record_tracking(hook_event: str, hook_input: HookInput, state: State, *, session_id: str, now: float) -> None:
    if hook_event == "SessionStart" and session_id:
        state["session_start_times"][session_id] = now
    if hook_event == "UserPromptSubmit":
        state["last_prompt_time"] = now
    if hook_event == "SubagentStart":
        child_id = hook_input.get("child_session_id", "")
        if child_id:
            state["subagent_sessions"][child_id] = now


def _is_suppressed(hook_event: str, state: State, config: Config, *, session_id: str, now: float) -> bool:
    if hook_event == "Stop" and should_debounce(state, config, now=now):
        logger.info("debounced Stop event")
        return True
    if hook_event != "SessionStart" and should_suppress_replay(state, config, session_id=session_id, now=now):
        logger.info("suppressed replay event %s", hook_event)
        return True
    if hook_event == "Stop" and should_suppress_subagent(state, config, session_id=session_id):
        logger.info("suppressed subagent Stop for %s", session_id)
        return True
    return False


def main() -> None:
    hook_input: HookInput = json.loads(sys.stdin.read())
    logger.info("hook_input=%s", json.dumps(hook_input, sort_keys=True))

    hook_event = hook_input.get("hook_event_name", "")
    if not hook_event:
        return

    session_id = hook_input.get("session_id", "")
    now = time.time()

    config = load_config(CONFIG_PATH)

    # Check the entrypoint before taking the lock so other surfaces never touch the shared state file, where their events would debounce a later CLI clip
    entrypoint = current_entrypoint()
    logger.info("entrypoint=%s", entrypoint)
    if not config["enabled"] or entrypoint not in config["entrypoints"]:
        return

    lock_fd = os.open(str(LOCK_PATH), os.O_CREAT | os.O_RDWR)
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX)

        state = load_state(STATE_PATH)
        try:
            _record_tracking(hook_event, hook_input, state, session_id=session_id, now=now)

            if hook_input.get("agent_id") and _is_main_agent_only(hook_event):
                logger.info("suppressed %s in subagent (main_agent_only)", hook_event)
                return

            if _is_suppressed(hook_event, state, config, session_id=session_id, now=now):
                return

            if not MANIFEST_PATH.is_file():
                logger.error("manifest not found: %s", MANIFEST_PATH)
                return

            manifest = json.loads(MANIFEST_PATH.read_text())
            tool_name = hook_input.get("tool_name", "")
            result = match_manifest(manifest, hook_event, tool_name, hook_input, state)

            if result is None:
                logger.info("no match for %s", hook_event)
                return

            category, clip = result
            logger.info("matched %s -> %s", category, clip)

            kill_previous_sound(state)
            pid = play_sound(PLUGIN_ROOT / clip, config["volume"])

            state["last_played"][category] = clip
            if hook_event == "Stop":
                state["last_stop_time"] = now
            state["sound_pid"] = pid

            if hook_event == "SessionEnd":
                cleanup_old_sessions(state, now=now)
        finally:
            save_state(STATE_PATH, state)
    finally:
        fcntl.flock(lock_fd, fcntl.LOCK_UN)
        os.close(lock_fd)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logger.exception("unhandled error")
    finally:
        sys.exit(0)
