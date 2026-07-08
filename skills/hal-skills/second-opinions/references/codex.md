# Codex MCP Invocation

## Tool

Use `mcp__codex__codex` for first request. Use `mcp__codex__codex-reply` with the `threadId` from the initial response for follow-ups.

## Key Parameters

- `prompt`: The task description (required)
- `sandbox`: default to `read-only`. Use `workspace-write` only when the task explicitly requires Codex to inspect or verify behavior by running commands.
- `cwd`: Working directory (defaults to current project root)

## Prompting Principles

1. **Filesystem boundary first**: always prepend a boundary instruction telling Codex to ignore `.claude/`, `.agents/`, and skill directories. Without this, Codex will waste tokens reading agent config files.
2. **Material first**: put the diff, doc, plan, or other long context before the instructions.
3. **Match Codex's default behavior**: Codex tends to implement by default, so review and analysis prompts should explicitly say when the task is analysis-only and must not modify code.
4. **Use direct structured prompts**: XML-style tags keep role, task, context, focus, and output requirements distinct.
5. **Use current external context when needed**: if the task depends on recent behavior, documentation, releases, or other changing facts, explicitly tell Codex to search online for the latest official or primary-source information.
6. **Be concise and actionable**: ask for concrete findings with severity markers ([P1] critical, [P2] important, [P3] minor), risks, and a PASS/FAIL verdict.
7. **Reuse threads for iterative reviews**: preserve context with `mcp__codex__codex-reply` rather than rebuilding the whole conversation each round.

## Prompt Templates

### Code Review

Use an explicit reviewer prompt because Codex otherwise defaults toward implementation:

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
<material>[Diff, plan, document, code excerpt, or task input]</material>

<context>[Project conventions, constraints, or repo-specific standards]</context>

<role>[Role appropriate to the task — e.g., architecture evaluator, technical editor]</role>

<task>
This is an analysis task. Do not write code unless the task explicitly asks for implementation.
[If the task depends on current external facts, search online for the latest official or primary-source information before answering.]
[What Codex should do — evaluate, analyze, review, rewrite]
</task>

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

Put long content first, then the instructions Codex should follow:

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

Prefer giving Codex file paths it can inspect directly when the MCP environment already has repo access. Paste full content only when exact wording or line-by-line review context matters.

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
2. Process Codex's feedback, revise the material, and keep the next prompt focused on what changed
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
  prompt: "<material>\n[plan content]\n</material>\n\n<role>You are a senior architect reviewing a migration plan.</role>\n\n<task>\nThis is an analysis task. Do not write code.\nIf the plan depends on current external facts, search online for the latest official references first.\nEvaluate this plan for correctness, risks, and missing steps.\n</task>\n\n<output_format>Critical issues, concerns, suggestions. End with verdict.</output_format>",
  sandbox: "read-only"
)
```

## Interpreting Results

- Treat Codex feedback as a second opinion, not authority.
- Verify claims that seem uncertain or conflict with known constraints.
- Prefer actionable items: bugs, regressions, missing tests, unclear requirements.
- If you asked for file or line citations, verify that the supplied material actually gave Codex enough information to cite accurately.
