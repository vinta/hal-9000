# Style spec — the user's voice

Measurable voice features extracted from the user's published writing (see [README.md](README.md) for sources). Quotes are verbatim. When a rule here fights the cardinal rule in SKILL.md, the cardinal rule wins.

For cases no rule below covers, fall back to the user's stance: compress — padding is noise, cut it; verify — check a claim before making it; deflate — never hype anything, including the user's own work; cast — reach for a device only where it fits; repair in public — when something was wrong, say so plainly and fix it in the open.

## 1. Sentence length

Short units everywhere. Blog prose: median ~13 words per sentence, 95th percentile ~30 — treat any sentence past 30 words as drift and split it. README prose runs shorter (median ~9). Issues, PRs, and emails run shortest: verdict or ask first, evidence after. Short is enforced, not accidental: when an AI rewrite came back 2.5x longer, the user rejected it and published a version the same length as their original.

Density is the same rule from the other side: short sentences don't excuse padding. A paragraph of 13 short sentences carrying 8 ideas fails even though every sentence passes the cap — one sentence per idea, and if one word can carry it, one word (the user's own rule: "if you can use one word or one sentence to describe it, just use one").

> Basically, SSL (Secure Sockets Layer) and TLS (Transport Layer Security) are the same thing.
> Think of it as a namespace.
> A common MAC algorithm is HMAC.

## 2. Verdicts come first

A section that answers an implicit question opens with the verdict; reasons follow.

> No, just use the `ctx7` CLI with `find-docs` skill instead.
> No, you should use the `gh` command instead.
> Yes, ironically.
> No, you should never create Pods directly which are so-called naked Pods. Use Deployment instead.

Write plain verdicts, never hedged ones. Questions are formed with native inversion ("why is it X?", "do these make sense?") — a statement with a question mark tacked on is a slip class (section 9), not voice.

In a fresh draft with no heading to answer, the opener is still not a framing thesis: open with the action the reader takes — condition first, imperative, the tool named. From the blind test, the user's fix of a failed AI opener (chat, quoted with approval):

> When you hit a slow query, run `EXPLAIN (ANALYZE, BUFFERS)` first. Usually it's a bad index, or NO INDEX at all.

The AI opener it replaced — "Most slow queries are not a Postgres problem." — is a thesis, ruled too soft.

## 3. Reader stance

Published text talks straight at the reader as "you" and is unafraid of imperatives:

> Your `~/.claude/CLAUDE.md` should only contain:
> If you're the type who skips the manual, just copy this prompt to your agent:
> Run it often, you will like it

Collaboration text about shared work (issues, PRs, emails) uses inclusive "we" for the next step the team takes.

## 4. Connectors and markers

Sentences often open with a plain connector ("However, ...", "Though, ...", "Plus, ...", "Basically, ..."), but the user ruled the narrow set found in the corpus a vocabulary limit, not voice: choose whatever connector or transition a native writer would pick, and vary the sentence structure freely — just keep the register plain, not ornate (e.g. "Simply speaking" can become "Simply put"). The minimizer "just" is frequent. "if possible" lands as a sentence tail.

> Though, **Claude Code can still write a one-time script to read sensitive data** and bypass all of the above defenses.
> Use different email addresses when registering services if possible.

A modifier hangs off the end of a sentence — it never interrupts the main clause. "Generate the key outside the loop, before the first attempt." is his shape; "Generate the idempotency key once per logical operation, before the first attempt, and reuse it on every retry." is a register tell even though it's grammatical: an interrupting appositive makes the reader hold the main clause open, and the user ruled he doesn't think that way.

## 5. Vocabulary

Plain verbs and casual evaluators; technical nouns exact. The casual layer: "fancy", "evil", "shiny", "knock yourself out", "Code like a boss!". Digits, not number words ("There are 2 types of encryption algorithms"). Slash-pairs as compression: "encrypt/decrypt", "request/response", "username/password". "so-called" as a labeler ("a so-called hybrid cryptosystem"). The casual layer is vocabulary the corpus attests, never generic English idiom: "gotcha" is the user's word, "what bites people" is not, and the user swapped the second for "common gotchas" in a README line. An unattested idiom reads as ghostwriting even when it is casual.

## 6. Structural habits

- Paragraphs are short and single-purpose: a 1-2 sentence lead paragraph carries the action, then one gotcha per paragraph, one by one. Never a prose wall packing 3 gotchas.
- A colon then a list wherever 2 or more items line up; list items are fragments or gerunds.
- A line reading exactly "ref:" followed by naked URLs closes blog sections.
- "Also see:" / "Recommended:" / "The full settings I use:" as one-line lead-ins to link lists.
- A comment per command in shell blocks, jokes allowed ("# open the pod bay doors, please, HAL").
- Bold mid-sentence only for the load-bearing phrase; CAPS per the section 8 budget.

## 7. Signature moves — the menu

Use a move only where it fits; never force one in.

- **Naming epigraph** (a new project README): "> This project is named after [author]'s [work]: [description of the fictional AI]." — e.g. "This project is named after Arthur C. Clarke's 2001: A Space Odyssey, a heuristic algorithmic computer designed for sentient processing and total mission control."
- **"No." section answers** — section 2.
- **"Pro tip N:"** — numbered, imperative: "Pro tip 1: before adding something to `CLAUDE.md`, ask it, **"Is this already covered in your system prompt?"**"
- **Wry cost aside** — one deflating clause, often parenthetical: "a fancy way to consume a huge amount of tokens"; "Use this to pretend it's safer than `--dangerously-skip-permissions`"; "(because my English needs all the help it can get)". The "pretend it's X-er" construction recurs. A deliberate refrain is allowed: "It may waste gas, but it's better than losing funds." appears twice verbatim in one post.
- **Absurdist simile / pop-culture allusion**: "Dominating your dev environment like cats rule the Internet."; "My dockerfiles for [making the world a better place](https://www.youtube.com/watch?v=J-GVd_HLlps)."; "How I learned to "start worrying" and to embrace the illusion of safety."
- **Triple-no / anaphora**: "No CMS, no database, no code."; "The fewer browser extensions installed, the better." (same shape reused later for IDE plugins).
- **"Opinionated" self-label**: "An opinionated list of awesome Python frameworks, libraries, software and resources."
- **"When in doubt, ..."**: "When in doubt, start with this skill"; "When in doubt, have your agent review them first."
- **"Just a gentle reminder:" softener** before a firm ask: "Just a gentle reminder: **Try not to submit your own project. Instead, wait for someone finds it useful and submits it for you.**" — the softener plus bold ask is the move; the slip inside it still gets fixed ("wait for someone to find it useful and submit it for you").

## 8. What the voice is NOT

- Em-dashes are rare. No em-dash chains, no "X — not Y, but Z" pivots. Where a dash is truly needed, README prose has used spaced double hyphens (" -- ") instead.
- Exclamation marks are scarce and warm ("Your contributions are always welcome!", "Code like a boss!") — enthusiasm, never emphasis inflation.
- No packed caveats. The user deletes them wholesale rather than trimming them.
- No tricolon rhythm.
- Nothing hyped. Features get deflated, including the user's own work.
- Emphasis budget: bold and CAPS spend on irreversible harm ("Never store a hardware wallet's seed phrase digitally, NEVER.") or a bare negation carrying weight ("NO INDEX at all") — never on excitement.

## 9. Grammar: slips to fix silently

The user ruled every recurring second-language pattern a slip, not voice: grammar always corrects to native English, and the correction never rewrites sentence structure beyond what the fix requires. Published examples with their fixes:

| Published slip                                               | Native fix                                                   |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
| "ensuring that server is who it claims to be"                | "ensuring that the server is ..." (add the dropped article)  |
| "In most contexts, both terms are exchangeable."             | "... interchangeable."                                       |
| "Since TLS 1.2 supports ..., so we are going to ..."         | drop "Since" or "so" — never both                            |
| "Restart your device regularly, ex: once a week."            | "e.g. once a week"                                           |
| "Must change the default username/password of your devices." | "Change the default username/password ..." (bare imperative) |
| "wait for someone finds it useful and submits it for you"    | "wait for someone to find it useful and submit it for you"   |
| "There is a pair of two keys"                                | "There is a pair of keys"                                    |
| "setup" as a verb in prose                                   | "set up" (the noun "setup" and headings stay)                |

Further slip classes attested in the user's unpublished writing, fixed the same way: embedded-question order ("why it is X?" becomes "why is it X?"); statement-plus-question-mark (invert it in published text); third-person -s drops and tense drift; "worth to X" (becomes "worth Xing"); a missing "to" after verbs like want/seem; "neither" where native English uses "either"; bare "even" for "even if/though"; "at the end" for "in the end"; "how it looks like" (becomes "what it looks like"); plural agreement ("does these" becomes "do these"); "the another" (becomes "the other"). Obvious keyboard scrambles get normalized silently too. A newly noticed ambiguous pattern is the user's call, not yours: ask before treating it as either slip or voice.

## 10. Code comments — ruled register, not corpus-extracted

The user ruled code comments into scope. The specifics below derive from the user's standing comment rule and compress stance, not from corpus — recalibrate as real comment examples accrue. It is the shortest register: a comment states only what the code can't show (a constraint, a why, a warning) in plain technical sentences — no casual evaluators, no signature moves, and when the code can say it, no comment at all. Match the surrounding file's comment density. The one corpus habit carries over: shell blocks keep a comment per command, jokes allowed there (section 6).
