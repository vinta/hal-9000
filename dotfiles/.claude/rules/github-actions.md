---
paths:
  - ".github/workflows/*.yml"
  - ".github/workflows/*.yaml"
---

# GitHub Actions

- Pin every third-party action to a full 40-char commit SHA with the version tag in a trailing comment. Per GitHub, SHA pinning is "the only way to use an action as an immutable release." Tag pinning is acceptable only for creators you trust (in practice, first-party `actions/*` and `github/*`); default to SHA everywhere else:

  ```yaml
  uses: owner/action@692973e3d937129bcbf40652eb9f2f61becf3332 # v4.1.7
  ```

- Verify the SHA comes from the action's upstream repo, not a fork, before pinning
- Enable Dependabot for the `github-actions` ecosystem. It updates the SHA and version comment together. Caveat: Dependabot raises security _alerts_ only for semver-pinned actions, not SHA-pinned ones, so pair SHA pinning with regular Dependabot update PRs
- Consider adding `ossf/scorecard-action` or CodeQL workflow scanning to catch unpinned actions, token over-scoping, and script injection automatically
- Add `.github/workflows/` (and ideally `.github/`) to `CODEOWNERS` so workflow changes require review from a designated reviewer
- Declare top-level `permissions:` explicitly, defaulting to `contents: read`. Add per-job overrides only where required. Omitting `permissions:` falls back to repo or org defaults, which may grant more than needed
- Use OIDC (`permissions: id-token: write` plus `contents: read`) to authenticate to cloud providers instead of storing access keys as long-lived secrets
- Never interpolate `${{ github.event.* }}` or any user-controlled context directly into a `run:` block. Route through step-level `env:` and reference the variable, quoted:

  ```yaml
  - run: echo "title: $TITLE"
    env:
      TITLE: ${{ github.event.pull_request.title }}
  ```

- Treat context fields ending in `body`, `default_branch`, `email`, `head_ref`, `label`, `message`, `name`, `page_name`, `ref`, `title` as untrusted input. Branch names and email addresses can contain shell metacharacters; GitHub's own example: `zzz";echo${IFS}"hello";#` is a valid branch name
- Prefer passing untrusted context to a typed action input (`with: title: ${{ ... }}`) over constructing a shell command. Context values reach typed inputs as arguments, bypassing shell expansion entirely
- Pass individual secrets via step-level `env:` only where needed. Never dump the full context: no `env: ALL: ${{ toJson(secrets) }}`, no `echo "${{ secrets.FOO }}"` in `run:`
- Don't store structured data (JSON/XML/YAML blobs) as a single secret. GitHub masks each registered secret individually, so sub-values inside a blob will not be redacted. Create one secret per sensitive value instead
- `pull_request_target` runs in the context of the base repo's default branch with write access and secrets. `workflow_run` can access secrets and write tokens even when the triggering workflow could not. Do not combine either with `actions/checkout` of `github.event.pull_request.head.sha`, a fork ref, or any other untrusted code. Use `pull_request` for anything that needs to execute fork code
- Set `persist-credentials: false` on `actions/checkout` unless the job pushes back to the repo. The default is `true`, which stores the token in git config and makes it readable by any subsequent step
- Set `timeout-minutes:` on every job. The default is 360 minutes (6 hours), which wastes runner minutes on hung jobs
- PR-triggered workflows include a `concurrency:` group keyed on ref with `cancel-in-progress: true` to drop superseded runs
- Matrix jobs default `fail-fast: true`. Set `fail-fast: false` only when you genuinely want every combination's result
- Consume step outputs via `steps.<id>.outputs.<name>` — requires `id:` on the producing step
- Cache keys must hash the lockfile: `key: ${{ runner.os }}-uv-${{ hashFiles('uv.lock') }}`. Static keys silently serve stale artifacts
