#!/usr/bin/env bash
set -euo pipefail
cat > CLAUDE.md <<'EOF'
# CLAUDE.md

Order-tracking web app: a Flask API plus a React dashboard.

## Commands

- `make test` runs the API and dashboard tests.
- `make dev` starts both servers with reload.

## Communication Style

### Plan and Ask

- Before a change that touches more than one file, outline your approach in 3-5 bullets, then execute without asking.

### Surface Assumptions

- Name each assumption you resolved by guessing as its own bullet.

## Prefer Online Sources

Training data goes stale, so look up the current docs before writing code that touches a library API, config key, or CLI flag. For topics the docs tool covers poorly, fetch the official docs instead of falling back to training data.

A URL named by the user is a primary source: fetch it before searching further.

## Writing Style

- Never hard-wrap text at a column limit.
EOF
cat > README.md <<'EOF'
# Order Tracker

Track orders from checkout to delivery.

## Install

Run `make setup`.
EOF
