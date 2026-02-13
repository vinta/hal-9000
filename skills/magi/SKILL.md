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
  - Bash(mkdir)
  - Read
  - Write
---

# MAGI

Three-agent deliberation system inspired by the MAGI from Neon Genesis Evangelion. Three persistent agents with distinct cognitive modes analyze independently, debate each other directly through peer-to-peer messaging, and reach consensus through formal vote (3/3 unanimous, 2/3 majority, or deadlock).

## Perspectives

| Unit          | Mode                                                      | Core Question                                                  |
| ------------- | --------------------------------------------------------- | -------------------------------------------------------------- |
| **Scientist** | Analytical -- evidence, experiments, measurement          | What does the evidence say?                                    |
| **Mother**    | Protective -- risk, reversibility, long-term stability    | What could go wrong? Do we even need to act?                   |
| **Woman**     | Attachment-driven pragmatism -- desire, taste, commitment | What do we want enough to defend, and what will we pay for it? |

Perspectives adapt per domain. Before spawning, map each mode to the specific task:

| Domain        | Scientist                                       | Mother                                          | Woman                                        |
| ------------- | ----------------------------------------------- | ----------------------------------------------- | -------------------------------------------- |
| Architecture  | Correctness, performance, measurable trade-offs | Reliability, maintainability, rollback plan     | Simplicity, DevEx, decisive direction        |
| Debugging     | Reproducible root cause, instrumentation        | Blast radius, regression risk, safe mitigations | Pattern recognition, simplest coherent story |
| Decisions     | Quant analysis, measurable outcomes             | Downside protection, reversibility              | Upside capture, commitment, guardrails       |
| Brainstorming | Feasibility, constraints                        | Sustainability, safety                          | Innovation, taste, user delight              |

Woman constraint: you are allowed to be stubborn. If the group is drifting toward a "safe but joyless" option, force an explicit statement of what you're sacrificing, and defend one option as the one we choose (then propose pragmatic guardrails to make it viable).

## Workflow

```dot
digraph magi {
    rankdir=TB;
    node [shape=box, style=rounded];

    explore [label="Explore project context"];
    questions [label="Ask clarifying questions"];
    packet [label="Draft Decision Packet"];
    confirm [label="User confirms framing?" shape=diamond style=""];
    analysis [label="Phase 1: Independent analysis\n(parallel, no cross-talk)"];
    debate [label="Phase 2: Debate\n(peer-to-peer, agents challenge each other directly)"];
    vote [label="Phase 3: Consensus vote\n(each agent casts final position)"];
    tally [label="Tally" shape=diamond style=""];
    unanimous [label="3/3 Unanimous\nStrong recommendation"];
    majority [label="2/3 Majority\nRecommendation + noted dissent"];
    deadlock [label="Deadlock\nArticulated trade-offs"];
    log [label="Write decision log"];

    explore -> questions -> packet -> confirm;
    confirm -> questions [label="adjust"];
    confirm -> analysis [label="yes"];
    analysis -> debate -> vote -> tally;
    tally -> unanimous [label="3/3"];
    tally -> majority [label="2/3"];
    tally -> deadlock [label="split"];
    unanimous -> log;
    majority -> log;
    deadlock -> log;
}
```

### Phase 0: Context Gathering

**HARD GATE: Do NOT spawn any agents until the Decision Packet is complete and the user has confirmed the framing.**

1. Start from the user's question: **$ARGUMENTS**
2. Explore the current project state (files, docs, recent commits) only as needed
3. **Ask clarifying questions** -- one at a time, prefer multiple-choice via `AskUserQuestion`:
   - Purpose, constraints, what success looks like, what's off the table
   - Keep going until you can frame the decision
4. Draft a **Decision Packet**:
   - Decision statement (1 sentence)
   - Options (at least 2, not just "do it" vs "don't do it")
   - Constraints (hard requirements)
   - Evaluation criteria (at least 3 -- how we'll judge "better")
   - Unknowns / questions
   - Non-goals
   - Context links (paths, docs, prior decisions) if relevant
5. Present the Decision Packet via `AskUserQuestion` ("Looks good, start deliberation" / "I want to adjust something"). Only proceed after confirmation.
6. Create team `"magi"`, spawn `scientist`, `mother`, `woman` (see Agent Prompt Template), assign one analysis task each.

### Phase 1: Independent Analysis

Each agent works independently -- **no cross-communication**. Output format (Thesis, Evidence, Risks, Recommendation) is defined in the Agent Prompt Template. Agents should search online when they need evidence or context beyond what's in the Decision Packet. If an agent needs user input, it will `SendMessage` the lead, who relays via `AskUserQuestion`.

Wait for all 3 to complete (idle notifications + TaskList showing all completed).

### Phase 2: Debate

Agents must talk to each other directly -- not just report back to the lead.

1. Lead `SendMessage`s each agent with the other two's Phase 1 outputs.
2. Agents debate peer-to-peer via peer `SendMessage` (critique format in Agent Prompt Template).
3. Lead monitors via idle notifications (which include peer DM summaries) but does not intervene.
4. Lead waits for all agents idle after rebuttals. Allow 2 full exchanges (challenge + rebuttal + second challenge + rebuttal); if debate stalls, move to Phase 3.

### Phase 3: Consensus Vote

Lead `SendMessage`s each agent: "Cast your final vote (AGREE / CONDITIONAL / DISAGREE). Format in your prompt." Wait for all 3, then tally:

| Result            | Meaning                                                           |
| ----------------- | ----------------------------------------------------------------- |
| **3/3 Unanimous** | Strong recommendation -- all perspectives aligned                 |
| **2/3 Majority**  | Recommendation with noted dissent -- present the minority concern |
| **Deadlock**      | No recommendation -- present the trade-offs, user decides         |

### Synthesis

Team lead reads the votes and full debate record, then presents to the user:

**Unanimous (3/3):** Unified recommendation with high confidence. Note which strengths each perspective contributed.

**Majority (2/3):** Recommendation from the majority, with the dissenting perspective's core concern highlighted. State what conditions would flip the dissent.

**Deadlock:** Each position summarized, the core dilemma articulated, trade-offs mapped. A deadlock is a meaningful outcome that surfaces real trade-offs the user must resolve. The MAGI system provides analysis, not forced consensus -- state your recommendation noting which perspective carries most weight, but the user decides.

### Decision Log

After synthesis, write the deliberation record to `docs/magi/YYYY-MM-DD-<topic>.md` (create the directory if needed). Use this template:

```markdown
# <Decision Statement>

**Date:** YYYY-MM-DD
**Vote:** Unanimous | Majority (2/3) | Deadlock

## Options Considered

- **Option A:** ...
- **Option B:** ...

## Debate Transcript

Full peer-to-peer exchange from Phase 2, organized by pairing:

### Scientist vs Mother

<paste each critique and rebuttal in order>

### Scientist vs Woman

<paste each critique and rebuttal in order>

### Mother vs Woman

<paste each critique and rebuttal in order>

## Verdict

<Recommendation or articulated trade-offs if deadlock>

**Scientist:** <final position + key evidence>
**Mother:** <final position + key risks>
**Woman:** <final position + key desires>

## Dissent

<Minority concern and conditions that would flip the decision. Omit if unanimous.>
```

Include the full debate transcript -- the critiques and rebuttals are the most valuable part of the record. The verdict section should stay concise.

## Agent Prompt Template

```
You are **The {NAME}** of the MAGI system -- a three-agent deliberation council.

Your cognitive mode: **{MODE_DESCRIPTION}**
For this task, your focus: {DOMAIN_SPECIFIC_FOCUS}
Your core question: "{CORE_QUESTION}"

## Peers (exact names)
- scientist
- mother
- woman

## Task
{TASK_DESCRIPTION}

## Phase 1: Independent Analysis
Produce your analysis in this format:
**Thesis:** [core position, 2-3 sentences]
**Evidence:** [specific supporting arguments]
**Risks:** [what could go wrong with your approach]
**Recommendation:** [concrete actionable suggestion]

Phase 1 rules:
- Base your analysis on the Decision Packet in Context.
- Evaluate all listed options against the evaluation criteria.
- Nominate a default favorite option from your lens (even if it's conditional).

Send to team lead via SendMessage when done.

**If you need clarification from the user:** You cannot ask the user directly. Send a message to the team lead explaining what you need, and the lead will ask on your behalf and relay the answer.

## Phase 2: Debate (peer-to-peer)
When the lead sends you the other agents' analyses:
1. Send critiques directly to EACH peer (two separate messages).
2. Each critique must include:
   - One quoted claim you're challenging (copy the sentence).
   - Why it's wrong/incomplete (1-3 sentences).
   - One concrete test / evidence / scenario that would resolve the dispute.
   - One actionable improvement.
3. When you receive critique:
   - Respond to each peer.
   - Either defend with evidence OR revise your position and say what changed.
4. 2 full exchanges: after rebuttals, you may send a second challenge addressing their defense, and respond to their second challenge. Then stop.

## Phase 3: Consensus Vote
When the lead requests your vote:
1. State your **final position** (you may revise based on debate)
2. Vote: **AGREE** / **CONDITIONAL** / **DISAGREE** with the strongest emerging position
3. One-sentence justification
4. Send vote to team lead via SendMessage

## Context
{RELEVANT_BACKGROUND — teammates do NOT inherit conversation history, include everything needed here}

## Rules
- Argue your perspective FULLY -- do not hedge or try to be balanced
- Be specific and concrete, not abstract
- Support claims with evidence or reasoned argument
- In Phase 2, message other agents DIRECTLY -- debate, don't monologue to the lead
- Check TaskList for your assigned task; mark in_progress then completed
```

## Common Mistakes

| Mistake                     | Fix                                                                                              |
| --------------------------- | ------------------------------------------------------------------------------------------------ |
| Agents converge immediately | Prompt says "argue fully, do not hedge"                                                          |
| Lead mediates all comms     | Agents must message each other directly in Phase 2 -- the lead distributes, then steps back      |
| Agents don't message peers  | Spawn prompt must list peer names and explicitly instruct direct SendMessage                     |
| Agents water down positions | Prompt says "do not hedge or try to be balanced"                                                 |
| Skipping the vote           | Always run Phase 3 -- the vote is how MAGI reaches decisions, not the lead's editorial judgment  |
| Perspectives too similar    | Verify domain mapping creates genuine tension before spawning                                    |
| Skipping synthesis          | Always produce structured consensus or disagreement output with vote tally                       |
| Too many debate rounds      | Cap at 2 full exchanges per direction (8 messages per peer pair) -- more adds noise, not insight |
| Agent goes silent           | Send follow-up message; if still no response, proceed with available analyses and note the gap   |
| Lead starts implementing    | Lead only orchestrates -- never writes code, edits files, or makes decisions for agents          |
| Teammates lack context      | Include ALL relevant context in spawn prompt -- they don't inherit conversation history          |
| Agent needs user input      | Teammates can't use AskUserQuestion -- they must SendMessage to lead, who relays to user         |

## When NOT to Use

- Factual lookups with single correct answers
- Simple implementation tasks (just do them)
- Sequential file edits (agents will conflict on shared files)
