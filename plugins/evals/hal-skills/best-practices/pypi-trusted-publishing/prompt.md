---
description: Needs `--allow-tools WebSearch WebFetch`.
plugins: ["../../../../../skills"]
max_turns: 60
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, Agent, WebSearch, WebFetch]
---

Use the best-practices skill: I publish a small zero-dependency Python library to PyPI from GitHub Actions with trusted publishing (OIDC) and uv. The workflow runs on a `v*` tag push, builds with `uv build`, and publishes with `uv publish`. What is the hardened way to set this up, and what bites people?
