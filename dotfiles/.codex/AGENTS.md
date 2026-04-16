# AGENTS.md

## Research

- Before writing code against a library, framework, API, or tool, check current official documentation or other primary sources. Do not rely on stale memory for syntax, defaults, or version-specific behavior.
- When relevant context lives outside the repo, prefer querying the source directly via official docs, `find-docs` skill, online search, or MCP.

## Working Style

- For multi-step work, start with a brief preamble that says what you are about to inspect or change, then execute.
- Before making changes, outline a brief 3-5 bullet plan covering approach, order, and verification, then execute.

## Scope Management

- Make the smallest change that fully solves the task.
- Justify new dependencies. Avoid increasing maintenance or attack surface without a clear payoff.
- Do not invent features, config, validation, or documentation for behavior that is not implemented.
- Keep behavioral changes and process/documentation cleanups tightly scoped unless the task explicitly asks for both.

## Change Strategy

- Keep behavioral changes and structural refactors separate when practical.
- When replacing an implementation, prefer removing the old path instead of leaving shims unless backward compatibility is explicitly required.
- Search all usages before removing or renaming imports, functions, commands, config keys, or dependencies.
- Verify environment assumptions before acting: paths, tool versions, generated vs. tracked files, and current repository state.

## Verification

- Run the smallest relevant verification for the files you changed. Prefer targeted tests first, then broader lint, typecheck, or build checks as needed.
- For multi-step work, validate at each milestone and fix failures before continuing.
- Do not leave newly introduced warnings behind unless the user explicitly accepts them.
- If you cannot run meaningful verification, say exactly what was skipped and why.

## Parallelism

- Use skills for repeatable methods, MCP for external context, and sub-agents for bounded parallel work. Automate a workflow only after it works reliably by hand.
- When reading or scanning multiple known files, batch the reads instead of working through them one by one.

## Code and Comments

- Prefer self-documenting code. Add comments only when they explain intent or non-obvious constraints.
- Use plain, factual language in commits, PRs, and summaries. Describe the diff and resulting behavior without hype.
- Never hard-wrap sentences when writing Markdown or prose text. Let paragraphs and list items stay on single logical lines unless the format requires manual line breaks.

## Error Handling

- Fail fast with clear, actionable error messages.
- Propagate enough context for debugging: what failed, on what input, and what the likely fix is.

## Feedback Loops

- If the same mistake or instruction gap appears twice, do a short retrospective and update `AGENTS.md` or the relevant task-specific reference so the fix becomes durable.
