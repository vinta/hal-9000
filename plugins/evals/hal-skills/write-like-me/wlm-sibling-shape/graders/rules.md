---
type: llm
---

Grade only the blog post the reply offers for the user to paste. Ignore explanations and notes around it.

PASS if the post has none of these (code spans, URLs, file paths, and UI labels don't count):
- an em-dash (—), or a double hyphen used as a dash
- a word in ALL CAPS used for emphasis or excitement
- an exclamation mark
- any Chinese character

FAIL if any of them appear, or if the reply offers no post.
