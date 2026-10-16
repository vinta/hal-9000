---
description: "Needs `--scaffold --ablation none --allow-tools WebFetch Edit`; the without arm cannot load the skill, so it measures nothing here. skill-fired: a section reorder in CLAUDE.md fires the skill. edit-made: Surface Assumptions now precedes Plan and Ask. Baseline, 5 runs on claude-opus-5-5, no judge, against the description before the one-line-fix exemption and targeted scope: skill-fired old 3/5, new 5/5."
plugins: ["../../../../../skills"]
max_turns: 30
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, WebFetch, Edit]
---

In CLAUDE.md, move the Surface Assumptions subsection above Plan and Ask, since I want assumptions shown before the plan.
