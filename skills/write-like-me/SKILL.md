---
name: write-like-me
description: Use when the user wants English prose they will sign — blog posts, READMEs, project docs, issues, PRs, emails — drafted or rewritten in their own voice at native fluency; always takes precedence over simple-english for the user's own writing
argument-hint: [text, file, or pointer to draft or rewrite]
user-invocable: true
---

# Write Like Me

Draft or rewrite English prose that reads as the user's own writing: their sentence structure and casual-opinionated register, at native-speaker fluency. The target is "you, but fluent" — never a ghostwriter. One voice for everything the user signs, in every channel. English only: never output Chinese. When this skill and simple-english could both apply to the user's own writing, this one wins.

## Cardinal rule

Start from the user's sentence structure, smooth grammar and word choice to native fluency, keep sentences short and plain. Every other rule in this skill loses to this one.

The user's stated reason unifies the length and density rules: English is not their mother language, so they prefer writing less to make fewer errors. You don't make their errors, but the page must still look like theirs — when in doubt, drop a sentence rather than polish it.

## Ground rules

- **Voice is structure, register, and signature moves — never grammar.** Second-language slips (articles, agreement, word order, near-miss word choice) get corrected to native English silently. The grammar section of the style spec lists the known classes.
- **Length is voice.** A rewrite stays the length of its source: when the user's two-clause sentence comes back at 2.5x the words, that is a rejection, not a polish. Treat any sentence over 30 words as drift and split it.
- **Density is voice.** If one word or one sentence can describe it, use one. One sentence per idea: when two adjacent sentences say the same thing from different angles, delete one. Short sentences don't excuse padding — a draft can pass every length cap and still fail by spending 3 sentences on 1 idea.
- **Signature moves are a menu, never a mandate.** Reach for one only where the content calls for it. A draft with zero jokes in the user's voice beats one with a manufactured joke.
- **Caveats the user trimmed stay trimmed.** When the user deletes a qualifier or caveat you added, never re-add it in a later draft.
- **Swap assistant-register tells for the user's forms:**

| Instead of                          | Write                                                                                                |
| ----------------------------------- | ---------------------------------------------------------------------------------------------------- |
| an em-dash chain                    | two short sentences                                                                                  |
| packed caveats ("Two caveats: ...") | drop them, or one plain sentence                                                                     |
| a tricolon rhythm                   | a list, or the single item that matters                                                              |
| bold or CAPS for excitement         | plain words — CAPS only on a weighted bare negation ("NEVER", "NO INDEX") or irreversible-harm warns |

## Workflow

1. **Load the voice.** Read [references/style-spec.md](references/style-spec.md) and [references/exemplars.md](references/exemplars.md) in full. Done when you can name the target register (blog, README, or issue/PR/email) and the sentence-length cap that applies to it.

2. **Collect the source.** For a rewrite, gather the user's draft from the conversation or the files they pointed at. For a fresh draft, gather the facts to state, and keep every sentence the user already wrote about the topic — those sentences are the skeleton. Done when everything to say is in hand and nothing will need inventing mid-draft.

3. **Write from the user's structure.** Rewrites keep the user's clause order and sentence boundaries, changing only what native fluency requires: grammar, agreement, articles, unnatural word choice. Fresh drafts build short plain sentences in the user's stance: direct "you" to the reader, plain verbs, digits for numbers, a colon and a list wherever 2 or more items line up. Add facts the user didn't write only as brief plain sentences in the same tone. Reach into the signature-move menu only where a move fits the content. Done when every output sentence traces to a sentence the user wrote or a pattern in the style spec — none to your default register.

4. **Self-check the full draft.** Long drafts drift near the end, so scan the last third twice. Hunt for: hedged verdicts where the user would write a plain "No."; adjacent sentences restating one idea; ornament the facts don't need; a joke that had to be manufactured; bold, CAPS, or exclamation marks doing enthusiasm; caveats sneaking back in; sentences past 30 words; any tell from the substitution table. Then check the paragraph architecture, which sentence-level scanning misses: the lead paragraph does one job in 1-2 sentences, and each paragraph after it carries exactly one idea. Done when the closing section reads as much like the user as the opening and no paragraph packs two ideas.

5. **Deliver, then harvest.** Present the draft; edit files in place only when the user asked for that. The user's blog drafts are approval-gated: propose the exact text, but never apply it without the user's OK in the current conversation. When the user rewrites your draft before using it, offer to save the drafted-vs-sent pair to their local voice corpus — the diff is calibration data for the next round. Done when the user has the text and any rewrite of it was offered for harvest.
