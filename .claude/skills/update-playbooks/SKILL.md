---
name: update-playbooks
description: (project) Use when refreshing install tasks in playbooks/roles/ against upstream docs — bumping a pinned version, adopting a newly recommended install method, repointing a doc link that moved, or realigning the community.general pin with the brew-installed ansible
user-invocable: true
model: sonnet
allowed-tools:
  - Grep
  - Read
  - Edit
  - WebFetch
  - Bash(grep:*)
  - Bash(gh api:*)
  - Bash(curl:*)
  - Bash(make lint:*)
  - Bash(ansible-galaxy collection list:*)
  - Skill(commit)
metadata:
  internal: true
---

# Update Playbooks

Close the **drift** between each install task in `playbooks/roles/*/tasks/main.yml` and the upstream docs it cites, then commit per tool.

Drift takes three forms, and all three are read off the same page — the `#` comment URL above the task:

- **Version drift** — the pin trails the newest release of its **release line**.
- **Method drift** — upstream now recommends a different way to install.
- **Link drift** — the doc URL itself moved.

A **release line** is the version prefix a project treats as a stable series: Node `24.x`, Python `3.14.x`, kubectl `1.35.x`, fnm `1.x`. Every bump stays inside the line (`24.15.0` -> `24.18.0` is in-line for Node because Node's line is the major). When a newer line exists (Node 26, Python 3.15, kubectl 1.36), keep the pin on its current line and report the newer line in the final summary so the user can decide.

One pin lives outside the roles and answers to a different source of truth — `playbooks/collections/requirements.yml`, covered in §4.

## 1. Scan

```bash
grep -rn -E '^# https?://|^- name:' playbooks/roles/*/tasks/main.yml
```

Adjacent line numbers pair each URL with the task it documents. Done when every install task is listed with its role, its doc URL, and any version pinned in its name, command body, or download URL.

## 2. Read the upstream docs

Fetch each doc URL once and take all three answers off that one page:

- **newest tag inside the release line** — `gh api repos/OWNER/REPO/releases --jq '.[].tag_name'` for a `github.com/OWNER/REPO` link, WebFetch otherwise
- **the install commands the page currently recommends for macOS** — quote them verbatim, including which method the page calls recommended when it ranks them
- **where the URL lands** — `curl -sIL -o /dev/null -w '%{http_code} %{url_effective}\n' URL`

Done when every task has today's version, install commands, and final URL confirmed from its page. Anything recalled from training data is stale by definition.

## 3. Edit

Apply the drift found, matching the surrounding task style:

- **Version** — replace the old version at every occurrence in the role: the task `name:`, each command line, and any URL. Done when grepping the file for the old version returns nothing.
- **Method** — adopt the upstream commands and point the `creates:` guard at the binary those commands actually produce.
- **Link** — repoint the `#` comment at the URL that resolved.

**Prefer Homebrew.** When the page lists Homebrew among the macOS installs it supports, install with the `homebrew` module at `state: latest` rather than the vendor script — `state: latest` also absorbs whatever separate upgrade task the script needed, as fnm and bun already show. Two things disqualify it, and both send you back to the method the page recommends:

- The page steers away from brew — listing it only as community-contributed, or warning that it lags.
- The formula lives in neither homebrew-core nor a tap the project itself publishes. A vendor-owned tap counts as official and takes a `homebrew_tap` task above the install; an unaffiliated third party's tap does not.

Homebrew always installs the newest release, so it cannot hold a pin. Where a task deliberately pins a version, keep the pinned download and leave the method alone — trading the pin for brew is a decision for the user, not drift to close.

## 4. Match the collection pin to brew's ansible

`playbooks/collections/requirements.yml` pins `community.general`, the collection supplying the `homebrew`, `homebrew_tap`, and `homebrew_cask` modules the roles install through. Upstream releases do not drive this pin — the brew-installed ansible does. Brew bundles its own copy of the collection, `~/.ansible/collections` takes precedence over it, and the pin is what fills `~/.ansible/collections`. So a pin that disagrees with brew means `ansible-lint` validates different module code than `ansible-playbook` executes, silently.

```bash
ansible-galaxy collection list community.general
```

When they differ, set the pin to brew's version. Never the reverse, and never to the newest release on Galaxy — a pin ahead of brew shadows the bundled collection just as badly as one behind it. Editing the pin is where this skill stops: installing it is `make install`'s job, so note in the final summary that the bump takes effect on the next `make install`.

## 5. Verify and commit

Run `make lint`. Then create one commit per tool with the `commit` skill, passing what moved, e.g. `bump kubectl to v1.35.7` or `install foundryup from getfoundry.sh`. A collection pin bump is its own commit, separate from any role. Close with a summary: what changed per tool, which tools were already current, and any newer release lines waiting on the user.
