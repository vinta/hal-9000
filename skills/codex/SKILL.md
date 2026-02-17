---
name: codex
description: Use when reviewing plans, diffs, or architecture decisions before acting, doing a fresh pass on code for bugs or missing requirements, sanity-checking work before sharing with stakeholders, or wanting an independent perspective from a different model family
context: fork
user-invocable: true
model: opus
allowed-tools:
  - Glob
  - Grep
  - Read
  - Bash(git diff:*)
  - Bash(git log:*)
  - Bash(cat:*)
  - mcp__codex__codex
  - mcp__codex__codex-reply
---

# Codex Second Opinion

Use Codex to get an independent review from OpenAI's reasoning models via the Codex MCP server.

Use when:

- You want a second opinion on a plan, diff, or architecture decision.
- You need a fresh pass for bugs, edge cases, or missing requirements.
- You want a quick sanity check before sharing with users or stakeholders.

## Invocation

Use the `mcp__codex__codex` tool. Codex runs in its own sandbox and can read files and run commands independently.

```
mcp__codex__codex(
  prompt: "Review bin/hal for bugs. Return numbered findings with severity and file:line references.",
  sandbox: "read-only",
  cwd: "/path/to/project"
)
```

For multi-turn follow-ups, use `mcp__codex__codex-reply` with the `threadId` from the initial response.

## Key Parameters

- `prompt`: The review task (required)
- `sandbox`: `read-only` (default for reviews) or `workspace-write` (when Codex needs to run tests)
- `cwd`: Working directory for Codex (defaults to current project root)

## Workflow

1. **Gather context**: Identify the files, plans, or diffs Codex needs to review
2. **Define the objective**: What does "good" look like? Include constraints and acceptance criteria
3. **Compose a focused prompt**: Be specific about what to review and what feedback you want. Include file paths, commit ranges, or pipe content directly in the prompt
4. **Invoke Codex**: Call `mcp__codex__codex` with appropriate sandbox policy
5. **Report findings**: Present Codex's feedback to the user with your own assessment of which points are valid

## Safety and Scope

- Default to `sandbox: "read-only"` for review-only tasks.
- Use `workspace-write` only when Codex needs to run tests or inspect generated artifacts.
- Never pass secrets, tokens, or private customer data in prompts.

## Prompt Guidelines

- State the review goal explicitly (e.g., "find logical errors", "evaluate scalability", "check for missing edge cases")
- Include constraints or requirements Codex should check against
- Ask for structured output (numbered issues, severity levels) for actionable feedback
- Ask for concrete references (file:line) when reviewing code or diffs
- Tell Codex which files or directories to read, or which git range to diff

## Interpreting Results

- Treat Codex feedback as a second opinion, not authority.
- Verify any claims that seem uncertain or conflict with known constraints.
- Prefer actionable items: bugs, regressions, missing tests, and unclear requirements.

## Prompt Examples

### Plan Review

```
mcp__codex__codex(
  prompt: "Read plan.md and review it for risks, missing steps, and unclear assumptions.
Return:
1) Critical issues
2) Medium risks
3) Suggested improvements
4) Questions to clarify",
  sandbox: "read-only"
)
```

### Diff Review

```
mcp__codex__codex(
  prompt: "Run `git diff main..HEAD` and review for bugs, regressions, security issues, and missing tests.
Return numbered findings with severity and file:line references.",
  sandbox: "read-only"
)
```

### Architecture Review

```
mcp__codex__codex(
  prompt: "Read design.md and evaluate the architecture for scalability, fault tolerance, and operational risk.
Call out assumptions and suggest alternatives where applicable.",
  sandbox: "read-only"
)
```

### Large Codebase Review

```
mcp__codex__codex(
  prompt: "Review the codebase with focus on correctness, edge cases, and missing tests.
Read these folders: src/, scripts/, and packages/.
Return numbered findings with severity and file:line references.",
  sandbox: "read-only"
)
```
