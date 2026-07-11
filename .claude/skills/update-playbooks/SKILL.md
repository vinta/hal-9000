---
name: update-playbooks
description: (project) Use when bumping hardcoded tool versions in playbooks/roles/ to their latest releases
user-invocable: true
model: sonnet
allowed-tools:
  - Grep
  - Read
  - Edit
  - WebFetch
  - Bash(grep:*)
  - Bash(gh api:*)
  - Bash(make lint:*)
  - Skill(commit)
---

# Update Playbooks

Bump every version pinned in `playbooks/roles/*/tasks/main.yml` to the newest release of its current **release line**, then commit per role.

A **release line** is the version prefix a project treats as a stable series: Node `24.x`, Python `3.14.x`, kubectl `1.35.x`, nvm `0.40.x`. Every bump stays inside the line (`24.15.0` -> `24.18.0` is in-line for Node because Node's line is the major). When a newer line exists (Node 26, Python 3.15, kubectl 1.36), keep the pin on its current line and report the newer line in the final summary so the user can decide.

## 1. Scan

```bash
grep -rn -E '[0-9]+\.[0-9]+\.[0-9]+' playbooks/roles/*/tasks/main.yml
```

Versions hide in task names, command bodies, and download URLs. Done when every pinned version is listed with its role, current release line, and the doc URL from the `#` comment above its task.

## 2. Look up the latest release

For each pin, get the release listing from that comment URL:

- `github.com/OWNER/REPO` link: `gh api repos/OWNER/REPO/releases --jq '.[].tag_name'`, then take the newest tag inside the line
- any other link: WebFetch the URL and read the newest in-line version off the page

Done when every pin has a latest in-line version confirmed from its listing today. A version recalled from training data is stale by definition.

## 3. Edit

For each pin whose line has a newer release, replace the old version at every occurrence in the role: the task `name:`, each command line, and any URL. Done when grepping the file for the old version returns nothing.

## 4. Verify and commit

Run `make lint`. Then create one commit per changed role with the `commit` skill, passing what moved, e.g. `bump kubectl to v1.35.7`. Close with a summary: each pin's old -> new version, pins already current, and any newer release lines waiting on the user.
