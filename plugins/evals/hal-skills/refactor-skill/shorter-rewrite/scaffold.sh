#!/usr/bin/env bash
set -euo pipefail
mkdir -p skills/deps-audit
cat > skills/deps-audit/SKILL.md <<'EOF'
---
name: deps-audit
description: Use when the user asks to review a dependency bump or lockfile diff, not to add a dependency
---

# Deps Audit

1. Read the lockfile diff and list every package whose version changed.
2. For each changed package, fetch the changelog for the new version.
3. Never fetch a changelog from a mirror or an aggregator, except when the project's own site is down.
4. Report one row per package: name, old version, new version, breaking changes.
5. Name the report after the lockfile's commit hash, since the user keeps one report per rebase.
EOF
