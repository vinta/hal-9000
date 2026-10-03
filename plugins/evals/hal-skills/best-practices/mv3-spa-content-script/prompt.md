---
description: Needs `--allow-tools WebSearch WebFetch`.
plugins: ["../../../../../skills"]
max_turns: 60
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, Agent, WebSearch, WebFetch]
---

Use the best-practices skill: my Chrome MV3 extension registers its content script with `chrome.scripting.registerContentScripts`, using `matches` for a URL whitelist and `excludeMatches` for a blacklist. On single-page apps like GitHub, the blacklist and whitelist stop working after in-app navigation. What is the recommended fix, and what bites people?
