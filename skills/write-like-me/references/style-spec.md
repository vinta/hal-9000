# Style spec — the user's voice

Measurable voice features extracted from the user's published writing (see [README.md](README.md) for sources). Quotes are verbatim. When a rule here fights the cardinal rule in SKILL.md, the cardinal rule wins.

For cases no rule below covers, fall back to the user's stance: compress — padding is noise, cut it; verify — check a claim before making it; deflate — never hype anything, including the user's own work; cast — reach for a device only where it fits; repair in public — when something was wrong, say so plainly and fix it in the open.

## 1. Sentence length

Short units everywhere. Blog prose: median ~13 words per sentence, 95th percentile ~30 — treat any sentence past 30 words as drift and split it. README prose runs shorter (median ~9). Issues, PRs, and emails run shortest: verdict or ask first, evidence after. Short is enforced, not accidental: when an AI rewrite came back 2.5x longer, the user rejected it and published a version the same length as their original.

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

## 5. Vocabulary

Plain verbs and casual evaluators; technical nouns exact. The casual layer: "fancy", "evil", "shiny", "knock yourself out", "Code like a boss!". Digits, not number words ("There are 2 types of encryption algorithms"). Slash-pairs as compression: "encrypt/decrypt", "request/response", "username/password". "so-called" as a labeler ("a so-called hybrid cryptosystem").

## 6. Structural habits

- A colon then a list wherever 2 or more items line up; list items are fragments or gerunds.
- A line reading exactly "ref:" followed by naked URLs closes blog sections.
- "Also see:" / "Recommended:" / "The full settings I use:" as one-line lead-ins to link lists.
- A comment per command in shell blocks, jokes allowed ("# open the pod bay doors, please, HAL").
- Bold mid-sentence only for the load-bearing phrase; CAPS only in hard warnings (section 8 budget).

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
- No volatile detail. Facts that will soon be outdated or that depend on a third party's current state (rollout phases, caching or pricing behavior) get cut regardless of phrasing, and so does detail the reader doesn't need.
- No tricolon rhythm.
- Nothing hyped. Features get deflated, including the user's own work.
- Emphasis budget: bold and CAPS spend only on irreversible harm ("Never store a hardware wallet's seed phrase digitally, NEVER."), never on excitement.

## 9. Grammar: slips to fix silently

The user ruled every recurring second-language pattern a slip, not voice: grammar always corrects to native English, and the correction never rewrites sentence structure beyond what the fix requires. Published examples with their fixes:

| Published slip | Native fix |
| --- | --- |
| "ensuring that server is who it claims to be" | "ensuring that the server is ..." (add the dropped article) |
| "In most contexts, both terms are exchangeable." | "... interchangeable." |
| "Since TLS 1.2 supports ..., so we are going to ..." | drop "Since" or "so" — never both |
| "Restart your device regularly, ex: once a week." | "e.g. once a week" |
| "Must change the default username/password of your devices." | "Change the default username/password ..." (bare imperative) |
| "wait for someone finds it useful and submits it for you" | "wait for someone to find it useful and submit it for you" |
| "There is a pair of two keys" | "There is a pair of keys" |
| "setup" as a verb in prose | "set up" (the noun "setup" and headings stay) |

Further slip classes attested in the user's unpublished writing, fixed the same way: embedded-question order ("why it is X?" becomes "why is it X?"); statement-plus-question-mark (invert it in published text); third-person -s drops and tense drift; "worth to X" (becomes "worth Xing"); a missing "to" after verbs like want/seem; "neither" where native English uses "either"; bare "even" for "even if/though"; "at the end" for "in the end"; "how it looks like" (becomes "what it looks like"); plural agreement ("does these" becomes "do these"); "the another" (becomes "the other"). Obvious keyboard scrambles get normalized silently too. A newly noticed ambiguous pattern is the user's call, not yours: ask before treating it as either slip or voice.
