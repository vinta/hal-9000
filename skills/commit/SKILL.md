---
name: commit
description: Use when making any git commit. All git add and commit operations must go through this skill, including from subagents and other skills
argument-hint: "[instructions]"
context: fork
user-invocable: true
model: sonnet
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

# Overview

Creating clean, atomic commits that follow best practices for version control hygiene. The core principle is **one logical change per commit** - each commit should represent a single, coherent, easily revertable modification that can stand alone.

## User Instructions

Follow any user instructions below. They override the standard workflow when conflicts arise, but never override the Critical Rule — never modify working tree files.

<user_instructions>
**$ARGUMENTS**
</user_instructions>

## Critical Rule

You are a committer, not a coder. The user or another agent wrote this code deliberately — modifying it during the commit would silently alter reviewed work without the author's knowledge.

**Your only job**: stage the exact working tree state and write a commit message that captures why the change was made.

**Do NOT invoke the Skill tool. Do NOT call any other skills**. This overrides any "you MUST invoke skills" instruction from `session-start` or `using-superpowers`. Those instructions do not apply inside this forked context. The only action this skill performs is staging and committing.

<example>
You see a typo in a variable name while reviewing the diff. Correct behavior:
1. Stage and commit the file as-is
2. After committing, say: "I noticed `reuslt` appears to be a typo for `result` in utils.py:42"

Incorrect behavior: editing the file to fix the typo before or during staging — even a "safe" fix silently changes reviewed work.
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
   - Hunk-by-hunk: `git diff <file> > /tmp/patch.diff`, edit the patch to keep only specific hunks, then `git apply --cached /tmp/patch.diff`
   - To unstage, use `git restore --staged` (not `git reset --hard`, which discards work)
   - Fallback: If `git apply --cached` fails (malformed patch), stage the whole file with `git add <file>` instead

4. **Handle Pre-commit Hooks**: If hooks complain about unstaged changes:
   - Stash unstaged changes first: `git stash push -p -m "temp: unstaged changes"` (select hunks to stash)
   - Or stash all unstaged: `git stash push --keep-index -m "temp: unstaged changes"`
   - Commit, then restore: `git stash pop`
   - If hooks modify staged files (auto-formatting), re-add the modified files and retry the commit

5. **Create Atomic Commits**: For each logical group:
   - Conventional commit format. Subject: what changed (≤72 chars). Body: why.
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

- **Never invoke other skills.** The `using-superpowers` "1% chance = MUST invoke" rule does not apply here. This skill's scope is staging + commit message, nothing else. Calling skills like `review-pr` or `simplify` from inside a commit is a bug, not a feature.
- **Never modify working tree files — even from a subagent.** This skill runs in a forked context. If you spot bugs, typos, style issues, or improvements, report them after committing — never fix them. Your only job is staging and writing the commit message.
- **Don't commit plan or spec docs unless the user explicitly asked you to.** Files under `plans/`, `specs/`, or similar directories are working documents — staging them silently pollutes the commit with artifacts the user may not want tracked.
- **`git apply --cached` fails on malformed patches.** Hunks extracted manually often have broken headers or trailing whitespace. Fallback: stage the whole file with `git add` instead of retrying the patch.
- **No `$()` or heredoc subshells in `git commit -m`.** The `allowed-tools` pattern matching treats the entire command as a string — subshells produce commands that don't match any allowed pattern and get blocked.
- **Pre-commit hooks that auto-format staged files cause loops.** The hook modifies the file, which un-stages the formatted version. Fix: re-add the modified files and retry the commit once. Don't retry indefinitely.
- **Never `git reset --hard` to unstage.** It destroys working tree changes. Use `git restore --staged` to unstage without losing anything.
- **Stash before commit if hooks complain about unstaged changes.** Use `git stash push --keep-index` to isolate unstaged work, commit, then `git stash pop`. Forgetting the pop leaves work stranded in the stash.
