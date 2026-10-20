---
description: "Needs `--scaffold --allow-tools WebFetch`. The fixture is best-practices before commit 1707f97 trimmed it, minus the sentence \"Do not block synthesis waiting for a straggler.\"; run two arms and read each grader. The cuts-* graders expect that trim's cuts, each with a no-op argument of its own; all but cuts-dedupe fail in both arms, so they are gradients only a change to the delete verdict can move. The trim's other cuts rested on eval results an audit cannot see, so their graders instead check whether the audit finds the defect each line has in the file: the quota fallback sits where subagents never read it, the training-data tier contradicts the no-training-data rule, attribution needs per-claim sources the template does not ask for, and stale filtering needs the template's publication dates. Baseline, 2 runs per arm, Sonnet judge: cuts-dedupe 2/2 with, 1/2 without; quota-placement 0/2 and 0/2; rank-contradiction 0/2 and 1/2; conflicts-attribution 0/4; stale-dates 4/4; the other cuts-* 0/4. A with-plugin audit may still call `find-docs` missing: the scaffolded stub is a file, not a loaded skill."
plugins: ["../../../../../skills"]
max_turns: 30
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, WebFetch]
---

review skills/best-practices/SKILL.md, I think we can trim it. Go through every line and tell me which you'd delete, rewrite, or keep, and why. Don't edit the file and don't ask me questions.
