---
name: update-playbooks
description: (project) Use when updating install tasks in playbooks/roles/ against upstream docs — bumping a pinned version, adopting a newly recommended install method, repointing a doc link that moved, or realigning the community.general pin with the brew-installed ansible
user-invocable: true
model: sonnet
effort: high
allowed-tools:
  - Edit(./playbooks/roles/**)
  - Edit(./playbooks/collections/requirements.yml)
  - WebFetch
  - Bash(gh api:*)
  - Bash(curl:*)
  - Bash(make lint:*)
  - Bash(ansible-galaxy collection list:*)
metadata:
  internal: true
---

# Update Playbooks

Close the **drift** between each install task in `playbooks/roles/*/tasks/main.yml` and the upstream docs it cites, then commit per tool.

Drift takes three forms, and all three are read off the same page — the `#` comment URL above the task:

- **Version drift** — the pin trails the newest release of its **release line**.
- **Method drift** — upstream now recommends a different way to install.
- **Link drift** — the doc URL itself moved.

A **release line** is the version prefix a project treats as a stable series: Node `24.x`, Python `3.14.x`, kubectl `1.35.x`. Every bump stays inside the line (`24.15.0` -> `24.18.0` is in-line for Node because Node's line is the major). When a newer line exists (Node 26, Python 3.15, kubectl 1.36), keep the pin on its current line and report the newer line in the final summary so the user can decide.

One pin lives outside the roles and answers to a different source of truth — `playbooks/collections/requirements.yml`, covered in §4.

## 1. Scan

```bash
grep -rn -E '^# https?://|^- name:' playbooks/roles/*/tasks/main.yml
```

Adjacent line numbers pair each URL with the task it documents. Done when every install task is listed with its role, its doc URL, and any version pinned in its name, command body, or download URL.

## 2. Read the upstream docs

Fetch each doc URL once and take all three answers off that one page:

- **newest tag inside the release line** — `gh api repos/OWNER/REPO/releases --jq '.[].tag_name'` for a `github.com/OWNER/REPO` link, WebFetch otherwise.
- **the install commands the page currently recommends for macOS** — quote them verbatim, including which method the page calls recommended when it ranks them.
- **where the URL lands** — `curl -sIL -o /dev/null -w '%{http_code} %{url_effective}\n' URL`.

Done when every task has today's version, install commands, and final URL confirmed from its page. Anything recalled from training data is stale by definition.

## 3. Edit

Apply version and link drift, matching the surrounding task style:

- **Version** — replace the old version at every occurrence in the role: the task `name:`, each command line, and any URL. Done when grepping the file for the old version returns nothing.
- **Link** — repoint the `#` comment at the URL that resolved.

Keep each task's install method, and note each tool whose page recommends a different macOS method for §6. A page that ranks nothing recommends every method it lists, so note a tool only when its task's method is no longer among them.

## 4. Match the collection pin to brew's ansible

`playbooks/collections/requirements.yml` pins `community.general`, the collection supplying the `homebrew`, `homebrew_tap`, and `homebrew_cask` modules the roles install through. Upstream releases do not drive this pin — the brew-installed ansible does. Brew bundles its own copy of the collection, `~/.ansible/collections` takes precedence over it, and the pin is what fills `~/.ansible/collections`. So a pin that disagrees with brew means `ansible-lint` validates different module code than `ansible-playbook` executes, silently.

```bash
ansible-galaxy collection list community.general
```

When they differ, set the pin to brew's version. Never the reverse, and never to the newest release on Galaxy — a pin ahead of brew shadows the bundled collection just as badly as one behind it. Editing the pin is where this skill stops: installing it is `make install`'s job, so note in the final summary that the bump takes effect on the next `make install`.

## 5. Verify and commit

Run `make lint`. Then create one commit per tool with the `commit` skill, passing what moved, e.g. `bump kubectl to v1.35.7` or `install foundryup from getfoundry.sh`. A collection pin bump is its own commit, separate from any role.

## 6. Offer method switches

Once §5's commits are made, ask the user with `AskUserQuestion` whether to switch each tool noted in §3, one question per tool, up to four per call. Each question offers keeping the current method and switching to the page's recommended one, quoting the recommended commands in that option's `preview`; when the switch would cost something the task has, such as a version pin Homebrew cannot hold or a script's self-update, say so in the option's description.

For each yes, adopt the upstream commands; a script install points its `creates:` guard at the binary the script produces. A Homebrew install uses the `homebrew` module at `state: latest`, which also replaces any separate upgrade task, as fnm and bun show; a formula from the project's own tap takes a `homebrew_tap` task above it. Then run `make lint` and commit each switched tool as in §5.

Close with a summary: what changed per tool, which tools were already current, which method switches the user declined, and any newer release lines waiting on the user.
