---
paths:
  - ".github/workflows/*.yml"
  - ".github/workflows/*.yaml"
---

# GitHub Actions

- Pin every third-party action to a full 40-char commit SHA with the version tag in a trailing comment. Tag pinning is acceptable only for first-party `actions/*` and `github/*`:

  ```yaml
  uses: owner/action@692973e3d937129bcbf40652eb9f2f61becf3332 # v4.1.7
  ```

- Verify the SHA comes from the action's upstream repo, not a fork, before pinning
- Declare top-level `permissions:` explicitly, defaulting to `contents: read`, with per-job overrides only where required. Omitting `permissions:` inherits repo or org defaults, which may grant more than needed
- Authenticate to cloud providers with OIDC (`permissions: id-token: write` plus `contents: read`), not long-lived access-key secrets
- Never interpolate `${{ github.event.* }}` or any user-controlled context into a `run:` block. Route through step-level `env:` and reference the variable, quoted:

  ```yaml
  - run: echo "title: $TITLE"
    env:
      TITLE: ${{ github.event.pull_request.title }}
  ```

- Treat context fields ending in `body`, `default_branch`, `email`, `head_ref`, `label`, `message`, `name`, `page_name`, `ref`, `title` as untrusted. Branch names and email addresses can contain shell metacharacters: `zzz";echo${IFS}"hello";#` is a valid branch name
- Prefer a typed action input (`with: title: ${{ ... }}`) over a shell command for untrusted context; typed inputs receive values as arguments, bypassing shell expansion
- Pass individual secrets via step-level `env:` only where needed. Never `env: ALL: ${{ toJson(secrets) }}`, never `echo "${{ secrets.FOO }}"` in `run:`
- One secret per sensitive value, never a JSON/XML/YAML blob: GitHub masks each registered secret whole, so sub-values inside a blob are not redacted
- `pull_request_target` and `workflow_run` run with write access and secrets. Never combine either with `actions/checkout` of `github.event.pull_request.head.sha`, a fork ref, or any other untrusted code. Use `pull_request` for anything that executes fork code
- Set `persist-credentials: false` on `actions/checkout` unless the job pushes back to the repo. The default `true` stores the token in git config, readable by any subsequent step
- Set `timeout-minutes: 10` on every job; the default is 360
- PR-triggered workflows include a `concurrency:` group keyed on ref with `cancel-in-progress: true`
- Set `fail-fast: false` on a matrix only when every combination's result matters
- Cache keys must hash the lockfile: `key: ${{ runner.os }}-uv-${{ hashFiles('uv.lock') }}`. Static keys serve stale artifacts
- Renaming a workflow file is safe: the Actions sidebar lists only workflows whose file exists on the default branch, so the old entry disappears once the rename merges, and its old runs stay reachable by `gh run list --workflow <old>.yml`. Never propose deleting old runs to clear it. Required status checks in rulesets are job names, not workflow names, so they survive the rename too
