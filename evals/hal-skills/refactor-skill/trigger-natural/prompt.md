---
description: Needs `--scaffold --allow-tools WebFetch Edit`. Tests that the description alone triggers the skill.
plugins: ["../../../../skills"]
max_turns: 60
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, WebFetch, Edit]
---

skills/release-notes/SKILL.md feels bloated, can you tighten it up without changing what it does?
