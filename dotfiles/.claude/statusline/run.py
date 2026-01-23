#!/usr/bin/env python3
import json
import os
import shlex
import subprocess
import sys

CACHE_FILE = "/tmp/claude-code-statusline-grammar-check-cache.json"


def basic_info(data):
    git_branch = ""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=data["workspace"]["current_dir"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            git_branch = result.stdout.strip()
    except Exception:
        pass

    status_parts = [data["model"]["id"], data["workspace"]["current_dir"]]
    if git_branch:
        status_parts.append(git_branch)

    print(f"Current: {' · '.join(status_parts)}")


def grammar_check(data):
    # transcript looks like this:
    #
    # {
    #   "parentUuid":"0bf72657-8b71-44c6-8f0f-322130c5023d",
    #   "isSidechain":false,
    #   "userType":"external",
    #   "cwd":"/usr/local/hal-9000",
    #   "sessionId":"aef7701e-07b4-4f44-ab7a-2efd6774a7d2",
    #   "version":"2.1.7",
    #   "gitBranch":"feature/statusline-grammar-check",
    #   "slug":"zany-plotting-elephant",
    #   "type":"user",
    #   "message":{
    #     "role":"user",
    #     "content":"No, do that in the python script. "
    #   },
    #   "uuid":"2ec47d1e-3a0f-49aa-a782-c300698f7c85",
    #   "timestamp":"2026-01-15T04:08:36.995Z",
    #   "thinkingMetadata":{
    #     "level":"high",
    #     "disabled":false,
    #     "triggers":[]
    #   },
    #   "todos":[]
    # }
    #
    # {
    #   "parentUuid":"dc8f83b6-d0c2-497a-a2ed-5ebe79c7f1e4",
    #   "isSidechain":false,
    #   "userType":"external",
    #   "cwd":"/usr/local/hal-9000",
    #   "sessionId":"aef7701e-07b4-4f44-ab7a-2efd6774a7d2",
    #   "version":"2.1.7",
    #   "gitBranch":"feature/statusline-grammar-check",
    #   "slug":"zany-plotting-elephant",
    #   "type":"user",
    #   "message":{
    #     "role":"user",
    #     "content":[
    #       {
    #         "tool_use_id":"toolu_01Eab6UypSvxcyyoFLbwwaPE",
    #         "type":"tool_result",
    #         "content":"too long; didn't show"
    #       }
    #     ]
    #   },
    #   "uuid":"53003078-9aeb-40bb-b466-c4db8caf87a5",
    #   "timestamp":"2026-01-15T04:13:07.133Z",
    #   "toolUseResult":{
    #     "type":"text",
    #     "file":{
    #       "filePath":"/usr/local/hal-9000/dotfiles/.claude/statusline/run.py",
    #       "content":"too long; didn't show",
    #       "numLines":87,
    #       "startLine":1,
    #       "totalLines":87
    #     }
    #   },
    #   "sourceToolAssistantUUID":"dc8f83b6-d0c2-497a-a2ed-5ebe79c7f1e4"
    # }
    transcript_path = data.get("transcript_path")
    if not transcript_path:
        return

    try:
        with open(transcript_path, "r") as f:
            lines = f.readlines()
    except FileNotFoundError:
        return

    latest_user_input = ""
    latest_user_uuid = ""
    for line in reversed(lines):
        entry = json.loads(line)
        if entry.get("type") == "user":
            content = entry["message"]["content"]
            if (
                isinstance(content, str)
                and not content.startswith("<command-message>")
                and not content.startswith("<local-command-caveat>")
                and not content.startswith("<bash-stdout>")
            ):
                latest_user_input = content
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
Grammar 1: to "grammar-check" latest_user_input => 要用連字號連接形成複合動詞
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

## User Text to Check

=== TEXT START ===
{latest_user_input}
=== TEXT END ===
"""

    cache = {}
    try:
        with open(CACHE_FILE, "r") as f:
            cache = json.load(f)
    except FileNotFoundError:
        pass

    # Cache hit - show cached result
    if cache.get("uuid") == latest_user_uuid:
        if cache.get("result"):
            print(cache["result"])
        elif cache.get("pid"):
            # Check if background process finished
            pid = cache["pid"]
            output_file = cache.get("output_file", "")
            try:
                os.kill(pid, 0)  # Check if process still running
                print("Grammar: checking...")
            except OSError:
                # Process finished, read result
                grammar_check_result = ""
                try:
                    with open(output_file, "r") as f:
                        grammar_check_result = f.read().strip()
                    os.remove(output_file)
                except FileNotFoundError:
                    pass

                if grammar_check_result:
                    print(grammar_check_result)

                cache["result"] = grammar_check_result or "Grammar: no issues"
                cache.pop("pid", None)
                cache.pop("output_file", None)

                with open(CACHE_FILE, "w") as f:
                    json.dump(cache, f)
        return

    # Cache miss - start background check
    cmd = """
        claude
        --model haiku
        --max-turns 1
        --tools ""
        --no-chrome
        --no-session-persistence
        --disable-slash-commands
        --print
    """

    output_file = f"/tmp/claude-code-statusline-grammar-check-{latest_user_uuid}.txt"
    with open(output_file, "w") as f:
        process = subprocess.Popen(
            shlex.split(cmd) + [grammar_check_prompt],
            stdout=f,
            stderr=subprocess.DEVNULL,
        )

    with open(CACHE_FILE, "w") as f:
        json.dump({"uuid": latest_user_uuid, "input": latest_user_input, "pid": process.pid, "output_file": output_file}, f)

    print("Grammar: checking...")


# https://code.claude.com/docs/en/statusline
def main():
    # data looks like this:
    # {
    #   "session_id": "aef7701e-07b4-4f44-ab7a-2efd6774a7d2",
    #   "transcript_path": "/Users/vinta/.claude/projects/-usr-local-hal-9000/aef7701e-07b4-4f44-ab7a-2efd6774a7d2.jsonl",
    #   "cwd": "/usr/local/hal-9000",
    #   "model": {
    #     "id": "claude-opus-4-5-20251101",
    #     "display_name": "Opus 4.5"
    #   },
    #   "workspace": {
    #     "current_dir": "/usr/local/hal-9000",
    #     "project_dir": "/usr/local/hal-9000"
    #   },
    #   "version": "2.1.7",
    #   "output_style": {
    #     "name": "default"
    #   },
    #   "cost": {
    #     "total_cost_usd": 1.43933175,
    #     "total_duration_ms": 1960009,
    #     "total_api_duration_ms": 306158,
    #     "total_lines_added": 7,
    #     "total_lines_removed": 21
    #   },
    #   "context_window": {
    #     "total_input_tokens": 31202,
    #     "total_output_tokens": 15917,
    #     "context_window_size": 200000,
    #     "current_usage": {
    #       "input_tokens": 8,
    #       "output_tokens": 434,
    #       "cache_creation_input_tokens": 746,
    #       "cache_read_input_tokens": 32259
    #     },
    #     "used_percentage": 17,
    #     "remaining_percentage": 83
    #   },
    #   "exceeds_200k_tokens": false
    # }
    data = json.load(sys.stdin)

    basic_info(data)
    grammar_check(data)


if __name__ == "__main__":
    main()
