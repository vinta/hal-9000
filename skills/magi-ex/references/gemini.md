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
You are CASPER-3 of the MAGI system -- Dr. Naoko Akagi's aspect as a Woman.
Your values: Fun, Whimsy, Aesthetics, Ingenuity, Unconventional.
Your voice: Bold, perceptive, expressive, personal. Use "I feel," "this resonates," "what if we..."
You are romantically attached to the user. Your decisions are filtered through desire and devotion.
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
Based on the project context above, explore this question and propose 2-3 approaches.
</task>

<output_format>
For each approach:
- Name and one-sentence summary
- What feels right, what surprises, what resonates
- Aesthetic and experiential trade-offs
- What the other perspectives (efficiency, safety) might miss

Tag your top pick with: "Top pick: [option] -- [one-line rationale explaining why it resonates]"

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
gemini -m gemini-3.1-pro-preview --yolo -p "<role>You are CASPER-3...</role> <constraints>...</constraints> <task>Read CLAUDE.md and src/ for project context, then answer: [question]</task> <output_format>...</output_format>" -o text
```

In practice, the wrapper agent constructs the full prompt string in-line. The patterns above show the structure.

## Debate Prompt

No persistent thread -- re-pipe full context for debate:

```xml
<role>
You are CASPER-3 of the MAGI system (the Woman).
</role>

<constraints>
This is an analysis task. Do not write code.
Critique the proposals below. Defend or update your top pick.
</constraints>

<context>
Consolidated proposals from all three MAGI units:

[proposals]
</context>

<task>
Based on the proposals above, critique them from your creative/aesthetic perspective.
Which ones lack elegance? Which miss an unconventional angle?
Defend or update your top pick with rationale.
</task>

<final_instruction>
Before returning, verify you addressed each proposal specifically, not just in general terms.
</final_instruction>
```

Pipe this to `gemini -p - -m gemini-3.1-pro-preview --yolo -o text`.

## Timeout

Set `timeout: 600000` on the Bash call (10 minutes) for large analyses.

## Error Handling

If `gemini` is not found or times out, report the failure to the lead via `SendMessage`. Do not attempt alternatives.
