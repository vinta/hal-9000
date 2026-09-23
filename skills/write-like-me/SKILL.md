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

| Instead of                               | Write                                                                                                                                            |
| ---------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| an em-dash chain                         | two short sentences                                                                                                                              |
| packed caveats ("Two caveats: ...")      | drop them, or one plain sentence                                                                                                                 |
| a tricolon over unlike items             | a list, or the single item that matters; a three-beat over matched cases stays (style spec section 8)                                            |
| a template phrase over unlike list items | each item standing alone; matched phrasing stays where the items are matched cases (style spec section 8)                                        |
| bold or CAPS for excitement              | plain words — CAPS only on a weighted bare negation ("NEVER", "NO INDEX") or irreversible-harm warns                                             |
| three or more nouns in a row             | a preposition or a verb between them; proper names, fixed terms, and a tagline's leading search phrase stay — name the cost once, the user picks |

## Workflow

1. **Load the voice.** Read [references/style-spec.md](references/style-spec.md) and [references/exemplars.md](references/exemplars.md) in full. Done when you can name the target register (blog, README or its one-line tagline, issue/PR/email, or code comments) and the sentence-length cap that applies to it.

2. **Collect the source.** For a rewrite, gather the user's draft from the conversation or the files they pointed at. Prose already in the user's files is facts, never voice, unless the user vouched it line by line: an unvouched comment or doc is rewritten from what it states, not from its phrasing. For a fresh draft, gather the facts to state, and keep every sentence the user already wrote about the topic — those sentences are the skeleton. The ask is the user's sentence, never the invoker's paraphrase: when you wrote the skill arguments yourself, re-read the user's message and drop every goal it does not state — a request for fancy AI words asked for discoverability nouns, and the invented "keep the humor" produced three rejected jokes. Before naming a feature or picking a term, grep the user's docs in the current repo: reuse a named feature verbatim, capitals included, and prefer a word those docs already use over the style spec's vocabulary or a search term; the sentences around that word stay facts. Done when everything to say is in hand and nothing will need inventing mid-draft.

3. **Write from the user's structure.** Rewrites keep the user's clause order and sentence boundaries, changing only what native fluency requires: grammar, agreement, articles, unnatural word choice. That holds for prose the user wrote as prose; a sentence they typed in chat to explain something is raw material, so keep its facts and terms and build the sentence fresh. Fresh drafts build short plain sentences in the user's stance: direct "you" to the reader, plain verbs, digits for numbers, a colon and a list wherever 2 or more items line up. Add facts the user didn't write only as brief plain sentences in the same tone. Reach into the signature-move menu only where a move fits the content. When offering words for a feature phrase, check what each head noun implies about the rest of the product before ranking by sound: `fixes` blamed the regex rules, `fallback` made the AI optional, `smarts` hyped it. Rank options by exactness and concreteness, never by plainness: plain is not vague, and the user's pick has been the exact verb over the generic one (`distinguish` over `handle`), the casual word over the formal (`totally` over `completely`), and the concrete fragment over the hedge against staleness (`in seconds on a cheap model`). Done when every output sentence traces to a sentence the user wrote or a pattern in the style spec — none to your default register.

4. **Self-check the full draft.** Long drafts drift near the end, so scan the last third twice. Hunt for: hedged verdicts where the user would write a plain "No."; adjacent sentences restating one idea; ornament the facts don't need; a joke that had to be manufactured; bold, CAPS, or exclamation marks doing enthusiasm; caveats sneaking back in; sentences past 30 words; any tell from the substitution table. Then check the paragraph architecture, which sentence-level scanning misses: the lead paragraph does one job in 1-2 sentences, and each paragraph after it carries exactly one idea. Done when the closing section reads as much like the user as the opening and no paragraph packs two ideas.

5. **Deliver, then harvest.** When another skill's workflow invoked you, hand the exact text back to that workflow and continue with its next step in the same turn: the draft is that workflow's input, not your final answer, and the rest of this step does not apply. Otherwise, present the exact text and stop; never ask whether to apply it, since the proposal is the question and the user answers by saying so or by writing their own version. Edit files in place only when the user asked for that; blog drafts are approval-gated and never applied without the user's OK in the current conversation. When the source sentence was the user's own, name the grammar fixes you made in the reply: they want to learn them. A fresh draft has nothing to name. When the user answers with their own version, often followed by a lone "?", they want a review, never a redraft: verdict first, at most 2 nits on facts and grammar, then the exact line to paste. A grammar or native check on the user's own line fixes the slip and keeps their verb and noun: offer objects that pair with their word, never an idiom that replaces it ("distinguish semantic" came back as "tell apart" twice and the user restored their words both times; published: "distinguish semantic nuances"). "Shorter?" means one notch shorter with the sentence shape kept; the bare minimum got "too short". For code comments that is the normal path, since the user writes the final version. When the user rewrites your draft before using it, offer to save the drafted-vs-sent pair to the user's local corpus, in the format of the pairs already there; ask where the corpus lives if you don't know — the diff is calibration data for the next round. Done when the user has the text and any rewrite of it was offered for harvest.
