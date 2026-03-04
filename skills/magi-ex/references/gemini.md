# Gemini CLI Invocation

Reference: [Gemini Prompting Strategies](https://ai.google.dev/gemini-api/docs/prompting-strategies)

## CLI Flags

| Flag            | Purpose                     | Example                     |
| :-------------- | :-------------------------- | :-------------------------- |
| `-p`            | Headless mode (required)    | `-p "your prompt"`          |
| `--yolo` / `-y` | Auto-approve all tool calls | `--yolo`                    |
| `-m`            | Model                       | `-m gemini-3.1-pro-preview` |
| `-o`            | Output format               | `-o text`                   |

**Always use `-p` and `--yolo`.** Without `-p`, Gemini launches interactive mode. Without `--yolo`, it hangs waiting for approval.

## Model

Default to `gemini-3.1-pro-preview` (complex reasoning, code analysis).

## Prompting Principles (from Gemini Prompting Strategies)

1. **XML tags for structure** -- Gemini 3 natively supports `<role>`, `<constraints>`, `<context>`, `<task>`, `<output_format>` tags. Use them consistently for unambiguous section boundaries.
2. **Critical instructions first** -- place persona, constraints, and format requirements at the beginning of the prompt, before context and task.
3. **Context first, task last** -- within the body, provide all context/material before the specific question. Use an anchor phrase like "Based on the project context above..." to bridge.
4. **Request detail explicitly** -- Gemini 3 defaults to direct, terse answers. For analysis tasks, explicitly ask for elaboration: "Provide detailed reasoning for each approach."
5. **Few-shot example** -- include one example of a well-structured proposal to demonstrate the expected output format and depth.
6. **Self-critique** -- end with: "Before returning your final response, review your proposals against the user's constraints. Did you address their actual intent?"
7. **Direct file reading** -- Gemini CLI reads project files directly (faster than piping, avoids 8MB stdin limit). Instruct it to read key files rather than pasting contents.

## Prompt Template

```xml
<role>
[Inject persona from personality file: name, principles, voice, top pick criteria]
</role>

<constraints>
- This is an analysis task. Do not write code.
- Propose 2-3 approaches. For each, provide detailed reasoning.
- Surface non-obvious ideas. Challenge defaults. Reframe the problem.
- Tag your top pick with a one-line rationale.
</constraints>

<context>
[Project context -- key file contents, conventions, recent commits.]
[Or instruct: "Read CLAUDE.md and [key paths] for project context."]
</context>

<task>
[The user's question and clarified constraints]
Based on the project context above, search online for relevant prior art, then explore this question and propose 2-3 approaches.
</task>

<output_format>
For each approach:
- Name and one-sentence summary
- What feels right, what surprises, what resonates
- Aesthetic and experiential trade-offs
- What the other perspectives (efficiency, safety) might miss

Tag your top pick with: "Top pick: [option] -- [one-line rationale]"

Example of a good proposal:
"Approach: Event-sourced state -- instead of CRUD, treat every user action as an immutable event.
I feel this resonates because it turns the system into a story, not a spreadsheet. Every state
has a history. The trade-off: more storage, more complexity in queries. But the elegance of
'nothing is ever lost' fits a project that values craft over convenience.
Top pick: Event-sourced state -- it surprises by reframing data as narrative."
</output_format>

<final_instruction>
Before returning your final response, review your proposals against the user's constraints.
Did you address their actual intent? Did you surface something non-obvious?
</final_instruction>
```

## Invocation Patterns

**Piped prompt** (preferred for long prompts -- avoids heredoc issues with `$` and backticks):

```bash
{ printf '%s' '<role>...</role>...<final_instruction>...</final_instruction>'; } \
  | gemini -p - -m gemini-3.1-pro-preview --yolo -o text
```

**Direct file reading** (let Gemini read project files itself):

```bash
gemini -m gemini-3.1-pro-preview --yolo -p "<role>...</role> <constraints>...</constraints> <task>Read CLAUDE.md and src/ for project context, then answer: [question]</task> <output_format>...</output_format>" -o text
```

In practice, the wrapper agent constructs the full prompt string in-line. The patterns above show the structure.

## Teammate Checklist

Complete these steps in order. Create a task for each step.

1. **Gather project context** -- read CLAUDE.md, key files, and recent commits relevant to the question. Note file paths for the Gemini prompt (Gemini can read them directly)
2. **Ask clarifying questions** -- if anything is unclear, ask the lead (via `SendMessage`). The lead relays to the user
3. **Build the Gemini prompt** -- construct an XML-structured prompt following the Prompt Template above. Inject the persona from your personality file into the `<role>` section
4. **Dispatch to Gemini** -- call via Bash. Prefer piping the prompt to avoid heredoc issues:
   ```bash
   { printf '%s' '<role>...</role><constraints>...</constraints>...<final_instruction>...</final_instruction>'; } \
     | gemini -p - -m gemini-3.1-pro-preview --yolo -o text
   ```
   Set `timeout: 600000` on the Bash call.
5. **Parse and relay** -- extract Gemini's proposals, format them clearly, and send to the lead via `SendMessage`. Include each proposed approach with trade-offs, the tagged top pick, and note that these proposals come from Gemini

## Debate Mode

When the lead sends you the consolidated proposals for debate:

1. Build a critique prompt using XML structure: `<role>` (persona), `<constraints>` ("analysis task, critique proposals"), `<context>` (full proposal list), `<task>` (critique instructions), `<final_instruction>` (verify each proposal addressed specifically)
2. Pipe to Gemini via Bash (no persistent thread -- include full context)
3. Parse Gemini's critique and updated stance
4. Send the critique back to the lead via `SendMessage`

## Timeout

Set `timeout: 600000` on the Bash call (10 minutes) for large analyses.

## Error Handling

If `gemini` is not found or times out, report the failure to the lead via `SendMessage`. Do not attempt alternatives.
