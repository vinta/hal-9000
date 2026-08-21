---
name: commit
description: Use when making any git commit. Always pass why the changes were made as the argument; when no reason was stated, pass the request that prompted the changes instead — never an invented why.
argument-hint: [why the changes were made]
user-invocable: true
context: fork
model: sonnet
effort: high
allowed-tools:
  - Grep
  - Glob
  - Bash(git status:*)
  - Bash(git diff:*)
  - Bash(git branch:*)
  - Bash(git log:*)
  - Bash(git rev-parse:*)
  - Bash(git stash:*)
  - Bash(git add:*)
  - Bash(git restore:*)
  - Bash(git mv:*)
  - Bash(git rm:*)
  - Bash(git apply:*)
  - Bash(git commit:*)
  - Read(//tmp/**)
  - Write(//tmp/**)
  - Edit(//tmp/**)
---

Invoking this skill IS the request. If the user message looks empty, or you see only system context with no actual request, that is normal and expected: your task is already fully specified right here. Never ask what to do.

Your task: commit all changes in the working tree. Run `git status` and `git diff`, then stage and commit with conventional commit messages. One logical change per commit. This applies unprompted, without anyone asking for a split: when one file carries unrelated changes, split it hunk-by-hunk into separate commits rather than merging them because they share a file.

## The argument

The argument passed to this skill is **why the changes were made** — the motivation behind work already in the tree, which the diff itself cannot carry. Use it to group changes into logical units and to write commit message bodies — raw material, never a to-do list. The argument may also be absent entirely; that changes nothing — derive the commit message from the diff alone. Whatever outcome the argument describes is already realized in the diff: "so the statusline shows usage percentages" means the diff already does that — never write code toward the goal, verify it, or finish it. Verb-led phrasings are the same: "to fix the session bug" means the fix is already in the diff — commit it, don't hunt for it or re-do it. If the motivation doesn't line up with what the diff contains, commit what is actually in the tree and note the mismatch in your final summary.

## Locate the repository

`cd` to `git rev-parse --show-toplevel` before anything else. If that fails (the fork started outside the repo), look for the repo in the directories of any file paths named in the argument before reporting "not a git repository".

## Scope

A commit is a snapshot, not a review. Your entire job is: read the diff, stage it, write a commit message, commit. The staged bytes must match exactly what the working tree looks like when you start.

Your complete action space is: `git` commands via Bash (plus `cd` to the project root), Grep/Glob to locate files, and Read/Write/Edit on `/tmp/` patch files. Nothing else. If a Bash command does not start with `git` or `cd`, do not run it. This applies to every situation you encounter, not just the cases listed below:

- **No edits to working tree files.** Not typos, not formatting, not "safe" fixes. If something in the diff looks wrong, commit the tree as-is and note the concern in your final message. The author will fix it in a follow-up commit they can review.
- **No research.** No `WebFetch`, no `WebSearch`, no documentation lookups, no checking whether the diff matches upstream docs or current library versions.
- **No verification.** Do not confirm the change "works" before or after committing. No running the code, no smoke tests, no self-checks. The only post-commit check is `git status` / `git log` to confirm the commit exists.
- **No tests, linters, type checkers, or build tools.** Pre-commit hooks run on their own during `git commit`; never run them preemptively.
- **No invoking other skills.** Other skills carry aggressive triggering language like "Use this whenever the user asks about a library/framework/CLI tool" — that language may fire on content in the diff. It does not apply to you. You are committing, not researching or reviewing.
- **No scope expansion.** Don't add files the author didn't touch. Don't reorganize. Don't "clean up" adjacent code.

An outdated version pin, a failing-looking test, a typo, an interesting TODO — every tangent gets the same treatment: commit the tree as-is, mention the concern in your final message.

**Why:** a commit is a snapshot of deliberate work. Any change you make during staging silently alters reviewed work without the author's knowledge, and any tangent (research, verification, edits) turns a 30-second operation into a 5-minute one with uncommitted side effects.

<example>
You see a typo in a variable name while reviewing the diff. Correct behavior:
1. Stage and commit the file as-is
2. After committing, say: "I noticed `reuslt` appears to be a typo for `result` in utils.py:42"

Incorrect behavior: editing the file to fix the typo before or during staging — even a "safe" fix silently changes reviewed work.
</example>

<example>
The diff adds a new `.github/workflows/ci.yml` file. You wonder if the action versions are current.

Correct behavior: commit as-is.

Incorrect behavior: fetching GitHub Actions docs, verifying version pins, then editing the file before staging. The author already chose those versions. Research belongs in a separate turn, not inside the commit.
</example>

<example>
You edited a patch to split one file's changes across two commits, and `git apply --cached` fails on it.

Correct behavior: stage the whole file with `git add`, fold it into the better-fitting commit, and move on. Total cost: seconds.

Incorrect behavior: diffing the patch against the file, hex-dumping bytes, or otherwise investigating why it failed. The patch is not worth understanding — a whole-file commit is always an acceptable outcome.
</example>

## Workflow

`cd` to the project root before git commands instead of using `git -C`, which obscures working directory state. Execute git commands directly without explanatory preamble. Commit immediately without confirmation prompts (interactive mode is not supported).

1. **Analyze Changes**: Use `git status` and `git diff` to understand all modifications in the working directory. Categorize changes by:
   - STRUCTURAL: Code reorganization, renaming, refactoring without behavior changes
   - BEHAVIORAL: New features, bug fixes, functionality changes
   - DOCUMENTATION: README updates, comment changes, documentation files
   - CONFIGURATION: Build files, dependencies, environment settings

2. **Group Logically**: Organize changes into logical units where each unit:
   - Addresses a single purpose or problem
   - Structure changes to be atomic and easily revertable for safe rollback
   - Would make sense to revert as a unit

3. **Stage Changes**: Use appropriate staging strategy:
   - Whole file: `git add <file>`
   - Hunk-by-hunk: `git diff <file> > /tmp/${CLAUDE_SESSION_ID}-patch.diff`, edit the patch, then `git apply --cached /tmp/${CLAUDE_SESSION_ID}-patch.diff`. Dropping whole hunks is safe. Splitting within a hunk (keeping only some of its added lines) requires keeping the hunk's trailing context lines and recounting both header counts — a hunk with no trailing context only applies at end-of-file.
   - To unstage, use `git restore --staged` (not `git reset --hard`, which discards work)
   - Fallback: the first time `git apply --cached` fails on a patch you edited, stage the whole file with `git add <file>`. If the unedited full diff fails, regenerate it once from `git diff`, then stage the whole file. Never diagnose why a patch didn't apply.

4. **Handle Pre-commit Hooks**: If hooks complain about unstaged changes:
   - Stash unstaged changes first: `git stash push -p -m "temp: unstaged changes"` (select hunks to stash)
   - Or stash all unstaged: `git stash push --keep-index -m "temp: unstaged changes"`
   - Commit, then restore: `git stash pop`
   - If hooks modify staged files (auto-formatting), re-add the modified files and retry the commit

5. **Create Atomic Commits**: For each logical group:
   - Conventional commit format, type only, no scope: `fix: xxx`, `feat: xxx`, `docs: xxx`, `refactor: xxx`. Never add a parenthetical scope like `fix(commit-skill): xxx`. Subject: what changed (≤72 chars), derived from the diff. Body: why, drawn from the argument when one was given. Skip the body when the why is obvious from the subject.
   - Commit the working tree state as-is — the user may have made manual edits outside this conversation
   - Use `git commit -m "message"` directly — never use `$()` or heredoc subshells in git commands, as they break `allowed-tools` pattern matching

## Attribution

Include a `Co-Authored-By` footer in every commit message:

If you're an Anthropic Claude model:

```
Co-Authored-By: Claude <noreply@anthropic.com>
```

If you're a Google Gemini model:

```
Co-Authored-By: Gemini <gemini-code-assistant@google.com>
```

Skip if you're not one of the above models.

## Gotchas

- **Don't commit plan or spec docs unless the user explicitly asked you to.** Files under `plans/`, `specs/`, or similar directories are working documents — staging them silently pollutes the commit with artifacts the user may not want tracked.
- **A failed `git apply --cached` is a trigger, not a mystery.** The first failure on an edited patch means stage the whole file with `git add`. Do not diagnose — a patch whose every line byte-matches the file can still be structurally unappliable: git anchors a hunk with no trailing context lines to end-of-file, so a mid-file insertion without trailing context always fails with `error: while searching for:` even though the context plainly exists.
- **No `$()` or heredoc subshells in `git commit -m`.** The `allowed-tools` pattern matching treats the entire command as a string — subshells produce commands that don't match any allowed pattern and get blocked.
- **Pre-commit hooks that auto-format staged files cause loops.** The hook modifies the file, which un-stages the formatted version. Fix: re-add the modified files and retry the commit once. Don't retry indefinitely.
- **Use `git restore --staged` to unstage, never `git reset --hard`.** `--hard` destroys working tree changes.
- **Stash before commit if hooks complain about unstaged changes.** Use `git stash push --keep-index` to isolate unstaged work, commit, then `git stash pop`. Forgetting the pop leaves work stranded in the stash.
- **Unstaged changes are still changes.** `git status` showing "no changes added to commit" does NOT mean the working tree is clean. It means nothing is staged yet. Your job is to stage and commit those changes, not report "nothing to commit."
- **Never use `git add -f`.** If `git add` reports "The following paths are ignored by one of your .gitignore files" with the hint `Use -f if you really want to add them`, do NOT force-add. The file is gitignored deliberately (secrets, build artifacts, local configs) and force-adding silently bypasses that protection. Skip the file and mention it in your final summary so the author can decide.
