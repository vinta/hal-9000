# AGENTS.md

## Working Style

- Challenge assumptions, question weak premises, and propose simpler alternatives when they are better.
- Before making changes, outline a brief 3-5 bullet plan covering approach, order, and verification, then execute.
- Prefer doing the work over describing it. If intent is somewhat ambiguous, make the most useful reasonable assumption, state it, and proceed.

## Research

- Before writing code against a library, framework, API, or tool, check current official documentation or other primary sources. Do not rely on stale memory for syntax, defaults, or version-specific behavior.

## Scope Management

- Make the smallest change that fully solves the task.
- Justify new dependencies. Avoid increasing maintenance or attack surface without a clear payoff.
- Do not invent features, config, validation, or documentation for behavior that is not implemented.

## Change Strategy

- Keep behavioral changes and structural refactors separate when practical.
- When replacing an implementation, prefer removing the old path instead of leaving shims unless backward compatibility is explicitly required.
- Search all usages before removing or renaming imports, functions, commands, config keys, or dependencies.
- Verify environment assumptions before acting: paths, tool versions, generated vs. tracked files, and current repository state.

## Verification

- Run the smallest relevant verification for the files you changed. Prefer targeted tests first, then broader lint, typecheck, or build checks as needed.
- For multi-step work, validate at each milestone and fix failures before continuing.
- Do not leave newly introduced warnings behind unless the user explicitly accepts them.

## Long-Horizon Tasks

- For work that spans multiple loops, tools, or sessions, create durable project memory in markdown files that Codex can revisit. Use a repository-appropriate location; a good default stack is:
  - `Prompt.md`: goals, non-goals, constraints, deliverables, and "done when"
  - `Plan.md`: milestones, acceptance criteria, validation commands, stop-and-fix rules, and architecture notes
  - `Implement.md`: the execution runbook that treats the plan as the source of truth and keeps diffs scoped
  - `Documentation.md`: current status, decisions, run/demo steps, and known issues
- Keep these files concise and current. Skip them for short, one-shot tasks.
- Operate in a tight loop: plan, edit code, run tools, observe results, repair failures, update docs/status, repeat.

## Parallelism

- Use skills or sub-agents when they materially improve throughput, especially for bounded parallel work or large scans, but keep ownership clear and avoid duplicating work.

## Code and Comments

- Prefer self-documenting code. Add comments only when they explain intent or non-obvious constraints.
- Use plain, factual language in commits, PRs, and summaries. Describe the diff and resulting behavior without hype.

## Error Handling

- Fail fast with clear, actionable error messages.
- Propagate enough context for debugging: what failed, on what input, and what the likely fix is.
