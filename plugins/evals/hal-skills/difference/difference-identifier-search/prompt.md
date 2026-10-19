---
description: Needs `--model claude-fable-5-1 --allow-tools WebSearch WebFetch`; Opus searches even under the old text, so only Fable at the skill's low effort separates the arms. web-search checks the identifier trigger fires; dialog-expiry-scope checks the answer matches the settings reference (dialogExpiry covers remote and forwarded dialogs, not local permission prompts) and also measures which sources the search lands on. Baseline (Fable 5.1, Sonnet judge, 5 runs per arm) web-search 5/5 new text vs 2/5 old, dialog-expiry-scope 1/5 in both; failing runs answered from third-party Agent SDK pages.
plugins: ["../../../../../skills"]
max_turns: 10
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, WebSearch, WebFetch]
---

/hal-skills:difference dialogExpiry vs askUserQuestionTimeout
