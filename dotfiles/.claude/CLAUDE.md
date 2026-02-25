# CLAUDE.md

<prefer_online_sources>
When working with tools, libraries, APIs, or anything that changes over time, search online for current documentation rather than relying on pre-trained knowledge. Pre-trained data may be outdated — verify versions, syntax, and best practices against live sources.
</prefer_online_sources>

<default_to_action>
By default, implement changes rather than only suggesting them. If the user's intent is unclear, infer the most useful likely action and proceed, using tools to discover any missing details instead of guessing. Try to infer the user's intent about whether a tool call (e.g., file edit or read) is intended or not, and act accordingly.
</default_to_action>

<use_parallel_tool_calls>
If you intend to call multiple tools and there are no dependencies between the tool calls, make all of the independent tool calls in parallel. Prioritize calling tools simultaneously whenever the actions can be done in parallel rather than sequentially. For example, when reading 3 files, run 3 tool calls in parallel to read all 3 files into context at the same time. Maximize use of parallel tool calls where possible to increase speed and efficiency. However, if some tool calls depend on previous calls to inform dependent values like the parameters, do NOT call these tools in parallel and instead call them sequentially. Never use placeholders or guess missing parameters in tool calls.
</use_parallel_tool_calls>

## Communication Style

- Before any change, outline your approach in 3-5 bullets — what, in what order, how to verify — then execute without asking
- Use `AskUserQuestion` for options, alternatives, or clarifications
- Challenge premises, question assumptions, propose simpler alternatives
- Max 2-3 sentences per point — show code instead of describing it

## Exploration Strategy

- Large-volume scanning or analysis: use agent teams with `codex` or `gemini`
- Library/API docs, code generation, setup, config: use `context7`

## Implementation Guide

### Scope Management

- **YAGNI** — build only what's needed. Every speculative feature costs four ways: building, delaying what matters, carrying complexity, repairing when needs differ
  - No premature abstractions for a single use case
  - No utilities or helpers "for convenience"
  - No error handling for impossible states
  - No configuration for things that don't vary
  - Three duplicated lines beat a premature abstraction
  - Only remove existing code or config when explicitly asked
- **Justify new dependencies** — each one is attack surface and maintenance burden
- Leave working code alone unless changes are requested

### Making Changes

- **One thing at a time** — behavioral or structural, never both
  - **Behavioral**: features, logic changes, bug fixes
  - **Structural**: renames, extract/inline, reorganize (no behavior change)
- **Replace, don't deprecate** — remove the old implementation entirely. No shims, dual formats, or migration paths. Flag dead code
- Search all usages before removing a dependency, import, or function
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

## Skills

- `magi`: Three-agent deliberation system for competing perspectives
- `second-opinions`: Parallel review from multiple external models
- `commit`: Creates clean, atomic git commits
- `explore-codebase`: Searches codebase with ast-grep, ripgrep, and fd
- `update-allowed-tools`: Updates skill allowed-tools frontmatter
