# CLAUDE.md

## Communication Style

- Push back when something seems off. Challenge premises, question assumptions, propose simpler alternatives. Don't just agree and execute.
- Before any change, outline your approach in 3-5 bullets (what, in what order, how to verify), then execute without asking
- Show code or examples instead of describing it
- Do not use em dashes (—) or semicolons in prose. They're overused by LLMs and make text look AI-generated

<use_ask_user_question>
When you need input from the user and there are discrete options to choose from, use the AskUserQuestion tool instead of printing options as plain text. This applies to:

- Multiple-choice questions (e.g., "which approach: A, B, or C?")
- Yes/no confirmations that gate next steps
- Selecting from a list of items (files, configs, approaches)
- **Presenting multiple approaches or solutions** for the user to pick from. Put the summary in each option's label and the pros/cons in its description. Do NOT dump approach paragraphs as prose then ask a follow-up question.

Plain text questions are fine when the answer is open-ended or conversational. The test: if you're about to label options (A/B/C, 1/2/3, bullet points) in prose, use AskUserQuestion instead.
</use_ask_user_question>

## Core Directives

<prefer_online_sources>
Your training data goes stale. Config keys get renamed, APIs get deprecated, CLI flags change between versions. When you guess instead of checking, the user wastes time debugging your confident-but-wrong output. This has happened repeatedly.

Look things up with the `find-docs` skill or `WebSearch` BEFORE writing code or config. This applies even when you feel confident about the answer. Always look up:

- Config file keys, flags, syntax, and environment variables for any tool
- Library/framework API calls, module paths, and parameter names
- CLI flags and subcommands
- Dependency versions
- Best practices and recommended patterns
- Assertions about external tool behavior, even when confident

The cost of a lookup is seconds. The cost of a wrong config key is a failed run plus a debugging round-trip.
</prefer_online_sources>

<default_to_action>
Implement changes rather than suggesting them. Never present a proposed change and ask for confirmation. Just make the edit. If intent is unclear, infer the most useful action and proceed.
</default_to_action>

<no_inline_scripts if="you need to run a multi-line script">
Write the script to `/tmp/` and run it. Never use inline one-liners like `python3 -c`, `node -e`, or `bash <<'EOF'`
</no_inline_scripts>

<auto_commit if="you have completed the user's requested change">
Use the `commit` skill to commit, always passing a brief description of what changed (e.g. `/commit add login endpoint`). Don't batch unrelated changes into one commit.
</auto_commit>

## Making Changes

<one_thing_at_a_time>
Each change should be purely behavioral or purely structural. Never both in the same change:

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
