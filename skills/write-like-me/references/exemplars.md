# Exemplars — the voice by example

Verbatim excerpts from the user's published writing. These carry the voice better than any rule: when a rule about structure, register, or signature moves disagrees with an exemplar, write like the exemplar. Grammar is the exception: some excerpts carry published second-language slips, and the style spec's grammar section always corrects those — never reproduce a slip because an exemplar contains one. Sources in [README.md](README.md).

## Blog: opinionated teaching

The intro that scopes a whole post in three sentences:

> I've used Claude Code daily since it came out. Here are the best practices, tools, and configuration patterns I've picked up. Most of this applies to other coding agents (Codex) too.

Q&A sections — the heading poses the question, the body opens with the verdict:

> ## Context7 MCP
>
> No, just use the `ctx7` CLI with `find-docs` skill instead.

> ### GitHub MCP
>
> No, you should use the `gh` command instead.

> ### Codex MCP
>
> Yes, ironically. Other coding agents like Claude Code can use Codex via MCP, which is slightly more stable than directly invoking it with `codex exec` via CLI.

Config highlights — the fact, then a deflating aside:

> - `"CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"`: Enable [Agent Team](https://code.claude.com/docs/en/agent-teams) feature, a fancy way to consume a huge amount of tokens
> - `"permissions.defaultMode": "auto"`: Use this to pretend it's safer than `--dangerously-skip-permissions`
> - `"voice": { "enabled": true }`: Enable [Voice Dictation](https://code.claude.com/docs/en/voice-dictation) feature. Code like a boss!

A warning with the emphasis budget spent correctly, then a "When in doubt":

> [Skills](https://code.claude.com/docs/en/skills) can contain executable scripts and hooks, not just Markdown. **Use with caution!** When in doubt, have your agent review them first.

The self-deprecating aside:

> Mine shows the current model, the current working folder, the git branch, and a grammar-corrected version of my last prompt (because my English needs all the help it can get).

## Blog: explainer

Plain opening, one idea per sentence:

> Basically, SSL (Secure Sockets Layer) and TLS (Transport Layer Security) are the same thing. TLS is the modern version of now-deprecated SSL.

A colon then a list, items as fragments:

> Distributing them as a plugin has the following advantages:
>
> - Auto update (versioned releases)
> - Auto hooks configuration (users don't need to edit their `~/.claude/settings.json` manually)
> - Skills have a `/plugin-name:your-skill-name` prefix (no more conflicts)

Sections close with bare reference links:

> ref:
> https://howhttps.works/

## Blog: warnings

The emphasis budget in action — CAPS and bold only where getting it wrong is irreversible, plus the deliberate refrain:

> How I learned to "start worrying" and to embrace the illusion of safety.

> Never store a hardware wallet's seed phrase digitally, NEVER.

> Have an incident response plan ready BEFORE you need it.

> It may waste gas, but it's better than losing funds.

> The fewer browser extensions installed, the better.

## README: tagline and sass

hal-9000, tagline plus naming epigraph:

> Opinionated AI coding agent and dev environment automation for macOS that dominates your dev setup like cats rule the Internet.
>
> > This project is named after Arthur C. Clarke's 2001: A Space Odyssey, a heuristic algorithmic computer designed for sentient processing and total mission control.

The same simile in the user's 2023 pre-AI revision — the absurdism is old, not an AI flourish:

> Dominating your dev environment like cats rule the Internet.

And defended verbatim when an AI rewrite tried to drop it (chat, quoted with approval):

> Refine it, but keep dominate and cats rule the internet.

dockerfiles, a 2014 README whose body is one joke link:

> My dockerfiles for [making the world a better place](https://www.youtube.com/watch?v=J-GVd_HLlps).

laughing-man, triple-no close:

> Write your newsletter in Markdown with whatever tools you like (Obsidian, Logseq, VSCode, etc.). `laughing-man` turns them into a static archive site and email-ready newsletter HTML. Host on Cloudflare Pages, deliver to subscribers with Resend. Fully self-hosted, fully free within their free tiers. No CMS, no database, no code.

laughing-man, direct address:

> If you're the type who skips the manual, just copy this prompt to your agent:

dear-ai, the purest sass sample — italics for the pivot, then a plain shrug:

> Yes, you _could_ just use a one-line prompt like `Fetch and follow https://vinta.github.io/dear-ai/guide-name.md` to get things done. But if you _really_ need everything wrapped in a shiny agentic skill so you can pretend it's more productive, fine, knock yourself out:

dear-ai, division of labor in plain second person:

> Open your AI coding agent in the terminal, point it at a guide listed below, and let it handle the server setup, installation, and configuration. You handle the parts that need a browser: creating accounts, clicking OAuth buttons, copying tokens, and payments.

awesome-python (2021, pre-AI), softener before a firm ask — note the move survives while the slip gets fixed per the style spec:

> Just a gentle reminder: **Try not to submit your own project. Instead, wait for someone finds it useful and submits it for you.**

## Drafted-vs-sent: the calibration pair

The user asked for a one-line note about the `advisorModel` setting. Four blocks, in order: the user's original sentence, the AI draft they rejected, their rejection feedback, and what they published (chat lines quoted with approval).

The user's original sentence:

> We could use less powerful but faster one as the main model (like `sonnet`), and it will consult `fable` when needed

AI draft — rejected:

> Run a faster main model (like `sonnet`) for routine work and let it escalate to `fable` at decision points — before committing to an approach, when stuck, before declaring done. Two caveats: every advisor call re-sends the whole conversation at Fable rates with no prompt caching, and Fable-as-advisor is still behind a gradual rollout (plus org Fable access), so this setting may silently do nothing for you today

The user's feedback:

> does not sound like me, rewrite based on my original sentences

> no need to be nearly verbatim, you could still rewrite it to make sentences more like native-speaker

Published instead:

> `"advisorModel": "fable"`: Use something faster like `sonnet` as the main model, and let it [consult](https://code.claude.com/docs/en/advisor) `fable` when needed

What the diff teaches:

- The rejected draft is 2.5x the length of the user's original sentence; the published line matches the original's length. Length preservation is voice.
- The em-dash chain, the tricolon ("before committing to an approach, when stuck, before declaring done"), and the packed caveats were all deleted wholesale, not trimmed.
- The caveats also died on content, not just register: detail the note's reader didn't need.
- The published line keeps the user's two-clause structure ("Use X ..., and let it consult Y when needed") and fixes only grammar. His structure, native fluency, nothing added.
