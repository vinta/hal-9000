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
hal link ~/.config/file                 # Move file into dotfiles and symlink it back
hal unlink ~/.config/file               # Restore file from dotfiles and remove symlink
hal copy ~/.config/file                 # Copy file into dotfiles (no symlink)
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
plugins/hal-skills/                     # Claude Code plugin - Agent skills
plugins/hal-voice/                      # Claude Code plugin - HAL 9000 voice clips
plugins/hal-statusline/                 # Claude Code statusline
scripts/generate-completion.py          # Generates zsh completion for bin/hal
scripts/install-hal-statusline.sh       # One-liner statusline installer
tests/                                  # pytest tests
```

## Gotchas

- **Dotfiles are the source of truth**: `dotfiles/` is the source of truth for files under `~/`. `dotfiles/.claude/` syncs to `~/.claude/` via `hal_dotfiles.json`. Always edit under `dotfiles/`, never under `~/` directly.
- **Skills are the source of truth in `plugins/hal-skills/`**: Distributed via Claude Code plugin marketplaces configured in `dotfiles/.claude/settings.json`. The `hal-9000` marketplace loads the published version from GitHub. Use `hal-9000-local` (points to `/usr/local/hal-9000`) to test local changes before pushing.
- All skill descriptions must start with `Use when` (may have a `(project)` prefix if it's a project-level skill)
- Use `make` targets — don't run underlying commands directly.

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

### Documentation Links

For topics not well covered by Context7, use `WebFetch` on these URLs:

- Claude Prompting Best Practices
  - https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices
- Claude Code Settings
  - https://code.claude.com/docs/en/settings
- Claude Code Rules
  - https://code.claude.com/docs/en/memory#path-specific-rules
- Claude Code Plugins / Marketplaces
  - https://code.claude.com/docs/en/plugins-reference
  - https://code.claude.com/docs/en/plugin-marketplaces
