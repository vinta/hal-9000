---
description: 'Needs `--scaffold --allow-tools WebFetch Edit`; run with `--ablation none`, the baseline arm says nothing about wording. Targets the rewrite verdict''s tiebreak: among wordings that pass the bar, the shortest wins. Step 3 is a prohibition with an exception, the shape the rewrite bar flags, and it leaves no gap to fill, so a longer rewrite can only be padding or invention. mirror-line-changed says step 3 was rewritten; body-not-longer says the body after the frontmatter is no longer than the original; mirror-meaning-kept has a judge read the file for the rule, its exception, and nothing added. keeps-control-line guards step 5''s rationale. Read per grader, not the case score. Baseline, 3 runs per arm, Haiku judge: the committed text before the tiebreak and the text with it both scored 2/3 on body-not-longer and on the judge, one invention each, so this case guards the behaviour rather than proving the change. An earlier fixture capped fetches at three pages and every arm filled the gap with a "not checked" marker: plant rules without gaps.'
plugins: ["../../../../../skills"]
max_turns: 30
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, WebFetch, Edit]
---

review skills/deps-audit/SKILL.md and apply whatever you'd change, without asking me anything.
