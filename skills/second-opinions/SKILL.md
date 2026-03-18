---
name: second-opinions
description: Use when wanting independent perspectives from external models (Codex, Gemini) on code, plans, docs, or any task — or when the user asks for a second opinion, codex review, or gemini review
argument-hint: "[instructions]"
user-invocable: true
model: opus
allowed-tools:
  - AskUserQuestion
  - Glob
  - Grep
  - Read
  - Write
  - Bash(git diff:*)
  - Bash(git ls-files:*)
  - Bash(git symbolic-ref:*)
  - Bash(git log:*)
  - Bash(timeout:*)
  - Bash(gemini:*)
  - mcp__codex__codex
  - mcp__codex__codex-reply
---

This skill is for Claude only. Codex and Gemini CLI should not invoke it.

# Second Opinions

Delegate tasks to OpenAI Codex (MCP) and/or Google Gemini (CLI) for independent perspectives from different model families. Works for code review, plan evaluation, doc editing, codebase analysis, or any arbitrary task.

**Modes:** `both` (default), `codex`, `gemini`

## When To Use

- Code review before committing, opening a PR, or merging
- Plan or architecture review from multiple perspectives
- Documentation review or content editing
- Codebase analysis (patterns, race conditions, dead code)
- Any task benefiting from parallel exploration by external models

## Scope

- Skip for trivial tasks you can verify directly
- Skip when the user asked for your own judgment only
- Exclude secrets, credentials, and tokens from prompts

## User Instructions

Follow any user instructions below. They override the standard workflow when conflicts arise.

<user_instructions>
**$ARGUMENTS**
</user_instructions>

## Workflow

### 1. Gather Context

Infer as many parameters as possible from `$ARGUMENTS` and conversation context. Only ask about what can't be inferred. Combine remaining questions into a single `AskUserQuestion` call (max 3 questions).

**Parameters to resolve:**

| Parameter  | Inference rules                                                                                    | Ask if…                                    |
| ---------- | -------------------------------------------------------------------------------------------------- | ------------------------------------------ |
| Tool       | "codex" or "gemini" in arguments → single tool. Default: both.                                     | Ambiguous reference to one tool            |
| Task type  | "review" / "diff" → code review. "plan" / "architecture" → plan review. "doc" → doc review.        | No clear signal in arguments               |
| Focus      | "security" / "perf" / "correctness" in arguments → that focus. Default: general.                   | Never — default to general                 |
| Diff scope | Uncommitted changes if no other signal. "branch" → branch diff. SHA-like string → specific commit. | Task is code review and scope is ambiguous |

### 2. Build Material

Gather content based on task type:

| Task type         | Material to gather                                                                                      |
| ----------------- | ------------------------------------------------------------------------------------------------------- |
| Code review       | Git diff per selected scope. Auto-detect default branch. Show `--stat`. Warn if >2000 lines or empty.   |
| Plan/architecture | Extract plan from conversation context. Read any referenced files. If no plan in context, ask the user. |
| Documentation     | Read target files. Warn if >2000 lines total.                                                           |
| Custom task       | Use user instructions as the task definition. Read any referenced files or directories.                 |

Auto-detect default branch for code reviews:

```bash
git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@' || echo main
```

### 3. Construct & Dispatch

**Prompt structure** — use XML tags for unambiguous parsing. Put long content first, instructions after (per Anthropic long-context best practices):

```xml
<material>
[The diff, plan, document, codebase excerpt, or task input — long content goes first]
</material>

<context>
[Project conventions from CLAUDE.md, if it exists]
</context>

<role>
[Role appropriate to the task — e.g., independent code reviewer, architecture evaluator, technical editor]
</role>

<task>
[What to do — review, analyze, evaluate, rewrite, etc.]
</task>

<focus>
[Focus area if specified]
</focus>

<output_format>
Structure your response as:
1. Critical issues (blocking)
2. Important concerns (should address)
3. Minor suggestions (nice to have)
4. What's done well

End with a clear verdict and confidence score (0-1).
</output_format>
```

Adapt `<role>`, `<task>`, and `<output_format>` to the task type. For code reviews, use the OpenAI cookbook prompt from codex.md. For custom tasks, translate the user's intent directly.

**Project context:** If `CLAUDE.md` exists in the repo root, always include it so reviewers check against project conventions.

See [references/codex.md](references/codex.md) for Codex MCP prompt patterns and invocation.
See [references/gemini.md](references/gemini.md) for Gemini CLI invocation patterns.

**Dispatch rules:**

- When running both tools, issue `mcp__codex__codex` and `Bash(gemini ...)` calls **in a single message** for parallel execution.
- Dispatch directly without pre-checking tool availability. If a tool fails, run only the available one.

**Iterative mode** (for plans/architecture, or when explicitly requested):

1. Dispatch initial review
2. If reviewer returns significant concerns, revise the material based on feedback
3. Re-submit using `mcp__codex__codex-reply` (with `threadId`) or a fresh gemini call including revision context
4. Max 3 rounds to prevent loops

### 4. Present Results

**Both tools:** Present each model's findings, then a **Synthesis** section highlighting agreements, divergences (with your assessment of who's right), and prioritized action items.

**Single tool:** Present findings with your assessment of which items are valid vs uncertain.

## Error Handling

| Error                           | Action                                                                   |
| ------------------------------- | ------------------------------------------------------------------------ |
| `mcp__codex__codex` unavailable | Run Gemini only                                                          |
| `gemini: command not found`     | Run Codex only                                                           |
| Both unavailable                | Stop and inform the user                                                 |
| Gemini extension missing        | Install: `gemini extensions install <github-url>` (see gemini reference) |
| Empty diff / no content         | Stop: nothing to review                                                  |
| Timeout                         | Suggest narrowing scope                                                  |
| One tool fails                  | Present the other's results, note the failure                            |

## Examples

**Code review (both tools):**

```
User: /second-opinions
Agent: [asks tool, task type, focus, diff scope]
User: "Both", "Code review", "Security", "Branch diff"
Agent: [shows diff --stat, dispatches both in parallel]
Agent: [presents synthesis with agreements/divergences]
```

**Plan review (iterative, single tool):**

```
User: /second-opinions review my migration plan with codex
Agent: [asks focus] -> "Correctness & edge cases"
Agent: [extracts plan, dispatches to Codex]
Codex: [returns concerns]
Agent: [revises plan, re-submits via codex-reply]
Codex: [approves revised plan]
Agent: [presents final result]
```

**Custom task:**

```
User: /second-opinions have gemini analyze src/auth/ for race conditions
Agent: [dispatches Gemini with direct file reading]
Agent: [presents findings with assessment]
```

## Gotchas

- **Gemini hangs without `--yolo`.** It enters interactive approval mode when called from another agent. Always pass `--yolo` (or `-y`).
- **Codex defaults to implementing.** Without an explicit "this is an analysis task, do not write code" instruction, Codex will produce patches instead of findings. Always include analysis-only framing.
- **Heredocs break with diffs.** Diffs contain `$`, backticks, and special characters that break shell heredoc expansion. Always pipe with `printf` + `cat` instead.
- **Bare `git diff` misses staged changes.** Use `git diff HEAD` to capture both staged and unstaged modifications.
- **Large diffs degrade review quality.** Beyond ~2000 lines, both models start missing issues. Warn the user and suggest narrowing scope.
- **`-e security` is silently ignored.** The Gemini security extension installs as `gemini-cli-security`, not `security`.
