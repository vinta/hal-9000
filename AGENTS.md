# AGENTS.md

macOS dev environment automation: dotfiles, AI agent configs, skills, and dev stacks. Domain vocabulary (manifest, link, copy, backup, sync, restore) is defined in `CONTEXT.md`.

## Commands

Run `make help` to list targets and `hal --help` for the CLI. Use `make` targets instead of running the underlying commands directly. They chain the right tools with the right flags (e.g. `make lint-python` runs ruff format --check and ruff check; `make lint-ansible` runs ansible-lint and a playbook syntax check; `make lint` runs both).

## Gotchas

- **Dotfiles are the source of truth**: `dotfiles/` is the source of truth for files under `~/`. `dotfiles/.claude/` syncs to `~/.claude/` via `hal_dotfiles.json`. Always edit under `dotfiles/`, never under `~/` directly.
- **Skills are the source of truth in `skills/hal-skills/`**: Distributed via Claude Code plugin marketplaces configured in `dotfiles/.claude/settings.json` (the `hal-9000` marketplace loads the published version from GitHub), and via `npx skills add vinta/hal-9000`.
- For generated artifacts such as zsh completion, regenerate them with the repo command instead of editing them by hand (e.g. `make hal-completion` after modifying `bin/hal`).

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

- Codex Prompting Best Practices
  - https://developers.openai.com/api/docs/guides/latest-model
  - https://developers.openai.com/api/docs/guides/prompt-guidance-gpt-5p6
- Codex Configs
  - https://learn.chatgpt.com/docs/config-file/config-reference
