#!/usr/bin/env python3
from __future__ import annotations

import json
import logging
import os
import re
import sys
import tempfile
import unicodedata
from pathlib import Path
from typing import Literal, TypedDict

LOG_PATH = Path("/tmp/hal-session-auto-rename.log")  # noqa: S108 hardcoded-temp-file

# Claude Code appends `ai-title` entries throughout the session, so the newest one is near the end of the transcript
TRANSCRIPT_TAIL_BYTES = 256 * 1024
# Terminal columns rather than characters, so a CJK title takes up the same room in the prompt bar as an English one
TITLE_MAX_COLUMNS = 30

logger = logging.getLogger("session-auto-rename")
logger.setLevel(logging.DEBUG)
logger.propagate = False

if not logger.handlers:
    file_handler = logging.FileHandler(LOG_PATH)
    file_handler.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
    logger.addHandler(file_handler)


# https://code.claude.com/docs/en/hooks#userpromptsubmit-input
class HookInput(TypedDict):
    session_id: str
    transcript_path: str
    cwd: str
    permission_mode: str
    hook_event_name: Literal["UserPromptSubmit"]
    prompt: str


class State(TypedDict):
    title: str


def state_path(session_id: str) -> Path:
    return Path(f"/tmp/hal-session-auto-rename-{session_id}.json")  # noqa: S108 hardcoded-temp-file


def read_state(session_id: str) -> State | None:
    try:
        with state_path(session_id).open() as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def write_state(session_id: str, payload: State) -> None:
    fd, tmp_path = tempfile.mkstemp(dir="/tmp", prefix="hal-session-auto-rename-")
    with os.fdopen(fd, "w") as f:
        json.dump(payload, f)
    Path(tmp_path).rename(state_path(session_id))


def read_latest_ai_title(transcript_path: str) -> str:
    try:
        with Path(transcript_path).open("rb") as f:
            f.seek(0, os.SEEK_END)
            size = f.tell()
            f.seek(max(0, size - TRANSCRIPT_TAIL_BYTES))
            tail = f.read().decode("utf-8", errors="ignore")
    except FileNotFoundError:
        return ""

    lines = tail.splitlines()
    for line in reversed(lines):
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            # The first line of the tail is usually a partial entry, the rest are always whole
            continue
        if entry.get("type") == "ai-title":
            return entry.get("aiTitle", "")
    return ""


def is_wide(char: str) -> bool:
    # CJK and other East Asian wide characters take two terminal columns each
    return unicodedata.east_asian_width(char) in {"W", "F"}


def display_width(text: str) -> int:
    return sum(2 if is_wide(char) else 1 for char in text)


def slugify(text: str) -> str:
    # `\W` is Unicode-aware, so a title written in any script keeps its letters instead of slugifying to nothing
    slug = re.sub(r"[\W_]+", "-", text.lower()).strip("-")
    if display_width(slug) <= TITLE_MAX_COLUMNS:
        return slug

    head = ""
    width = 0
    for char in slug:
        width += display_width(char)
        if width > TITLE_MAX_COLUMNS:
            break
        head += char
    if is_wide(head[-1]):
        # Scripts written without spaces have no hyphen to cut back to, and each character stands on its own anyway
        return head.strip("-")
    # Cut at a word boundary so the title never ends mid-word, unless the first word alone is already too long
    return head.rsplit("-", 1)[0].strip("-") or head.strip("-")


def main() -> None:
    data: HookInput = json.load(sys.stdin)
    session_id = data["session_id"]

    ai_title = read_latest_ai_title(data["transcript_path"])
    if not ai_title:
        # Claude Code writes the first `ai-title` after the first assistant turn, so the first prompt of a session has nothing to read yet
        logger.debug("session=%s no ai-title yet", session_id)
        return

    slug = slugify(ai_title)
    if not slug:
        logger.debug("session=%s ai-title=%r slugified to nothing", session_id, ai_title)
        return

    # Claude Code keeps updating `ai-title` as the conversation drifts, and the session name follows it, but only when it actually changed
    state = read_state(session_id)
    if state is not None and state["title"] == slug:
        return

    logger.debug("session=%s ai-title=%r slug=%s", session_id, ai_title, slug)
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "sessionTitle": slug}}))
    write_state(session_id, {"title": slug})


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logger.exception("unhandled error")
    finally:
        sys.exit(0)
