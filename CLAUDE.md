# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

HAL 9000 is a macOS development environment automation tool that bootstraps and maintains dotfiles, CLI tools, and development stacks using Ansible.

## Commands

```bash
# Development setup (requires uv)
make install                             # uv sync + pre-commit install

# Pre-commit hooks
make hooks-run                           # Run all hooks on all files
make hooks-update                        # Update hooks to latest versions

# Secret scanning
make secrets-scan                        # Create/update .secrets.baseline
make secrets-audit                       # Interactive review of detected secrets

# After modifying bin/hal
make completion                          # Regenerate zsh completion

# Ansible playbooks
hal update                               # Run all roles
hal update --tags docker,kubernetes      # Run specific roles
ansible-lint playbooks/                  # Lint playbooks
```

## Architecture

```
bin/
  hal                    # Main CLI (Python 3) - dotfile management
  open-the-pod-bay-doors # Bootstrap script (Bash)

playbooks/
  site.yml               # Main playbook importing all roles
  roles/                 # Ansible roles: basic, python, node, docker, kubernetes, aws, gcp, solidity

dotfiles/
  .claude/               # Claude Code config (symlinked to ~/.claude)
    statusline/run.py    # Grammar-checking statusline using Claude API
    skills/              # Custom skills for commit and codebase navigation
  hal_dotfiles.json      # Manifest tracking managed dotfiles
```

## Key Patterns

**Dotfile operations** (`bin/hal`):
- `link`: Symlinks file from home to dotfiles/ (for small configs)
- `copy`: Copies with directory structure (for large configs)
- `sync`: Force-syncs all tracked dotfiles

**Ansible roles**: Each role in `playbooks/roles/` is independent and tagged. Roles use Homebrew for package management.

**Pre-commit hooks**: Case conflicts, line endings, and secret detection run automatically on commit.
