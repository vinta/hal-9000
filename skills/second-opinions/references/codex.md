# Codex MCP Invocation

## Tool

Use `mcp__codex__codex` for first request. Use `mcp__codex__codex-reply` with the `threadId` from the initial response for follow-ups.

## Key Parameters

- `prompt`: The task description (required)
- `sandbox`: `read-only` (default) or `workspace-write` (when Codex needs to run tests/commands)
- `cwd`: Working directory (defaults to current project root)

## Prompt Templates

### Code Review

From OpenAI's code review cookbook (Codex models received specific training on this):

```
You are acting as a reviewer for a proposed code change made by another engineer.
Focus on issues that impact correctness, performance, security, maintainability, or developer experience.
Flag only actionable issues introduced by the pull request.
When you flag an issue, provide a short, direct explanation and cite the affected file and line range.
Prioritize severe issues and avoid nit-level comments unless they block understanding of the diff.
After listing findings, produce an overall correctness verdict ("patch is correct" or "patch is incorrect") with a concise justification and a confidence score between 0 and 1.
Ensure that file citations and line numbers are exactly correct using the tools available; if they are incorrect your comments will be rejected.
```

### General Task

For plan reviews, architecture evaluation, codebase analysis, doc review, or arbitrary tasks:

```xml
<role>[Role appropriate to the task — e.g., architecture evaluator, technical editor]</role>

<task>[What Codex should do — evaluate, analyze, review, rewrite]</task>

<context>[Project conventions, constraints, requirements]</context>

<material>[Content to evaluate — files, plans, docs, code excerpts]</material>

<focus>[Specific focus area if any]</focus>

<output_format>
1. Critical issues
2. Important concerns
3. Minor suggestions
4. What's done well
For each issue: severity, why it matters, file:line (if applicable), concrete fix.
End with verdict and confidence score (0-1).
</output_format>
```

## Prompt Assembly

**Put long content first, instructions after** (per Anthropic long-context best practices — queries at the end improve quality by up to 30%):

```xml
<material>
[Diff, plan, document, or other content — long data goes first]
</material>

<context>
Project conventions:
[Contents of CLAUDE.md if available]
</context>

[Review prompt or general task template from above]

<focus>[Focus area if specified]</focus>
```

### Generating Diffs

| Scope                   | Command                                                                                          |
| ----------------------- | ------------------------------------------------------------------------------------------------ |
| Uncommitted (tracked)   | `git diff HEAD`                                                                                  |
| Uncommitted (untracked) | `git ls-files --others --exclude-standard`, then `git diff --no-index /dev/null <file>` per file |
| Branch diff             | `git diff <branch>...HEAD`                                                                       |
| Specific commit         | `git diff <sha>~1..<sha>`                                                                        |

**Uncommitted scope must include untracked files.** `git diff HEAD` alone misses new unstaged files.

## Iterative Review

For tasks requiring back-and-forth (plan refinement, iterative improvement):

1. Send initial prompt via `mcp__codex__codex` — capture `threadId` from response
2. Process Codex's feedback, revise the material
3. Re-submit via `mcp__codex__codex-reply` with the same `threadId`:
   ```
   mcp__codex__codex-reply(
     threadId: "<threadId from step 1>",
     prompt: "I've revised based on your feedback. Here's what changed: [summary]. Please re-review."
   )
   ```
4. Max 3 rounds to prevent loops

## Examples

**Code review:**

```
mcp__codex__codex(
  prompt: "<material>\n[diff output]\n</material>\n\nYou are acting as a reviewer for a proposed code change...\n\nFocus: security",
  sandbox: "read-only"
)
```

**General task:**

```
mcp__codex__codex(
  prompt: "<role>You are a senior architect reviewing a migration plan.</role>\n\n<task>Evaluate this plan for correctness, risks, and missing steps.</task>\n\n<material>\n[plan content]\n</material>\n\n<output_format>Critical issues, concerns, suggestions. End with verdict.</output_format>",
  sandbox: "read-only"
)
```

## Interpreting Results

- Treat Codex feedback as a second opinion, not authority.
- Verify claims that seem uncertain or conflict with known constraints.
- Prefer actionable items: bugs, regressions, missing tests, unclear requirements.
