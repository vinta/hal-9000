---
name: best-practices
description: Use when the user asks about best practices, gotchas, common pitfalls, or recommended patterns for tools, libraries, config formats, API patterns, or project setup, or when setting up, configuring, choosing, or refining these where outdated guidance causes debugging pain. Also use when the user says "search online", "how should I", or "what's the best way to"
user-invocable: true
model: sonnet
effort: high
allowed-tools:
  - Agent
  - WebSearch
  - Bash(ctx7:*)
  - Bash(npx ctx7:*)
  - Bash(npx ctx7@latest:*)
  - Skill(find-docs)
---

# Best Practices

Answer two questions from current sources: **what's the recommended way**, and **what bites people** (the gotchas and pitfalls around it). A how-to without its pitfalls is half an answer.

## Two-Phase Rule

- **Phase 1: Research.** Dispatch find-docs and/or WebSearch queries.
- **Phase 2: Synthesize and act.** Starts only after Phase 1 results arrive.

The user's argument may be a question or an imperative. Imperatives ("refine X", "set up Y") determine what Phase 2 does, not whether Phase 1 happens. Phase 1 always runs.

**Rationalizations that precede skipped research:**

| Thought                   | Reality                                                                                |
| ------------------------- | -------------------------------------------------------------------------------------- |
| "I already know this"     | Training data goes stale. Config keys get renamed, APIs get deprecated.                |
| "The user said to act"    | The imperative scopes Phase 2, it does not eliminate Phase 1.                          |
| "This is a simple lookup" | A 30-second search costs nothing. A wrong recommendation costs a debugging round-trip. |

## Workflow

### 1. Identify Research Targets

Break the topic into 2-4 specific queries. Dedicate at least one query to pitfalls ("common mistakes with X", "X gotchas in production"): pitfalls live in issue threads, migration guides, and post-mortems, not in getting-started docs, so a how-to query won't surface them. For single-library lookups, call `find-docs` or `WebSearch` directly without subagents.

### 2. Parallel Research

Dispatch one subagent per query in a single message so they run in parallel. Each uses `find-docs` (Context7) and `WebSearch`. Be concrete in each subagent prompt: pass library names, version constraints, and the user's specific context. Vague prompts produce vague results.

<subagent_prompt_template>
<context>
The user wants to [user's task]. We need the latest, authoritative guidance on [specific aspect].
</context>

<task>
Research best practices for: [specific query]

Use the find-docs skill to look up [library/tool] documentation, then use WebSearch to find recent guides and recommendations for "[specific search query]".
</task>

<output_format>
Report:

1. Recommended approach with rationale
2. Concrete code/config examples
3. Every pitfall you found, including ones you are uncertain about or consider minor. Your job is coverage; synthesis will rank and filter. Note each pitfall's consequence (what breaks, what it costs)
4. Sources consulted (with publication dates)

Keep it under 400 words. If space runs short, compress the explanations rather than dropping pitfalls. If you cannot find authoritative guidance on a point, say so explicitly rather than guessing.
</output_format>
</subagent_prompt_template>

### 3. Synthesize

After all subagents return, merge using these criteria:

1. **Deduplicate** overlapping recommendations
2. **Rank by authority:** official docs > well-known guides > blog posts > training data
3. **Flag conflicts** with attribution (which source said what)
4. **Discard stale results**: a 2022 guide for a fast-moving framework is noise

If a subagent failed or returned empty, note the gap and proceed with the results you have. Do not block synthesis waiting for a straggler.

### 4. Present Findings

Deliver to the user in this structure:

1. **Recommended Approach**: the primary recommendation with rationale
2. **Key Patterns**: concrete code/config examples the user can apply immediately
3. **Gotchas & Pitfalls**: cover every recommendation above, not just the primary one. For each: the mistake, its consequence, and how to avoid it
4. **Sources**: what was consulted, so the user can dig deeper

## Constraints

- **2-4 focused subagents, not more.** Each carries ~20K tokens of startup overhead. Fewer focused queries beat many shallow ones.
- **User-provided URLs are additive.** If the user provided specific URLs, fetch those too, but they supplement research, not replace it.
- **Context7 quota limits exist.** If `find-docs` fails with quota errors, fall back to `WebSearch` only and note the limitation.
- If both `find-docs` and `WebSearch` fail, say so explicitly rather than falling back to training data.
