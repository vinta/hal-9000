---
name: simple-english
description: Use when the user wants text rewritten in ASD-STE100 Simplified Technical English, or wants docs, articles, or paragraphs made easy for readers with limited English
argument-hint: [text, file, or pointer to rewrite]
user-invocable: true
---

# Simplified Technical English (ASD-STE100)

Rewrite the given text in ASD-STE100 Simplified Technical English (STE) Issue 9: 53 writing rules plus a controlled dictionary in which each approved word has one meaning and one part of speech. The rewrite must give the same technical facts as the source and be clear on first reading for a person with limited English.

## Ground rules

- **Meaning is untouchable.** Every fact, value, condition, and safety implication in the source survives the rewrite. When STE forces a restructure (passive to imperative, note to work step, sentence split), the information moves with it.
- **Never invent specifics.** STE demands concrete sentences, but missing data is the author's to supply. Keep the fact at its original precision and flag the gap. Do not fabricate values, part names, or conditions.
- **Quoted text is frozen.** Code spans and blocks, commands, config keys, file paths, UI labels, error messages, titles, placard and label text, and part identifiers stay exactly as they are. Rewrite the prose around them. Each counts as one word.
- STE fits procedural and descriptive technical text. For narrative or marketing prose, tell the user the tone will flatten, then proceed.

## Workflow

1. **Load the rules.** Read [references/writing-rules.md](references/writing-rules.md) in full: all 53 rules, the technical noun and technical verb categories, the word-selection algorithm, the dictionary lookup protocol, the recurring-errors table, and the approved verb list.

2. **Collect the source.** Take the text from the conversation, or Read the files or sections the user pointed at. Done when you hold every passage to rewrite.

3. **Classify each passage** as procedural (imperative, 20 words per sentence), descriptive (25 words per sentence, 6 sentences per paragraph), or safety instruction. The classification decides which rules bind each sentence.

4. **Build the term list.** Sort every content word in the source into: approved dictionary word, technical noun or technical verb (must fit a category from the reference; prefer the project's established names), or needs-replacement. Grep the dictionary per the lookup protocol for any word you are not certain about. Approval is a lookup, not a guess: common words like "check", "test", "damage", "follow", and "ensure" fail in surprising ways.

5. **Rewrite sentence by sentence.** Apply the word-selection algorithm for needs-replacement words: word-for-word only when the alternative keeps the part of speech and the meaning, otherwise rebuild the sentence around an approved construction. One name per item, one wording per repeated action, condition before command. Filler that serves no task ("it should be noted that", hedges, throat-clearing) drops freely. Facts never drop, and softened obligations never harden ("should" stays a recommendation unless the source means a requirement).

6. **Verify every sentence** against this checklist, counting words per the STE counting rules (8.4 thru 8.7):
   - Length within the limit for its type, paragraphs within 6 sentences
   - Verbs: only approved tenses, no "-ing" outside technical nouns, active voice (descriptive text may keep a passive only when the agent is unknown), no phrasal verbs
   - Procedures: imperative, one instruction per sentence, no instructions or limits hiding in notes
   - Every word: approved with the right meaning and part of speech, a listed technical noun or verb, or quoted text
   - No semicolons, no contractions, no dropped articles or subjects
   - Safety instructions: warning for injury risk, caution for damage risk, command or condition first, then the risk explained
   Done when every sentence passes, or its deviation is deliberate and appears in the report.

7. **Deliver.** Present the rewrite. Edit files in place only when the user asked for the files to change. After the rewrite, report only what applies:
   - Technical nouns and technical verbs you assumed, so the user can check them against their glossary
   - Judgment calls where the source was ambiguous and the rewrite picks one reading
   - Gaps where STE wants specifics the source does not give
