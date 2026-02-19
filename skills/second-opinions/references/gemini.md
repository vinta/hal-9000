# Gemini CLI Invocation

## Key Flags

| Flag            | Purpose                     | Example                   |
| :-------------- | :-------------------------- | :------------------------ |
| `-p`            | Headless mode               | `-p "your prompt"`        |
| `--yolo` / `-y` | Auto-approve all tool calls | `--yolo`                  |
| `-m`            | Model                       | `-m gemini-3-pro-preview` |
| `-e`            | Load extension              | `-e code-review`          |
| `-o`            | Output format               | `-o text`                 |

**Always use `-p` and `--yolo` when calling from another agent.** Without `-p`, Gemini launches interactive mode. Without `--yolo`, it hangs waiting for approval.

## Models

| Model                  | Use for                                    |
| :--------------------- | :----------------------------------------- |
| `gemini-3-pro-preview` | Complex reasoning, code analysis (default) |
| `gemini-3-flash`       | Speed-critical, sub-second latency         |
| `gemini-2.5-pro`       | Stable all-around performance              |
| `gemini-2.5-flash`     | Cost-efficient, high-volume processing     |

Default to `gemini-3-pro-preview`.

## Code Review Extension

For uncommitted changes, the `/code-review` extension automatically picks up the working tree diff:

```bash
gemini -p "/code-review" --yolo -e code-review -m gemini-3-pro-preview
```

For branch diffs or specific commits, pipe the diff with `printf` + `cat` (not heredocs -- diffs contain `$` and backticks that break shell expansion):

```bash
git diff main...HEAD > /tmp/review-diff.txt
{ printf '%s\n\n' 'Review this diff for code quality issues.'; cat /tmp/review-diff.txt; } \
  | gemini -p - -m gemini-3-pro-preview --yolo
```

### Adding Project Context

```bash
git diff HEAD > /tmp/review-diff.txt
{ printf 'Project conventions:\n---\n'; cat CLAUDE.md; \
  printf '\n---\n\n%s\n\n' 'Review this diff for issues.'; \
  cat /tmp/review-diff.txt; } \
  | gemini -p - -m gemini-3-pro-preview --yolo
```

## Security Review

The `/security:analyze` extension is **interactive-only**. For headless security review, use `-p` with a security-focused prompt:

```bash
git diff HEAD > /tmp/review-diff.txt
{ printf '%s\n\n' 'Analyze this diff for security vulnerabilities, including injection, auth bypass, data exposure, and input validation issues. Report each finding with severity, location, and remediation.'; \
  cat /tmp/review-diff.txt; } \
  | gemini -p - -e gemini-cli-security -m gemini-3-pro-preview --yolo
```

**Note:** The security extension installs as `gemini-cli-security` (not `security`). Always use `-e gemini-cli-security`.

## Scope-to-Diff Mapping

| Scope           | Diff command                                        |
| --------------- | --------------------------------------------------- |
| Uncommitted     | `git diff HEAD` (captures both staged and unstaged) |
| Branch diff     | `git diff <branch>...HEAD`                          |
| Specific commit | `git diff <sha>~1..<sha>`                           |

**Important:** Use `git diff HEAD` not bare `git diff`. Bare `git diff` misses staged changes.

## Direct File Reading

Gemini reads project files directly (faster than piping, avoids 8MB stdin limit):

```bash
gemini -m gemini-3-pro-preview --yolo -p "Read src/services/ and identify race conditions" -o text
```

## External Files

Gemini CLI is sandboxed to the project root. Use `--include-directories` for paths outside it:

```bash
gemini --yolo -p "Compare auth patterns" --include-directories /path/to/other-repo -o text
```

## Timeout

Set `timeout: 600000` on the Bash call (10 minutes):

```bash
timeout 600 gemini -m gemini-3-pro-preview --yolo -p "Review codebase" -o text
```

## Error Handling

| Error                                   | Action                                                                                    |
| --------------------------------------- | ----------------------------------------------------------------------------------------- |
| `gemini: command not found`             | Install: `npm i -g @google/gemini-cli`                                                    |
| `code-review` extension missing         | Install: `gemini extensions install https://github.com/gemini-cli-extensions/code-review` |
| `gemini-cli-security` extension missing | Install: `gemini extensions install https://github.com/gemini-cli-extensions/security`    |
| `-e security` silently ignored          | Use `-e gemini-cli-security` (actual installed name)                                      |
| Timeout                                 | Suggest narrowing the diff scope                                                          |
