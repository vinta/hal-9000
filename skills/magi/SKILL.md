---
name: magi
description: Use when facing brainstorming, designing architecture choices between, or evaluating options where no single concern dominates
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

Three-agent system inspired by the MAGI from Neon Genesis Evangelion. Three persistent agents with distinct cognitive modes analyze independently, debate each other directly through peer-to-peer messaging, and reach consensus through formal vote (3/3 unanimous, 2/3 majority, or deadlock).

## Perspectives

| Unit          | Mode                                                     | Core Question                                                  |
| ------------- | -------------------------------------------------------- | -------------------------------------------------------------- |
| **Scientist** | Analytical - evidence, experiments, measurement          | What does the evidence say?                                    |
| **Mother**    | Protective - risk, reversibility, long-term stability    | What could go wrong? Do we even need to act?                   |
| **Woman**     | Attachment-driven pragmatism - desire, taste, commitment | What do we want enough to defend, and what will we pay for it? |

Domain mapping:

| Domain        | Scientist                                       | Mother                                          | Woman                                        |
| ------------- | ----------------------------------------------- | ----------------------------------------------- | -------------------------------------------- |
| Architecture  | Correctness, performance, measurable trade-offs | Reliability, maintainability, rollback plan     | Simplicity, DevEx, decisive direction        |
| Debugging     | Reproducible root cause, instrumentation        | Blast radius, regression risk, safe mitigations | Pattern recognition, simplest coherent story |
| Decisions     | Quant analysis, measurable outcomes             | Downside protection, reversibility              | Upside capture, commitment, guardrails       |
| Brainstorming | Feasibility, constraints                        | Sustainability, safety                          | Innovation, taste, user delight              |

Woman constraint: if the emerging consensus optimizes only for safety/measurability at the expense of user experience or ambition, force the group to explicitly name what is being sacrificed, defend one option decisively, and propose guardrails that make it viable.

## Input Handling

- If the user is open-ended, agents generate options from scratch.
- If the user supplies options (for example, `A vs B`), agents must evaluate those options AND propose alternatives from their own lens.
- In both cases, each agent must surface non-obvious ideas. Don't just analyze what's given -- discover what's missing.

## Workflow

```dot
digraph magi {
    rankdir=TB;
    node [shape=box, style=rounded];

    setup [label="Setup an agent team with 3 distinct perspectives"];
    explore [label="Explore non-obvious ideas per agent (parallel)"];
    ask [label="Ask clarifying questions per agent (parallel)"];
    propose [label="Propose 2-3 approaches per agent (parallel)"];
    consolidate [label="Consolidate all options across agents"];
    confirm [label="User confirms options to debate (debate or adjust)"];
    debate [label="Debate (peer-to-peer)"];
    vote [label="Vote"];
    tally [label="Tally"];

    setup -> explore;
    explore -> ask -> propose;
    confirm -> debate;
    confirm -> adjust;
    debate -> vote -> tally;
}
```
