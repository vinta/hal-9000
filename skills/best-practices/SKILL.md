---
name: best-practices
description: Use when about to choose, configure, or refine a tool, library, config format, API pattern, or project setup, or before proposing a design or fix of your own — research current guidance, pitfalls, and prior art for the problem it solves first; already knowing an approach, or assuming no prior art exists, is not an exemption. Also use when the user asks about best practices, gotchas, or recommended patterns
argument-hint: "[problem, tool, library, or pattern to research]"
---

# Best Practices

Answer two questions from current sources: **what's the recommended way**, and **what bites people** (the gotchas and pitfalls around it). A how-to without its pitfalls is half an answer.

## Two-Phase Rule

- **Phase 1: Research.** Dispatch `find-docs` and/or web search queries (`WebSearch` in Claude Code, `web_search` in Codex).
- **Phase 2: Synthesize and act.** Starts only after Phase 1 results arrive.

The user's argument may be a question or an imperative. Imperatives ("refine X", "set up Y") determine what Phase 2 does, not whether Phase 1 happens. Phase 1 always runs.

## Workflow

1. Size the topic.
   - **Narrow** (one tool or library, and a question its docs or issue tracker can settle): research it yourself with `find-docs` and web search, sending independent lookups in one message, at least one of them for pitfalls, and read the page behind each claim, not only its search snippet. Then go to step 3.
   - **Broad** (a choice between approaches, a setup spanning several tools, a design of your own): break it into 2-4 queries that don't overlap. Dedicate at least one query to pitfalls ("common mistakes with X", "X gotchas in production"): pitfalls live in issue threads, migration guides, and post-mortems, not in getting-started docs. Dedicate one query to how leading open source projects or production teams do it, which can differ from what the docs recommend.
2. Dispatch one subagent per query in a single message: in Claude Code, pass `model: sonnet` on each Agent call; in Codex, spawn them in one request, selecting a faster model in each spawn. Open each brief with the user's situation and constraints, so the findings fit their setup, and name what the other subagents cover, so none repeats it. Tell each subagent to use `find-docs` and web search, to settle questions about a tool, package, or script by reading it, to run one only when reading can't and only sandboxed (pass along the sandbox command your instructions name), to stop at about 15 tool calls, or sooner once new results repeat what it has, and to report in under 400 words: the recommended approach, concrete code/config examples, and every pitfall it found with its consequence, including minor or uncertain ones (its job is coverage; you rank and filter), with each claim citing its source and publication date.
3. Present the recommended approach, key patterns, and gotchas covering every recommendation (not just the primary one), each claim keeping its source citation.
