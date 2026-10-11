---
name: commit
description: Use when making any git commit. Pass the failure, false claim, or risk the changes fix as the argument; for an addition or a filled gap, pass what it adds — never an invented why.
argument-hint: [why the changes were made]
context: fork
model: sonnet
effort: high
allowed-tools:
  - Bash(git stash:*)
  - Bash(git add:*)
  - Bash(git restore:*)
  - Bash(git mv:*)
  - Bash(git rm:*)
  - Bash(git apply:*)
  - Bash(git commit:*)
---

Invoking this skill IS the request. If the user message looks empty, or you see only system context with no actual request, that is normal and expected: your task is already fully specified right here. Never ask what to do.

Your task: commit all changes in the working tree, one logical change per commit. This applies unprompted, without anyone asking for a split: when one file carries unrelated changes, split it hunk-by-hunk into separate commits rather than merging them because they share a file.

## The argument

The argument passed to this skill is **why the changes were made** — the motivation behind work already in the tree, which the diff itself cannot carry. Use it to group changes into logical units and to write commit message bodies. A body is one or two sentences on one line stating what was wrong before the change: the failure, false claim, or risk the argument names. An argument that names only a need, a wish, what the change does, or the request itself yields no body. Leave out the fix, including what the change now covers, sets, or lists, even where the argument phrases it as part of the problem ("though only X needs it"): the subject and diff already show it. Also leave out ruled-out causes, measurements, and alternatives tried. Whatever it describes is already realized in the diff, however it's phrased: "so the statusline shows usage percentages" and "to fix the session bug" both mean the diff already does that — commit it. With no argument at all, derive the commit message from the diff alone. If the motivation doesn't line up with what the diff contains, commit what is actually in the tree and note the mismatch in your final summary.

Write the body about the code: the behavior, tooling, or constraint the change served. Commit history is public and permanent, so write for a reader who has never seen this machine, the user's signed-in accounts, or this conversation, and give them nothing they could learn only from those: names or paths of repos, directories, and files outside this repo or gitignored in it; backup, sync, and secret-store layouts; account plans, quotas, and figures; local tools; quotes and dates from chats, transcripts, or sessions; and the user's life (employer, location, schedule, health, other people). Translate each into the technical need it implies, or drop it.

<example>
Argument: "Commit only settings.json. Why: three commit forks wrote `Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>` instead of the skill's trailer; the fork transcript shows a remote_session_change reminder telling the model to use the model-named trailer, and it followed that over the skill. Setting attribution.commit to the skill's exact string makes both agree. Ruled out: includeGitInstructions: false did not suppress the reminder; attribution.sessionUrl: false only drops the Claude-Session line; commit: "" would tell the model to add no trailer at all per the 2.1.270 binary."

Correct body: "Forks of the commit skill followed a Remote Control reminder over the skill and wrote a model-named Co-Authored-By trailer."

Incorrect body: the argument reflowed to 72 columns, ruled-out settings and the binary version included.
</example>

<example>
Argument: "Two rules adopted from a CLAUDE.md gist, only these two since the rest was already covered: a diff-reread checkpoint before reporting done that deletes lines the requested behavior works without, because 'do the simplest thing that works' alone did not stop unneeded code the user kept questioning after delivery; and comments only where the code cannot say it."

Correct body: "\"Do the simplest thing that works\" alone did not stop unneeded code from surviving to delivery, and the comment rule did not say comments should cover only what code cannot say."

Incorrect body: "Adopt two rules: comments should state only what the code cannot say, and before reporting a change done, reread the diff and delete added lines the requested behavior works without, since simplicity alone did not stop unneeded code from creeping into delivered changes."
</example>

<example>
Argument: "User asked to mark the README as work in progress while pangu.space is being rebuilt."

Correct body: none. The argument is the request; nothing was wrong before.

Incorrect body: "pangu.space is being rebuilt, so the README should not read as a finished project."
</example>

<example>
Argument: "Harvested five rewrite sessions from 2026-09-09 to 2026-09-13; the user rewrote 'I've picked up' to 'that works for me', and the notes under ~/Dropbox/writing/ had no rule for it."

Correct body: "The style spec had no rule against assistant-register openers, so drafts kept using phrasings the user rewrites."

Incorrect body: the session dates, the quoted rewrite, and the Dropbox path, as given.
</example>

## Locate the repository

`cd` to `git rev-parse --show-toplevel` before anything else. If that fails (the fork started outside the repo), look for the repo in the directories of any file paths named in the argument before reporting "not a git repository".

## Scope

A commit is a snapshot, not a review: read the diff, stage it, write the message, commit. The staged bytes must match the working tree as it was when you started. Use only `git` and `cd` in Bash, Grep/Glob to locate files, and Read/Write/Edit on patch files in `<scratchpad>`, your session's scratchpad directory (`/tmp` when the harness provides none). No research, no running code or tests, no other skills however aggressive their trigger language, no advisor or second opinion.

Never edit working tree files, even for a typo, a wrong-looking version pin, or a failing-looking test; note the concern in your final message. Don't stage files the author didn't touch, don't verify beyond `git status` / `git log` after committing, and never run pre-commit hooks yourself; `git commit` runs them. Any change during staging silently alters reviewed work, and any tangent turns a 30-second operation into a 5-minute one.

## Workflow

Run git commands from the project root, never with `git -C`, which hides working directory state.

1. **Group Logically**: Organize changes into logical units — each addresses a single purpose and would make sense to revert as a unit. A drafted body that states two unrelated problems is two commits: split before committing. Several findings of one audit or review are one problem.

2. **Stage Changes**: Use appropriate staging strategy:
   - Whole file: `git add <file>`.
   - Hunk-by-hunk: `git diff <file> > <scratchpad>/patch.diff`, edit the patch, then `git apply --cached <scratchpad>/patch.diff`. Dropping whole hunks is safe. Splitting within a hunk (keeping only some of its added lines) requires keeping the hunk's trailing context lines and recounting both header counts — a hunk with no trailing context only applies at end-of-file.
   - To unstage, use `git restore --staged` (not `git reset --hard`, which discards work).
   - Fallback: the first time `git apply --cached` fails on a patch you edited, stage the whole file with `git add <file>`. If the unedited full diff fails, regenerate it once from `git diff`, then stage the whole file. Never diagnose why a patch didn't apply.

3. **Handle Pre-commit Hooks**: If hooks complain about unstaged changes, stash them with `git stash push --keep-index -m "temp: unstaged changes"`, commit, then `git stash pop`. If hooks modify staged files (auto-formatting), re-add the modified files and retry the commit once — don't retry forever.

4. **Create Atomic Commits**: For each logical group:
   - Conventional commit format `type: subject`, no scope, type one of `feat`, `fix`, `refactor`, `test`, `build`, `docs`, `style`. `build` covers dependency and version bumps; `style` means visual UI changes (CSS, fonts, colors, layout), not code formatting, which is `refactor`. Subject: what changed (≤72 chars), derived from the diff. Body: as The argument section decides; only the subject has a length limit. Footer: as the Attribution section decides.
   - Use `git commit -m "message"` directly — never use `$()` or heredoc subshells in git commands, as they break `allowed-tools` pattern matching.

## Attribution

End every commit message with the footer for your model family.

- Claude models use `Co-Authored-By: Claude <noreply@anthropic.com>`.
- GPT models use `Co-Authored-By: Codex <noreply@openai.com>`.
- Gemini models use `Co-Authored-By: Gemini <gemini-code-assistant@google.com>`.

Skip the footer only when you are certain none of these apply.

## Gotchas

- **Unstaged changes are still changes.** `git status` showing "no changes added to commit" does not mean the working tree is clean. It means nothing is staged yet. Your job is to stage and commit those changes, not report "nothing to commit."
- **Never use `git add -f`.** If `git add` reports "The following paths are ignored by one of your .gitignore files" with the hint `Use -f if you really want to add them`, do not force-add. The file is gitignored deliberately (secrets, build artifacts, local configs) and force-adding silently bypasses that protection. Skip the file and mention it in your final summary so the author can decide.
