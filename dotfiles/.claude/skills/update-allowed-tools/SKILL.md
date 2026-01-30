---
name: update-allowed-tools
description: Find tools a skill's content needs but its allowed-tools frontmatter is missing
allowed-tools:
  - Grep
  - Glob
  - Read
context: fork
user-invocable: true
disable-model-invocation: true
model: haiku
---

# Overview

Analyzes a skill's body content to find tools it references or requires, then compares against that same skill's `allowed-tools` frontmatter to find missing entries.

## Usage

```
/update-allowed-tools @path/to/SKILL.md
```

## Instructions

1. **Parse argument**: The argument is a file path to a SKILL.md file.

2. **Read the skill file** and separate the YAML frontmatter from the body content.

3. **Extract declared allowed-tools**: Parse all entries under `allowed-tools:` in the frontmatter.

4. **Scan the body content** for tool usage. Look for:
   - Explicit tool names: `Read`, `Write`, `Edit`, `Glob`, `Grep`, `Bash`, `WebFetch`, `WebSearch`, `Task`, `AskUserQuestion`, `NotebookEdit`, `Skill`
   - Bash command patterns: any mention of `git status`, `git diff`, `git add`, `git commit`, `git stash`, `git restore`, `git log`, `git branch`, `git mv`, `git rm`, `git apply`, `git reset`, `git push`, `git pull`, `git rebase`, `git cherry-pick`, `git checkout`, `git merge`, `git tag`, `git fetch`, `git clone`, `git init`, `git remote`, `make`, `npm`, `yarn`, `pip`, `uv`, `docker`, `ansible`, `pytest`, `python`, `node`, `ls`, `tree`, `pwd`, `which`, `cd`, `mkdir`, `cp`, `mv`, `rm`, `cat`, `head`, `tail`, `jq`, `curl`, `wget`, etc.
   - For Bash commands found, the required allowed-tool format is `Bash(<command>:*)` (e.g., `git stash push` needs `Bash(git stash:*)`)
   - For file tools with path patterns (Read, Write, Edit), note the paths referenced (e.g., `/tmp/` needs `Read(//tmp/**)`)

5. **Compare**: For each tool detected in the body, check if it's covered by an entry in `allowed-tools`. A tool is covered if:
   - Exact match exists (e.g., `Grep` matches `Grep`)
   - A Bash pattern covers the command (e.g., `Bash(git stash:*)` covers `git stash push`)
   - A path pattern covers referenced paths

6. **Report**: Output:
   - **Missing**: Tools the body uses but `allowed-tools` doesn't declare
   - **Suggestion**: The exact `allowed-tools` entries to add
   - **Already covered**: Tools that are properly declared (brief summary)
