---
name: best-practices
description: Use when asking "how should I", "what's the recommended way to", "which library for", or needing current best practices on config formats, API patterns, library selection, or tool setup where outdated guidance causes debugging pain
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

Research the latest best practices for any task by searching documentation and the web in parallel, then synthesize into actionable guidance.

<HARD-GATE>
Do NOT synthesize, present recommendations, or edit any file until at least one research query (find-docs or WebSearch) has returned results. Training data is not a substitute for live research. This applies to EVERY invocation regardless of how confident you feel about the topic.
</HARD-GATE>

## Anti-Pattern: "I Already Know This"

The most common failure mode is skipping research because you feel confident. You have broad training data, so the topic feels familiar, and you jump straight to presenting recommendations. This defeats the entire purpose of the skill. Training data goes stale. Config keys get renamed, APIs get deprecated, conventions shift between releases. A 30-second lookup costs nothing. A confident-but-wrong recommendation costs the user a debugging round-trip.

Even if another skill (like writing-skills) provided relevant context in this conversation, that context is not a replacement for searching current sources on the specific topic.

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

### 3. Synthesize

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
