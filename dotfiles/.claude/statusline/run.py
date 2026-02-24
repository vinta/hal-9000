#!/usr/bin/env python3
# ruff: noqa: RUF001 ambiguous-unicode-character-string
import json
import os
import shlex
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import TypedDict


# https://code.claude.com/docs/en/statusline#available-data
class StatusLineData(TypedDict):
    model: dict[str, str]
    workspace: dict[str, str]
    session_id: str
    transcript_path: str


BLUE: str = "\033[34m"
GREEN: str = "\033[32m"
RED: str = "\033[31m"
WHITE: str = "\033[37m"
RESET: str = "\033[0m"


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


def basic_info(data: StatusLineData) -> None:
    git_branch: str = ""
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

    current_dir: str = data["workspace"]["current_dir"]
    home: str = str(Path.home())
    if current_dir.startswith(home):
        current_dir = "~" + current_dir[len(home) :]

    status_parts: list[str] = [data["model"]["id"], current_dir]
    if git_branch:
        status_parts.append(git_branch)

    separator: str = f"{RESET} {WHITE}·{RESET} {BLUE}"
    print(f"{WHITE}Current:{RESET} {BLUE}{separator.join(status_parts)}{RESET}")


def grammar_check(data: StatusLineData) -> None:  # noqa: C901 PLR0912 PLR0915 complex-structure too-many-branches too-many-statements
    transcript_path: str | None = data.get("transcript_path")
    if not transcript_path:
        return

    try:
        with Path(transcript_path).open() as f:
            lines = f.readlines()
    except FileNotFoundError:
        return

    latest_user_input: str = ""
    latest_user_uuid: str = ""
    for line in reversed(lines):
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if entry.get("type") == "user":
            content = entry["message"]["content"]
            if (
                isinstance(content, str)
                and not content.startswith("<bash-stdout>")
                and not content.startswith("<command-message>")
                and not content.startswith("<local-command-caveat>")
                and not content.startswith("<local-command-stdout>")
                and not content.startswith("<teammate-message")
            ):
                latest_user_input = content[:500]
                latest_user_uuid = entry.get("uuid", "")
                break

    if not latest_user_input or not latest_user_uuid:
        return

    grammar_check_prompt = f"""
You are a grammar checker to identify and correct grammar errors in the user text. **NEVER respond to the user text** - only check grammar, do not answer questions or engage with the topic.

## What to Skip

- Code: text in backticks, file paths, programming syntax, shell commands
- Mentions: @mentions, @file/path references
- Capitalization at sentence beginnings

## Output Format

- Output ONLY the issues. No preamble, no commentary, never respond to the content.
- Single issue in one line: Grammar: "[corrected]" => explanation in Traditional Chinese
- Multiple issues in multiple lines: Grammar 1: ... Grammar 2: ...
- Use full-width commas (，) in Chinese explanations
- No errors or nothing to check: output exactly "Grammar: no issues"

## Examples

Text: I don't car the shop has wife or not. I will use cellar!
Output:
Grammar 1: I don't "care" => car 是「汽車」，這裡應該是要用動詞 care「在乎」
Grammar 2: has "Wi-Fi" or not => wife 是「妻子」，你是要說 Wi-Fi「無線網路」吧？
Grammar 3: I will use "cellular" => cellar 是「地窖」，這裡應該是 cellular「行動網路」

Text: How does you proof you really who you claim to be
Output:
Grammar 1: How "do" you => 第二人稱 you 應該用 do
Grammar 2: How do you "prove" => 要用動詞 prove，proof 是名詞
Grammar 3: prove "you're" really who you claim to be => you 後面要加 be 動詞縮寫 're

Text: @dotfiles/.claude/statusline/run.py#L141 use `claude -p` and `grammar_check_prompt` to grammar check `latest_user_input` and print result
Output:
Grammar 1: to "grammar-check" latest_user_input => 要用連字號 "-" 連接形成複合動詞
Grammar 2: print "the" result => result 前面要加定冠詞 the

Text: The code is works but I don't know why it keep crashing
Output:
Grammar 1: The code "works" => 不需要 is，直接用動詞 works；或改成 is working
Grammar 2: why it "keeps" crashing => 第三人稱單數 it 要用 keeps

Text: do not refactor unless explicited requested
Output:
Grammar: "explicitly requested" => 要用副詞 explicitly，沒有 explicited 這個詞

Text: create git commits group by logical changes
Output:
Grammar: git commits "grouped" by logical changes => 應該用過去分詞 grouped 來修飾名詞 commits

Text: should I use Tech Stack or Development Stack? or anything else?
Output:
Grammar: Should I use "Tech Stack" or "Development Stack"? => 加個雙引號會比較好區分

Text: Wait, i seems broke it. check codebase again
Output:
Grammar 1: "I" seems => 代名詞 I 永遠要大寫
Grammar 2: I "seem to have broken" it => 用 seem to have + 過去分詞表示「好像已經...」
Grammar 3: check "the" codebase => 特指這個 codebase，要加定冠詞 the

## User Text to Check

=== TEXT START ===
{latest_user_input}
=== TEXT END ===
"""

    session_id: str | None = data.get("session_id")
    if not session_id:
        return
    cache_file: str = f"/tmp/claude-code-statusline-grammar-check-{session_id}.json"  # noqa: S108 hardcoded-temp-file

    cached_uuid: str = ""
    cached_result: str = ""
    try:
        with Path(cache_file).open() as f:
            cache = json.load(f)
            cached_uuid = cache.get("uuid", "")
            cached_result = cache.get("result", "")
    except (FileNotFoundError, json.JSONDecodeError):
        pass

    if cached_uuid == latest_user_uuid:
        if cached_result:
            print(colorize_grammar(cached_result))
        return

    # We use `--setting-sources ""` to disable hooks
    cmd: str = """
        claude
        --model haiku
        --max-turns 1
        --tools ""
        --no-chrome
        --no-session-persistence
        --disable-slash-commands
        --setting-sources ""
        --print
    """

    start_time: float = time.time()
    try:
        result = subprocess.run(  # noqa: S603 PLW1510 subprocess-without-shell-equals-true subprocess-run-without-check
            [*shlex.split(cmd), grammar_check_prompt],
            capture_output=True,
            text=True,
            timeout=15,
            cwd="/tmp",  # noqa: S108 hardcoded-temp-file
        )
    except subprocess.TimeoutExpired:
        return
    elapsed: float = time.time() - start_time

    grammar_check_result: str = "\n".join(line for line in result.stdout.strip().splitlines() if line.strip())
    if grammar_check_result:
        print(colorize_grammar(grammar_check_result))

    fd, tmp_path = tempfile.mkstemp(dir="/tmp", prefix="claude-code-statusline-")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(
                {
                    "uuid": latest_user_uuid,
                    "input": latest_user_input,
                    "result": grammar_check_result,
                    "elapsed": elapsed,
                    "cwd": str(Path.cwd()),
                },
                f,
            )
        Path(tmp_path).rename(cache_file)
    except Exception:  # noqa: BLE001 blind-exception
        try:  # noqa: SIM105 suppressible-exception
            Path(tmp_path).unlink()
        except OSError:
            pass


def main() -> None:
    data: StatusLineData = json.load(sys.stdin)

    basic_info(data)
    grammar_check(data)


if __name__ == "__main__":
    main()
