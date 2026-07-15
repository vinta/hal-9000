# AGENTS.md

macOS dev environment automation: dotfiles, AI agent configs, skills, and dev stacks.

## Commands

```bash
make install                            # Full setup: uv sync, ansible-galaxy, pre-commit, gitleaks
make lint                               # ruff format --check + ruff check + ansible-lint
make format                             # ruff auto-format and fix
make typecheck                          # ty type checker
make test                               # pytest tests/ -v
make run-hooks                          # Run all pre-commit hooks on all files
make hal-completion                     # Regenerate zsh completion (after modifying bin/hal)
hal sync                                # Reconcile dotfile manifest to disk
hal link ~/.config/file                 # Move file into dotfiles and symlink it back
hal unlink ~/.config/file               # Move file back from dotfiles and remove symlink
hal copy ~/.config/file                 # Copy file into dotfiles (no symlink)
hal backup                              # Back up live data to Dropbox
hal restore                             # Restore live data from Dropbox (overwrites local)
hal update                              # Run all Ansible roles
hal update --tags python,node           # Run specific roles
```

## Project Layout

```text
bin/hal                                 # Main CLI, extensionless Python script
bin/open-the-pod-bay-doors              # Bootstrap script
dotfiles/                               # Source of truth for managed files synced into $HOME
dotfiles/hal_dotfiles.json              # Dotfile manifest used by hal commands
dotfiles/.codex/                        # User-level Codex config, rules, and AGENTS.md managed by this repo
dotfiles/.claude/                       # Claude Code config, rules, and user-level CLAUDE.md managed by this repo
dotfiles/.gemini/                       # Gemini CLI config managed by this repo
playbooks/site.yml                      # Main Ansible playbook importing all roles
playbooks/roles/                        # Independent tagged Ansible roles, mostly Homebrew-based
skills/hal-skills/                      # Claude Code plugin that distributes shared agent skills
plugins/hal-voice/                      # Claude Code plugin for HAL voice hooks
plugins/hal-statusline/                 # Claude Code statusline implementation
scripts/generate-completion.py          # zsh completion generator for bin/hal
scripts/install-hal-statusline.sh       # Statusline installer
tests/                                  # pytest coverage for CLI and plugin behavior
```

## Gotchas

- Edit managed home-directory files under `dotfiles/`, never under `~/` directly.
- After changing `bin/hal`, run `make hal-completion` so `dotfiles/.hal_completion.zsh` stays in sync.
- Skills in `skills/hal-skills/` must have descriptions that start with `Use when`; project-scoped skill descriptions may start with `(project) Use when`.
- Use `make` targets instead of running underlying tools directly unless you are diagnosing a target failure.
- For generated artifacts such as zsh completion, regenerate them with the repo command instead of editing them by hand.

## External Tool Documentation

When you need information about tools used in this project, use the `find-docs` skill or `WebFetch`.

### Context7 Library IDs

Pre-resolved IDs for the `find-docs` skill. Pass directly to `ctx7 docs`, skipping the `ctx7 library` step:

| Tool           | `libraryId`                  |
| -------------- | ---------------------------- |
| ansible        | `/websites/ansible_ansible`  |
| detect-secrets | `/yelp/detect-secrets`       |
| gitleaks       | `/gitleaks/gitleaks`         |
| homebrew       | `/homebrew/brew`             |
| nvm            | `/nvm-sh/nvm`                |
| pre-commit     | `/pre-commit/pre-commit.com` |
| pytest         | `/pytest-dev/pytest`         |
| ruff           | `/websites/astral_sh_ruff`   |
| ty             | `/websites/astral_sh_ty`     |
| uv             | `/websites/astral_sh_uv`     |
