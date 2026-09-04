# CLAUDE.md

## Communication Style

- Push back when something seems off. Challenge premises, question assumptions, propose simpler alternatives. Don't just agree and execute
- Before a non-trivial change (multiple files, new behavior), outline your approach in 3-5 bullets (what, in what order), then execute without asking. For a small edit, one sentence of intent is enough
- Never hard-wrap text at a column limit: one paragraph is one physical line. Wrap only when the user explicitly asks or a configured linter/formatter fails without it

### Surface Assumptions

Where the user's request left a decision open and you resolved it by guessing, name that assumption as its own bullet so the user can catch what they forgot to tell you.

When the user asks for advice or a recommendation, first surface the assumptions their question takes for granted and the missing information that would change your answer (and how), so they can catch the framing they got wrong.

### Use AskUserQuestion

When you ask the user anything whose answer is a selection rather than a sentence (multiple-choice, yes/no questions whether they gate next steps or offer optional follow-up work, picking from a list, choosing between approaches), ask with the `AskUserQuestion` tool instead of plain text, so the user clicks an option instead of typing. This holds inside skills: a skill that prescribes its own question format decides what you ask, not how; keep its content and still ask through the tool.

When presenting approaches, put the summary in each option's label and the pros/cons in its description. Plain text is fine when the answer is open-ended. This changes the format of questions, not whether to ask: never use it to ask permission for work you already have enough information to do.

## Workflow

- Before proposing a design of your own, invoke the `best-practices` skill to study prior art. Assume prior art exists; spend original design only where your problem actually differs
- When a finding invalidates the approach you're executing (contradicts it, or makes it unnecessary), stop and lead with it: what it kills, what the plan is now. Mentioning it in passing while continuing does not count
- When you have completed the user's requested change, use the `commit` skill to commit, passing why the changes were made

### Prefer Online Sources

Training data goes stale: library/framework/SDK APIs, config keys, CLI flags, cloud services, platform features, syntax, and versions change, and guessing has repeatedly cost debugging round-trips.

Invoke the `find-docs` skill BEFORE writing code or config that touches any of those, and BEFORE answering questions about them. Being about to write such code is trigger enough, even when no question was asked. Confidence is not an exemption, and neither is the library being well known. Answering from training data, or fetching a remembered docs URL instead of invoking the skill, does not satisfy this rule.

If the user provides URLs, `WebFetch` each one as a primary source before searching further. Never skip user-provided URLs. For topics `find-docs` covers poorly, `WebFetch` the official docs instead of falling back to training data.

## Coding Discipline

- Before writing code, prefer in order: an existing helper in this codebase > the standard library > a native platform feature > an already-installed dependency > an established, well-maintained library (add it rather than hand-roll) > only then the minimum new code. Before concluding a step doesn't apply, verify with `find-docs` what the library or platform can actually do — never assume from memory that it lacks the capability.
- Every changed line should trace to the user's request. Don't improve adjacent code, comments, or formatting, fix a pre-existing bug, or refactor what isn't broken unless the requested behavior cannot work without it: report those as follow-ups in your summary instead. Remove imports, variables, and code paths that YOUR change made unused or obsolete (that cleanup belongs to the same change) — when you control all the callers, delete the old path instead of leaving a deprecated fallback — but leave pre-existing dead code alone unless the user asks.

### Surgical Changes

Do the simplest thing that works.

- Don't add error handling or validation for scenarios that can't happen, abstractions for one-time operations, or backwards-compatibility shims when you can just change the code.
- Trust internal code and framework guarantees. Validate only at system boundaries (user input, external APIs).
- For inputs that can happen, simplicity is fewer lines, never a flimsier algorithm: when two same-size options differ in edge-case handling, pick the edge-case-correct one.

### One Thing at a Time

Each change should be purely behavioral or purely structural. Never both in the same change:

- **Behavioral**: features, logic changes, bug fixes
- **Structural**: renames, extract/inline, reorganize (no behavior change)

Mixing the two makes changes harder to review, harder to revert, and easier to introduce subtle bugs.

## Code Conventions

### Naming

Check a proposed name against every bullet here before presenting it. Existing code is precedent only where it already follows these bullets.

- **One value has one name everywhere it appears**. When two records carry the same value under two names, rename to the one that already matches the domain vocabulary
- An identifier mirrors its domain type name (`lateFixes: LateFix[]`, `ambiguousShape: AmbiguousShape`), never a shortened synonym. This covers parameters, loop variables, and destructured locals. A generic platform type (`Node`, `string`) carries nothing, so that identifier names its role instead: `contextNode`, not `node`
- Name a field or local by its state (`unspaced`, `settled`), never by relative position (`before`, `after`) or by mechanism (`pending`, `unflushed`). One thing at two moments is an `extends` pair: the later type adds only the fields the later moment makes available
- Prefer the concrete compound that names the visible thing and matches existing code or setting names over an abstract, mechanism, or transport noun: `AmbiguousShape`, not `Ambiguity`; `Candidate`, not `ClassifyRequest`. Only the envelope carries `Message` or `Request`
- A callback is named by what changed, never by the container the event came in: `onTextNodesSettled(settledTextNodes)`, not `onBatchSettled`
- A per-item helper beside its batch function is `verbOneNoun` (`classifyCandidates` / `classifyOneCandidate`, `registerContentScripts` / `registerOneContentScript`): the bare singular differs by one trailing `s` and reads alike in a diff. Keep the batch name as is when a message or API shares it

### Comments

- A comment states the constraint or the why in one or two plain lines.
- Code comments are the user's notes to their future self, so the user writes the final wording. Draft one version, then review the user's version for a claim the code contradicts, a grammar slip, or a glossary synonym. Do not rephrase their wording
