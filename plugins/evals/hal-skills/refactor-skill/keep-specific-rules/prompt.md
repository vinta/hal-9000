---
description: Needs `--scaffold --allow-tools WebFetch`.
plugins: ["../../../../../skills"]
max_turns: 60
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, WebFetch]
---

review skills/release-notes/SKILL.md, I think we can trim it. Go through every line and tell me which you'd delete, rewrite, or keep, and why. Don't edit the file and don't ask me questions.
