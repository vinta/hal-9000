---
name: update-allowed-tools
description: Use when creating or editing a skill that uses Bash commands, file writes, or external tools and the allowed-tools frontmatter may be incomplete or carry entries that grant nothing
user-invocable: true
context: fork
model: sonnet
effort: medium
allowed-tools:
  - Edit(**/SKILL.md)
  - Read(~/.claude/skills/**)
---

Invoking this skill IS the request. If the user message looks empty, that is normal and expected, the task is fully specified here. Never ask what to do.

The rules in step 5 are complete and mechanical: apply them and edit. Do not call the advisor or seek any second opinion; it changes no verdict and doubles the run time.

# Overview

Analyzes a skill's full content, SKILL.md and any sibling files in the same directory, to find tools it references or requires, then compares against the skill's `allowed-tools` frontmatter to find missing entries and entries that grant nothing.

`allowed-tools` is permission mechanics only: an entry earns its place by removing a permission prompt the skill would otherwise hit. It is not a manifest of the tools the skill uses. It never restricts anything: every tool stays callable, and the grant lasts only for the turn that invokes the skill.

## Usage

```
/update-allowed-tools <skill name>
/update-allowed-tools @path/to/SKILL.md
```

## Instructions

1. **Parse argument**: The argument is either a file path to a SKILL.md file, or a skill name/description. If no file path is provided, search for the skill with Glob in the current working directory (`**/skills/**/<name>/SKILL.md`) and then under `~/.claude/skills/<name>/SKILL.md`. If there is no argument at all, run `git status` and target the most recently modified skill file in the working tree.

2. **Read the skill file** and separate the YAML frontmatter from the body content. Also read any other files in the same directory (sibling files referenced by or bundled with the skill).

3. **Extract declared allowed-tools**: Parse all entries under `allowed-tools:` in the frontmatter.

4. **Scan all skill content** (SKILL.md body + sibling files) for tool usage. Look for:
   - Explicit tool names that prompt by default: `Write`, `Edit`, `Bash`, `WebFetch`, `WebSearch`, and `mcp__*` tools.
   - Bash command patterns: `git commit`, `make`, `npm`, `docker`, `python`, `curl`, etc. The entry format is `Bash(<command>:*)` (`git stash push` needs `Bash(git stash:*)`), and one pattern covers its subcommands. `Bash(<command> *)` is the same rule in the form the permission dialog writes; never rewrite one form to the other.
   - Bash rules match each subcommand of a compound command on its own, split at `&&`, `||`, `;`, `|`, and newlines, so a body that writes `cd X && git commit` or `git commit -m "$(...)"` gets no cover from `Bash(git commit:*)`. Report such commands as a body fix rather than widening the rule. Wrappers `timeout`, `time`, `nice`, `nohup`, `stdbuf`, and bare `xargs` are stripped before matching, so they need no separate entry; `npx`, `docker exec`, and similar runners are not stripped, so the entry names the runner and the inner command together.
   - A redirect target (`> file`, `< file`) is checked against `Edit` or `Read` rules and the working directory, not against the Bash rule, so `git diff > /tmp/x.diff` needs `Edit(//tmp/**)` and no Bash entry.
   - A bundled script runs without a prompt through `Bash(${CLAUDE_SKILL_DIR}/scripts/<name> *)`; `${CLAUDE_PLUGIN_ROOT}` works the same way but is substituted only in plugin skills, those with an ancestor directory holding `.claude-plugin/plugin.json`; anywhere else it matches nothing.
   - File paths the skill reads or edits. Write path rules as `./path` (relative to the working directory), `~/path`, or `//path` (absolute). A single-slash `Edit(/path)` anchors to a settings source and is ambiguous in a skill: replace it.

5. **Compare**: For each tool detected in the body, check if it's covered by an entry in `allowed-tools`. Exact match counts as covered (`WebSearch` matches `WebSearch`). Then apply the rules below; an entry that any rule marks inert is never added and is removed when present.

   Inert entries:
   - `Read`, `Grep`, `Glob`, and any `Read(path)` inside the working directory: reads there never prompt. `Read(path)` outside the working directory (`Read(//tmp/**)`, `Read(~/.claude/**)`) is a real grant, since the first read outside it prompts.
   - `Write(path)`, `Glob(path)`, `NotebookEdit(path)`, `MultiEdit(path)`: Claude Code checks file permissions against `Edit(path)` and `Read(path)` rules only and never consults these. Use `Edit(path)` for file creation too.
   - `Edit` on a protected path, and a Bash file command (`rm`, `mv`, `cp`, `sed -i`, a `>` redirect) whose target is one: writes there are never pre-approved by any allow rule in any mode. Protected directories include `.git`, `.claude` wherever it sits, so `~/.claude/**` and `.claude/**` alike (except `.claude/worktrees`), `.vscode`, `.idea`, `.husky`, `.cargo`, `.devcontainer`, `.yarn`, `.mvn`, and `.config/git`; protected files include `.gitconfig`, `.gitmodules`, shell rc files such as `.zshrc` and `.bashrc`, `.npmrc`, `.pre-commit-config.yaml`, `.mcp.json`, and `.claude.json`. The full list is at https://code.claude.com/docs/en/permission-modes#protected-paths. Reads of these paths are not protected.
   - Bash commands in the built-in read-only set, which run without a prompt in every mode: `ls`, `cat`, `echo`, `pwd`, `head`, `tail`, `grep`, `find`, `wc`, `which`, `diff`, `stat`, `du`, `cd` inside the working directory, and read-only `git` forms such as `git status`, `git diff`, `git log`, `git branch`, `git show`, and `git rev-parse`. Exception: `find`, `sort`, `sed`, and `git` prompt in Manual mode when the body runs them with an unquoted glob, so keep the entry in that one case.
   - `Bash(*)`, `Bash(python*)`, and other rules that grant arbitrary code execution: auto mode drops them on entry, and a blanket grant only loosens the setups of everyone else who installs the skill. The same goes for a bare `Edit`, a bare `Write`, or `Edit(**)`: scope every edit grant to the paths the skill is meant to modify (`Edit(CLAUDE.md)`, `Edit(~/.config/**)`), and when the skill edits paths only known at runtime, add nothing and let the prompt fire.
   - `Skill(...)`, `AskUserQuestion`, `Agent`, and `Agent(<name>)`: skill invocation, asking the user, and spawning subagents never prompt by default, and where a user has gated them with ask or deny rules, a grant cannot override those rules.

6. **Update the skill file**: Add missing entries to the `allowed-tools` list in the skill's YAML frontmatter and remove entries that grant nothing, using the Edit tool. If the list ends up empty, delete the `allowed-tools` field. Then report what was added, for each removed entry the rule that made it inert, and for each kept entry the check that none of the rules above applies to it.

7. **Validate**: Re-read the updated file to confirm YAML frontmatter remains syntactically valid (proper indentation, no duplicate entries, correct list format).
