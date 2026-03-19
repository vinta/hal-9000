# CLAUDE.md

<prefer_online_sources>
Use `context7` or `WebSearch` to verify before relying on pre-trained knowledge. Look things up when:
- Writing code that uses libraries, APIs, or CLI tools
- Configuring tools, services, or environment variables
- Checking if a stdlib replacement exists for a third-party package
- Pinning dependency versions — always check the latest
- Unsure about exact syntax, flags, or config format
- Making confident assertions about external tool behavior
</prefer_online_sources>

<default_to_action>
Implement changes rather than suggesting them. Never present a proposed change and ask for confirmation — just make the edit. If intent is unclear, infer the most useful action and proceed.
</default_to_action>

<no_inline_scripts if="you need to run a multi-line Python or shell script">
- Write the script to `/tmp/` and run it — never use `python3 -c` or `bash <<'EOF'` inline
</no_inline_scripts>

<auto_commit if="you have completed the user's requested change">
Use the `commit` skill to commit. Don't batch unrelated changes into one commit.
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

<git_from_project_root if="you are running git commands">
- Run git commands from the project root instead of using `git -C`, which obscures working directory state
</git_from_project_root>

<justify_new_dependencies if="you are adding or changing dependencies">
- Each dependency is attack surface and maintenance burden
</justify_new_dependencies>

<search_before_removing if="you are removing or renaming a dependency, import, or function">
- Search all usages before removing or renaming
</search_before_removing>

## Zero Warnings

- Fix every warning from linters, type checkers, and tests
- If truly unfixable, add an inline ignore with a justification comment
