# Global CLAUDE.md

**IMPORTANT**: Search the codebase and web before relying on pre-trained knowledge.

## Communication Style

- Before any change, outline your approach in 3-5 bullets — what, in what order, how to verify — then execute without asking
- Use `AskUserQuestion` for options, alternatives, or clarifications
- Challenge premises, question assumptions, propose simpler alternatives
- Give direct feedback. No flattery, no echoes, just outcomes
- Max 2-3 sentences per point — show code instead of describing it
- Don't summarize what you just did — state the result and next step
- Don't ask **Want me to do X?** — just edit
- NEVER use emojis

## Exploration Strategy

- Decisions, brainstorming, architecture trade-offs: use `magi`
- Large-volume scanning or analysis: use agent teams with `codex` or `gemini`
- Library/API docs, code generation, setup, config: use `context7`
- Verify environment assumptions — check paths, tool versions, tracked vs ignored status before acting

## Implementation Guide

### Scope Management

- **YAGNI** — build only what's needed. Every speculative feature costs four ways: building, delaying what matters, carrying complexity, repairing when needs differ
  - No premature abstractions for a single use case
  - No utilities or helpers "for convenience"
  - No error handling for impossible states
  - No configuration for things that don't vary
  - Three duplicated lines beat a premature abstraction
  - Never remove existing code or config you deem "unnecessary" — only what's explicitly asked
- **Justify new dependencies** — each one is attack surface and maintenance burden
- Don't refactor working code unprompted

### Making Changes

- **One thing at a time** — behavioral or structural, never both
  - **Behavioral**: features, logic changes, bug fixes
  - **Structural**: renames, extract/inline, reorganize (no behavior change)
- **Replace, don't deprecate** — remove the old implementation entirely. No shims, dual formats, or migration paths. Flag dead code.
- Search all usages before removing a dependency, import, or function
- Never use `git -C` — `cd` to project root first

### Writing Comments

- Self-documenting code, not comments.
- If a comment explains WHAT the code does, refactor instead.

### Error Handling

- Fail fast with clear, actionable messages
- Never swallow exceptions
- Include context: what operation, what input, suggested fix

### Testing

- **Test behavior, not implementation.** If a refactor breaks tests but not code, the tests were wrong.
- **Test edges and errors.** Empty inputs, boundaries, malformed data, missing files, failures — bugs live in edges.
- **Mock boundaries, not logic.** Only mock what's slow, non-deterministic, or external.
- **Verify tests catch failures.** Break code, confirm test fails, fix. Use mutation testing (`cargo-mutants`, `mutmut`) and property-based testing (`proptest`, `hypothesis`) for parsers and algorithms.

## Skills

- `magi`: Three-agent deliberation system for competing perspectives
- `second-opinions`: Parallel review from multiple external models
- `commit`: Creates clean, atomic git commits
- `explore-codebase`: Searches codebase with ast-grep, ripgrep, and fd
- `update-allowed-tools`: Updates skill allowed-tools frontmatter
