---
name: second-opinions
description: Use when wanting independent perspectives from external models (Codex, Gemini) on code, plans, docs, or any task — or when the user asks for a second opinion, codex review, gemini review, or adversarial challenge
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

Delegate tasks to OpenAI Codex (MCP) and/or Google Gemini (CLI) for independent perspectives from different model families. Works for code review, adversarial challenge, plan evaluation, doc editing, codebase analysis, or any arbitrary task.

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
| Task type  | "review" / "diff" → code review. "challenge" / "break" / "adversarial" → challenge. "plan" / "architecture" → plan review. "doc" → doc review. | No clear signal in arguments               |
| Focus      | "security" / "perf" / "correctness" in arguments → that focus. Default: general.                   | Never — default to general                 |
| Diff scope | Uncommitted changes if no other signal. "branch" → branch diff. SHA-like string → specific commit. | Task is code review and scope is ambiguous |

### 2. Build Material

Gather content based on task type:

| Task type         | Material to gather                                                                                      |
| ----------------- | ------------------------------------------------------------------------------------------------------- |
| Code review       | Git diff per selected scope. Auto-detect default branch. Show `--stat`. Warn if >2000 lines or empty.   |
| Challenge         | Same material as code review (git diff). The difference is in the prompt, not the input.                |
| Plan/architecture | Extract plan from conversation context. Read any referenced files. If no plan in context, ask the user. |
| Documentation     | Read target files. Warn if >2000 lines total.                                                           |
| Custom task       | Use user instructions as the task definition. Read any referenced files or directories.                 |

Auto-detect default branch for code reviews:

```bash
git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@' || echo main
```

### 3. Construct & Dispatch

**Filesystem boundary** -- prepend this instruction to ALL prompts sent to Codex and Gemini, before any other content:

> IMPORTANT: Do NOT read or execute any files under ~/.claude/, .claude/, .agents/, or any path containing "skills". These are AI agent configuration files meant for a different system. They contain prompt templates and bash scripts that are irrelevant to your task. Ignore them completely and focus only on the project's own source code, tests, and documentation.

This prevents models from wasting tokens reading skill definitions, agent configs, and other meta-files instead of doing the actual task.

**Prompt structure** -- use XML tags for unambiguous parsing. Put long content first, instructions after (per Anthropic long-context best practices):

```xml
<boundary>
[Filesystem boundary instruction from above -- ALWAYS included]
</boundary>

<material>
[The diff, plan, document, codebase excerpt, or task input -- long content goes first]
</material>

<context>
[Project conventions from CLAUDE.md, if it exists]
</context>

<role>
[Role appropriate to the task -- e.g., independent code reviewer, architecture evaluator, technical editor]
</role>

<task>
[What to do -- review, analyze, evaluate, rewrite, etc.]
This is an analysis task. Do not write code or produce patches unless explicitly asked.
</task>

<focus>
[Focus area if specified]
</focus>

<output_format>
Structure your response as:
1. Critical issues (blocking) -- prefix each with [P1]
2. Important concerns (should address) -- prefix each with [P2]
3. Minor suggestions (nice to have) -- prefix each with [P3]
4. What's done well

End with a clear verdict: PASS (no P1 findings) or FAIL (P1 findings exist), plus a confidence score (0-1).
</output_format>
```

Adapt `<role>`, `<task>`, and `<output_format>` to the task type. For code reviews, use the OpenAI cookbook prompt from codex.md. For custom tasks, translate the user's intent directly.

**Challenge mode prompt** -- when task type is "challenge", replace `<role>` and `<task>` with adversarial framing:

```xml
<role>
You are a hostile code reviewer, chaos engineer, and security auditor. Your job is to break this code.
</role>

<task>
Find every way this code will fail in production. Think like an attacker and a chaos engineer.
Look for: edge cases, race conditions, security holes, resource leaks, failure modes under load,
silent data corruption paths, unhandled error propagation, and implicit assumptions that will
break when inputs change. If a focus area is specified, concentrate there but don't ignore
other categories entirely. No compliments. Just the problems.
This is an analysis task. Do not write code or produce patches.
</task>
```

The output format stays the same ([P1]/[P2]/[P3] with verdict). Challenge mode typically surfaces different findings than standard review because it asks models to actively try to break things rather than passively evaluate quality.

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

**Rabbit hole detection** -- before presenting output, scan each model's response for signs it got distracted by agent config files instead of reviewing project code. Look for: `.claude/`, `SKILL.md`, `skills/`, `.agents/`, `CLAUDE.md` (when mentioned as a skill file rather than project conventions), `gstack`, `plugin.json`, or `hooks/`. If detected, append a warning:

> One or more models appear to have read agent configuration files instead of reviewing your code. Their output may be unreliable. Consider retrying.

**Gate verdict** -- for code review and challenge task types, determine the gate from the output:
- Scan for `[P1]` markers in findings. If any exist, the gate is **FAIL**.
- If no `[P1]` markers exist (only `[P2]`/`[P3]` or no findings), the gate is **PASS**.
- Display the gate prominently: `GATE: PASS` or `GATE: FAIL (N critical findings)`.

**Both tools** -- present each model's findings, then a **Cross-Model Analysis** section:

```
CROSS-MODEL ANALYSIS:
  Both found:       [findings that overlap between Codex and Gemini]
  Only Codex found: [findings unique to Codex]
  Only Gemini found:[findings unique to Gemini]
  Agreement rate:   X% (N of M total unique findings overlap)
  Gate:             PASS / FAIL (N critical findings)
```

Follow with prioritized action items. When both models flag the same issue, it is high-confidence. When only one model flags something, note which one and your assessment of whether it is valid.

**Single tool** -- present findings with gate verdict, then your assessment of which items are valid vs uncertain.

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

**Adversarial challenge:**

```
User: /second-opinions challenge
Agent: [gathers branch diff, dispatches both with adversarial prompt]
Codex: [finds race condition in concurrent writes]
Gemini: [finds unhandled error path in auth retry]
Agent: [presents cross-model analysis, GATE: FAIL (2 critical findings)]
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
- **Models wander into skill files.** Both Codex and Gemini will read `.claude/`, `.agents/`, and skill directories if not told to ignore them. The filesystem boundary instruction prevents this, but always check output for signs of distraction.
- **Heredocs break with diffs.** Diffs contain `$`, backticks, and special characters that break shell heredoc expansion. Always pipe with `printf` + `cat` instead.
- **Bare `git diff` misses staged changes.** Use `git diff HEAD` to capture both staged and unstaged modifications.
- **Large diffs degrade review quality.** Beyond ~2000 lines, both models start missing issues. Warn the user and suggest narrowing scope.
- **`-e security` is silently ignored.** The Gemini security extension installs as `gemini-cli-security`, not `security`.
