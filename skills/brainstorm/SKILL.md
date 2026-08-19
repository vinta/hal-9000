---
name: brainstorm
description: Use when the user wants ideas rather than answers — what to build, do, or try ("give me ideas", "what could we build", "brainstorm this", "surprise me") on any topic, technical or not. Returns ~30 one-line ideas from independent perspectives, a quarter deliberately absurd; gathers options, never plans or judges them
argument-hint: "[topic — omit to use the current conversation]"
user-invocable: true
---

# Brainstorm

Divergence only: many one-line ideas from perspectives that cannot hear each other. The deliverable is the pool of options — *what* to do or build. Picking, planning, and feasibility belong to the conversation after, not to this skill.

Independent generation is the point of the machinery: ideas produced in one shared context drift toward whatever came first (anchoring), so each perspective runs blind in its own subagent — the nominal-group structure that outperforms people (and models) riffing in one room.

## 1. Pin the topic

Take the argument as the topic. Without one, use what the conversation is about. Only when both are empty, ask the user one question: what are we generating ideas for?

The argument may carry free-text overrides alongside the topic — a count ("10 ideas", "50 ideas") resizes the batch; "surprise me" makes the whole roster wildcards. Honor them; otherwise defaults below apply.

## 2. Cast six perspectives

Derive **four** from the topic: stakeholders it touches, adjacent fields, its opposite or its victim — people who would each want a different thing from it. Sample **two wildcards** from: a seven-year-old, a supervillain, a sci-fi author, a person from 1900, a street-food vendor, a game designer, a broke artist, an alien anthropologist.

Name each perspective concretely ("night-shift nurse", not "healthcare stakeholder") — vague personas produce interchangeable ideas.

## 3. Dispatch all six blind, in one response

Issuing all six Agent dispatches in the same response is what makes them run in parallel; one dispatch per response makes them sequential. Send all six in a single response, each with this prompt, nothing shared between them:

> You are {persona}, brainstorming about: {topic — two or three sentences of context, written for someone who has not seen this conversation}.
> Return 5–6 ideas. Each idea is ONE line naming a thing to do, build, or try — never how to do it, never a plan. At least 2 of your ideas must be impractical or absurd on purpose: illegal-in-three-countries energy, physics-optional, budget-of-a-nation. Stay in character; want what {persona} would want.
> You may run one or two WebSearch queries for stimulus (what exists, what's weird in this space) — or none. Do not cite or justify.
> Your final message is the raw idea list only, one per line.

## 4. Pool and present

Merge near-duplicates across perspectives, keeping the sharpest phrasing. Present the survivors grouped under a small header per perspective, one line per idea — no elaboration, no ranking, no feasibility notes. A perspective that returned nothing is dropped silently; present what came back.

Done when the pool is on screen: roughly 30 lines (whatever the overrides said), at least a quarter of them absurd, six voices visibly wanting different things. Stop there — riffing, expanding, or choosing happens only if the user asks next.
