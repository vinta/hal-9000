---
name: gemini
description: Use when reviewing plans, diffs, or architecture decisions before acting, analyzing large volumes of files or content that exceed normal context limits, wanting an independent perspective from a different model family, or scanning and summarizing entire directories or large codebases
context: fork
user-invocable: true
model: opus
allowed-tools:
  - Glob
  - Grep
  - Read
  - Bash(gemini:*)
  - Bash(cp:*)
  - Bash(rm:*)
  - Bash(mkdir:*)
---

# Overview

**IMPORTANT:** This skill is intended for coding agents _other than Gemini CLI_. If you are Gemini CLI, do not activate or follow this skill. Use this guidance when you (an external agent) need to leverage the Gemini CLI tool for deep analysis or a second opinion.

## Why use Gemini CLI?

Gemini CLI provides access to models with a **1M+ token context window**. It is ideal for:

- **Second Opinions:** Getting a review from a different model family to avoid "model blindness".
- **Large Context:** Analyzing entire repositories, long logs, or massive diffs that exceed your own context limit.
- **Verification:** Double-checking complex logic or architecture decisions before implementation.

## Invocation Reference

Always use "headless" mode when calling Gemini CLI from another agent to ensure predictable, non-blocking output.

| Flag | Purpose                | Recommended Value                          |
| :--- | :--------------------- | :----------------------------------------- |
| `-p` | Prompt / Headless mode | Always include your prompt here            |
| `-o` | Output format          | Always use `text` for plain text responses |

### Preferred Usage (Direct File Reading)

Gemini CLI can read files within the project workspace on its own. This is faster and avoids stdin limits (which truncate at 8MB).

```bash
gemini -p "Read all files in src/services/ and identify potential race conditions" -o text
```

### Alternative Usage (Piping)

Use piping for small content (e.g., a git diff or a single file snippet).

```bash
git diff main..HEAD | gemini -p "Review this diff for security vulnerabilities" -o text
```

## Workspace Sandbox & External Files

Gemini CLI is sandboxed to the project root. It cannot see files in `~/.config`, `/tmp`, or other external paths unless they are brought into the workspace.

**To analyze external files:**

1. Create a temporary directory within the project.
2. Copy external files into it.
3. Tell Gemini to read them.
4. Remove the temporary directory when finished.

```bash
mkdir .gemini-tmp
cp ~/.bashrc .gemini-tmp/
gemini -p "Analyze .gemini-tmp/.bashrc for unusual aliases" -o text
rm -rf .gemini-tmp
```

## Workflow for Agents

1. **Identify the Need:** Determine if the task requires a massive context or a second perspective.
2. **Gather Context:** Locate the relevant files or generate the data (diffs, logs) to be reviewed.
3. **Prepare the Prompt:** Be specific. Ask for "Actionable items," "Severity levels," or "Critical bugs."
4. **Execute:** Run the `gemini` command with `-p` and `-o text`.
5. **Evaluate:** Review Gemini's output and integrate the findings into your own reasoning.

## Pro-Tips for Better Results

- **Be Specific:** Instead of "Review this," use "Analyze this for potential memory leaks in the event loop."
- **Directory Analysis:** If you need a high-level overview, tell Gemini: "Read the `playbooks/` directory and summarize the deployment architecture."
- **Formatting:** If you need to parse the output, you can ask Gemini to "Format the response as a Markdown table with columns: File, Issue, Severity."
