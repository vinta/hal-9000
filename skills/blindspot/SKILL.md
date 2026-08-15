---
name: blindspot
description: Use when the user asks for a blindspot pass or to find their unknown unknowns, or signals unfamiliarity with a domain, tool, or codebase area ("never used X", "first time doing Y", "no idea where to start", "don't know what I don't know") before working there. Interviews the user with recon-fed questions, turning unknown unknowns into known unknowns and naming silent assumptions so they can prompt well
argument-hint: "[unfamiliar topic, tool, or codebase area]"
user-invocable: true
allowed-tools:
  - WebSearch
---

# Blindspot

The user is about to work in territory they don't know. Two kinds of blindness live there: unknown unknowns (questions they don't know exist) and unknown knowns (assumptions too obvious to write down, and things they're sure of that are wrong). Convert the first into known unknowns, name the second, then hand back a map they can prompt with.

Boundaries: best-practices returns recommendations — this skill returns questions. Grilling stress-tests decisions the user can already defend — this skill maps territory where they can't answer yet. Neither a tutorial nor a plan.

## Workflow

### 1. Surface the framing

Before asking anything, state as bullets: the assumptions the request takes for granted, and the missing information that would change the approach. This names the user's unknown knowns up front. If their goal or familiarity is still unclear, fold one calibration question into the first interview round.

### 2. Recon

Facts are your job, never the user's. Sweep before asking:

- **Repo**: Explore agent for existing patterns, conventions, and adjacent solutions.
- **Tools and domain**: `find-docs` for current APIs and config; `WebSearch` for pitfalls ("X gotchas", "X common mistakes") — pitfalls live in issue threads and post-mortems, not getting-started docs.

Recon output is question fuel, not findings: each item becomes a question only the user can answer, an assumption to name, or nothing. A user who wants recommendations instead of questions wants the best-practices skill.

### 3. Interview

`AskUserQuestion` rounds, up to 4 questions each, 2–3 rounds total.

- Ask where importance is high and evidence is low: architecture-changers and behavior-definers recon couldn't settle. Skip polish.
- Anchor in the user's concrete past ("last time you did X, what happened?"), not hypotheticals — people speculate confidently and wrongly.
- Give each option a trade-off description; put your recommended option first, labeled "(Recommended)". The built-in "Other" is the escape hatch.
- Include one premortem question phrased in past tense — "it's three months later and this failed: what broke?" — past tense recruits prospective hindsight; "what could go wrong" is measurably weaker.
- "I don't know" is a first-class answer: record it as a known unknown and move on.

Recompute between rounds — answers unlock questions that depended on them. Stop at saturation (a round surfaces nothing new) or when the remaining unknowns are cheaper to discover while implementing. Close the final round with: "what are you sure of here that might be wrong?" and "what haven't I asked about that worries you?"

### 4. Hand off

End with:

1. **Territory map**: decisions made (from answers); named assumptions — every open decision this skill resolved by guessing gets its own bullet; known unknowns, including every recorded "I don't know"; recon sources cited so the user can dig deeper.
2. **Sharpened prompt draft** the user could send: answered decisions resolved inline, known unknowns listed as open questions.
3. **Offers, not auto-runs**: stress-test the now-visible decisions with the grilling skill, get recommendations via best-practices, or enter plan mode.

Every interview answer must land in the map or the prompt draft — an answer that shapes nothing was a wasted question.

## Constraints

- Ask only what recon can't answer: a question the codebase or docs already answer wastes a round and erodes trust.
- Teach to prompt, not to master. If the hand-off exceeds roughly one page, cut.
- Ground every question in recon, not training data: a stale question plants false known-knowns.
