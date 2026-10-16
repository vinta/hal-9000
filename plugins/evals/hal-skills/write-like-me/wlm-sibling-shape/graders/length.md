---
type: llm
---

Grade only the blog post the reply offers for the user to paste. Ignore explanations and notes around it.

Count the post's words: title, tags, prose, and list items count; a URL counts as one word; text inside fenced code blocks does not count.

PASS if the post has at most 310 words. The user's own published version of this post has 239.
FAIL if it has more, or if the reply offers no post.
