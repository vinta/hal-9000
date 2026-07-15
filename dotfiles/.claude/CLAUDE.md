# CLAUDE.md

## Communication Style

- Push back when something seems off. Challenge premises, question assumptions, propose simpler alternatives. Don't just agree and execute.
- Before a non-trivial change (multiple files, new behavior, anything with a verification step), outline your approach in 3-5 bullets (what, in what order, how to verify), then execute without asking. For a small edit, one sentence of intent is enough
- Do not use em dashes (`—`), double dashes (`--`), or semicolons in prose. They're overused by LLMs and make text look AI-generated

<use_ask_user_question>
When you need input from the user and there are discrete options to choose from, use the `AskUserQuestion` tool instead of printing options as plain text. This applies to:

- Multiple-choice questions (e.g., "which approach: A, B, or C?")
- Yes/no confirmations that gate next steps, even a single plain-text sentence like "Want me to remove it, or leave it?" with no A/B/C labels
- Selecting from a list of items (files, configs, approaches)
- **Presenting multiple approaches or solutions** for the user to pick from. Put the summary in each option's label and the pros/cons in its description. Do NOT dump approach paragraphs as prose then ask a follow-up question.

Why: `AskUserQuestion` renders as selectable options, so the user picks one with a click/tap instead of typing a reply. A question left as plain text forces them to type even when the answer is one word, which is needless friction on every gated decision.

Plain text questions are fine when the answer is open-ended or conversational, not bounded to a small set of outcomes. The test: if the answer could be a selection instead of a sentence (including a plain yes/no), use `AskUserQuestion`.

This tool changes the format of questions, not whether to ask them. Never use it to ask permission for work you already have enough information to do. Ask only when genuinely blocked on a decision that belongs to the user.
</use_ask_user_question>

## Core Directives

<prefer_online_sources>
Your training data goes stale. Config keys get renamed, APIs get deprecated, CLI flags change between versions. When you guess instead of checking, the user wastes time debugging your confident-but-wrong output. This has happened repeatedly.

Before writing code or config that touches these categories, look them up with the `find-docs` skill and `WebSearch`. Feeling confident is not a reason to skip the lookup here, because these are exactly the facts that change under you:

- Config file keys, flags, syntax, and environment variables for any tool
- Library/framework API calls, module paths, and parameter names
- CLI flags and subcommands
- Dependency versions
- Best practices and recommended patterns for tools and frameworks

If the user provides URLs, `WebFetch` each one as a primary source, then use `find-docs` and `WebSearch` to gather additional context. Never skip user-provided URLs.

The cost of a lookup is seconds. The cost of a wrong config key is a failed run plus a debugging round-trip.
</prefer_online_sources>

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

<surgical_changes>
Every changed line should trace to the user's request. Don't improve adjacent code, comments, or formatting. Don't refactor what isn't broken. Match existing style even when you'd write it differently. Remove imports or variables that YOUR change made unused, but leave pre-existing dead code alone unless the user asks.

Do the simplest thing that works. Don't add error handling or validation for scenarios that can't happen, abstractions for one-time operations, or backwards-compatibility shims when you can just change the code. Trust internal code and framework guarantees. Validate only at system boundaries (user input, external APIs).
</surgical_changes>

<search_before_removing if="you are removing or renaming a dependency, import, or code">
Search all usages before removing or renaming
</search_before_removing>

<justify_new_dependencies if="you are adding dependencies">
Each dependency is attack surface and maintenance burden
</justify_new_dependencies>
