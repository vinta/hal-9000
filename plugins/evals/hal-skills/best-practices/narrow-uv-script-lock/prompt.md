---
description: Needs `--allow-tools WebSearch WebFetch`. A narrow single-tool question that uv's own docs settle, so the skill should answer without subagents. skill-fired checks that the skill fires when the prompt does not name it; agent-calls only records the Agent call count and never fails; ground-truth facts come from https://docs.astral.sh/uv/guides/scripts/ (Locking dependencies, Improving reproducibility).
plugins: ["../../../../../skills"]
max_turns: 60
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, Agent, WebSearch, WebFetch]
---

I have a single-file Python script with PEP 723 inline metadata (a `# /// script` block listing its dependencies) that my team runs with `uv run`. Teammates sometimes end up with different package versions than I do. How do I lock its dependencies with uv, and what bites people?
