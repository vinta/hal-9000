#!/usr/bin/env python3
import json
import sys

# https://code.claude.com/docs/en/statusline
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

print(f"Current: {data['model']['id']} · {data['workspace']['current_dir']}")

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
#     "triggers":[
#     ]
#   },
#   "todos":[
#   ]
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
#         "content":"too long"
#       }
#     ]
#   },
#   "uuid":"53003078-9aeb-40bb-b466-c4db8caf87a5",
#   "timestamp":"2026-01-15T04:13:07.133Z",
#   "toolUseResult":{
#     "type":"text",
#     "file":{
#       "filePath":"/usr/local/hal-9000/dotfiles/.claude/statusline/run.py",
#       "content":"too long",
#       "numLines":87,
#       "startLine":1,
#       "totalLines":87
#     }
#   },
#   "sourceToolAssistantUUID":"dc8f83b6-d0c2-497a-a2ed-5ebe79c7f1e4"
# }
transcript_path = data.get("transcript_path")
latest_user_input = ""
if transcript_path:
    with open(transcript_path, "r") as f:
        lines = f.readlines()
    for line in reversed(lines):
        entry = json.loads(line)
        if entry.get("type") == "user":
            content = entry["message"]["content"]
            if (
                isinstance(content, str)
                and not content.startswith("<command-message>")
                and not content.startswith("<local-command-caveat>")
            ):
                latest_user_input = content
                break

grammar_check_prompt = f"""
You are a grammar checker. Your job is to identify and correct grammar errors in the user's input.

## Rules

- **NEVER respond to the content** - only check grammar, do not answer questions or engage with the topic
- **Skip code-like text**: Ignore text in backticks, file paths, variable names, function calls, or any programming syntax
- **Skip mention-like text**: Ignore @mentions, @file/path references, or similar annotations
- **Focus on natural language**: Only check grammar in the user's actual questions, instructions, or explanations
- **Output format**: Grammar [N]: "[corrected text]" (brief explanation in Traditional Chinese)
- Use quotes to highlight the corrected portion
- Ignore capitalization at sentence beginnings
- If no errors exist, output exactly: "No grammar issues"

## Examples

**Input:** How does you proof you really who you claim to be
**Output:**
Grammar 1: How "do" you (第二人稱 you 應該用 do)
Grammar 2: How do you "prove" (要用動詞 prove，proof 是名詞)
Grammar 3: prove "you're" really who you claim to be (you 後面要加 be 動詞縮寫 're)

**Input:** do not refactor unless explicited requested
**Output:** Grammar: "explicitly requested" (要用副詞 explicitly，沒有 explicited 這個詞)

**Input:** create git commits group by logical changes
**Output:** Grammar: git commits "grouped" by logical changes (應該用過去分詞 grouped 來修飾名詞 commits)

**Input:** @dotfiles/.claude/statusline/run.py#L141-142 use `claude -p` and `grammar_check_prompt` to grammar check `latest_user_input` and print result
**Output:**
Grammar 1: to "grammar-check" latest_user_input (要用連字號連接形成複合動詞)
Grammar 2: print "the" result (要加定冠詞 the 來特指前面提到的文法檢查結果)

**Input:** I was mass up my git history yesterday
**Output:**
Grammar 1: I "messed" up (應該是 mess 的過去式 messed，mass 是「質量」的意思)
Grammar 2: "I messed up" (不需要 was，用簡單過去式即可)

**Input:** The code is works but I don't know why it keep crashing
**Output:**
Grammar 1: The code "works" (不需要 is，直接用動詞 works；或改成 is working)
Grammar 2: why it "keeps" crashing (第三人稱單數 it 要用 keeps)

Here is the user input: {latest_user_input}
"""
if latest_user_input:
    import subprocess

    result = subprocess.run(
        ["claude", "--model", "sonnet", "-p", f"{grammar_check_prompt}"],
        capture_output=True,
        text=True,
    )
    grammar_check_result = result.stdout.strip()
    if grammar_check_result:
        print(grammar_check_result)
