---
description: Needs `--allow-tools WebSearch WebFetch`.
plugins: ["../../../../../skills"]
max_turns: 60
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, Agent, WebSearch, WebFetch]
---

Use the best-practices skill: I maintain a CLI that launches other CLI tools inside a macOS sandbox, configured by ~/.mytool/config.json (allowed paths, network domains). I want to add a per-project config, ./.mytool/config.json in the current directory, merged on top of the user one. The sandboxed process can write to the current directory. How do other tools handle project-local config like this, and what should I watch out for?
