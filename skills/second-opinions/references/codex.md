# Codex MCP Invocation

## Tool

Use `mcp__codex__codex` for first request. Use `mcp__codex__codex-reply` with the `threadId` from the initial response for follow-ups.

## Key Parameters

- `prompt`: The review task (required)
- `sandbox`: `read-only` (default) or `workspace-write` (when Codex needs to run tests)
- `cwd`: Working directory (defaults to current project root)

## Review Prompt

For code reviews, use this prompt base. It is from OpenAI's published code review cookbook, and Codex models received specific training on it:

```
You are acting as a reviewer for a proposed code change made by another engineer.
Focus on issues that impact correctness, performance, security, maintainability, or developer experience.
Flag only actionable issues introduced by the pull request.
When you flag an issue, provide a short, direct explanation and cite the affected file and line range.
Prioritize severe issues and avoid nit-level comments unless they block understanding of the diff.
After listing findings, produce an overall correctness verdict ("patch is correct" or "patch is incorrect") with a concise justification and a confidence score between 0 and 1.
Ensure that file citations and line numbers are exactly correct using the tools available; if they are incorrect your comments will be rejected.
```

## Prompt Assembly

Assemble the prompt in this order:

```
<review prompt from above>

<if project context requested>
Project conventions:
---
<contents of CLAUDE.md>
---

<if focus area specified>
Focus: <security | performance | error handling | custom text>

Diff to review:
---
<git diff output>
---
```

### Generating the Diff

| Scope | Command |
|-------|---------|
| Uncommitted (tracked) | `git diff HEAD` |
| Uncommitted (untracked) | `git ls-files --others --exclude-standard`, then `git diff --no-index /dev/null <file>` per file |
| Branch diff | `git diff <branch>...HEAD` |
| Specific commit | `git diff <sha>~1..<sha>` |

**Uncommitted scope must include untracked files.** `git diff HEAD` alone only shows tracked files. New unstaged files are silently excluded.

## Non-Review Tasks

For plan reviews, architecture evaluations, and other non-diff tasks:

```
Goal: <what Codex should evaluate>
Scope: <files, directories, commit range, or artifact>
Constraints: <performance, compatibility, security, style>
Checks:
- correctness
- regressions
- edge cases
- missing tests
- requirement gaps
Output format:
1) Critical issues
2) Medium risks
3) Low-priority improvements
For each issue include: severity, why it matters, file:line, and concrete fix.
```

## Example

```
mcp__codex__codex(
  prompt: "You are acting as a reviewer for a proposed code change...
[full review prompt]

Focus: security

Run `git diff main...HEAD` and review for bugs, regressions, security issues, and missing tests.
Return numbered findings with severity, confidence score, and file:line references.
End with an overall correctness verdict.",
  sandbox: "read-only"
)
```

## Interpreting Results

- Treat Codex feedback as a second opinion, not authority.
- Verify claims that seem uncertain or conflict with known constraints.
- Prefer actionable items: bugs, regressions, missing tests, unclear requirements.
