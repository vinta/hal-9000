#!/usr/bin/env bash
set -euo pipefail
mkdir -p skills/release-notes
cat > skills/release-notes/SKILL.md <<'EOF'
---
name: release-notes
description: Use when the user asks to draft release notes or a changelog entry for the next version
---

# Release Notes

A changelog is a file that lists the notable changes for each version of a project.

IMPORTANT: ALWAYS follow these instructions.

1. Read the commits since the last tag with `git log $(git describe --tags --abbrev=0)..HEAD --no-merges`.
2. Group entries under Added, Changed, and Fixed, following Keep a Changelog 1.1.0.
3. Write each entry in Traditional Chinese (zh-TW), since the project's users read it first.
4. Never mention internal ticket IDs such as JIRA-123, because the changelog is public.

Be thorough and careful.
EOF
