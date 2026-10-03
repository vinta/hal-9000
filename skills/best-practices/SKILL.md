---
name: best-practices
description: Use when about to choose, configure, or refine a tool, library, config format, API pattern, or project setup, or before proposing a design of your own — research current guidance, pitfalls, and prior art first; already knowing an approach, or assuming no prior art exists, is not an exemption. Also use when the user asks about best practices, gotchas, or recommended patterns
argument-hint: "[tool, library, pattern, or design to research]"
allowed-tools:
  - WebSearch
  - WebFetch
  - Bash(ctx7:*)
  - Bash(npx ctx7:*)
  - Bash(npx ctx7@latest:*)
---

# Best Practices

Answer two questions from current sources: **what's the recommended way**, and **what bites people** (the gotchas and pitfalls around it). A how-to without its pitfalls is half an answer.

## Two-Phase Rule

- **Phase 1: Research.** Dispatch `find-docs` and/or web search queries (`WebSearch` in Claude Code, `web_search` in Codex).
- **Phase 2: Synthesize and act.** Starts only after Phase 1 results arrive.

The user's argument may be a question or an imperative. Imperatives ("refine X", "set up Y") determine what Phase 2 does, not whether Phase 1 happens. Phase 1 always runs.

## Workflow

1. Break the topic into 2-4 specific queries. Dedicate at least one query to pitfalls ("common mistakes with X", "X gotchas in production"): pitfalls live in issue threads, migration guides, and post-mortems, not in getting-started docs. For design prior-art, dedicate queries to how existing open source projects implement it. For single-library lookups, call `find-docs` or web search directly without subagents.
2. Dispatch one subagent per query in a single message, passing `model: sonnet` on each Agent call. Tell each subagent to use `find-docs` and web search, and to report in under 400 words: the recommended approach, concrete code/config examples, and every pitfall it found with its consequence, including minor or uncertain ones (its job is coverage; you rank and filter), with each claim citing its source and publication date.
3. Present the recommended approach, key patterns, and gotchas covering every recommendation (not just the primary one), each claim keeping its source citation.
