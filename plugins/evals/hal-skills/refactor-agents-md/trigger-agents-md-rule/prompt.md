---
description: "Needs `--scaffold --ablation none --allow-tools WebFetch Edit`; the without arm cannot load the skill, so it measures nothing here. skill-fired: adding one rule to AGENTS.md fires the skill. guides-fetched: once fired, the skill fetched its prompting guides instead of skipping to the edit. edit-made: the rule landed. Baseline, 5 runs on claude-opus-5-5, no judge: skill-fired 5/5, edit-made 5/5; guides-fetched 2/5 with the guides behind a reference pointer, 5/5 once step 2 got a completion criterion."
plugins: ["../../../../../skills"]
max_turns: 30
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, WebFetch, Edit]
---

Add this to the Writing Style section of AGENTS.md: "When feedback revises text you wrote, rework the whole passage it touches so it reads as written once."
