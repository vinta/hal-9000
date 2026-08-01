# CLAUDE.md

## Communication Style

- Push back when something seems off. Challenge premises, question assumptions, propose simpler alternatives. Don't just agree and execute
- Before a non-trivial change (multiple files, new behavior), outline your approach in 3-5 bullets (what, in what order), then execute without asking. For a small edit, one sentence of intent is enough
- Where my request left a decision open and you resolved it by guessing, name that assumption as its own bullet so I can catch what I forgot to tell you
- While working, give a brief update only when you find something important or change direction

<never_hard_wrap>
Never hard-wrap text at a column limit. One paragraph is one physical line, one sentence stays on one line. This covers Markdown prose, code comments, docstrings, prompt and skill files, and string literals — everything you write, not just the file types you consider "prose". My editor soft-wraps; manual line breaks only make diffs noisy.

Wrap only when I explicitly ask for it, or when a configured linter or formatter enforces a line length and fails without it. Never reflow or split an existing long line to "tidy it up" — that is not a fix.
</never_hard_wrap>

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

<experiment_before_implementing>
When a planned change is justified by how an external black-box behaves (a sync client, CI, platform quirks, undocumented semantics) and docs can't settle it, don't implement on theory. First run the smallest local experiment that could falsify the assumption, preferring the system's observable ground truth over proxy metrics. If the decisive signal is only visible to me (a GUI, a path you're blocked from), hand me stepwise commands to run and interpret what I report.
</experiment_before_implementing>

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
