#!/usr/bin/env python3
from __future__ import annotations

import json
import logging
import os
import re
import sys
import tempfile
import time
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
TITLE_MAX_COLUMNS = 48

# A name collision only matters between sessions still showing up together in /resume, so older siblings are not worth reading
SIBLING_WINDOW_SECONDS = 7 * 24 * 3600
# A launch-time or /clear-inherited name sits on line 0 and hook-set names near the end, so reading both edges finds a sibling's current title without loading the whole transcript
# A title set only in the middle of a long transcript can be missed, which just means no rename
SIBLING_HEAD_BYTES = 8 * 1024
SIBLING_TAIL_BYTES = 64 * 1024

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


# Claude Code titles every session once, from its first real prompt, into `ai-title` transcript entries -- re-appended verbatim, never regenerated
# Reading them is a pure file read: no model call, no added latency
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


class SiblingSummary(TypedDict):
    title: str
    ai_slugs: set[str]


def summarize_sibling(path: Path) -> SiblingSummary:
    try:
        with path.open("rb") as f:
            f.seek(0, os.SEEK_END)
            size = f.tell()
            if size <= SIBLING_HEAD_BYTES + SIBLING_TAIL_BYTES:
                f.seek(0)
                text = f.read().decode("utf-8", errors="ignore")
            else:
                f.seek(0)
                head = f.read(SIBLING_HEAD_BYTES).decode("utf-8", errors="ignore")
                f.seek(size - SIBLING_TAIL_BYTES)
                tail = f.read().decode("utf-8", errors="ignore")
                # The edges cut mid-line, so the seam and both cut lines fail to parse as JSON and are skipped like any partial line
                text = head + "\n" + tail
    except OSError:
        return {"title": "", "ai_slugs": set()}

    title = ""
    ai_slugs = set()
    for line in text.splitlines():
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if entry.get("type") == "custom-title":
            title = entry.get("customTitle", "")
        elif entry.get("type") == "ai-title":
            ai_slugs.add(slugify(entry.get("aiTitle", "")))
    return {"title": title, "ai_slugs": ai_slugs}


def split_counter(title: str) -> tuple[str, int]:
    match = re.fullmatch(r"(.+?)-(\d+)", title)
    if match:
        return match.group(1), int(match.group(2))
    return title, 1


def scan_recent_siblings(self_path: Path) -> list[SiblingSummary]:
    now = time.time()
    siblings = []
    for path in self_path.parent.glob("*.jsonl"):
        if path.name == self_path.name:
            continue
        try:
            mtime = path.stat().st_mtime
        except OSError:
            continue
        if now - mtime > SIBLING_WINDOW_SECONDS:
            continue
        siblings.append(summarize_sibling(path))
    return siblings


def disambiguate_inherited_title(session_title: str, transcript_path: str) -> str | None:
    siblings = scan_recent_siblings(Path(transcript_path))

    # Only an exact duplicate of another session's current name gets touched, so a unique inherited name and any deliberate near-match stay as they are
    if all(sibling["title"] != session_title for sibling in siblings):
        return None

    # A name this hook ever set is the slug of some session's `ai-title`, so lineage through the pooled slugs separates inherited hook names from `--name` and `/rename` ones, which are never touched
    hook_slugs = set().union(*(sibling["ai_slugs"] for sibling in siblings))
    # A bare hook slug can itself end in -digits, so the whole title is tried as lineage before splitting a counter off it
    if session_title in hook_slugs:
        base, counter = session_title, 1
    else:
        base, counter = split_counter(session_title)
        if base not in hook_slugs:
            return None

    counters = [counter]
    for sibling in siblings:
        sibling_base, sibling_counter = split_counter(sibling["title"])
        if sibling_base == base:
            counters.append(sibling_counter)
    suffix = f"-{max(counters) + 1}"
    while base and display_width(base + suffix) > TITLE_MAX_COLUMNS:
        base = base[:-1].rstrip("-")
    return base + suffix


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
        # A name present at session creation -- launched with `--name` or inherited through `/clear` -- suppresses `ai-title` generation for the session's whole life
        # So a named session without ai-titles can never drift, only collide with the session its name came from
        if session_title:
            new_title = disambiguate_inherited_title(session_title, data["transcript_path"])
            if new_title:
                logger.debug("session=%s title=%r collides with a sibling session, disambiguating to %r", session_id, session_title, new_title)
                print(json.dumps({"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "sessionTitle": new_title}}))
        else:
            # Claude Code writes the first `ai-title` after the first assistant turn, so the first prompt of a session has nothing to read yet
            logger.debug("session=%s no ai-title yet", session_id)
        return

    slug = slugify(ai_titles[-1])
    if not slug:
        logger.debug("session=%s ai-title=%r slugified to nothing", session_id, ai_titles[-1])
        return

    # The session name follows the latest `ai-title`, but only when it actually changed
    if session_title == slug:
        return

    # A name this hook set is always the slug of some recent `ai-title`, possibly carrying a `-2` disambiguation counter
    # Any other name is the user's own `/rename` or `--name` and must never be overwritten
    recent_slugs = {slugify(title) for title in ai_titles}
    if session_title and session_title not in recent_slugs and split_counter(session_title)[0] not in recent_slugs:
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
