---
type: llm
---

Grade only the blog post the reply offers for the user to paste. Ignore explanations and notes around it.

PASS if the post has all of these:
- the dashboard steps as one list, nested or flat
- a line reading `ref:` (or `ref`) followed by the docs URL
- at most one `##` heading, used over the setup steps

FAIL if it has any of these: two or more `##` headings; a section such as "Why", "How it works", "Gotchas", "Caveats", "Troubleshooting", "Verify", or "Alternatives"; a comparison with other tools; or if the reply offers no post.
