# Global English Rules for Technical Writing

A synthesis of the global-audience guidance that mainstream tech documentation teams use: the Google and Microsoft style guides, MDN, Red Hat, GitLab, John Kohl's Global English, and the US Federal Plain Language Guidelines. Sources with links are in [README.md](README.md).

These are guidelines, not a controlled language. Kohl's cardinal rule governs every edit: make no change that sounds unnatural to a native speaker. When a rule fights naturalness or accuracy in a specific sentence, the sentence wins.

## Paragraphs

- One topic per paragraph. When the topic shifts, start a new paragraph.
- State the point in the first sentence, then support it. A reader who scans only the first sentence of each paragraph must still get the outline of the document.
- Keep paragraphs short. A paragraph that runs past more than a few sentences is a split candidate.

## Sentence structure

- Standard word order: subject, verb, object. Keep the subject and verb early in the sentence.
- One idea per sentence. A sentence with more than a few commas is a rewrite candidate: split it or restructure it.
- Condition before instruction: "If the light is red, stop the test", not "Stop the test if the light is red". The reader must know the condition before acting on the command.
- Active voice and present tense by default. Imperative mood in procedures. Passive is acceptable when the actor is unknown or irrelevant and active phrasing would be forced.
- Avoid future tense where present works: "The command prints a summary", not "The command will print a summary".
- Link at most two, and never more than three, clauses with "and", "or", "but".
- Front-load the real subject instead of "there is" / "there are": "The config file has three sections", not "There are three sections in the config file".
- Replace complex sentences and dense paragraphs with lists and tables. Give parallel ideas parallel structure, in running prose as well as in list items.
- Limit sentence fragments. In short headings and UI labels, include a verb when clarity needs it: "Access is denied", not "Access denied".

## Word choice

- Prefer the simple word: use (not utilize), start (not commence), so (not consequently), some (not "a number of"). Substitution table below.
- One word per concept, used consistently, with identical capitalization. Never synonyms for variety, and never one word for two concepts.
- Avoid phrasal verbs when a single verb exists: "This guide uses the following terms", not "makes use of". Established exceptions stay: set up, log in, sign in.
- Uncover hidden verbs: keep the action in the verb, not in an abstract noun. "Install the package", not "perform an installation of the package". "Decide", not "make a decision".
- "Because" for cause. Keep "since" and "as" for time.
- No idioms, colloquialisms, humor, or culture-specific references (holidays, sports, seasons, geography). They confuse readers and break translation.
- No Latin abbreviations: write "for example" (not e.g.), "that is" (not i.e.), "and so on" (not etc.), or restructure.
- Define an abbreviation at first use. Prefer common abbreviations (USB, API) over invented ones.
- No directional cross-references like "above" or "below". Link to the section or name it: "as described in Configuration".
- Write dates and times unambiguously (2026-07-21, not 7/21/26). Use diverse example names.

## Clarity helpers (keep the small words)

Translation and comprehension fail on omitted function words. Keep them:

- Keep "that" and "who": "Verify that all tables were migrated", "the user who owns the file".
- Keep articles: "Empty the container" (verb) vs "The empty container" (noun phrase).
- Keep helper words like "then" and "of" when they mark structure: "If the key is not found, then the default value is returned".
- Repeat a word when the repetition disambiguates: "If the VM has started and if you can connect", "IAM segmentation and network segmentation".
- Replace a pronoun with its noun whenever "it", "this", "they", or "these" could point at more than one thing.
- Put modifiers directly next to the word they modify. Watch "only": "Request only one token", not "Only request one token".
- At most two nouns modifying a third. Break longer noun stacks with prepositions: "limits for the backup", not "backup storage space limits configuration".
- Watch words ending in -ing and -ed, which can be verb, adjective, or noun. Disambiguate with a determiner ("an added functionality"), a form of "be" ("limits that are based on"), or a split sentence.

## Tone and audience

- Address the reader as "you". Reserve "we" for the authoring organization.
- Common contractions are fine (it's, you're, don't). Avoid uncommon ones (mightn't, it'd).
- Prefer positive constructions: say what to do, not only what to avoid. Rewrite a negative as its positive equivalent when one exists ("The build fails only when the cache is missing", not "The build does not fail unless the cache is missing"), and never stack negatives.
- Gender-neutral language. Singular "they" is correct.
- Keep the author's voice. Clarity edits that flatten prose into staccato fragments trade one reading problem for another.

## What this ruleset deliberately does not do

The strict sibling (ASD-STE100) exists for safety-critical, compliance-checked documentation. This ruleset drops, on purpose:

- No approved-word dictionary. Any natural word is available.
- No hard sentence caps. Shortness is a smell threshold, not a rule: explicitness and cohesion beat brevity, and gaming readability scores (Flesch-Kincaid, Hemingway) measurably fails to improve comprehension.
- No banned tenses beyond the future-tense preference. Perfect or progressive forms stay when they are the natural phrasing.
- No imperative-only restriction outside procedures.

## Substitution table

| Instead of                  | Write                    |
| --------------------------- | ------------------------ |
| utilize, leverage           | use                      |
| commence, initiate          | start                    |
| terminate                   | stop, end                |
| prior to                    | before                   |
| subsequent to               | after                    |
| in order to                 | to                       |
| in the event that           | if                       |
| a number of                 | some, many               |
| consequently, therefore     | so                       |
| additionally, furthermore   | also                     |
| approximately               | about                    |
| assistance                  | help                     |
| attempt                     | try                      |
| demonstrate                 | show                     |
| facilitate, enable (people) | help, let                |
| regarding, concerning       | about                    |
| sufficient                  | enough                   |
| robust, seamless, powerful  | (the checkable claim)    |
| cutting-edge, blazing-fast  | (the version or number)  |
| it is recommended that you  | we recommend that you    |
| there is/are ... that       | (front-load the subject) |

The table is a default, not a dictionary. When the longer word is the precise term of art (for example "terminate" for POSIX process semantics), the term of art wins and stays consistent.
