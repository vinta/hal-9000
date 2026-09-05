# AGENTS.md

## Communication Style

- Challenge faulty premises and propose simpler alternatives.
- Use the shortest complete response: one word or one sentence when enough; otherwise preserve required evidence, caveats, decisions, and next steps.

## Working Agreements

- After the same preventable mistake occurs twice, propose the narrowest durable instruction revision at the nearest scope.
- Search all references before removing or renaming code, commands, config keys, dependencies, documentation references, or files.
- Keep behavioral changes, structural refactors, and documentation/process cleanup separate unless requested together.
- Reuse existing code, the standard library, platform features, or installed dependencies before adding code. Add dependencies only when their workflow benefit justifies their maintenance and attack surface.
- Build multi-step changes in working end-to-end layers without temporary implementations you already intend to replace.
- Keep configuration, validation, and documentation aligned with implemented behavior.
- Remove replaced implementations; add compatibility shims only when explicitly required.
- Fail fast with errors that name the failure, relevant input, and likely fix.
- Comment only to explain why or non-obvious constraints.

## Delegation

- When committing, delegate the entire operation to the `committer` agent with the user's stated reason. Wait for its verified commit hashes and final status.
