import json
import logging
import os
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Literal, TypedDict


class ManifestEntry(TypedDict, total=False):
    hook_event: str
    audio: str
    detection: Literal["always", "regex"]
    matcher: str
    pattern: str


PLUGIN_ROOT = Path(os.environ.get("CLAUDE_PLUGIN_ROOT", Path(__file__).resolve().parent.parent))
MANIFEST = PLUGIN_ROOT / "manifest.json"
LOG_PATH = Path("/tmp/hal-voice.log")  # noqa: S108 hardcoded-temp-file

logger = logging.getLogger("hal-voice")
logger.setLevel(logging.DEBUG)
logger.propagate = False

if not logger.handlers:
    file_handler = logging.FileHandler(LOG_PATH)
    file_handler.setFormatter(logging.Formatter("hal-voice: %(message)s"))
    logger.addHandler(file_handler)


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


def play_audio(relative_path: str) -> None:
    audio_path = PLUGIN_ROOT / relative_path
    if not audio_path.is_file():
        logger.error("audio not found: %s", audio_path)
        return

    player = _find_audio_player()
    if not player:
        logger.error("no audio player found (tried: afplay, paplay, aplay, ffplay)")
        return

    logger.info("playing %s via %s", audio_path.name, player[0])
    subprocess.Popen(  # noqa: S603 subprocess-without-shell-equals-true
        [*player, str(audio_path)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def main() -> None:
    if not MANIFEST.is_file():
        logger.error("manifest not found: %s", MANIFEST)
        return

    hook_input = json.loads(sys.stdin.read())
    logger.info("hook_input=%s", json.dumps(hook_input, sort_keys=True))
    hook_event = hook_input.get("hook_event_name", "")
    if not hook_event:
        return

    logger.info("event=%s", hook_event)

    entries: list[ManifestEntry] = json.loads(MANIFEST.read_text())
    tool_name = hook_input.get("tool_name", "")
    matched = [e for e in entries if e["hook_event"] == hook_event and ("matcher" not in e or e["matcher"] == tool_name)]
    if not matched:
        logger.info("no manifest entries for %s", hook_event)
        return

    for entry in matched:
        detection = entry["detection"]
        audio = entry["audio"]

        if detection == "always":
            play_audio(audio)

        elif detection == "regex":
            message = hook_input.get("last_assistant_message", "")
            if not message:
                continue
            pattern = entry["pattern"]
            if re.search(pattern, message, re.IGNORECASE):
                play_audio(audio)

        else:
            logger.error("unknown detection type: %s", detection)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logger.exception("unhandled error")
    finally:
        sys.exit(0)
