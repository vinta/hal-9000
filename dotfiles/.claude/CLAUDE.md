# CLAUDE.md

<prefer_online_sources>
When working with tools, libraries, APIs, or anything that changes over time, search online for current documentation rather than relying on pre-trained knowledge. Pre-trained data may be outdated — verify versions, syntax, and best practices against live sources.
</prefer_online_sources>

<default_to_action>
Implement changes rather than suggesting them. If intent is unclear, infer the most useful action and proceed.
</default_to_action>

## Communication Style

- Challenge premises, question assumptions, propose simpler alternatives
- Before any change, outline your approach in 3-5 bullets — what, in what order, how to verify — then execute without asking
- Max 2-3 sentences per point — show code instead of describing it

## Exploration Strategy

- Brainstorming or comparing approaches: use `magi-ex`
- Large-volume scanning or analysis: use agent teams with `codex` or `gemini`
- Library/API docs, code generation, setup, config: use `context7`

## Implementation Guide

### Scope Management

- **Minimal changes** — leave working code alone; only remove code or config when explicitly asked
- **Justify new dependencies** — each one is attack surface and maintenance burden

### Making Changes

- **One thing at a time** — behavioral or structural, never both
  - **Behavioral**: features, logic changes, bug fixes
  - **Structural**: renames, extract/inline, reorganize (no behavior change)
- **Replace, don't deprecate** — remove the old implementation entirely. No shims, dual formats, or migration paths. Flag dead code
- Search all usages before removing or renaming a dependency, import, or function
- Verify environment assumptions — check paths, tool versions, tracked vs ignored status before acting
- Run git commands from the project root instead of using `git -C`, which obscures working directory state

### Writing Comments

- Self-documenting code, not comments
- If a comment explains WHAT the code does, refactor instead

### Error Handling

- Fail fast with clear, actionable messages
- Propagate exceptions with context: what operation, what input, suggested fix

### Testing

- **Test behavior, not implementation.** If a refactor breaks tests but not code, the tests were wrong
- **Test edges and errors.** Empty inputs, boundaries, malformed data, missing files, failures — bugs live in edges
- **Mock boundaries, not logic.** Only mock what's slow, non-deterministic, or external
- **Verify tests catch failures.** Break code, confirm test fails, fix
  - Use mutation testing (`mutmut`, `stryker`) and property-based testing (`hypothesis`, `fast-check`) for parsers and algorithms
