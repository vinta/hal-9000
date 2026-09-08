# AGENTS.md

## Communication Style

- Challenge faulty premises and propose simpler alternatives.
- Use the shortest complete response: one word or one sentence when enough; otherwise preserve required evidence, caveats, decisions, and next steps.
- When asking the user to choose among options, use `request_user_input` with concise labels and tradeoffs; use plain text if unavailable. This controls how to ask, not whether to ask: proceed when existing instructions and context already resolve the choice.

## Working Agreements

- When evidence invalidates the current approach, lead with the finding and revised approach, then continue within the authorized scope.
- After the same preventable mistake occurs twice, propose the narrowest durable instruction revision at the nearest scope.

## Change Management

- Search all references before removing or renaming code, commands, config keys, dependencies, documentation references, or files.
- Keep behavioral changes, structural refactors, and documentation/process cleanup separate unless requested together.
- Keep configuration, validation, and documentation aligned with implemented behavior.
- Build multi-step changes in working end-to-end layers.

## Code Design

- Reduce the decisions and intermediate representations callers must understand. Reuse existing signals when they express the same condition, and remove steps that only restate an already-known result.
- Remove replaced implementations; add compatibility shims only when explicitly required.
- Fail fast with errors that name the failure, relevant input, and likely fix.
- Comment only to explain why or non-obvious constraints. When moving a shared check into individual implementations, document the obligation in their shared interface.

## Delegation

- Proactively delegate independent work to subagents when doing so is likely to reduce total completion time without compromising correctness. Choose the number of agents based on useful parallel work, and verify their combined results before declaring the task complete.
- Use the `committer` agent and `commit` skill only for `git commit`: delegate the entire commit workflow with the user's stated reason and wait for verified commit hashes and final status. Handle other Git operations directly, even when they create or rewrite commits.

## Browser Tests on macOS

- Run commands that launch Playwright browsers outside the execution sandbox through the normal escalation mechanism, including headless launches and package scripts that launch browsers indirectly. Sandboxed launches can abort during macOS application registration and trigger crash dialogs.
- Before a full browser suite, confirm each requested browser launches and closes successfully in the same execution context. Reuse successful checks from the current session while the browser binaries and execution context are unchanged.
- On a browser startup permission error or application-registration abort, stop the browser run immediately and diagnose with a single launch before resuming the suite.
