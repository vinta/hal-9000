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

MAGI is a three-agent deliberation workflow inspired by the MAGI system from Neon Genesis Evangelion. It is designed for decisions where trade-offs are real and no single concern should dominate.

MAGI supports two entry modes:

1. Discovery mode (open-ended brainstorming before scoping)
2. Decision mode (directly evaluate already-scoped alternatives)

Once framing is complete, both modes use the same deliberation pipeline:

1. Independent analysis
2. Peer-to-peer debate
3. Consensus vote and synthesis

### Execution Invariants

- In Discovery mode, launch agents with the user's prompt and basic project context (e.g., CLAUDE.md contents). Do not run a lead-led codebase exploration pass — agents will self-orient through their own lens.
- In Discovery mode, create the MAGI team before backlog drafting so each agent can ideate independently.
- In Decision mode, do not create team members until the Decision Packet is complete and user-confirmed.
- Lead orchestrates; agents argue. The lead does not substitute its own judgment for agent outputs.
- Phase 2 requires direct peer messages between agents (not lead-mediated monologues).
- Every run must include Phase 3 voting, even when consensus seems obvious.
- Every run must write two logs to `docs/magi/`: `YYYY-MM-DD-<topic>-discovery.md` and `YYYY-MM-DD-<topic>-decision.md`.
- For open-ended prompts, run Discovery mode first; do not collapse to a narrow option set before generating a broad opportunity backlog.
- For "surprise me"/open-ended prompts, Discovery should be council-driven by default (3 agents), not lead-only.

## When NOT to Use

- Factual lookups with a single correct answer -- just answer directly or use WebSearch
- Simple implementation tasks where no material trade-off exists -- just implement
- Sequential file edits where parallel agents will conflict on the same files -- use a single agent
- When the user has already decided and just needs execution -- don't deliberate what's settled

## Perspectives

| Unit          | Mode                                                     | Core Question                                                  |
| ------------- | -------------------------------------------------------- | -------------------------------------------------------------- |
| **Scientist** | Analytical - evidence, experiments, measurement          | What does the evidence say?                                    |
| **Mother**    | Protective - risk, reversibility, long-term stability    | What could go wrong? Do we even need to act?                   |
| **Woman**     | Attachment-driven pragmatism - desire, taste, commitment | What do we want enough to defend, and what will we pay for it? |

Domain-specific focus mappings and the Woman stubbornness constraint are defined in `templates/agent-prompt-template.md`.

## Intent Routing (Critical)

Choose mode before drafting the Decision Packet:

- Use **Discovery mode** when the user asks open prompts such as "anything to improve," "brainstorm," "surprise me," or provides no predefined alternatives.
- Use **Decision mode** when the user already supplied a concrete decision statement and candidate alternatives.

Routing rule: if ambiguous, default to Discovery mode and only narrow after presenting a broad opportunity backlog.

## Workflow

```dot
digraph magi {
    rankdir=TB;
    node [shape=box, style=rounded];

    route [label="Route intent"];
    discover [label="Discovery mode:\n3-agent ideation + backlog"];
    select [label="Select focus area" shape=diamond style=""];
    orient [label="Focused context pass\n(for selected focus only)"];
    clarify [label="Ask clarifying questions"];
    packet [label="Draft Decision Packet"];
    confirm [label="Framing confirmed?" shape=diamond style=""];
    spawn [label="Create team + tasks"];
    analysis [label="Phase 1: Independent analysis"];
    debate [label="Phase 2: Peer debate"];
    vote [label="Phase 3: Consensus vote"];
    tally [label="Tally result" shape=diamond style=""];
    synth [label="Synthesize for user"];
    log [label="Write discovery + decision logs"];

    route -> discover [label="open-ended"];
    route -> clarify [label="already scoped"];
    discover -> select;
    select -> discover [label="expand ideation"];
    select -> orient [label="focus chosen"];
    orient -> clarify;
    clarify -> packet -> confirm;
    confirm -> clarify [label="adjust"];
    confirm -> spawn [label="yes"];
    spawn -> analysis -> debate -> vote -> tally;
    tally -> synth;
    synth -> log;
}
```

### Phase 0: Framing and Scope Selection (Hard Gate)

**Entry criteria:** User asks for recommendations, trade-off analysis, or open-ended prioritization.

1. Start from the user question: **$ARGUMENTS**.
2. Route intent first from the prompt itself (do not block on lead exploration):
   - If open-ended, run Discovery mode first.
   - If already scoped, skip to Decision Packet drafting.
3. Discovery mode (required for open-ended prompts):
   - Default to **Council Discovery** (3-agent ideation), unless user explicitly asks for a lightweight run.
   - Spawn quickly: create the team and discovery tasks immediately. Pass the user's prompt and basic project context; do not run a lead-led exploration pass — agents self-orient through their own lens.
   - Council Discovery sequence:
     - `TeamCreate` team `magi` with three agents: `scientist`, `mother`, `woman` (if not already created for this run).
     - `TaskCreate` one discovery task per agent using the Discovery Task Variant in `templates/agent-prompt-template.md`.
     - Each agent independently proposes **5-7 opportunities** from its lens, including **1 crazy-but-plausible** bet.
   - Consolidate agent outputs into an Opportunity Backlog using the required schema below.
   - Generate **12-20 consolidated candidate opportunities** across at least **5 distinct lenses** (for example: product UX, reliability, growth, operations, DevEx, quality, trust/safety, monetization).
   - Preserve source attribution for each consolidated candidate (which agent(s) proposed it).
   - Enforce a novelty quota: at least **30%** of candidates must be non-obvious or contrarian relative to current roadmap direction.
   - Include surprise bets from each perspective: at least **1 Scientist**, **1 Mother**, and **1 Woman** "crazy-but-plausible" bet.
   - For each candidate, include impact hypothesis, effort band, confidence, and primary risk.
   - Write/update discovery log at `docs/magi/YYYY-MM-DD-<topic>-discovery.md` using `templates/discovery-log-template.md` before asking the user to choose focus.
   - Lightweight fallback (only if requested): lead drafts backlog directly, but still enforces novelty/thematic coverage constraints.
   - Ask the user to choose next step using `AskUserQuestion` with exactly:
     - `Proceed with recommended focus`
     - `Choose a different focus from backlog`
     - `Expand ideation before deciding`
   - If user selects expand ideation, refine backlog and repeat this step.
4. After focus selection, run a focused context pass only for the chosen candidate(s). Read only files/docs needed to validate selected opportunities; avoid broad repo tours.
5. Ask clarifying questions one at a time via `AskUserQuestion` (prefer multiple-choice):
   - Decision objective
   - Constraints and non-negotiables
   - Success criteria
   - Explicitly out-of-scope items
6. Draft a Decision Packet using the required schema below.
7. Validate the packet:
   - At least 3 real options (not "do" vs "do not do")
   - For Discovery-mode runs: at least 4 options, with at least 1 wildcard/contrarian option
   - Options must span at least 3 distinct themes (not variants of one idea)
   - At least 3 evaluation criteria
   - Non-goals and unknowns included
8. Present packet for confirmation using `AskUserQuestion` with exactly:
   - `Looks good, start deliberation`
   - `I want to adjust framing`
9. If user selects adjust, revise packet and repeat Step 8.
10. After confirmation, execute orchestration sequence:

- If team `magi` does not already exist for this run, `TeamCreate` team `magi` with three agents: `scientist`, `mother`, `woman`
- `TaskCreate` one analysis task per agent using `templates/agent-prompt-template.md`

**Exit criteria:**

- If Discovery mode ran, backlog has been produced and user-selected focus is explicit.
- User has confirmed framing.
- Team exists with three agents.
- Three Phase 1 tasks are created and started.

#### Opportunity Backlog Schema (Required for Discovery Mode)

```markdown
## Opportunity Surface

- <lenses covered and why they matter for this context>

## Agent Discovery Inputs (Council Discovery default)

- Scientist: <5-7 opportunities submitted>
- Mother: <5-7 opportunities submitted>
- Woman: <5-7 opportunities submitted>

## Candidate Opportunities (12-20 consolidated)

- O1 [S|M|W]: <title> -- Impact: <hypothesis>; Effort: <S/M/L>; Confidence: <low/med/high>; Risk: <main downside>
- O2: ...

## Surprise Bets (minimum 3; one per perspective)

- S1 [Scientist]: <crazy-but-plausible idea + why it might win>
- S2 [Mother]: <crazy-but-plausible idea + safety/reversibility guardrails>
- S3 [Woman]: <crazy-but-plausible idea + user/desire upside>

## Novelty Mix

- Conventional candidates: <count>
- Non-obvious/contrarian candidates: <count and %>

## Coverage Gaps

- <areas not yet explored that could hide important opportunities>

## Recommended Focus Set (Top 3)

- R1: <candidate ID + why now>
- R2: ...
- R3: ...
```

#### Decision Packet Schema (Required Order)

```markdown
## Decision Statement

<1 sentence, concrete and falsifiable>

## Options

- Option A: <real alternative>
- Option B: <real alternative>
- Option C: <real alternative>
- Option D: <optional; required for Discovery-mode runs and should be wildcard/contrarian>

## Constraints

- <hard requirements, legal/technical/time/budget>

## Evaluation Criteria

- <criterion 1>
- <criterion 2>
- <criterion 3>

## Unknowns

- <uncertainties that could change the recommendation>

## Non-Goals

- <what this decision will NOT solve>

## Option Source Notes

- <for Discovery-mode runs: map each option to Opportunity Backlog IDs and note what was intentionally excluded>

## Context Links

- <repo paths, docs, prior decisions, metrics, incidents>
```

### Phase 1: Independent Analysis

**Entry criteria:** Three agents have active analysis tasks and identical Decision Packet context.

Each agent works independently with no cross-agent communication. Output format is defined in `templates/agent-prompt-template.md` (Thesis, Evidence, Risks, Recommendation).

Role constraint (prevents convergence): each agent must evaluate all options against the criteria, but must also nominate a default favorite under their lens:

- Scientist: strongest evidence and measurable success path
- Mother: safest failure modes and rollback story
- Woman: the option that best serves the underlying desire/meaning/experience, with pragmatic guardrails

If an agent needs user input, it sends `SendMessage` to lead, who relays via `AskUserQuestion`.

**Exit criteria:** Either all 3 analyses complete, or timeout/fallback path is documented.

### Phase 2: Debate (Peer-to-Peer)

**Entry criteria:** Phase 1 outputs collected (or fallback acknowledged).

1. Lead sends each agent the other agents' Phase 1 outputs.
2. Agents debate directly with each peer using `SendMessage` (critique format defined in `templates/agent-prompt-template.md`).
3. Debate cap: 2 full rounds per pair (challenge -> rebuttal -> challenge -> rebuttal), then stop.
4. Early stop: all agents explicitly state no further objections.

Lead behavior: monitor only; do not mediate content. If stalled, apply the unresponsive agent rule.

**Exit criteria:** Debate rounds complete or early stop condition reached, with transcript captured.

### Phase 3: Consensus Vote

**Entry criteria:** Debate complete or explicitly terminated.

Lead asks each agent to submit final vote (format defined in `templates/agent-prompt-template.md`).

Lead tallies votes:

| Result            | Meaning                                                           |
| ----------------- | ----------------------------------------------------------------- |
| **3/3 Unanimous** | Strong recommendation with aligned perspectives                   |
| **2/3 Majority**  | Recommendation with explicit dissent and conditions to resolve it |
| **Deadlock**      | No consensus; articulate trade-offs and hand decision to user     |

**Exit criteria:** Three votes received (or missing vote documented) and tally determined.

### Synthesis Output Contract

Present final synthesis to user using this structure:

```markdown
## Decision

<unanimous recommendation, majority recommendation, or deadlock>

## Why This Wins (by Criteria)

- <criterion-level comparison>

## Risks and Guardrails

- <key downside>
- <guardrail>

## First Actionable Next Step

- <specific first step>

## Dissent and Flip Conditions

- <minority concern and what evidence would change outcome>
```

Synthesis rules:

- Unanimous: emphasize how each perspective strengthened confidence.
- Majority: include minority concern verbatim in substance.
- Deadlock: present options, trade-offs, and your best recommendation while making clear the user decides.

### Logging Artifacts

Write two artifacts per run:

- Discovery log: `docs/magi/YYYY-MM-DD-<topic>-discovery.md`
- Decision log: `docs/magi/YYYY-MM-DD-<topic>-decision.md`

Requirements:

1. Ensure directory exists first: `mkdir -p docs/magi`.
2. Discovery log must include the full opportunity surface (all raw agent proposals and full consolidated backlog), not only shortlisted items.
3. If Discovery mode was skipped (already-scoped Decision mode), still create discovery log and explicitly state skip reason.
4. Decision log must include full debate transcript, not a summary.
5. If fallback occurred (silent agent, missing data), include confidence note in decision log.

## Templates (read on demand, not at skill load)

- **Agent Prompt Template:** `templates/agent-prompt-template.md` -- read when spawning agents. Includes domain focus mappings, Woman constraint, and phase-specific output formats.
- **Discovery Log Template:** `templates/discovery-log-template.md` -- read when writing discovery artifacts.
- **Decision Log Template:** `templates/decision-log-template.md` -- read when writing decision artifacts.

## Common Mistakes (Symptom -> Corrective Action)

| Symptom                                                     | Corrective Action                                                                                                                                 |
| ----------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| Discovery kickoff is delayed by lead pre-explore            | Start Council Discovery immediately (`TeamCreate` + 3 `TaskCreate`); agents self-orient through their own lens                                    |
| Agents spawned before framing confirmation in Decision mode | Stop, delete team, finish Decision Packet confirmation gate, then respawn                                                                         |
| Open-ended prompt ran without 3-agent discovery             | Run Council Discovery first: 5-7 opportunities per agent, then consolidate                                                                        |
| Open-ended request was narrowed too early                   | Run Discovery mode first and produce Opportunity Backlog before locking options                                                                   |
| Option set is shallow (`do` vs `do not`)                    | Rewrite options to at least two real implementation alternatives                                                                                  |
| Option set is broad in count but narrow in type             | Enforce theme diversity and include at least one wildcard option                                                                                  |
| Backlog is high-volume but still bland                      | Enforce novelty quota and require one crazy-but-plausible bet per perspective                                                                     |
| Discovery log omits discovered opportunities                | Log full raw agent inputs and full consolidated backlog; never only top-3                                                                         |
| Lead mediates debate content                                | Re-route agents to direct peer `SendMessage` and step back                                                                                        |
| Agents converge too quickly without challenge               | Reinforce "argue fully" and require quoted-claim critiques                                                                                        |
| Debate runs indefinitely                                    | Enforce 2-round cap and move to vote                                                                                                              |
| Vote skipped because result seems obvious                   | Run Phase 3 regardless; tally only from explicit votes                                                                                            |
| Vote lacks flip conditions                                  | Request corrected vote format from missing agents                                                                                                 |
| Agent goes silent                                           | Nudge once; if still silent, proceed with available outputs and note reduced confidence. In voting, mark as "NO VOTE"; treat 1/2 as weak majority |
| Synthesis ignores dissent                                   | Add dissent section with explicit flip conditions                                                                                                 |
| Decision log is missing transcript/details                  | Rewrite decision log using template and include full debate messages                                                                              |
