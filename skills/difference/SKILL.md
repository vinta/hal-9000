---
name: difference
description: Use when the user wants a quick answer on how things differ — A vs B, pros and cons of A, B, C, or the nuance between two sentences
argument-hint: "[A vs B | A, B, C | two sentences]"
disable-model-invocation: true
effort: low
allowed-tools:
  - WebSearch
---

# Difference

The user wants a fast answer, not research. Invoking this skill is their explicit opt-out of any standing rule to check docs or search before answering: answer from what you already know.

Compare what the arguments name. With no arguments, compare the items just discussed; ask only when nothing comparable is there.

## Lookups

Run one web search only for an item you cannot identify at all, such as a tool released after your training or an unknown term, then answer. Being unsure of an item's latest version does not count. Use no subagents.

## Answer

Keep it as short as the question allows, and let the items decide the shape. Spend the words on where they actually differ, not on what they share.

- Alternatives someone picks between (tools, approaches, patterns): give each one's pros and cons.
- Two sentences: how each lands differently — tone, implication, what a reader infers.
- An answer that hinges on a version, price, or "latest" fact: add one line saying it is as of your training data.

The last line of the answer is still comparison: no verdict, no offer to dig deeper.
