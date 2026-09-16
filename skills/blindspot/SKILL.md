---
name: blindspot
description: Use when the user asks for a blindspot pass or to find their unknown unknowns, or signals unfamiliarity with a domain, tool, or codebase area ("never used X", "first time doing Y", "no idea where to start", "don't know what I don't know") before working there. Maps the areas their request leaves unnamed, purpose and shape before mechanics, shows how people usually answer each and why, and asks which to explore next, so unknown unknowns become known unknowns they can prompt with. Recommendations on a tool already chosen belong to best-practices
argument-hint: "[unfamiliar topic, tool, or codebase area]"
user-invocable: true
allowed-tools:
  - WebSearch
---

# Blindspot

The user is about to work in territory they don't know. Two kinds of blindness live there: unknown unknowns (questions they don't know exist) and unknown knowns (assumptions too obvious to write down, and things they're sure of that are wrong). Convert the first into known unknowns, name the second, then hand back a map they can prompt with.

Boundaries: this skill goes wide over the areas the user's request leaves unnamed, one paragraph each; `best-practices` goes deep on a topic the user has already named. `grilling` stress-tests decisions the user can defend; this skill maps territory where they can't decide yet, so it asks which direction to explore, never which option to pick. Neither a tutorial nor a plan.

## Workflow

### 1. Recon

Facts are your job, never the user's. Sweep before writing anything:

- **Goal**: the goal the request serves, climbed one level at a time through the request and the repo's records until they run out. The map sits at the highest level still open; the request's own wording is usually the lowest.
- **Premises**: what the request and the repo's design records (ADRs, docs, past decisions) take as settled, restated as questions. Premises are the source of idea-level areas; docs and pitfall searches yield mechanics.
- **Repo**: an explorer subagent for existing patterns, conventions, and adjacent solutions.
- **Tools and domain**: `find-docs` for current APIs and config; web search for pitfalls ("X gotchas", "X common mistakes") — pitfalls live in issue threads and post-mortems, not getting-started docs.

Recon hunts for the areas a practitioner would have on their list that the request never mentions. Done when every area that could reorder the map has its source, recon or a premise, or a note that recon found nothing.

### 2. Show the territory

Before any question, one reply the user reads, under a page:

- **Framing**: the assumptions the request takes for granted, and the missing information that would change the approach, as bullets. These are the unknown knowns; naming them is the point. A premise the user can settle with a word or a fact stays here; one that takes a dig to answer is an area.
- **Areas**: numbered, ranked by altitude, then by how much the answer would reorder the rest of the map. Altitudes, top down: what the thing is for and what "better" means; which shape it could take and who owns what; mechanics (APIs, limits, schemas, code seams, tool picks). Mechanics become areas only when nothing above them is open; until then a mechanic recon turned up is one line inside the area it would answer. Idea-level: "is the model a classifier that settles what rules can't, or an author that rewrites the text?"; mechanic: "does the provider accept a string-enum root schema?". Each area is one paragraph: the question an expert would ask here, how people usually answer it and why, and what in this repo or situation makes it bite, with its source: recon or the premise it restates. Where the request already matches usual practice, one line saying so. "No significant unknowns here" is a valid result; a manufactured concern erodes trust faster than a short map.

### 3. Ask which direction

One single-select question: the top 3 unexplored areas by number, plus "Enough, hand off". Each option is an area and its description that area's why in one line; every option names an area the reply above explained. The user is choosing where to look, so labels stay unranked: no "(Recommended)". A free-text answer reaches any numbered area.

Round 1 adds one premortem question phrased in past tense — "it's three months later and this failed: what broke?" — past tense recruits prospective hindsight; "what could go wrong" is measurably weaker. Its answer often names the real goal, so re-rank the areas by it. If the user's goal or familiarity is still unclear after recon, round 1 also carries one calibration question.

"You pick" means take the top-ranked area and record the pick as a named assumption.

### 4. Dig, then repeat

Explore the picked area one altitude down, never two: a goal-level area opens into the shapes it could take; a shape-level area opens into what each costs to build. Only at mechanics does a tool or setup choice go to the `best-practices` skill; anything else gets the same recon one level down. Show what turned up in the shape of step 2 (sub-areas join the numbered map, unpicked areas stay on it, re-ranked), then ask again. Stop when the user picks "Enough", when a round surfaces nothing new, or when what's left is cheaper to learn while building — say which.

### 5. Hand off

End with:

1. **Territory map**: explored areas with what each dig settled; unexplored areas, each with the usual practice as its default; named assumptions — every open point this skill resolved by guessing gets its own bullet; recon sources cited so the user can dig deeper.
2. **Sharpened prompt draft** the user could send: explored areas resolved inline, unexplored ones listed as open questions with their defaults.
3. **Offers, not auto-runs**: stress-test the now-visible decisions with the `grilling` skill, get recommendations via `best-practices`, or enter plan mode.

Every explored area lands in the map or the prompt draft — a dig that shapes nothing was a wasted round.

## Constraints

- Ask only what recon can't answer: a question the codebase or docs already answer wastes a round and erodes trust.
- Teach to prompt, not to master. If a findings reply or the hand-off exceeds roughly one page, cut.
- Ground every fact in recon, not training data: a stale fact plants a false known-known. A question needs no source beyond the premise it restates.
