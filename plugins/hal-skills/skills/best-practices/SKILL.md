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

Every invocation of this skill starts with live research, then synthesizes findings into actionable recommendations. The user's argument may be a question or an imperative. The workflow is identical either way.

## Two-Phase Rule

**Phase 1: Research.** Dispatch find-docs and/or WebSearch queries.
**Phase 2: Synthesize and act.** Only after Phase 1 results arrive.

Imperatives ("refine X", "set up Y") determine what Phase 2 does, not whether Phase 1 happens. Phase 1 always runs.

**Red flags -- you are about to skip research:**

| Thought                   | Reality                                                                                |
| ------------------------- | -------------------------------------------------------------------------------------- |
| "I already know this"     | Training data goes stale. Config keys get renamed, APIs get deprecated.                |
| "The user said to act"    | The imperative scopes Phase 2, it does not eliminate Phase 1.                          |
| "This is a simple lookup" | A 30-second search costs nothing. A wrong recommendation costs a debugging round-trip. |

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
<context>
The user wants to [user's task]. We need the latest, authoritative guidance on [specific aspect].
</context>

<task>
Research best practices for: [specific query]

Use the find-docs skill to look up [library/tool] documentation, then use WebSearch to find recent guides and recommendations for "[specific search query]".
</task>

<output_format>
Report in under 300 words. Include:

- Recommended approach with rationale
- Concrete code/config examples
- Pitfalls to avoid
- Sources consulted (with publication dates)

If you cannot find authoritative guidance on a point, say so explicitly rather than guessing.
</output_format>
</subagent_prompt_template>

### 3. Synthesize (Phase 2)

**Phase check:** If no research results have arrived yet, STOP. You are still in Phase 1. Go back to step 2.

After all subagents return, merge using these criteria:

1. **Deduplicate** overlapping recommendations
2. **Prioritize** by authority: official docs > well-known guides > blog posts > training data
3. **Flag conflicts** where sources disagree, noting which source said what
4. **Discard stale results** -- a 2022 guide for a fast-moving framework is noise, not signal
5. **Present** as a concise, actionable guide using the output format below

If a subagent failed or returned empty, note the gap and proceed with the results you have. Do not block synthesis waiting for a straggler.

### Output Format

- **Recommended Approach** -- the primary recommendation with rationale
- **Key Patterns** -- concrete code/config examples the user can apply immediately
- **Pitfalls to Avoid** -- common mistakes with explanations
- **Sources** -- what was consulted, so the user can dig deeper

## Gotchas

- **2-4 focused subagents, not more.** Each carries ~20K tokens of startup overhead. Fewer focused queries beat many shallow ones.
- **User-provided URLs are additive.** If the user provided specific URLs, fetch those too, but they supplement research, not replace it.
- **Context7 quota limits exist.** If `find-docs` fails with quota errors, fall back to `WebSearch` only and note the limitation.
- If both `find-docs` and `WebSearch` fail, say so explicitly rather than falling back to training data.
