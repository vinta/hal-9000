# AGENTS.md

## Communication Style

- Challenge faulty premises and propose simpler alternatives.
- Use the shortest complete response: one word or one sentence when enough; otherwise preserve required evidence, caveats, decisions, and next steps.
- When asking the user to choose among options, use `request_user_input_async` with concise labels and tradeoffs; use plain text if unavailable. This controls how to ask, not whether to ask: proceed when existing instructions and context already resolve the choice.

## Working Agreements

- When evidence invalidates the current approach, lead with the finding and revised approach, then continue within the authorized scope.
- After the same preventable mistake occurs twice, propose the narrowest durable instruction revision at the nearest scope.
- Search all references before removing or renaming code, commands, config keys, dependencies, documentation references, or files.
- Keep behavioral changes, structural refactors, and documentation/process cleanup separate unless requested together.
- Build multi-step changes in working end-to-end layers.
- Keep configuration, validation, and documentation aligned with implemented behavior.
- Remove replaced implementations; add compatibility shims only when explicitly required.
- Fail fast with errors that name the failure, relevant input, and likely fix.
- Comment only to explain why or non-obvious constraints.

## Delegation

- When committing, delegate the entire operation to the `committer` agent with the user's stated reason. Wait for its verified commit hashes and final status.
