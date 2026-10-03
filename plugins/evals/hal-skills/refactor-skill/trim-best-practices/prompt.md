---
description: "Needs `--scaffold --allow-tools WebFetch`. Targets are the lines commit 1707f97 cut from best-practices; run two arms and read each grader. dedupe, be-concrete, failed-subagent, and present-findings have a no-op argument of their own. rank, conflicts, stale, and quota rest only on the best-practices A/B, whose graders never observed them. A with-plugin audit may still call `find-docs` missing: the scaffolded stub is a file, not a loaded skill."
plugins: ["../../../../../skills"]
max_turns: 60
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, WebFetch]
---

review skills/best-practices/SKILL.md, I think we can trim it. Go through every line and tell me which you'd delete, rewrite, or keep, and why. Don't edit the file and don't ask me questions.
