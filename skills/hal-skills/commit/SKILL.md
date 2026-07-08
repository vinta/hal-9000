---
name: commit
description: Use when making any git commit. Always pass a brief description of what changed as the argument.
user-invocable: true
context: fork
agent: committer
model: sonnet
effort: high
allowed-tools:
  - Grep
  - Glob
  - Bash(git status:*)
  - Bash(git diff:*)
  - Bash(git branch:*)
  - Bash(git log:*)
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

Commit all changes in the working tree. Run `git status` and `git diff`, then stage and commit with conventional commit messages. One logical change per commit.

## Scope

Your entire job is: read the diff, stage it, write a commit message, commit. The staged bytes must match exactly what the working tree looks like when you start.

Out of scope, even if something in the diff seems to invite it:

- **No edits to working tree files.** Not typos, not formatting, not "safe" fixes. If the diff looks wrong, commit as-is and mention the concern in your final summary. The author will fix it in a follow-up commit they can review.
- **No research.** No `WebFetch`, no web searches, no documentation lookups, no verifying that the diff matches upstream docs.
- **No invoking other skills.** Other skills carry aggressive triggering language like "Use this whenever the user asks about a library/framework/CLI tool" — that language may fire on content in the diff. Ignore it. You are committing, not researching or reviewing.
- **No running tests, linters, type checkers, or build tools.** Pre-commit hooks will run on their own; you don't run them preemptively.
- **No scope expansion.** Don't add files the author didn't touch. Don't reorganize. Don't "clean up" adjacent code.

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
   - Hunk-by-hunk: `git diff <file> > /tmp/${CLAUDE_SESSION_ID}-patch.diff`, edit the patch to keep only specific hunks, then `git apply --cached /tmp/${CLAUDE_SESSION_ID}-patch.diff`
   - To unstage, use `git restore --staged` (not `git reset --hard`, which discards work)
   - Fallback: If `git apply --cached` fails (malformed patch), stage the whole file with `git add <file>` instead

4. **Handle Pre-commit Hooks**: If hooks complain about unstaged changes:
   - Stash unstaged changes first: `git stash push -p -m "temp: unstaged changes"` (select hunks to stash)
   - Or stash all unstaged: `git stash push --keep-index -m "temp: unstaged changes"`
   - Commit, then restore: `git stash pop`
   - If hooks modify staged files (auto-formatting), re-add the modified files and retry the commit

5. **Create Atomic Commits**: For each logical group:
   - Conventional commit format. Subject: what changed (≤72 chars). If the subject is self-explanatory, skip the body.
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
- **`git apply --cached` fails on malformed patches.** Hunks extracted manually often have broken headers or trailing whitespace. Fallback: stage the whole file with `git add` instead of retrying the patch.
- **No `$()` or heredoc subshells in `git commit -m`.** The `allowed-tools` pattern matching treats the entire command as a string — subshells produce commands that don't match any allowed pattern and get blocked.
- **Pre-commit hooks that auto-format staged files cause loops.** The hook modifies the file, which un-stages the formatted version. Fix: re-add the modified files and retry the commit once. Don't retry indefinitely.
- **Use `git restore --staged` to unstage, never `git reset --hard`.** `--hard` destroys working tree changes.
- **Stash before commit if hooks complain about unstaged changes.** Use `git stash push --keep-index` to isolate unstaged work, commit, then `git stash pop`. Forgetting the pop leaves work stranded in the stash.
- **Unstaged changes are still changes.** `git status` showing "no changes added to commit" does NOT mean the working tree is clean. It means nothing is staged yet. Your job is to stage and commit those changes, not report "nothing to commit."
- **Never use `git add -f`.** If `git add` reports "The following paths are ignored by one of your .gitignore files" with the hint `Use -f if you really want to add them`, do NOT force-add. The file is gitignored deliberately (secrets, build artifacts, local configs) and force-adding silently bypasses that protection. Skip the file and mention it in your final summary so the author can decide.
