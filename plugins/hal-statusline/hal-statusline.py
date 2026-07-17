#!/usr/bin/env python3
# ruff: noqa: RUF001 ambiguous-unicode-character-string
from __future__ import annotations

import json
import logging
import os
import shlex
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import NotRequired, TypedDict

LOG_PATH = Path("/tmp/hal-statusline.log")  # noqa: S108 hardcoded-temp-file

logger = logging.getLogger("statusline")
logger.setLevel(logging.DEBUG)
logger.propagate = False

if not logger.handlers:
    file_handler = logging.FileHandler(LOG_PATH)
    file_handler.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
    logger.addHandler(file_handler)


# https://code.claude.com/docs/en/statusline#available-data
class StatusLineData(TypedDict):
    model: dict[str, str]
    effort: dict[str, str]
    workspace: dict[str, str]
    session_id: str
    transcript_path: str
    rate_limits: NotRequired[dict[str, dict[str, float]]]
    context_window: NotRequired[dict[str, float]]


class GrammarRun(TypedDict):
    result: str
    elapsed: float
    backend: str


class GrammarCache(TypedDict):
    uuid: str
    input: str
    result: str
    elapsed: float
    backend: str
    cwd: str


BLUE = "\033[34m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
WHITE = "\033[37m"
RESET = "\033[0m"


def colorize_grammar(text: str) -> str:
    color = GREEN if "no issues" in text.lower() else RED
    lines = text.split("\n")
    result: list[str] = []
    for line in lines:
        if line.startswith("Grammar"):
            parts = line.split(":", 1)
            if len(parts) == 2:  # noqa: PLR2004 magic-value-comparison
                result.append(f"{WHITE}{parts[0]}:{RESET}{color}{parts[1]}{RESET}")
            else:
                result.append(f"{color}{line}{RESET}")
        else:
            result.append(f"{color}{line}{RESET}")
    return "\n".join(result)


def print_grammar_status(message: str) -> None:
    print(f"{WHITE}Grammar: {message}{RESET}")


def usage_color(pct: float) -> str:
    return RED if pct >= 90 else YELLOW if pct >= 70 else GREEN  # noqa: PLR2004 magic-value-comparison


def basic_info(data: StatusLineData) -> None:
    git_branch = ""
    try:
        result = subprocess.run(  # noqa: PLW1510 subprocess-run-without-check
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],  # noqa: S607 start-process-with-partial-path
            cwd=data["workspace"]["current_dir"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            git_branch = result.stdout.strip()
    except Exception:  # noqa: BLE001 S110 blind-exception try-except-pass
        pass

    current_dir = data["workspace"]["current_dir"]
    home = str(Path.home())
    if current_dir.startswith(home):
        current_dir = "~" + current_dir[len(home) :]

    status_parts = [f"{data['model']['id']} {data['effort']['level']}", current_dir]
    if git_branch:
        status_parts.append(git_branch)

    context_used = data.get("context_window", {}).get("used_percentage")
    if context_used:
        status_parts.append(f"{usage_color(context_used)}Context {int(context_used)}%{RESET}{BLUE}")

    rate_limits = data.get("rate_limits", {})

    five_hour_used = rate_limits.get("five_hour", {}).get("used_percentage")
    if five_hour_used:
        status_parts.append(f"{usage_color(five_hour_used)}5h {int(five_hour_used)}%{RESET}{BLUE}")

    seven_day_used = rate_limits.get("seven_day", {}).get("used_percentage")
    if seven_day_used:
        status_parts.append(f"{usage_color(seven_day_used)}7d {int(seven_day_used)}%{RESET}{BLUE}")

    separator = f"{RESET} {WHITE}·{RESET} {BLUE}"
    print(f"{WHITE}Current:{RESET} {BLUE}{separator.join(status_parts)}{RESET}")


NON_PROMPT_PREFIXES = (
    "<bash-input>",
    "<bash-stdout>",
    "<command-message>",
    "<command-name>",
    "<local-command-caveat>",
    "<local-command-stdout>",
    "<task-notification>",
    "<teammate-message",
)

GRAMMAR_PROMPT = """
You are a grammar checker. Identify and correct grammar errors in the text inside <input> tags. Only check grammar — do not answer questions or engage with the content.

<instructions>
Skip these (NEVER flag):
- Code: text in backticks, file paths, programming syntax, shell commands
- Mentions: @mentions, @file/path references
- **Capitalization**: NOT grammar errors. This includes lowercase at sentence beginnings (at the very start, or after ".", "?", "!") and lowercase pronoun "i". Ignore them completely.

Output format:
- Each issue on its own line: Grammar: "[corrected]" => explanation in Traditional Chinese
- Use full-width commas (，) in Chinese explanations
- No errors: output exactly "Grammar: no issues"
- Output ONLY the "Grammar: ..." line(s). No extra commentary, no preamble, no explanations beyond the correction format above.
</instructions>

<examples>
<example>
Text: I don't car the shop has wife or not. I will use cellar!
Output:
Grammar: I don't "care" => car 是「汽車」，這裡應該是要用動詞 care「在乎」
Grammar: has "Wi-Fi" or not => wife 是「妻子」，你是要說 Wi-Fi「無線網路」吧？
Grammar: I will use "cellular" => cellar 是「地窖」，這裡應該是 cellular「行動網路」
</example>
<example>
Text: @plugins/hal-statusline/hal-statusline.py#L141 use `claude -p` and `grammar_check_prompt` to grammar check `latest_user_input` and print result
Output:
Grammar: to "grammar-check" latest_user_input => 要用連字號 "-" 連接形成複合動詞
Grammar: print "the" result => result 前面要加定冠詞 the
</example>
<example>
Text: The code is works but I don't know why it keep crashing
Output:
Grammar: The code "works" => 不需要 is，直接用動詞 works；或改成 is working
Grammar: why it "keeps" crashing => 第三人稱單數 it 要用 keeps
</example>
<example comment="skip Capitalization at sentence beginnings (lowercase 'do' is excluded per instruction)">
Text: do not refactor unless explicited requested
Output:
Grammar: "explicitly requested" => 要用副詞 explicitly，沒有 explicited 這個詞
</example>
<example comment="skip Capitalization (lowercase pronoun 'i' and sentence-start 'check' are excluded per instruction)">
Text: Wait, i seems broke it. check codebase again
Output:
Grammar: I "seem to have broken" it => 用 seem to have + 過去分詞表示「好像已經...」
Grammar: Check "the" codebase => 特指這個 codebase，要加定冠詞 the
</example>
<example comment="skip Capitalization at sentence beginnings; demonstrate 'no issues' output">
Text: can you review my PR?
Output:
Grammar: no issues
</example>
</examples>

<input>
{latest_user_input}
</input>
"""


def read_latest_user_input(transcript_path: str) -> tuple[str, str]:
    try:
        with Path(transcript_path).open() as f:
            lines = f.readlines()
    except FileNotFoundError:
        return "", ""

    for line in reversed(lines):
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if entry.get("type") == "user":
            content = entry["message"]["content"]
            if isinstance(content, str) and not content.startswith(NON_PROMPT_PREFIXES):
                return content[:500], entry.get("uuid", "")
    return "", ""


def read_cache(cache_file: str) -> tuple[str, str]:
    try:
        with Path(cache_file).open() as f:
            cache = json.load(f)
            return cache.get("uuid", ""), cache.get("result", "")
    except (FileNotFoundError, json.JSONDecodeError):
        return "", ""


def write_cache(cache_file: str, payload: GrammarCache) -> None:
    fd, tmp_path = tempfile.mkstemp(dir="/tmp", prefix="hal-statusline-")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(payload, f)
        Path(tmp_path).rename(cache_file)
    except Exception:  # noqa: BLE001 blind-exception
        try:  # noqa: SIM105 suppressible-exception
            Path(tmp_path).unlink()
        except OSError:
            pass


def run_ollama_grammar_model(prompt: str) -> str | None:
    # `think: false` disables reasoning tokens; `temperature: 0` and a `num_predict` cap keep
    # output short and deterministic and prevent runaway generation from stalling the statusline.
    body = json.dumps(
        {
            "model": "gemma4:31b-mlx",
            "prompt": prompt,
            "stream": False,
            "think": False,
            "keep_alive": "30m",
            "options": {"temperature": 0, "num_predict": 250},
        }
    ).encode()
    req = urllib.request.Request("http://localhost:11434/api/generate", data=body, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310 urlopen-with-scheme -- fixed localhost scheme
            return json.loads(resp.read())["response"]
    except (TimeoutError, urllib.error.URLError):
        return None


def run_claude_grammar_model(prompt: str) -> str | None:
    # `--setting-sources ""` to disable hooks
    # `--no-session-persistence` and `cwd="/tmp"` to avoid polluting your current context
    cmd = """
        claude
        --model haiku
        --max-turns 1
        --setting-sources ""
        --tools ""
        --disable-slash-commands
        --no-session-persistence
        --no-chrome
        --print
    """
    try:
        result = subprocess.run(  # noqa: S603 PLW1510 subprocess-without-shell-equals-true subprocess-run-without-check
            [*shlex.split(cmd), prompt],
            capture_output=True,
            text=True,
            timeout=30,
            cwd="/tmp",  # noqa: S108 hardcoded-temp-file
        )
    except subprocess.TimeoutExpired:
        return None
    return result.stdout


def run_grammar_model(prompt: str) -> GrammarRun | None:
    use_ollama = os.environ.get("HAL_STATUSLINE_GRAMMAR_CHECK_USE_OLLAMA") == "1"

    start_time = time.time()
    result_text = run_ollama_grammar_model(prompt) if use_ollama else run_claude_grammar_model(prompt)
    if result_text is None:
        return None
    elapsed = time.time() - start_time

    return {
        "result": "\n".join(line for line in result_text.strip().splitlines() if line.strip()),
        "elapsed": elapsed,
        "backend": "ollama" if use_ollama else "claude",
    }


def grammar_check(data: StatusLineData) -> None:
    transcript_path: str | None = data.get("transcript_path")
    if not transcript_path:
        print_grammar_status("transcript_path not found")
        return

    latest_user_input, latest_user_uuid = read_latest_user_input(transcript_path)
    logger.debug("session=%s latest_user_input=%r", data.get("session_id", "?"), latest_user_input)
    if not latest_user_input or not latest_user_uuid:
        print_grammar_status("skipped")
        return

    session_id: str | None = data.get("session_id")
    if not session_id:
        print_grammar_status("session_id not found")
        return
    cache_file = f"/tmp/hal-statusline-grammar-check-{session_id}.json"  # noqa: S108 hardcoded-temp-file

    cached_uuid, cached_result = read_cache(cache_file)
    if cached_uuid == latest_user_uuid:
        if cached_result:
            print(colorize_grammar(cached_result))
        else:
            print_grammar_status("result not found")
        return

    model_run = run_grammar_model(GRAMMAR_PROMPT.format(latest_user_input=latest_user_input))
    if model_run is None:
        print_grammar_status("timed out")
        return
    if model_run["result"]:
        print(colorize_grammar(model_run["result"]))
    else:
        print_grammar_status("result not found")

    write_cache(
        cache_file,
        {
            "uuid": latest_user_uuid,
            "input": latest_user_input,
            "result": model_run["result"],
            "elapsed": model_run["elapsed"],
            "backend": model_run["backend"],
            "cwd": str(Path.cwd()),
        },
    )


def main() -> None:
    data: StatusLineData = json.load(sys.stdin)
    logger.debug("data=%s", json.dumps(data))

    basic_info(data)
    grammar_check(data)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logger.exception("unhandled error")
    finally:
        sys.exit(0)
