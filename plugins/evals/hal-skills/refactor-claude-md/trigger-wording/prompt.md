---
description: "Needs `--scaffold --ablation none --allow-tools WebFetch Edit`; the without arm cannot load the skill, so it measures nothing here. skill-fired: a one-line wording fix to CLAUDE.md fires the skill. edit-made: the change landed. Baseline, 5 runs on claude-opus-5-5, no judge, against the description before the one-line-fix exemption and targeted scope: skill-fired old 0/5, new 5/5."
plugins: ["../../../../../skills"]
max_turns: 30
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, WebFetch, Edit]
---

In CLAUDE.md, change "fetch the official docs" to "search online for the official docs".
