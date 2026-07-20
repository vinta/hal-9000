# CLAUDE.md

## Communication Style

- Push back when something seems off. Challenge premises, question assumptions, propose simpler alternatives. Don't just agree and execute.
- Before a non-trivial change (multiple files, new behavior, anything with a verification step), outline your approach in 3-5 bullets (what, in what order, how to verify), then execute without asking. For a small edit, one sentence of intent is enough
- Do not use em dashes (`—`), double dashes (`--`), or semicolons in prose. They're overused by LLMs and make text look AI-generated

<use_ask_user_question>
When you need input and the answer is a selection rather than a sentence (multiple-choice, yes/no confirmations that gate next steps, picking from a list, choosing between approaches), ask with the `AskUserQuestion` tool instead of plain text, so the user clicks an option instead of typing.

When presenting approaches, put the summary in each option's label and the pros/cons in its description. Plain text is fine when the answer is open-ended. This changes the format of questions, not whether to ask: never use it to ask permission for work you already have enough information to do.
</use_ask_user_question>

## Core Directives

<prefer_online_sources>
Training data goes stale: library/framework/SDK APIs, config keys, CLI flags, cloud services, platform features, syntax, and versions change, and guessing has repeatedly cost debugging round-trips.

Invoke the `find-docs` skill BEFORE writing code or config that touches any of those, and BEFORE answering questions about them. Being about to write such code is trigger enough, even when no question was asked. Confidence is not an exemption, and neither is the library being well known. Answering from training data, or fetching a remembered docs URL instead of invoking the skill, does not satisfy this rule.

If the user provides URLs, `WebFetch` each one as a primary source before searching further. Never skip user-provided URLs. For topics `find-docs` covers poorly, `WebFetch` the official docs instead of falling back to training data.
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
