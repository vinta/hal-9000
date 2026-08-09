#!/usr/bin/env python3
from __future__ import annotations

import json
import logging
import os
import re
import sys
import tempfile
import unicodedata
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Literal, TypedDict

# `gettempdir()` honours `$TMPDIR`, which on macOS is a per-user directory, so the log never collides with another user's on a shared machine
LOG_PATH = Path(tempfile.gettempdir()) / "hal-session-auto-rename.log"
LOG_MAX_BYTES = 1024 * 1024

# Claude Code appends `ai-title` entries throughout the session, so the newest one is near the end of the transcript
TRANSCRIPT_TAIL_BYTES = 256 * 1024
# Terminal columns rather than characters, so a CJK title takes up the same room in the prompt bar as an English one
TITLE_MAX_COLUMNS = 30

logger = logging.getLogger("session-auto-rename")
logger.setLevel(logging.DEBUG)
logger.propagate = False

if not logger.handlers:
    file_handler = RotatingFileHandler(LOG_PATH, maxBytes=LOG_MAX_BYTES, backupCount=1)
    file_handler.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
    logger.addHandler(file_handler)


# https://code.claude.com/docs/en/hooks#userpromptsubmit-input
class HookInputBase(TypedDict):
    session_id: str
    transcript_path: str
    cwd: str
    permission_mode: str
    hook_event_name: Literal["UserPromptSubmit"]
    prompt: str


class HookInput(HookInputBase, total=False):
    # Absent until the session has a name, then the current name -- whether set by this hook or by the user
    session_title: str


# Claude Code summarizes every session into `ai-title` transcript entries and rewrites them as the conversation drifts, so naming is a pure file read -- no model call, no added latency
def read_recent_ai_titles(transcript_path: str) -> list[str]:
    try:
        with Path(transcript_path).open("rb") as f:
            f.seek(0, os.SEEK_END)
            size = f.tell()
            f.seek(max(0, size - TRANSCRIPT_TAIL_BYTES))
            tail = f.read().decode("utf-8", errors="ignore")
    except FileNotFoundError:
        return []

    titles = []
    for line in tail.splitlines():
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            # The first line of the tail is usually a partial entry, the rest are always whole
            continue
        if entry.get("type") == "ai-title":
            titles.append(entry.get("aiTitle", ""))
    return titles


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
    session_title = data.get("session_title", "")

    ai_titles = read_recent_ai_titles(data["transcript_path"])
    if not ai_titles:
        # Claude Code writes the first `ai-title` after the first assistant turn, so the first prompt of a session has nothing to read yet
        logger.debug("session=%s no ai-title yet", session_id)
        return

    slug = slugify(ai_titles[-1])
    if not slug:
        logger.debug("session=%s ai-title=%r slugified to nothing", session_id, ai_titles[-1])
        return

    # Claude Code keeps updating `ai-title` as the conversation drifts, and the session name follows it, but only when it actually changed
    if session_title == slug:
        return

    # A name this hook set is always the slug of some recent `ai-title`, so any other name is the user's own `/rename` or `--name` and must never be overwritten
    if session_title and session_title not in {slugify(title) for title in ai_titles}:
        logger.debug("session=%s session_title=%r is user-set, backing off", session_id, session_title)
        return

    logger.debug("session=%s ai-title=%r slug=%s", session_id, ai_titles[-1], slug)
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "sessionTitle": slug}}))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logger.exception("unhandled error")
    finally:
        sys.exit(0)
