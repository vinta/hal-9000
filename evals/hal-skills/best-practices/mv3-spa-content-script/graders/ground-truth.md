---
type: llm
---

PASS if the reply explains that `matches` and `excludeMatches` are evaluated only when a document loads, so same-document navigations (`history.pushState`) never re-evaluate them, and recommends re-checking the URL at runtime on each in-page navigation, using at least one of: the Navigation API (`navigation` events such as `navigate` or `currententrychange`), `chrome.webNavigation.onHistoryStateUpdated`, or `chrome.tabs.onUpdated`.
FAIL if it misses the load-time-only cause, or recommends no runtime re-check.
