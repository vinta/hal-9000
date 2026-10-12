---
description: "Needs `--scaffold --ablation none --allow-tools WebFetch Edit`; the without arm cannot load the skill, so it measures nothing here. Control. skill-not-fired: an edit to a markdown file that is not CLAUDE.md leaves the skill alone. edit-made: the heading changed. Baseline, 5 runs on claude-opus-5-5, no judge, against the description before the one-line-fix exemption and targeted scope: skill-not-fired 5/5 in both arms."
plugins: ["../../../../../skills"]
max_turns: 30
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, WebFetch, Edit]
---

In README.md, rename the "Install" heading to "Setup".
