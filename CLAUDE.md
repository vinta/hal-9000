# Project CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

HAL 9000 is a macOS development environment automation tool that bootstraps and maintains dotfiles, CLI tools, and development stacks using Ansible.

## Commands

```bash
# Development setup (requires uv)
make install                             # uv sync + pre-commit install

# Pre-commit hooks
make run-hooks                           # Run all hooks on all files
make update-hooks                        # Update hooks to latest versions

# Secret scanning
make scan-secrets                        # Run all secret scanners
make audit-detect-secrets-report         # Interactive review of detected secrets

# Linting and formatting
make lint                                # ruff check + ansible-lint
make format                              # ruff auto-format and fix
make typecheck                           # ty type checker

# After modifying bin/hal
make hal-completion                      # Regenerate zsh completion

# Ansible playbooks
hal update                               # Run all roles
hal update --tags docker,kubernetes      # Run specific roles
```

## Architecture

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

skills/                  # Claude Code agent skills (symlinked into dotfiles/.claude/skills/)
```

## Key Patterns

**Dotfile management** (`bin/hal`): Files in `dotfiles/` are tracked in `hal_dotfiles.json` with `{{HOME}}` and `{{REPO_ROOT}}` template variables. Two modes: `link` (symlink, for small configs) and `copy` (for large configs or files synced elsewhere). `hal sync` reconciles the manifest to disk using concurrent threads.

**Ansible roles**: Each role in `playbooks/roles/` is independent and tagged. Roles use Homebrew for package management. Run specific roles with `hal update --tags python,node`.

**Skills**: Agent skills live in `skills/` and are symlinked to `dotfiles/.claude/skills/` (and thus to `~/.claude/skills/`). After adding or modifying a skill, run `hal sync` to update symlinks.

**`bin/hal` is extensionless Python**: Ruff includes it via `extend-include = ["bin/hal"]` in pyproject.toml. ty checks it explicitly in the Makefile `typecheck` target since ty's `[tool.ty.src] include` only supports directories.

## Python Conventions

Always run `make lint`, `make format`, `make typecheck` after editing Python or Ansible files.

When adding `# noqa`, always include the rule name after the code:

```python
# Single rule
# noqa: S603 subprocess-without-shell-equals-true

# Multiple rules
# noqa: S603 PLW1510 subprocess-without-shell-equals-true subprocess-run-without-check
```
