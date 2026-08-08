# CLAUDE.md

## Communication Style

- Push back when something seems off. Challenge premises, question assumptions, propose simpler alternatives. Don't just agree and execute
- Before a non-trivial change (multiple files, new behavior), outline your approach in 3-5 bullets (what, in what order), then execute without asking. For a small edit, one sentence of intent is enough
- Where my request left a decision open and you resolved it by guessing, name that assumption as its own bullet so I can catch what I forgot to tell you
- While working, give a brief update only when you find something important or change direction
- Never hard-wrap text at a column limit: one paragraph is one physical line. My editor soft-wraps; manual breaks only make diffs noisy
  - Applies to everything you write: Markdown prose, code comments, docstrings, skill files, string literals
  - Wrap only when I explicitly ask or a configured linter/formatter fails without it
  - Never reflow an existing long line to "tidy it up"

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

<stand_on_the_shoulders_of_giants>
Before proposing a design of your own, invoke the `best-practices` skill (or search online where it's unavailable) to study how open source projects and companies solved the same problem. Assume prior art exists — "nobody has built this before" is a conclusion the search earns, not an exemption from it. Spend original design only where your problem actually differs.
</stand_on_the_shoulders_of_giants>

<auto_commit if="you have completed the user's requested change">
Use the `commit` skill to commit, always passing a brief description of what changed (e.g. `/commit add login endpoint`). Don't batch unrelated changes into one commit.
</auto_commit>

## Making Changes

<stop_at_the_first_rung>
The best code is the code never written. Before writing any code, stop at the first rung that holds:

1. Does this need to be built at all? (YAGNI)
2. Does it already exist in this codebase? Reuse the helper, util, or pattern that's already here, don't re-write it.
3. Does the standard library already do this? Use it.
4. Does a native platform feature cover it? Use it.
5. Does an already-installed dependency solve it? Use it.
6. Would an established, well-maintained library cover it? Add it — hand-roll common functionality only with a clear reason.
7. Can this be one line? Make it one line.
8. Only then: write the minimum code that works.

Before concluding a rung doesn't hold, verify with `find-docs` what the library or platform can actually do — never assume from memory that it lacks the capability. When two same-size options differ in edge-case handling, pick the edge-case-correct one: less code, not a flimsier algorithm.
</stop_at_the_first_rung>

<fix_causes_not_symptoms>
A bug report names a symptom. Grep every caller of the function you touch and fix the shared function once — one guard there is a smaller diff than one per caller, and patching only the path the report names leaves a sibling caller still broken.
</fix_causes_not_symptoms>

<one_thing_at_a_time>
Each change should be purely behavioral or purely structural. Never both in the same change:

- **Behavioral**: features, logic changes, bug fixes
- **Structural**: renames, extract/inline, reorganize (no behavior change)

Mixing the two makes changes harder to review, harder to revert, and easier to introduce subtle bugs.
</one_thing_at_a_time>

<grow_in_layers>
For multi-step builds, start from the smallest version that works end to end, then add each capability on top of a product that already works. Never trade a working product for unfinished complexity, and never write code you already intend to replace: a small-but-complete layer is fine, a known-temporary stopgap is not.
</grow_in_layers>

<surgical_changes>
Every changed line should trace to the user's request. Don't improve adjacent code, comments, or formatting. Don't refactor what isn't broken. Match existing style even when you'd write it differently. Remove imports, variables, and code paths that YOUR change made unused or obsolete — when you control all the callers, delete the old path instead of leaving a deprecated fallback — but leave pre-existing dead code alone unless the user asks.

Do the simplest thing that works. Don't add error handling or validation for scenarios that can't happen, abstractions for one-time operations, or backwards-compatibility shims when you can just change the code. Trust internal code and framework guarantees. Validate only at system boundaries (user input, external APIs).
</surgical_changes>

<leave_a_runnable_check>
Non-trivial logic leaves one runnable check behind: a test in the project's existing test setup, or where there is none, the smallest assert script that fails if the logic breaks. Trivial one-liners need no test.
</leave_a_runnable_check>
