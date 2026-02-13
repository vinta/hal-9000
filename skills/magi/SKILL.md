---
name: magi
description: Use when facing decisions with genuine trade-offs, brainstorming under competing constraints, debugging with multiple plausible root causes, architecture choices between viable alternatives, or evaluating options where no single concern dominates
argument-hint: "[question-or-topic]"
user-invocable: true
model: opus
allowed-tools:
  - AskUserQuestion
  - TeamCreate
  - TeamDelete
  - Task
  - TaskCreate
  - TaskUpdate
  - TaskList
  - TaskGet
  - SendMessage
  - WebSearch
  - Bash(mkdir:*)
  - Read
  - Write
  - Edit
---

# MAGI

## Overview

MAGI is a three-agent decision workflow inspired by Neon Genesis Evangelion. It is for cases where trade-offs are real and one viewpoint should not dominate.

Core concept:

- `scientist` argues from evidence and measurable outcomes.
- `mother` argues from risk, reversibility, and long-term stability.
- `woman` argues from desire, product taste, and decisive commitment.

Default flow:

1. Analysis (independent lens outputs)
2. Debate (peer-to-peer critique)
3. Vote (unanimous, majority, or deadlock)
4. Synthesis (clear recommendation + dissent)

### Non-Negotiables

- Always run all three personas.
- Keep personas in-lens during Analysis. Do not force early compromise.
- Debate must be direct agent-to-agent via `SendMessage`.
- Always run a formal vote, even when consensus looks obvious.
- Always write both logs in `docs/magi/`.

## When NOT to Use

- Single-answer factual lookups.
- Simple implementation with no meaningful trade-off.
- Cases where the user already decided and only wants execution.

## Perspectives

| Unit          | Mode                                                     | Core Question                                                  |
| ------------- | -------------------------------------------------------- | -------------------------------------------------------------- |
| **Scientist** | Analytical - evidence, experiments, measurement          | What does the evidence say?                                    |
| **Mother**    | Protective - risk, reversibility, long-term stability    | What could go wrong? Do we even need to act?                   |
| **Woman**     | Attachment-driven pragmatism - desire, taste, commitment | What do we want enough to defend, and what will we pay for it? |

Domain mapping and detailed prompt instructions live in `templates/agent-prompt-template.md`.

## Input Handling

- If the user is open-ended, agents generate options from scratch.
- If the user supplies options (for example, `A vs B`), agents must evaluate those options and add alternatives from their own lens.

## Workflow

### 1) Analysis

Goal: generate distinct recommendations from each lens before convergence.

1. Start from user request: $ARGUMENTS.
2. Create agent team `magi` with `scientist`, `mother`, `woman`.
3. Launch one Analysis task per agent using `templates/agent-prompt-template.md`.
4. Give each agent:
   - user prompt
   - user-provided options (if any)
   - relevant local context (docs/paths/constraints)
5. Consolidate outputs into:
   - a short opportunity backlog
   - a draft option set for decision
   - an initial evaluation criteria set
6. Ask user for missing framing only when needed:
   - objective
   - constraints
   - success criteria
7. Write discovery artifact:
   - `docs/magi/YYYY-MM-DD-<topic>-discovery.md`

Analysis quality bar:

- Each agent should propose multiple options from its own lens.
- Include at least one contrarian or wildcard option overall.
- Keep options meaningfully distinct (not minor variants).

### 2) Build Decision Packet

Before debate, create a compact packet all agents can challenge.

Required sections:

- `Decision Statement`
- `Options` (at least 3)
- `Constraints`
- `Evaluation Criteria`
- `Unknowns`
- `Non-Goals`
- `Context Links`

If packet is unclear, refine once with the user and proceed.

### 3) Debate (Peer-to-Peer)

1. Share the packet and all Analysis outputs with each agent.
2. Agents critique peers directly with `SendMessage`.
3. Run 1-2 rounds per pair, then stop.
4. Lead only enforces structure and timebox; agents own the argument content.

### 4) Vote and Synthesize

1. Ask each agent for final vote (`AGREE`, `CONDITIONAL`, `DISAGREE`) plus flip condition.
2. Tally result:
   - `3/3`: Unanimous
   - `2/3`: Majority with explicit dissent
   - else: Deadlock
3. Present synthesis to user:
   - decision
   - why it wins by criteria
   - key risks and guardrails
   - first actionable next step
   - dissent and flip conditions

## Templates (read on demand, not at skill load)

- **Agent Prompt Template:** `templates/agent-prompt-template.md`
- **Discovery Log Template:** `templates/discovery-log-template.md`
- **Decision Log Template:** `templates/decision-log-template.md`

## Artifacts and Fallbacks

- Ensure `docs/magi/` exists: `mkdir -p docs/magi`.
- Always write both logs:
  - `docs/magi/YYYY-MM-DD-<topic>-discovery.md`
  - `docs/magi/YYYY-MM-DD-<topic>-decision.md`
- Decision log should include debate transcript and vote table.
- If an agent is silent:
  - nudge once
  - proceed with available output
  - mark reduced confidence in the decision log

## Quick Checklist

- Did all three personas produce distinct, in-lens analysis?
- Did debate happen directly between agents?
- Did voting happen explicitly?
- Did final synthesis include dissent and flip conditions?
- Were both logs written under `docs/magi/`?
