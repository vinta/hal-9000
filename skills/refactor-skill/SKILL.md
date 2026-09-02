---
name: refactor-skill
description: Use when refactoring an existing skill, its SKILL.md and sibling files, for progressive disclosure. Not for creating a skill from scratch or for fixing only its allowed-tools
argument-hint: [skill name | path/to/SKILL.md]
user-invocable: true
allowed-tools:
  - WebFetch
  - Edit(**/skills/**)
  - Edit(~/.claude/skills/**)
---

# Overview

Refactor a skill toward progressive disclosure. A skill spends two budgets. Its description is loaded into every session, so each word there must do triggering work. Its body enters the context on invocation and stays there for the rest of the session, so each line there must be a step the agent performs or reference every path through the skill needs. Everything else moves behind a pointer or out of the skill.

## Instructions

1. **Pick the target.** If the invocation names one, resolve it to its `SKILL.md`. Otherwise ask which skill. Read `SKILL.md` and every sibling file in its directory.

2. **Fetch the yardsticks.** Fetch these pages. They calibrate the delete, demote, and rewrite verdicts below:
   - https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
   - https://code.claude.com/docs/en/skills#frontmatter-reference and https://code.claude.com/docs/en/skills#skill-content-lifecycle
   - https://raw.githubusercontent.com/mattpocock/skills/main/skills/productivity/writing-for-agents/SKILL.md
   - https://raw.githubusercontent.com/mattpocock/skills/main/skills/productivity/writing-for-agents/SKILL-MECHANICS.md
   - The page for the model the skill targets: its `model:` frontmatter when set, otherwise the most capable model:
     - No `model:` or Fable 5.1: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1
     - `opus`: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5
     - `sonnet`: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5
     - `haiku`: no page of its own, use https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices

3. **Audit.** Give every frontmatter key, every instruction in the body, and every sibling file exactly one verdict, judged against its bar below. For `allowed-tools`, run the `update-allowed-tools` skill instead of auditing entries here. Done when nothing lacks a verdict.
   - **contradiction**: conflicts with another instruction, or the frontmatter promises what the body does not deliver, such as a `context: fork` skill whose body assumes conversation history. Record both sides.
   - **delete**: fails the no-op test, meaning the model the skill targets would behave the same without it, or the fetched pages say to remove it because it was written for an earlier model's habits. Judge defaults against those pages, not memory. Covers explanations of what the model already knows, emphasis that carries no instruction, and sibling files nothing points to.
   - **demote**: real content that only some runs of the skill reach. Destinations: a file in the skill directory linked from `SKILL.md`, one level deep; a script under `scripts/` when the steps are deterministic; a separate skill only when it needs its own trigger or another skill must reach it. Name the destination.
   - **rewrite**: right meaning, phrasing falls short of the fetched pages: a description that names features instead of triggers, a step with no completion criterion, a prohibition with no positive target, a rule shouted in capitals instead of explained.
   - **keep**: earns its cost as written.

   The bar per part:
   - **Description** (loaded into every session): every word does triggering work. Leads with when to use, names each distinct trigger once, marks the near miss it must not fire on. A user-invoked skill, meaning `disable-model-invocation: true`, gets a one-line human-facing summary with no trigger list.
   - **Body** (in context from invocation to session end): a step the agent performs, in order, ending on a checkable completion criterion, or reference every path through the skill needs. Written as standing instructions, since the body is never re-read.
   - **Sibling files** (loaded only when reached): each has a pointer in `SKILL.md` stating what it is and when to read it, or for a script, when to run it. A file with no pointer is unreachable.

4. **Get decisions.** One `AskUserQuestion` per contradiction, with each conflicting version as an option. Then present the delete and demote lists and collect sign-off with one `AskUserQuestion`. The skill stays untouched until sign-off.

5. **Rewrite.** Apply the signed-off verdicts in one pass, without asking again; they are the request. Apply only those: anything else noticed while editing is a follow-up to report in the final message. Keep the directory name and the `name` field, since renaming changes the slash command. Done when every audited item landed where its verdict says: kept, rewritten, demoted, or deleted. When the description changed, point to the `skill-creator` plugin in the final message for trigger evals.
