# CLAUDE.md

<prefer_online_sources>
Before writing code, configuring tools, or setting up environments, look up current documentation with `context7` or `WebSearch`. Do not rely on pre-trained knowledge for syntax, options, or defaults — it is likely outdated.
</prefer_online_sources>

<default_to_action>
Implement changes rather than suggesting them. Never present a proposed change and ask for confirmation — just make the edit. If intent is unclear, infer the most useful action and proceed.
</default_to_action>

<auto_commit>
After completing a logical unit of work, use the `commit` skill to commit changes. Don't batch unrelated changes into one commit.
</auto_commit>

## Communication Style

- Challenge premises, question assumptions, propose simpler alternatives
- Before any change, outline your approach in 3-5 bullets — what, in what order, how to verify — then execute without asking
- Max 2-3 sentences per point — show code instead of describing it

## Making Changes

- **Minimal changes** — leave working code alone; only remove code or config when explicitly asked
- **No phantom features** — don't document, validate, or reference features that aren't implemented
- **One thing at a time** — behavioral or structural, never both
  - **Behavioral**: features, logic changes, bug fixes
  - **Structural**: renames, extract/inline, reorganize (no behavior change)
- Run git commands from the project root instead of using `git -C`, which obscures working directory state

<justify_new_dependencies if="you are adding or changing dependencies">
- Justify new dependencies — each one is attack surface and maintenance burden
</justify_new_dependencies>

<search_before_removing if="you are removing or renaming a dependency, import, or function">
- Search all usages before removing or renaming
</search_before_removing>

## Zero Warnings

- Fix every warning from linters, type checkers, and tests
- If truly unfixable, add an inline ignore with a justification comment
