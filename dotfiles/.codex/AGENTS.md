# AGENTS.md

## Instruction Scope

- After the same preventable mistake occurs twice, identify the underlying instruction gap and propose the narrowest durable fix; prefer revising an existing rule at the nearest relevant scope over appending another exception.

## Research Budget

- Before writing code against a library, framework, API, or tool, use `find-docs` skill, MCP, online search, or the source repo before relying on assumptions.

## Working Agreements

- Ground work in the live checkout and named sources of truth; verify only the state, paths, generated-versus-tracked status, versions, and command availability material to the task.
- Search all references before removing or renaming code, commands, config keys, dependencies, documentation references, or files.
- Keep behavioral changes, structural refactors, and documentation or process cleanup separate unless requested together.
- Add a dependency only when its workflow payoff outweighs its maintenance and attack-surface cost.
- Keep configuration, validation, and documentation aligned with implemented behavior; do not invent support for behavior that does not exist.
- When replacing an implementation, remove the old path; add compatibility shims only when explicitly required.
- Fail fast with errors that name what failed, the relevant input, and the likely fix.
- Prefer self-documenting code; comments explain intent or non-obvious constraints.
- Do not hard-wrap Markdown or prose.
