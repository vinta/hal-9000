# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

HAL 9000 is a macOS development environment automation tool that manages dotfiles, AI coding agent configs, agent skills, and development stacks using Ansible.

## Project Structure

```
bin/
  hal                    # Main CLI (Python 3) - dotfile management
  open-the-pod-bay-doors # Bootstrap script (Bash)

playbooks/
  site.yml               # Main playbook importing all roles
  roles/                 # Ansible roles

dotfiles/
  .claude/               # Claude Code config (symlinked to ~/.claude)
  .codex/                # Codex CLI config (symlinked to ~/.codex)
  .gemini/               # Gemini CLI config (symlinked to ~/.gemini)
  hal_dotfiles.json      # Manifest tracking managed dotfiles

skills/                  # Agent skills (symlinked into ~/.claude/skills/)

scripts/
  generate-completion.py # Generates zsh completion for bin/hal
```

## Components

**CLI tool: `hal`** (`bin/hal`): Main CLI for managing the dev environment — syncs dotfiles, runs Ansible playbooks, regenerates completions. Extensionless Python 3 script.

**Ansible roles**: Each role in `playbooks/roles/` is independent and tagged. Roles use Homebrew for package management. Run specific roles with `hal update --tags python,node`.

**Dotfile management**: Files in `dotfiles/` are tracked in `hal_dotfiles.json` with `{{HOME}}` and `{{REPO_ROOT}}` template variables. Two modes: `link` (symlink, for small configs) and `copy` (for large configs or files synced elsewhere). `hal sync` reconciles the manifest to disk using concurrent threads.

**Skills**: Agent skills live in `skills/` and are symlinked to `~/.claude/skills/`. After adding or modifying a skill, run `hal sync` to update symlinks.

## Workflow

- Use the `modern-python` skill when writing or modifying Python code.
- Use the `writing-skills` skill when creating or editing files under `skills/`.
- Use `make` targets when available — don't run underlying commands directly. Check the Makefile before composing ad-hoc commands.
- Run `make lint`, `make format`, `make typecheck` after editing Python or Ansible files.

## Gotchas

- **Skills are symlinked**: `~/.claude/skills/` entries are symlinks to `skills/` in this repo. Always edit files under `skills/`, never under `~/.claude/skills/`, to keep changes in the repo working tree.
- **`bin/hal` is extensionless Python**: Ruff includes it via `extend-include`. ty checks it explicitly (`ty check bin/hal`) since `[tool.ty.src] include` only accepts directories.
- **Ruff enables all rules**: `select = ["ALL"]` with specific ignores in `pyproject.toml`. New code may trigger unexpected rules.
- **ty strict mode**: `error-on-warning = true` — warnings fail the type check.
- **`# noqa` format**: Always include the rule name: `# noqa: S603 subprocess-without-shell-equals-true`

## Commands

```bash
# Development setup (requires uv)
make install                            # Full setup: uv sync, ansible-galaxy, pre-commit, gitleaks

# Pre-commit hooks
make run-hooks                          # Run all hooks on all files
make update-hooks                       # Update hooks to latest versions

# Secret scanning
make scan-secrets                       # Run all secret scanners
make audit-detect-secrets-report        # Interactive review of detected secrets

# Linting and formatting
make lint                               # ruff format --check + ruff check + ansible-lint
make format                             # ruff auto-format and fix
make typecheck                          # ty type checker

# After modifying bin/hal
make hal-completion                     # Regenerate zsh completion

# Ansible playbooks
hal update                              # Run all roles
hal update --tags docker,kubernetes,gpc # Run specific roles
```
