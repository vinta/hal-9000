# AGENTS.md

## Scope

- This is the project-level Codex guidance for `hal-9000`, a macOS development environment automation repo covering dotfiles, AI agent configs, skills, plugins, and dev stacks.
- Keep user-level Codex defaults in `dotfiles/.codex/AGENTS.md`; keep this file focused on repository layout, source-of-truth rules, commands, and verification for this repo.

## Commands

```bash
make install                            # Full setup: uv sync, ansible-galaxy, pre-commit, gitleaks
make lint                               # ruff format --check, ruff check, ansible-lint, ansible syntax check
make format                             # ruff auto-format and fix
make typecheck                          # ty type checker
make test                               # pytest tests/ -v
make run-hooks                          # Run all pre-commit hooks on all files
make hal-completion                     # Regenerate zsh completion after modifying bin/hal
hal sync                                # Reconcile dotfile manifest to disk
hal link ~/.config/file                 # Move a file into dotfiles and symlink it back
hal unlink ~/.config/file               # Restore a file from dotfiles and remove the symlink
hal copy ~/.config/file                 # Copy a file into dotfiles without symlinking
hal update                              # Run all Ansible roles
hal update --tags python,node           # Run specific Ansible roles
```

## Project Layout

```text
bin/hal                                 # Main CLI, extensionless Python script
bin/open-the-pod-bay-doors              # Bootstrap script
dotfiles/                               # Source of truth for managed files synced into $HOME
dotfiles/hal_dotfiles.json              # Dotfile manifest used by hal sync/link/copy/unlink
dotfiles/.codex/                        # User-level Codex config, rules, and AGENTS.md managed by this repo
dotfiles/.claude/                       # Claude Code config, rules, and user-level CLAUDE.md managed by this repo
dotfiles/.gemini/                       # Gemini CLI config managed by this repo
playbooks/site.yml                      # Main Ansible playbook importing all roles
playbooks/roles/                        # Independent tagged Ansible roles, mostly Homebrew-based
plugins/hal-skills/                     # Claude Code plugin that distributes shared agent skills
plugins/hal-voice/                      # Claude Code plugin for HAL voice hooks
plugins/hal-statusline/                 # Claude Code statusline implementation
scripts/generate-completion.py          # zsh completion generator for bin/hal
scripts/install-hal-statusline.sh       # Statusline installer
tests/                                  # pytest coverage for CLI and plugin behavior
```

## Source Of Truth

- Edit managed home-directory files under `dotfiles/`, never under `~/` directly.
- Update `dotfiles/hal_dotfiles.json` when adding, moving, copying, or unlinking managed dotfiles.
- Keep root `AGENTS.md` project-specific; keep cross-project Codex preferences in `dotfiles/.codex/AGENTS.md`.
- Use make targets instead of running underlying tools directly unless you are diagnosing a target failure.
- After changing `bin/hal`, run `make hal-completion` so `dotfiles/.hal_completion.zsh` stays in sync.
- Skills in `plugins/hal-skills/` must have descriptions that start with `Use when`; project-scoped skill descriptions may start with `(project) Use when`.
- When testing unpublished Claude plugin changes, use the local marketplace entry that points at `/usr/local/hal-9000` before assuming the published GitHub marketplace reflects the edit.

## Research

- Before changing behavior that depends on Codex, Claude Code, Gemini, Ansible, Homebrew, uv, Ruff, ty, pytest, pre-commit, gitleaks, detect-secrets, or other external tools, check current official docs or primary sources.
- For OpenAI or Codex behavior, prefer the OpenAI Docs MCP or official `developers.openai.com` pages.
- For non-OpenAI tools, use `find-docs` or current official docs; `CLAUDE.md` keeps the longer Context7 and fallback documentation map.
- Do not copy Claude-only documentation links or settings patterns into Codex config unless the task is explicitly about Claude files or plugin packaging.

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

## Change Rules

- Keep changes small and atomic: separate dotfile sync changes, Codex config changes, plugin changes, Ansible role changes, and docs/process updates when practical.
- Preserve the manifest-driven dotfile model and existing `hal` command behavior unless the user explicitly asks to replace it.
- Do not add new dependencies, Homebrew packages, MCP servers, hooks, skills, or plugin files without a clear workflow payoff and matching manifest or config updates.
- For generated artifacts such as zsh completion, regenerate them with the repo command instead of editing them by hand.
- Keep Markdown and prose as single logical lines unless a format requires manual wrapping.

## Verification

- For docs-only or config-only edits, run `git diff --check` on the changed files.
- For `bin/hal`, scripts, plugin Python, or tests, run the narrowest relevant `uv run pytest ...` first, then `make test`, `make typecheck`, or `make lint` when the change affects shared behavior.
- For Ansible role or playbook changes, run `make lint` because it includes `ansible-lint` and an Ansible syntax check.
- For dotfile manifest or sync behavior changes, run the smallest relevant `hal` command or test that proves the manifest path works.
- For secret-sensitive changes, run `make run-hooks` or the specific scanner target that covers the touched files.
- If a relevant check is too expensive or cannot run on this machine, say exactly what was skipped, why, and the next best check.

## Stop Rules

- Stop and ask before changing files outside the repo or before rewriting existing user-level agent instructions in `dotfiles/.codex/AGENTS.md`, `dotfiles/.claude/CLAUDE.md`, or `dotfiles/.gemini/` beyond the requested scope.
- Stop and report when official docs conflict with current repo behavior, when `hal sync` would overwrite uncommitted local changes, or when validation shows a blocker that is outside the requested change.
