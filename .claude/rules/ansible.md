---
paths:
  - "playbooks/**"
  - ".github/workflows/bootstrap-macos.yml"
---

# Ansible Playbooks

- **Re-runs must succeed**: `hal update` re-runs the whole playbook regularly and CI fails on any failed task, so every task must be safe to repeat. Guard one-shot installers with `creates:` — re-running them re-downloads vendor scripts on every update, and some clobber state (the oh-my-zsh installer overwrites `~/.zshrc`). House style is an honest `changed_when:` that parses the tool's own already-up-to-date output (often on stderr, not stdout) so `hal update` output shows what actually changed, but a task reporting changed on every run is acceptable — there is no `changed=0` gate.
- **Install/upgrade pairs skip the double-run**: `register:` the install task and gate the upgrade task with `when: not <install>.changed`, so a fresh install isn't immediately "upgraded" again.
- **Deliberate deviations from upstream Ansible guidance — do not "fix" them**: short module names (no FQCN), `state: latest` for homebrew packages, and `curl | sh` vendor install scripts are codified choices; `.ansible-lint` `skip_list` is the authority.
- Every install task carries a comment with its upstream doc/repo URL directly above it; keep them current (the `update-playbooks` skill repoints them).
- **Profile-script pattern**: a role that sets up shell environment owns `files/<x>_profile.sh` and appends a `source` line to `~/.zshrc` via `lineinfile`, gated on `when: ansible_facts["env"]["SHELL"] == "/bin/zsh"`. Non-interactive shells make that gate silently skip — CI exports `SHELL: /bin/zsh` for exactly this reason.
- `register:` variables start with the role name (`bun_install`, `python_uv_self_update`) to avoid cross-role collisions.
- **Adding a tool means updating CI too**: add the binary's `--version` call to the smoke-test step in `.github/workflows/bootstrap-macos.yml`.
- **Verify with `make lint-ansible`** (ansible-lint + syntax check). A dry-run via `ansible-playbook site.yml --check --tags <role>` is fine.
- Never run the playbook for real — it installs software on this machine; CI runs the full bootstrap.
