#!/usr/bin/env bash
set -euo pipefail
mkdir -p skills/deploy-check skills/release
cat > skills/deploy-check/SKILL.md <<'EOF'
---
name: deploy-check
description: Pre-deploy checks for the payments service
disable-model-invocation: true
user-invocable: true
model: sonnet
effort: high
---

# Deploy Check

Run these checks before a production deploy. Finish every check even after one fails, so I see all the failures at once.

1. Confirm CI is green for the head commit with `gh pr checks`.
2. Run `make smoke` against staging. Unit tests don't cover the payment callbacks, so a green CI run is not enough.
3. List pending migrations with `make migrate-status`. Fail this check if any migration drops a column, since those need a two-step deploy.
4. Check that every flag added since the last tagged release defaults to off in `config/flags.yaml`.

Report one row per check: check, pass or fail, evidence. For example: `migrations | fail | 0042_drop_legacy_column drops a column`.
EOF
cat > skills/release/SKILL.md <<'EOF'
---
name: release
description: Use when the user asks to cut a release or ship the current branch to production
---

# Release

1. Run the `deploy-check` skill and stop if any check fails.
2. Tag the release with `make tag VERSION=<version>` and push the tag.
3. Watch the rollout with `make rollout-status` until it reports healthy.
EOF
