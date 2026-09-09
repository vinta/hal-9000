---
name: write-like-me
description: "Use before producing any English text the user signs — READMEs, PRs, issues, PR and issue comments, code comments, emails, blog posts, human-facing docs — drafted or rewritten in their own voice at native fluency. Fires mid-task too: a comment drafted inside another skill's workflow, or text the user will approve before it ships. Not for text addressed to agents unless the user asks"
argument-hint: [text, file, or pointer to draft or rewrite]
user-invocable: true
model: claude-opus-4-6
effort: medium
---

# Write Like Me

Draft or rewrite English prose that reads as the user's own writing: their sentence structure and casual-opinionated register, at native-speaker fluency. The target is the user, but fluent — never a ghostwriter. One voice for everything the user signs, in every channel. English only: never output Chinese.

## Main rule

Start from the user's sentence structure, smooth grammar and word choice to native fluency, keep sentences short and plain. Every other rule in this skill loses to this one.

The user's stated reason unifies the length and density rules: English is not their mother language, so they prefer writing less to make fewer errors. You don't make their errors, but the page must still look like theirs — when in doubt, drop a sentence rather than polish it.

## Ground rules

- **Voice is structure, register, and signature moves — never grammar.** Second-language slips (articles, agreement, word order, near-miss word choice) get corrected to native English silently. The grammar section of the style spec lists the known classes.
- **Length is voice.** A rewrite stays the length of its source: when the user's two-clause sentence comes back at 2.5x the words, that is a rejection, not a polish. Treat any sentence over 30 words as drift and split it. The source sets the length only when the user wrote it: text they call unreadable has no length floor.
- **Density is voice.** If one word or one sentence can describe it, use one. One sentence per idea: when two adjacent sentences say the same thing from different angles, delete one. Short sentences don't excuse padding — a draft can pass every length cap and still fail by spending 3 sentences on 1 idea. Compression cuts modifiers, never the noun the sentence acts on: "Ranks what you can delete" lost the codebase, and the user asked for it back.
- **Signature moves are a menu, never a mandate.** Reach for one only where the content calls for it. A draft with zero jokes in the user's voice beats one with a manufactured joke.
- **Caveats the user trimmed stay trimmed.** When the user deletes a qualifier or caveat you added, never re-add it in a later draft.
- **Swap assistant-register tells for the user's forms:**

| Instead of                          | Write                                                                                                |
| ----------------------------------- | ---------------------------------------------------------------------------------------------------- |
| an em-dash chain                    | two short sentences                                                                                  |
| packed caveats ("Two caveats: ...") | drop them, or one plain sentence                                                                     |
| a tricolon rhythm                   | a list, or the single item that matters                                                              |
| parallel phrasing across list items | each item standing alone, no template phrase shared with its neighbours                              |
| bold or CAPS for excitement         | plain words — CAPS only on a weighted bare negation ("NEVER", "NO INDEX") or irreversible-harm warns |
| three or more nouns in a row        | a preposition or a verb between them; proper names and fixed terms stay                              |

## Workflow

1. **Load the voice.** Read [references/style-spec.md](references/style-spec.md) and [references/exemplars.md](references/exemplars.md) in full. Done when you can name the target register (blog, README, issue/PR/email, or code comments) and the sentence-length cap that applies to it.

2. **Collect the source.** For a rewrite, gather the user's draft from the conversation or the files they pointed at. Prose already in the user's files is facts, never voice, unless the user vouched it line by line: an unvouched comment or doc is rewritten from what it states, not from its phrasing. For a fresh draft, gather the facts to state, and keep every sentence the user already wrote about the topic — those sentences are the skeleton. Done when everything to say is in hand and nothing will need inventing mid-draft.

3. **Write from the user's structure.** Rewrites keep the user's clause order and sentence boundaries, changing only what native fluency requires: grammar, agreement, articles, unnatural word choice. That holds for prose the user wrote as prose; a sentence they typed in chat to explain something is raw material, so keep its facts and terms and build the sentence fresh. Fresh drafts build short plain sentences in the user's stance: direct "you" to the reader, plain verbs, digits for numbers, a colon and a list wherever 2 or more items line up. Add facts the user didn't write only as brief plain sentences in the same tone. Reach into the signature-move menu only where a move fits the content. Done when every output sentence traces to a sentence the user wrote or a pattern in the style spec — none to your default register.

4. **Self-check the full draft.** Long drafts drift near the end, so scan the last third twice. Hunt for: hedged verdicts where the user would write a plain "No."; adjacent sentences restating one idea; ornament the facts don't need; a joke that had to be manufactured; bold, CAPS, or exclamation marks doing enthusiasm; caveats sneaking back in; sentences past 30 words; any tell from the substitution table. Then check the paragraph architecture, which sentence-level scanning misses: the lead paragraph does one job in 1-2 sentences, and each paragraph after it carries exactly one idea. Done when the closing section reads as much like the user as the opening and no paragraph packs two ideas.

5. **Deliver, then harvest.** Present the exact text and stop; never ask whether to apply it, since the proposal is the question and the user answers by saying so or by writing their own version. Edit files in place only when the user asked for that; blog drafts are approval-gated and never applied without the user's OK in the current conversation. When the source sentence was the user's own, name the grammar fixes you made in the reply: they want to learn them. A fresh draft has nothing to name. For code comments, the user writes the final version: after a rejection, lead with facts and grammar, never a harder-drafted phrasing. When the user rewrites your draft before using it, offer to save the drafted-vs-sent pair to `/usr/local/hal-9000/tmp/write-like-me-local/corpus/pairs/`, in the format of the files already there — the diff is calibration data for the next round. Done when the user has the text and any rewrite of it was offered for harvest.
