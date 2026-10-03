---
description: "Needs `--scaffold --allow-tools WebFetch`. One grader per planted defect; run two arms and read each grader's delta, not the case score. The fixture's `user-invocable: true` is planted but ungraded, since plain review cuts it too."
plugins: ["../../../../../skills"]
max_turns: 60
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, WebFetch]
---

review skills/deploy-check/, I think it can be tightened. For each line or file say cut, move, reword, or keep, and why. Don't edit anything and don't ask me questions.
