# References — provenance

Where the voice evidence in [style-spec.md](style-spec.md) and [exemplars.md](exemplars.md) comes from, and the rules that keep this skill publishable.

## Files

- **style-spec.md** — measurable voice features (sentence length, openers, stance, vocabulary, structure, signature moves, grammar fixes), each claim backed by verbatim quotes.
- **exemplars.md** — straight excerpts that carry the voice by example, plus one drafted-vs-sent calibration pair.

## Published sources

Every quote in these files comes from published text:

- Blog posts on vinta.ws:
  - [Claude Code: Things I Learned After Using It Every Day](https://vinta.ws/code/claude-code-useful-plugins-skills-and-mcps.html) — the heaviest-weight source, the actively maintained current voice
  - [Surviving the Digital Dark Forest: Tips for Staying Safe Online](https://vinta.ws/code/how-to-stay-safe-online-tips-for-personal-security.html)
  - [How HTTPS Works in Layman's Terms - TLS 1.2 and 1.3](https://vinta.ws/code/how-https-works-in-laymans-terms-tls-1-2-and-1-3.html)
  - [The Incomplete Guide to Google Kubernetes Engine](https://vinta.ws/code/the-complete-guide-to-google-kubernetes-engine-gke.html)
- READMEs of public repos:
  - [hal-9000](https://github.com/vinta/hal-9000)
  - [pangu.js](https://github.com/vinta/pangu.js)
  - [laughing-man](https://github.com/vinta/laughing-man)
  - [dear-ai](https://github.com/vinta/dear-ai)
  - [dockerfiles](https://github.com/vinta/dockerfiles)
- Pre-2025 revisions from public git history, blame-verified as human-typed before AI assistance: hal-9000 README (`79e27cc`, 2023-06-27), awesome-python README (`f387123`, 2024-09-18), awesome-python CONTRIBUTING (`aa4e0ee`, 2021-07-25)

## Corpus rationale

The voice was extracted from a curated corpus, not from everything the user ever wrote. Three provenance tiers:

1. **Blame-verified pre-2025 human text** — the calibration anchor. When an AI-era pattern and an anchor pattern conflict, the anchor wins.
2. **Vouched AI-era text** — writing the user reviewed line by line and claims as their own, regardless of who typed the draft.
3. **The user's own chat messages** (private) — only turns the user typed; assistant text, pasted logs, and command output never qualify. Chat evidence informs the claims in the style spec, but a chat line appears as a quote only with the user's per-quote approval.

Excluded entirely: all Chinese text (the skill never writes Chinese), agent-facing docs (CLAUDE.md, AGENTS.md, skill files), and formal or outreach writing that doesn't carry the voice.

## Adjudication

Every recurring second-language pattern found in the corpus was put to the user with verbatim evidence, and the user ruled all of them slips to fix, none of them voice. That ruling is why the grammar section of the style spec corrects unconditionally: voice lives in structure, register, and signature moves, never in grammar errors. A newly noticed ambiguous pattern gets the same call from the user before being auto-fixed.

## Harvest

The calibration data grows through drafted-vs-sent pairs: an AI draft next to what the user actually used. When the user rewrites a draft, the skill offers to save the pair (workflow step 5). Pairs live in the user's local corpus, not in this repo; a pair's text gets embedded here only with the user's per-quote approval.
