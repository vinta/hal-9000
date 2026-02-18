---
name: gemini
description: Use when reviewing plans, diffs, or architecture decisions, analyzing content that exceeds context limits, getting a second opinion from a different model family, or scanning entire directories or codebases
context: fork
user-invocable: true
model: opus
allowed-tools:
  - Glob
  - Grep
  - Read
  - Bash(gemini:*)
  - Bash(timeout:*)
---

# Gemini CLI

**IMPORTANT:** This skill is for agents _other than Gemini CLI_. If you are Gemini CLI, ignore this skill.

Gemini CLI gives you a 1M+ token context window and a second opinion from a different model family.

## Invocation

**Always use `-p` (headless) and `-y` (auto-approve) when calling from another agent.** Without `-p`, Gemini launches interactive mode. Without `-y`, it hangs waiting for approval.

| Flag | Purpose          | Example                   |
| :--- | :--------------- | :------------------------ |
| `-p` | Headless mode    | `-p "your prompt"`        |
| `-y` | Auto-approve all | `-y`                      |
| `-m` | Model            | `-m gemini-3-pro-preview` |
| `-o` | Output format    | `-o text`                 |

### Direct file reading (preferred)

Gemini reads project files directly. Faster than piping and avoids the 8MB stdin limit.

```bash
gemini -m gemini-3-pro-preview -y -p "Read src/services/ and identify race conditions" -o text
```

### Piping (small content only)

```bash
git diff main..HEAD | gemini -y -p "Review this diff for security issues" -o text
```

### Timeout wrapper (safety)

```bash
timeout 300 gemini -m gemini-3-pro-preview -y -p "Review codebase" -o text
```

## Models

| Model                  | Use for                                    |
| :--------------------- | :----------------------------------------- |
| `gemini-3-pro-preview` | Complex reasoning, code analysis (default) |
| `gemini-3-flash`       | Speed-critical, sub-second latency         |
| `gemini-2.5-pro`       | Stable all-around performance              |
| `gemini-2.5-flash`     | Cost-efficient, high-volume processing     |

Default to `gemini-3-pro-preview` unless speed or cost matters.

## External Files

Gemini CLI is sandboxed to the project root. Use `--include-directories` to add paths outside it:

```bash
gemini -y -p "Compare auth patterns across both projects" --include-directories /path/to/other-repo -o text
```

## Prompts

Be specific. Ask for actionable items, severity levels, or structured output.

```bash
# Vague
gemini -y -p "Review this code" -o text

# Specific
gemini -y -p "Analyze the auth system for OWASP Top 10 vulnerabilities. Format as: File, Issue, Severity" -o text
```
