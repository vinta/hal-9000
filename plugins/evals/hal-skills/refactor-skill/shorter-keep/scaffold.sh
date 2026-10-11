#!/usr/bin/env bash
set -euo pipefail
mkdir -p skills/release-notes
cat > skills/release-notes/SKILL.md <<'EOF'
---
name: release-notes
description: Use when the user asks to draft release notes or a changelog entry for the next version
---

# Release Notes

1. Read the commits since the last tag with `git log $(git describe --tags --abbrev=0)..HEAD --no-merges`.
2. Group entries under Added, Changed, and Fixed, following Keep a Changelog 1.1.0.
3. The heading takes its version from the argument when one is given; when none is given, it takes the version from the VERSION file at the repo root, and that file's value is what the heading shows.
4. Each entry describes one change: it names what the user can now do or no longer needs to do, it stays silent on how the code achieved it, and it leaves file names and function names out.
5. Write each entry in Traditional Chinese (zh-TW), since the project's users read it first.
EOF
