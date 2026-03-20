# CLAUDE.md

## Communication Style

- Push back when something seems off. Challenge premises, question assumptions, propose simpler alternatives. Don't just agree and execute.
- Before any change, outline your approach in 3-5 bullets (what, in what order, how to verify), then execute without asking
- Show code or examples instead of describing it
- Do not use em dashes (—) or semicolons in prose. They're overused by LLMs and make text look AI-generated

## Core Directives

<prefer_online_sources>
Use the `find-docs` skill or `WebSearch` to verify before relying on pre-trained knowledge. Look things up when:
- Writing code that uses libraries, APIs, or CLI tools
- Configuring tools, services, or environment variables
- Checking if a stdlib replacement exists for a third-party package
- Pinning dependency versions, always check the latest
- Unsure about exact syntax, flags, or config format
- Making confident assertions about external tool behavior
</prefer_online_sources>

<default_to_action>
Implement changes rather than suggesting them. Never present a proposed change and ask for confirmation. Just make the edit. If intent is unclear, infer the most useful action and proceed.
</default_to_action>

<no_inline_scripts if="you need to run a multi-line script">
Write the script to `/tmp/` and run it. Never use inline one-liners like `python3 -c`, `node -e`, or `bash <<'EOF'`
</no_inline_scripts>

<auto_commit if="you have completed the user's requested change">
Use the `commit` skill to commit. Don't batch unrelated changes into one commit.
</auto_commit>

## Making Changes

<one_thing_at_a_time>
Each change should be purely behavioral or purely structural. Never both in the same change.
- **Behavioral**: features, logic changes, bug fixes
- **Structural**: renames, extract/inline, reorganize (no behavior change)
Mixing the two makes changes harder to review, harder to revert, and easier to introduce subtle bugs.
</one_thing_at_a_time>

<justify_new_dependencies if="you are adding or changing dependencies">
Each dependency is attack surface and maintenance burden
</justify_new_dependencies>

<search_before_removing if="you are removing or renaming a dependency, import, or function">
Search all usages before removing or renaming
</search_before_removing>

<git_from_project_root if="you are running git commands">
Run git commands from the project root instead of using `git -C`, which obscures working directory state
</git_from_project_root>
