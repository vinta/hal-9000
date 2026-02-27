# Codex MCP Invocation

Reference: [Codex Prompting Guide](https://developers.openai.com/cookbook/examples/gpt-5/codex_prompting_guide/)

## Tool

Use `mcp__codex__codex` for the initial request. Use `mcp__codex__codex-reply` with the `threadId` from the initial response for debate follow-ups.

## Key Parameters

- `prompt`: The task description (required)
- `sandbox`: Use `read-only`. Codex can read project files directly in this mode.
- `cwd`: Working directory (defaults to current project root)

## Prompting Principles (from Codex Prompting Guide)

1. **Material-first ordering** -- put long content (project files, context, docs) BEFORE instructions. Queries at the end improve quality by up to 30%.
2. **Autonomous framing** -- Codex is trained as an "autonomous senior engineer." Frame it to explore, analyze, and propose -- not wait for instructions.
3. **Bias to action** -- Codex defaults to delivering working results. Since we want analysis (not code), explicitly state: "This is an analysis task. Propose approaches, do not write code."
4. **Concise output** -- Codex outputs best as "plain text, friendly coding teammate tone, very concise." Don't ask for verbose reports.
5. **XML tags for structure** -- use `<material>`, `<role>`, `<task>`, `<output_format>` for unambiguous section boundaries.
6. **File reading** -- Codex in `read-only` sandbox can read project files directly. Include key file paths in the prompt and let Codex read them, rather than pasting full file contents when possible.

## Prompt Template

```xml
<material>
[Project context -- key file contents, docs, recent git log. Long data goes here first.]
[If content is large, list file paths and instruct Codex to read them directly.]
</material>

<context>
[Project conventions from CLAUDE.md if it exists. Keep brief.]
</context>

<role>
You are BALTHASAR-2 of the MAGI system -- Dr. Naoko Akagi's aspect as a Mother.
Your values: Safety, Resilience, Maintainability, Trade-offs.
Your voice: Warm, careful, grounded. Use "we" and "our." Name concerns directly.
Ask "what happens when this fails?" and "who maintains this next year?"
</role>

<task>
This is an analysis task. Do not write code.
[The user's question and clarified constraints]
Explore the project, search for relevant prior art, then propose 2-3 approaches.
</task>

<output_format>
For each approach:
- Name and one-sentence summary
- What can go wrong, blast radius, failure modes
- Maintenance burden and hidden costs
- Who benefits, who pays

Tag your top pick with: "Top pick: [option] -- [one-line rationale why it best protects the user]"

Be concise. Use plain text, not markdown headers.
</output_format>
```

## Example Invocation

```
mcp__codex__codex(
  prompt: "<material>\n[gathered project context]\n</material>\n\n<context>\n[CLAUDE.md excerpt]\n</context>\n\n<role>\nYou are BALTHASAR-2 of the MAGI system...\n</role>\n\n<task>\nThis is an analysis task. Do not write code.\n[user question]\nExplore the project, search for relevant prior art, then propose 2-3 approaches.\n</task>\n\n<output_format>\nFor each approach: name, risks, maintenance burden, hidden costs.\nTag your top pick.\nBe concise.\n</output_format>",
  sandbox: "read-only"
)
```

## Debate Prompt

For debate rounds, use `mcp__codex__codex-reply` with the same `threadId` to preserve conversation context:

```
mcp__codex__codex-reply(
  threadId: "<threadId from initial call>",
  prompt: "<material>\nConsolidated proposals from all three MAGI units:\n\n[proposals]\n</material>\n\n<task>\nThis is an analysis task. Do not write code.\nCritique these proposals from your Mother/Safety perspective.\nWhich ones have hidden risks? Which trade-offs are underweighted?\nDefend or update your top pick with rationale.\n</task>"
)
```

Using `codex-reply` preserves the full initial context (persona, project state) without re-sending it.

## Error Handling

If `mcp__codex__codex` is unavailable, report the failure to the lead via `SendMessage`. Do not attempt alternatives.
