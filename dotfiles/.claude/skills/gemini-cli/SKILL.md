---
name: gemini-cli
description: Invokes Gemini CLI as a second opinion for reviewing plans, code, or architectural decisions. Leverages Gemini's large context window for complex plans or large codebases.
context: fork
user-invocable: true
model: opus
allowed-tools:
  - Glob
  - Grep
  - Read
  - Bash(gemini:*)
---

# Gemini CLI Second Opinion

Use Gemini CLI to get an independent review from a model with a 1M+ token context window.

## Invocation

Use positional prompt (`-p` is deprecated). Pipe content via stdin:

```bash
cat file1.py file2.py | gemini -o text "Review this code for bugs and design issues"
```

```bash
git diff main..HEAD | gemini -o text "Review this diff for issues"
```

For plans or other in-conversation content, write to a temp file first:

```bash
cat plans/plan.md | gemini -o text "Review this implementation plan for gaps and risks"
```

## Workflow

1. **Gather context**: Read relevant files, plans, or diffs
2. **Compose a focused prompt**: Be specific about what to review and what feedback you want
3. **Invoke Gemini**: Pipe content and use positional prompt with `-o text`
4. **Report findings**: Present Gemini's feedback to the user with your own assessment of which points are valid

## Prompt Guidelines

- State the review goal explicitly (e.g., "find logical errors", "evaluate scalability", "check for missing edge cases")
- Include constraints or requirements Gemini should check against
- Ask for structured output (numbered issues, severity levels) for actionable feedback
