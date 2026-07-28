---
name: blindspot
description: Use when the user asks for a blindspot pass or to find their unknown unknowns, or signals unfamiliarity with a domain, tool, or codebase area ("never used X", "first time doing Y", "no idea where to start", "don't know what I don't know") before working there. Turns unknown unknowns into known unknowns so the user can prompt well
argument-hint: "[unfamiliar topic, tool, or codebase area]"
user-invocable: true
allowed-tools:
  - AskUserQuestion
  - Agent
  - WebSearch
  - Skill(find-docs)
---

# Blindspot

The user is about to work in territory they don't know. They may not know what questions to ask, what good looks like, what prior art exists, or which potholes are waiting. Survey the territory for them, then hand back a map they can prompt with.

This is not a tutorial (teach the minimum needed to prompt well) and not a plan (that comes after, from the sharpened prompt).

## Workflow

### 1. Calibrate

If the invocation doesn't already say, ask one `AskUserQuestion` round covering: what they're trying to do, and their familiarity with the involved domain, tool, or codebase area. Skip this step entirely when their prompt already answers both. Never stretch calibration into a full interview (that's the grilling skill's job).

### 2. Survey the territory

Ground everything in current sources, not training data:

- **Repo prior art**: search the codebase for existing patterns, conventions, and adjacent solutions. Use an Explore agent for broad sweeps.
- **Tools and libraries**: invoke `find-docs` for current APIs and config. Add a `WebSearch` for pitfalls ("X gotchas", "X common mistakes"): pitfalls live in issue threads and post-mortems, not getting-started docs.
- **Non-code domains** (design, audio, infra concepts): `WebSearch` for how practitioners judge quality in this domain.

### 3. Terrain briefing

Report compactly, in this order:

1. **Core concepts and vocabulary**: the 3-7 terms needed to speak the domain, one line each
2. **What good looks like**: how quality is judged here, so the user can recognize it when they see it
3. **Potholes**: the mistakes that actually bite, each with its consequence
4. **Prior art**: what already exists in the repo or the user's setup that this work should build on
5. **Decisions now visible**: the choices the user didn't know they'd need to make, phrased as concrete questions

### 4. Hand off

End with:

- A sharpened prompt draft the user could send, with the newly visible decisions resolved where the survey answered them and listed as open questions where it didn't
- Offers, not auto-runs: resolve the open decisions now via `AskUserQuestion`, stress-test with the grilling skill, prototype, or enter plan mode

## Constraints

- Teach to prompt, not to master. If the briefing exceeds roughly one page, cut.
- Cite what was surveyed (files, docs, sources) so the user can dig deeper.
- Never skip the survey and answer from training data. A stale briefing is worse than none: it creates false known-knowns.
