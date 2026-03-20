# CLAUDE.md

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
hal update                              # Run all Ansible roles
hal update --tags python,node           # Run specific roles
```

## Project Structure

```
bin/hal                                 # Main CLI — extensionless Python script
bin/open-the-pod-bay-doors              # Bootstrap script (Bash)
dotfiles/                               # Tracked in hal_dotfiles.json, symlinked or copied to ~
playbooks/site.yml                      # Main playbook importing all roles
playbooks/roles/                        # Independent, tagged Ansible roles (Homebrew-based)
plugins/hal-voice/                      # Claude Code plugin — HAL 9000 voice clips
scripts/generate-completion.py          # Generates zsh completion for bin/hal
skills/                                 # Agent skills — symlinked into ~/.claude/skills/
tests/                                  # pytest tests
```

## Workflow

- **Load `writing-skills` skill before creating or editing any skill file.**
  - All skill descriptions must start with `Use when` (may have a `(project-name)` prefix, e.g. `(hal-9000) Use when …`)
- Use `make` targets — don't run underlying commands directly.
- Run `make lint`, `make format`, `make typecheck` after editing Python or Ansible files.
- After adding or modifying a skill, run `hal sync` to update symlinks.

## Gotchas

- **Python >=3.13** required. Package management via `uv`.
- **Dotfiles are the source of truth**: `dotfiles/.claude/` syncs to `~/.claude/` and `skills/` syncs to `~/.claude/skills/` via `hal_dotfiles.json`. Always edit under `dotfiles/` or `skills/`, never under `~/.claude/` directly. Update `hal_dotfiles.json` when adding new files, then run `hal sync`.
- **Dotfile modes**: `link` (symlink) for small configs, `copy` for large or externally synced files. Manifest uses `{{HOME}}` and `{{REPO_ROOT}}` template variables.

## External Tool Documentation

When you need information about tools used in this project, use the `find-docs` skill. These pre-resolved library IDs can be passed directly to `ctx7 docs`, skipping the `ctx7 library` step:

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
