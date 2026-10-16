---
description: "Needs `--scaffold --ablation none --allow-tools WebFetch Edit`; the without arm cannot load the skill, so it measures nothing here. skill-fired: adding one rule to CLAUDE.md fires the skill. guides-fetched: once fired, the skill fetched its prompting guides instead of skipping to the edit. edit-made: the rule landed. Baseline, 5 runs on claude-opus-5-5, no judge, against the description before the one-line-fix exemption and targeted scope: skill-fired old 4/5, new 5/5; guides-fetched old 0/5, new 5/5."
plugins: ["../../../../../skills"]
max_turns: 30
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, WebFetch, Edit]
---

Add this to the Writing Style section of CLAUDE.md: "When feedback revises text you wrote, rework the whole passage it touches so it reads as written once."
