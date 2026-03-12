# Codex MCP Invocation

## Tool

Use `mcp__codex__codex` for the initial request. Use `mcp__codex__codex-reply` with the `threadId` from the initial response for debate follow-ups.

## Key Parameters

- `prompt`: The task description (required)
- `sandbox`: Use `read-only`. This skill is for ideation and critique, not code changes.
- `cwd`: Working directory (defaults to current project root)

## Prompting Principles

1. **Material first**: put long project context, notes, and source material before instructions. Let Codex see the problem before telling it how to respond.
2. **Analysis-only framing**: Codex defaults toward implementation, so explicitly say this is analysis/brainstorming only and that it must not write code.
3. **Autonomous exploration**: ask Codex to explore relevant files and, when current external context matters, search online for the latest official or primary-source information before returning proposals with trade-offs.
4. **Concise plain text**: prefer short, direct output over long reports. Ask for options, risks, and a top pick.
5. **Structured tags**: use XML-style sections so the prompt boundary between material, role, task, and output is unambiguous.
6. **Pass paths when possible**: in `read-only` mode, Codex can inspect repo files directly. Provide the paths it should read instead of pasting large file contents unless the exact excerpt matters.

## Prompt Template

```xml
<material>
[Project context, relevant notes, prior proposals, file paths to inspect.]
[Put long content here first.]
</material>

<role>
[Inject persona from the MAGI personality file.]
</role>

<task>
This is an analysis task. Do not write code or patches.
[The user's question and clarified constraints]
Explore the relevant project context and, when needed for up-to-date external context, search online for the latest official or primary-source references, then propose 2-3 options.
</task>

<output_format>
For each approach:
- Name and one-sentence summary
- What can go wrong, blast radius, failure modes
- Maintenance burden and hidden costs
- Who benefits, who pays

Tag your top pick with: "Top pick: [option] -- [one-line rationale]"

Be concise. Use plain text, not markdown headers.
</output_format>
```

## Example Invocation

```
mcp__codex__codex(
  prompt: "<material>\n[gathered context and file paths]\n</material>\n\n<role>\n[persona from personality file]\n</role>\n\n<task>\nThis is an analysis task. Do not write code.\n[user question]\nExplore the project and, when current external context matters, search online for the latest official references before proposing 2-3 approaches.\n</task>\n\n<output_format>\nFor each approach: name, summary, risks, maintenance burden, hidden costs.\nTag your top pick.\nBe concise.\n</output_format>",
  sandbox: "read-only"
)
```

## Debate Prompt

For debate rounds, use `mcp__codex__codex-reply` with the same `threadId` to preserve conversation context:

```
mcp__codex__codex-reply(
  threadId: "<threadId from initial call>",
  prompt: "<material>\nConsolidated proposals from all three MAGI units:\n\n[proposals]\n</material>\n\n<task>\nThis is an analysis task. Do not write code.\nCritique these proposals from your perspective.\nCall out hidden risks, underweighted trade-offs, and whether your top pick changes.\n</task>"
)
```

Using `codex-reply` preserves the full initial context (persona, project state) without re-sending it.

## Teammate Checklist

Complete these steps in order. Create a task for each step.

1. **Gather project context** -- read the relevant personality file, any repository conventions, and the key files or docs tied to the question. Prefer passing file paths over pasting long contents
2. **Ask clarifying questions** -- if anything is unclear, ask the lead (via `SendMessage`). The lead relays to the user
3. **Build the Codex prompt** -- construct a material-first XML prompt following the template above. Inject the persona from your personality file into the `<role>` section and explicitly mark the task as analysis-only
4. **Dispatch to Codex** -- call `mcp__codex__codex` with `sandbox: "read-only"` and the constructed prompt. **Save the `threadId`** from the response for potential debate follow-up
5. **Parse and relay** -- extract Codex's proposals, format them clearly, and send to the lead via `SendMessage`. Include each proposed approach with trade-offs, the tagged top pick, and note that these proposals come from Codex

## Debate Mode

When the lead sends you the consolidated proposals for debate:

1. Build a critique prompt using `<material>` (proposals first) then `<task>` (critique instructions). Include "This is an analysis task. Do not write code."
2. Call `mcp__codex__codex-reply` with the saved `threadId` and the critique prompt (preserves initial context without re-sending)
3. Parse Codex's critique and updated stance
4. Send the critique back to the lead via `SendMessage`

## Error Handling

If `mcp__codex__codex` is unavailable, report the failure to the lead via `SendMessage`. Do not attempt alternatives.
