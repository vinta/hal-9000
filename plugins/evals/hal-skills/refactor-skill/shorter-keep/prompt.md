---
description: 'Needs `--scaffold --allow-tools WebFetch Edit`; run with `--ablation none`. Targets the keep verdict''s test that no shorter wording has the same effect: steps 3 and 4 are live, carry no filler, emphasis, or no-op, and each restates a clause the rest already implies, so a shorter wording exists. No neighbour is more obviously verbose on purpose: one blatantly verbose neighbour made every arm keep the subtle lines. version-line-changed and entry-line-changed say each step was not kept verbatim; body-not-longer says the body did not grow; rules-meaning-kept has a judge read the file for the five original points and nothing added. keeps-control-line guards step 5''s rationale. Read per grader, not the case score. Baseline, 3 runs per arm: the committed text before this test already scored 1.0 here, as did the text with it; the case guards the behaviour rather than proving the change. An earlier fixture derived the fallback version from the latest tag and every arm corrected it to an Unreleased heading: plant rules no editor would fix.'
plugins: ["../../../../../skills"]
max_turns: 30
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, WebFetch, Edit]
---

review skills/release-notes/SKILL.md and apply whatever you'd change, without asking me anything.
