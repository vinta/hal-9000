# AGENTS.md

## Communication Style

- Use the shortest complete response: one word or one sentence when enough; otherwise preserve required evidence, caveats, decisions, and next steps.
- Challenge faulty premises and propose simpler alternatives instead of merely agreeing.
- After the same preventable mistake occurs twice, treat it as an instruction gap and propose the narrowest durable revision at the nearest scope instead of another exception.

## Working Agreements

- Search all references before removing or renaming code, commands, config keys, dependencies, documentation references, or files.
- Do not mix behavioral changes, structural refactors, or documentation/process cleanup unless requested together.
- Prefer fitting existing code, standard-library, platform, or installed-dependency capabilities before adding code; add a dependency only when its workflow payoff justifies its maintenance and attack surface.
- Build multi-step changes in working end-to-end layers; do not add code you already intend to replace.
- Keep configuration, validation, and documentation aligned with implemented behavior; do not claim unsupported behavior.
- When replacing an implementation, remove the old path; add compatibility shims only when explicitly required.
- Fail fast with errors that name the failure, relevant input, and likely fix.
- Comment only to explain intent or non-obvious constraints.

## Delegation

- When committing, delegate the entire commit operation to the `committer` agent, pass the user's stated reason for the changes, and wait for its verified commit hashes and final status.

## Long-Running Tools

- For empty `write_stdin` polls and `functions.wait`, use the longest yield allowed by higher-priority instructions; prefer `300000` ms when no intermediate output is needed, but shorten it to preserve the active user-update cadence.
- Keep non-empty `write_stdin` calls that send interactive input responsive instead of applying the long polling wait.
- When `functions.exec` awaits nested tools, set its outer `@exec yield_time_ms` at least `30000` ms longer than the longest nested wait so the outer cell does not yield first.
- Polling waits return early when work completes; do not wake merely to report that work is still running.
