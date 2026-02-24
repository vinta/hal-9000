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
import time
from pathlib import Path

PLUGIN_ROOT = Path(os.environ.get("CLAUDE_PLUGIN_ROOT", Path(__file__).resolve().parent.parent))
MANIFEST_PATH = PLUGIN_ROOT / "manifest.json"
CONFIG_PATH = PLUGIN_ROOT / "config.json"
STATE_PATH = Path("/tmp/hal-voice-state.json")  # noqa: S108 hardcoded-temp-file
LOCK_PATH = Path("/tmp/hal-voice.lock")  # noqa: S108 hardcoded-temp-file
LOG_PATH = Path("/tmp/hal-voice.log")  # noqa: S108 hardcoded-temp-file

DEFAULT_CONFIG = {
    "enabled": True,
    "volume": 0.5,
    "debounce_seconds": 5,
    "replay_suppression_seconds": 3,
    "suppress_subagent_complete": True,
}

DEFAULT_STATE = {
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
    file_handler = logging.FileHandler(LOG_PATH)
    file_handler.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
    logger.addHandler(file_handler)


# -- Config --


def load_config(config_path: Path) -> dict:
    config = dict(DEFAULT_CONFIG)
    with contextlib.suppress(FileNotFoundError, json.JSONDecodeError, OSError):
        config.update(json.loads(config_path.read_text()))
    return config


# -- State --


def load_state(state_path: Path) -> dict:
    try:
        data = json.loads(state_path.read_text())
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        data = {}
    return {k: data.get(k, v) for k, v in DEFAULT_STATE.items()}


def save_state(state_path: Path, state: dict) -> None:
    try:
        state_path.write_text(json.dumps(state))
    except OSError:
        logger.exception("failed to write state")


# -- Detection --

# Maps hook_event_name to the hook_input field that matcher regexes test against.
# Mirrors MATCHER_FIELD in types.py. Events not listed have no matcher support.
_MATCHER_FIELD: dict[str, str] = {
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


def _detect_regex(rule: dict, hook_input: dict) -> bool:
    event = hook_input.get("hook_event_name", "")
    text = hook_input.get("prompt", "") if event == "UserPromptSubmit" else hook_input.get("last_assistant_message", "")
    if not text:
        return False
    return bool(re.search(rule["pattern"], text, re.IGNORECASE))


def _detect_matcher(rule: dict, hook_input: dict) -> bool:
    pattern = rule.get("matcher", "")
    field = _MATCHER_FIELD.get(hook_input.get("hook_event_name", ""), "")
    text = hook_input.get(field, "") if field else ""
    return bool(re.search(pattern, text, re.IGNORECASE))


def _detect_elapsed(rule: dict, state: dict) -> bool:
    last_prompt = state.get("last_prompt_time", 0.0)
    if last_prompt == 0.0:
        return False
    return (time.time() - last_prompt) >= rule["min_seconds"]


def evaluate_detection(rule: dict, hook_input: dict, state: dict) -> bool:
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


# -- Clip selection --


def pick_clip(clips: list[str], last_played: str | None) -> str:
    if len(clips) == 1:
        return clips[0]
    candidates = [c for c in clips if c != last_played]
    return random.choice(candidates)  # noqa: S311 standard-pseudo-random


# -- Suppression --


def should_debounce(state: dict, config: dict, *, now: float) -> bool:
    last = state.get("last_stop_time", 0.0)
    if last == 0.0:
        return False
    return (now - last) < config["debounce_seconds"]


def should_suppress_replay(state: dict, config: dict, *, session_id: str, now: float) -> bool:
    start_time = state.get("session_start_times", {}).get(session_id)
    if start_time is None:
        return False
    return (now - start_time) < config["replay_suppression_seconds"]


def should_suppress_subagent(state: dict, config: dict, *, session_id: str) -> bool:
    if not config.get("suppress_subagent_complete", True):
        return False
    return session_id in state.get("subagent_sessions", {})


# -- Manifest matching --


def match_manifest(manifest: dict, hook_event: str, tool_name: str, hook_input: dict, state: dict) -> tuple[str, str] | None:
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


# -- Cleanup --


def cleanup_old_sessions(state: dict, *, now: float, max_age: float = 86400) -> None:
    for bucket in ("session_start_times", "subagent_sessions"):
        state[bucket] = {k: v for k, v in state[bucket].items() if (now - v) < max_age}


# -- Audio --


def _find_audio_player() -> list[str]:
    system = platform.system()
    candidates: list[tuple[str, list[str]]] = []

    if system == "Darwin":
        candidates = [("afplay", ["afplay"])]
    elif system == "Linux":
        candidates = [
            ("paplay", ["paplay"]),
            ("aplay", ["aplay"]),
            ("ffplay", ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet"]),
        ]
    elif system == "Windows":
        candidates = [("ffplay", ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet"])]

    for name, cmd in candidates:
        if shutil.which(name):
            return cmd
    return []


def kill_previous_sound(state: dict) -> None:
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

    cmd = [*player]
    if player[0] == "afplay":
        cmd.extend(["-v", str(volume)])
    cmd.append(str(clip_path))

    logger.info("playing %s via %s", clip_path.name, player[0])
    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)  # noqa: S603 subprocess-without-shell-equals-true
    return proc.pid


# -- Main --


def _record_tracking(hook_event: str, hook_input: dict, state: dict, *, session_id: str, now: float) -> None:
    if hook_event == "SessionStart" and session_id:
        state["session_start_times"][session_id] = now
    if hook_event == "UserPromptSubmit":
        state["last_prompt_time"] = now
    if hook_event == "SubagentStart":
        child_id = hook_input.get("child_session_id", "")
        if child_id:
            state["subagent_sessions"][child_id] = now


def _is_suppressed(hook_event: str, state: dict, config: dict, *, session_id: str, now: float) -> bool:
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
    hook_input = json.loads(sys.stdin.read())
    logger.info("hook_input=%s", json.dumps(hook_input, sort_keys=True))

    hook_event = hook_input.get("hook_event_name", "")
    if not hook_event:
        return

    session_id = hook_input.get("session_id", "")
    now = time.time()

    config = load_config(CONFIG_PATH)
    if not config["enabled"]:
        return

    # Serialize concurrent hook invocations with an exclusive file lock.
    # Without this, rapid hooks race on state read/write and sounds overlap.
    lock_fd = os.open(str(LOCK_PATH), os.O_CREAT | os.O_RDWR)
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX)

        state = load_state(STATE_PATH)

        _record_tracking(hook_event, hook_input, state, session_id=session_id, now=now)

        if _is_suppressed(hook_event, state, config, session_id=session_id, now=now):
            save_state(STATE_PATH, state)
            return

        # Match manifest
        if not MANIFEST_PATH.is_file():
            logger.error("manifest not found: %s", MANIFEST_PATH)
            save_state(STATE_PATH, state)
            return

        manifest = json.loads(MANIFEST_PATH.read_text())
        tool_name = hook_input.get("tool_name", "")
        result = match_manifest(manifest, hook_event, tool_name, hook_input, state)

        if result is None:
            logger.info("no match for %s", hook_event)
            save_state(STATE_PATH, state)
            return

        category, clip = result
        logger.info("matched %s -> %s", category, clip)

        # Kill previous sound and play new one
        kill_previous_sound(state)
        pid = play_sound(PLUGIN_ROOT / clip, config["volume"])

        # Update state
        state["last_played"][category] = clip
        if hook_event == "Stop":
            state["last_stop_time"] = now
        state["sound_pid"] = pid

        # Cleanup on SessionEnd
        if hook_event == "SessionEnd":
            cleanup_old_sessions(state, now=now)

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
