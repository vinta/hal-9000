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

Every run starts with Discovery -- even when the user supplies predefined options. The three lenses may surface alternatives the user hasn't considered, or confirm the option space is well-scoped. User-supplied options are seeded as input to Discovery, not used to skip it.

Pipeline:

1. Discovery (3-agent ideation + opportunity backlog)
2. Independent analysis
3. Peer-to-peer debate
4. Consensus vote and synthesis

### Execution Invariants

- Launch agents with the user's prompt and basic project context (e.g., CLAUDE.md contents). Do not run a lead-led codebase exploration pass -- agents will self-orient through their own lens.
- Create the MAGI team before backlog drafting so each agent can ideate independently.
- Lead orchestrates; agents argue. The lead does not substitute its own judgment for agent outputs.
- Phase 2 requires direct peer messages between agents (not lead-mediated monologues).
- Every run must include Phase 3 voting, even when consensus seems obvious.
- Every run must write two logs to `docs/magi/`: `YYYY-MM-DD-<topic>-discovery.md` and `YYYY-MM-DD-<topic>-decision.md`.
- Never collapse to a narrow option set before generating a broad opportunity backlog, even when the user supplies predefined options.

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

## Input Handling

- If the user supplies predefined options (e.g., "A vs B"), seed those as context for Discovery agents. Agents must evaluate the supplied options AND propose alternatives from their lens.
- If the user asks an open-ended prompt ("anything to improve," "brainstorm," "surprise me"), agents ideate freely with no seed options.

## Workflow

```dot
digraph magi {
    rankdir=TB;
    node [shape=box, style=rounded];

    discover [label="3-agent ideation\n+ opportunity backlog"];
    disc_log [label="Log discovery"];
    select [label="Select focus" shape=diamond style=""];
    clarify [label="Clarify constraints\n+ success criteria"];
    packet [label="Draft Decision Packet"];
    confirm [label="Framing confirmed?" shape=diamond style=""];
    analysis [label="Independent analysis"];
    debate [label="Peer-to-peer debate"];
    vote [label="Vote + tally"];
    synth [label="Synthesize recommendation"];
    dec_log [label="Log decision"];

    discover -> disc_log -> select;
    select -> discover [label="expand"];
    select -> clarify [label="focus chosen"];
    clarify -> packet -> confirm;
    confirm -> clarify [label="adjust"];
    confirm -> analysis [label="confirmed"];
    analysis -> debate -> vote;
    vote -> synth;
    synth -> dec_log;
}
```

### Phase 0: Discovery and Framing (Hard Gate)

**Entry criteria:** User asks for recommendations, trade-off analysis, or open-ended prioritization.

1. Start from the user question: **$ARGUMENTS**.
2. Spawn Discovery immediately:
   - `TeamCreate` team `magi` with three agents: `scientist`, `mother`, `woman`.
   - `TaskCreate` one discovery task per agent using the Discovery Task Variant in `templates/agent-prompt-template.md`.
   - Pass the user's prompt, any user-supplied options, and basic project context. Do not run a lead-led exploration pass -- agents self-orient through their own lens.
   - Each agent independently proposes **5-7 opportunities** from its lens, including **1 crazy-but-plausible** bet. If the user supplied options, agents must evaluate those AND propose alternatives.
3. Consolidate agent outputs into an Opportunity Backlog using the required schema below.
   - Generate **12-20 consolidated candidate opportunities** across at least **5 distinct lenses** (for example: product UX, reliability, growth, operations, DevEx, quality, trust/safety, monetization).
   - Preserve source attribution for each consolidated candidate (which agent(s) proposed it).
   - Enforce a novelty quota: at least **30%** of candidates must be non-obvious or contrarian relative to current roadmap direction.
   - Include surprise bets from each perspective: at least **1 Scientist**, **1 Mother**, and **1 Woman** "crazy-but-plausible" bet.
   - For each candidate, include impact hypothesis, effort band, confidence, and primary risk.
4. Write/update discovery log at `docs/magi/YYYY-MM-DD-<topic>-discovery.md` using `templates/discovery-log-template.md`.
5. Ask the user to choose next step using `AskUserQuestion` with exactly:
   - `Proceed with recommended focus`
   - `Choose a different focus from backlog`
   - `Expand ideation before deciding`
   - If user selects expand ideation, refine backlog and repeat from step 3.
6. Ask clarifying questions one at a time via `AskUserQuestion` (prefer multiple-choice):
   - Decision objective
   - Constraints and non-negotiables
   - Success criteria
   - Explicitly out-of-scope items
7. Draft a Decision Packet using the required schema below.
8. Validate the packet:
   - At least 4 options, with at least 1 wildcard/contrarian option
   - Options must span at least 3 distinct themes (not variants of one idea)
   - At least 3 evaluation criteria
   - Non-goals and unknowns included
9. Present packet for confirmation using `AskUserQuestion` with exactly:
   - `Looks good, start deliberation`
   - `I want to adjust framing`
10. If user selects adjust, revise packet and repeat Step 9.
11. `TaskCreate` one analysis task per agent using `templates/agent-prompt-template.md`.

**Exit criteria:**

- Backlog has been produced and user-selected focus is explicit.
- User has confirmed framing.
- Team exists with three agents.
- Three Phase 1 tasks are created and started.

#### Opportunity Backlog Schema

```markdown
## Opportunity Surface

- <lenses covered and why they matter for this context>

## Agent Discovery Inputs

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
- Option D: <wildcard/contrarian alternative>

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

- <map each option to Opportunity Backlog IDs and note what was intentionally excluded>

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
3. Decision log must include full debate transcript, not a summary.
4. If fallback occurred (silent agent, missing data), include confidence note in decision log.

## Templates (read on demand, not at skill load)

- **Agent Prompt Template:** `templates/agent-prompt-template.md` -- read when spawning agents. Includes domain focus mappings, Woman constraint, and phase-specific output formats.
- **Discovery Log Template:** `templates/discovery-log-template.md` -- read when writing discovery artifacts.
- **Decision Log Template:** `templates/decision-log-template.md` -- read when writing decision artifacts.

## Common Mistakes (Symptom -> Corrective Action)

| Symptom                                                     | Corrective Action                                                                                                                                 |
| ----------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| Discovery kickoff is delayed by lead pre-explore            | Start Council Discovery immediately (`TeamCreate` + 3 `TaskCreate`); agents self-orient through their own lens                                    |
| Analysis tasks created before framing confirmation          | Stop; Discovery agents are already running but Phase 1 tasks require confirmed Decision Packet first                                              |
| Open-ended prompt ran without 3-agent discovery             | Run Council Discovery first: 5-7 opportunities per agent, then consolidate                                                                        |
| User-supplied options treated as final without Discovery     | Seed user options as input to Discovery agents; always produce full Opportunity Backlog before locking options                                     |
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
