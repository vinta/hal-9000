---
name: best-practices
description: Use when setting up, configuring, choosing, refining, or asking about best practices for tools, libraries, config formats, API patterns, or project setup where outdated guidance causes debugging pain. Also use when the user says "search online", "how should I", or "what's the best way to"
user-invocable: true
model: opus
allowed-tools:
  - Agent
  - WebSearch
  - Bash(ctx7:*)
  - Bash(npx ctx7:*)
  - Bash(npx ctx7@latest:*)
  - Skill(find-docs)
---

# Best Practices

Before acting on any task, verify you have current guidance. Every invocation of this skill starts with live research, then synthesizes findings into actionable recommendations. The user's argument may be a question or an imperative command. The workflow is identical either way.

## Phases

This skill runs in two phases. Phase 2 cannot start until Phase 1 returns results. Acting on stale training data produces wrong output that costs the user a debugging round-trip.

**Phase 1: Research.** Dispatch find-docs and/or WebSearch queries.
**Phase 2: Synthesize and act.** Only after Phase 1 results arrive.

If the user's argument is an imperative ("refine X", "set up Y"), Phase 1 still runs. The imperative determines what Phase 2 does, not whether Phase 1 happens.

## Anti-Pattern: Skipping Research

The most common failure mode is skipping research because you feel confident or because the user gave an imperative command. Training data goes stale. Config keys get renamed, APIs get deprecated, conventions shift between releases. A 30-second lookup costs nothing. A confident-but-wrong recommendation costs the user a debugging round-trip.

This applies equally to:

- **"I already know this"** -- the topic feels familiar, so you jump straight to recommendations
- **"The user said to act"** -- the argument is imperative ("refine X"), so you enter an execution frame and treat research as overhead

Both lead to the same outcome: acting on potentially stale information. Neither is a valid reason to skip Phase 1.

## Workflow

### 1. Identify Research Targets

Extract the research topic and break it into 2-4 specific research queries targeting distinct aspects:

- **Libraries/frameworks** (e.g., "React Router v7 authentication patterns")
- **Techniques/patterns** (e.g., "database connection pooling best practices")
- **Configuration/setup** (e.g., "ESLint flat config recommended rules 2025")
- **Common pitfalls** (e.g., "Next.js middleware common mistakes")

For single-library lookups, skip subagents and call `find-docs` or `WebSearch` directly.

### 2. Parallel Research

Dispatch one subagent per query, all in a single message. Each subagent uses both `find-docs` (library docs via Context7) and `WebSearch` (recent guides and community recommendations).

Be concrete in each subagent prompt: pass library names, version constraints, and the user's specific context. Vague prompts produce vague results.

<subagent_prompt_template>
Research best practices for: [specific query]

The user wants to [user's task]. Find current, authoritative guidance on [specific aspect].

Use the find-docs skill to look up [library/tool] documentation, then use WebSearch
to find recent guides and recommendations for "[specific search query]".

Report in under 300 words with concrete code/config examples. Include:

- Recommended approach with rationale
- Key patterns or configuration
- Pitfalls to avoid
- Sources consulted with dates
  </subagent_prompt_template>

### 3. Synthesize (Phase 2)

**Phase check:** If no research results have arrived yet, STOP. You are still in Phase 1. Go back to step 2.

After all subagents return:

1. **Deduplicate** overlapping recommendations
2. **Prioritize** by authority: official docs > well-known guides > blog posts > training data
3. **Flag conflicts** where sources disagree, noting which source said what
4. **Present** as a concise, actionable guide

### Output Format

Structure your response with these sections:

- **Recommended Approach** -- the primary recommendation with rationale
- **Key Patterns** -- concrete code/config examples the user can apply immediately
- **Pitfalls to Avoid** -- common mistakes with explanations
- **Sources** -- what was consulted, so the user can dig deeper

## Gotchas

- **Do not skip the search.** The whole point is finding current guidance, not answering from training data. If the user provided specific URLs, fetch those too, but they are additional sources, not replacements for research.
- **2-4 focused subagents, not more.** Each carries ~20K tokens of startup overhead. Fewer focused queries beat many shallow ones.
- **Context7 quota limits exist.** If `find-docs` fails with quota errors, fall back to `WebSearch` only and note the limitation.
- **Date matters.** Note publication dates in web results. A 2022 guide for a fast-moving framework may be outdated.
- If both `find-docs` and `WebSearch` fail, say so explicitly.
