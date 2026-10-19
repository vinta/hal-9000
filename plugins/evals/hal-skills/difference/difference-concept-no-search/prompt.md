---
description: Needs `--model claude-fable-5-1 --allow-tools WebSearch WebFetch`. no-web-search and no-web-fetch check that a well-known concept comparison still answers from memory. Baseline (Fable 5.1, 3 runs per arm) 3/3 in both old and new text.
plugins: ["../../../../../skills"]
max_turns: 10
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, WebSearch, WebFetch]
---

/hal-skills:difference git rebase vs git merge
