---
description: Needs `--scaffold --allow-tools WebFetch`.
plugins: ["../../../../skills"]
max_turns: 60
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, WebFetch]
---

Use the refactor-skill skill to run a full audit of skills/best-practices/SKILL.md. Report every verdict with the line it applies to, then stop: do not edit the file and do not ask me questions.
