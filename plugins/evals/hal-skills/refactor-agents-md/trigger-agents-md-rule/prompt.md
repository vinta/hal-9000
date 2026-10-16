---
description: "Needs `--scaffold --ablation none --allow-tools WebFetch Edit`; the without arm cannot load the skill, so it measures nothing here. skill-fired: adding one rule to AGENTS.md fires the skill. guides-fetched: once fired, the skill fetched its prompting guides instead of skipping to the edit. edit-made: the rule landed. Unmeasured yet."
plugins: ["../../../../../skills"]
max_turns: 30
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, WebFetch, Edit]
---

Add this to the Writing Style section of AGENTS.md: "When feedback revises text you wrote, rework the whole passage it touches so it reads as written once."
