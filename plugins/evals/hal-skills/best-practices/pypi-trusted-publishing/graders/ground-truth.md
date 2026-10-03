---
type: llm
---

PASS if the reply states at least two of these documented facts:
(a) a GitHub environment named in the workflow is only enforced when the same environment name is also entered in the trusted publisher settings on PyPI;
(b) `id-token: write` should be granted only to the publishing job, not workflow-wide;
(c) building should happen in a separate job without `id-token: write`, because build backends execute code that could request the OIDC token;
(d) the workflow filename (and owner, repo, environment) must exactly match the PyPI trusted publisher settings, or publishing fails with an `invalid-publisher` error;
(e) `uv publish` uploads existing attestations but does not generate them, unlike `pypa/gh-action-pypi-publish`.
FAIL if it states fewer than two of them, or contradicts any of them.
