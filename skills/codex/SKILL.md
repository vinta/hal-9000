---
name: codex
description: Use when reviewing plans, diffs, or architecture decisions, doing a fresh pass on code for bugs or missing requirements, or getting a second opinion from a different model family
context: fork
user-invocable: true
model: opus
allowed-tools:
  - Glob
  - Grep
  - Read
  - Bash(git diff:*)
  - mcp__codex__codex
  - mcp__codex__codex-reply
---

If you are Codex or `mcp__codex__codex` is unavailable, stop and do not use this skill.

# Overview

Use OpenAI Codex as an independent reviewer through the Codex MCP server.

## When To Use

- Plan review before implementation.
- Diff review before merge.
- Architecture review before committing to a direction.
- Final sanity check for bugs, regressions, edge cases, and missing tests.

## When Not To Use

- Do not use for trivial tasks that you can verify directly.
- Do not use when the user asked for your own judgment only.
- Do not send secrets, credentials, customer data, or tokens in prompts.

## Preflight

1. Confirm you are not Codex.
2. Confirm `mcp__codex__codex` is available.
3. Collect only the minimum context Codex needs (file paths, diff range, constraints, acceptance criteria).
4. Default to `sandbox: "read-only"` unless write access is required to run tests.

## Invocation

Use `mcp__codex__codex` for first request and `mcp__codex__codex-reply` for follow-ups on the same thread.

```
mcp__codex__codex(
  prompt: "Review bin/hal for bugs. Return numbered findings with severity and file:line references.",
  sandbox: "read-only",
  cwd: "/path/to/project"
)
```

For multi-turn follow-ups, use `mcp__codex__codex-reply` with the `threadId` from the initial response.

## Prompt Template

Use this structure to keep outputs actionable:

```
Goal: <what Codex should evaluate>
Scope: <files, directories, commit range, or artifact>
Constraints: <performance, compatibility, security, style, deadlines>
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

## Key Parameters

- `prompt`: The review task (required)
- `sandbox`: `read-only` (default for reviews) or `workspace-write` (when Codex needs to run tests)
- `cwd`: Working directory for Codex (defaults to current project root)

## Workflow

1. Gather context: identify the exact plan, diff, files, or design to review.
2. Define success criteria: specify correctness and acceptance constraints.
3. Write a focused prompt with explicit output format.
4. Invoke Codex with least-privilege sandbox.
5. Validate findings: sanity-check claims that affect safety, data integrity, or public APIs.
6. Report back with two layers:
   - Codex findings (structured, with severity and references)
   - Your assessment (which findings are valid, uncertain, or non-actionable)

## Safety and Scope

- Default to `sandbox: "read-only"` for review-only tasks.
- Use `workspace-write` only when Codex needs to run tests or inspect generated artifacts.
- Never pass secrets, tokens, or private customer data in prompts.
- Keep prompts scoped to task-relevant material to reduce noise and token cost.

## Prompt Guidelines

- State the review goal explicitly (e.g., "find logical errors", "evaluate scalability", "check for missing edge cases")
- Include constraints or requirements Codex should check against
- Ask for structured output (numbered issues, severity levels) for actionable feedback
- Ask for concrete references (file:line) when reviewing code or diffs
- Tell Codex which files or directories to read, or which git range to diff.

## Interpreting Results

- Treat Codex feedback as a second opinion, not authority.
- Verify any claims that seem uncertain or conflict with known constraints.
- Prefer actionable items: bugs, regressions, missing tests, and unclear requirements.

## Prompt Examples

### Plan Review

```
mcp__codex__codex(
  prompt: "Read plan.md and review for risks, missing steps, and unclear assumptions.
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
