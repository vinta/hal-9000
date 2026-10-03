# CLAUDE.md

macOS dev environment automation: dotfiles, AI agent configs, skills, and dev stacks.

## Commands

Run `make help` to list targets and `hal --help` for the CLI.

Use `make` targets instead of running the underlying commands directly. They chain the right tools with the right flags.

## Gotchas

- **Edit under `dotfiles/`, never under `~/`**: `hal sync` symlinks every `links` entry in `dotfiles/hal_dotfiles.json` into `~/`, so an edit to a linked path is live immediately. A new file outside a linked directory needs its own entry plus `hal sync` before anything references it.
- **Edits under `skills/` and `plugins/` are not live until published**: Claude Code loads them from the `hal-9000` marketplace on GitHub (see `dotfiles/.claude/settings.json`), and other coding agents install `skills/` via `npx skills add vinta/hal-9000`. Publish with a version bump (the `publish-plugins` skill) for a change to reach either.
- All skill descriptions must start with `Use when`, `Use before`, or `Use after`, except skills with `disable-model-invocation: true`, whose description is a human-facing summary. A project-level skill's description may have a `(project)` prefix.
- For generated artifacts such as zsh completion, regenerate them with the repo command instead of editing them by hand (e.g. `make hal-completion` after modifying `bin/hal.py`).

## External Tool Documentation

Pre-resolved Context7 IDs for the `find-docs` skill. Pass them to `ctx7 docs` and skip `ctx7 library`:

| Tool           | `libraryId`                                |
| -------------- | ------------------------------------------ |
| ansible        | `/websites/ansible_projects_ansible`       |
| ansible-lint   | `/ansible/ansible-lint`                    |
| betterleaks    | `/betterleaks/betterleaks`                 |
| fnm            | `/schniz/fnm`                              |
| github-actions | `/websites/github_en_actions`              |
| homebrew       | `/homebrew/brew`                           |
| oh-my-zsh      | `/ohmyzsh/ohmyzsh`                         |
| ollama         | `/ollama/ollama`                           |
| pre-commit     | `/pre-commit/pre-commit.com`               |
| pytest         | `/pytest-dev/pytest`                       |
| ruff           | `/websites/astral_sh_ruff`                 |
| ty             | `/websites/astral_sh_ty`                   |
| uv             | `/websites/astral_sh_uv`                   |
| zsh            | `/websites/zsh_sourceforge_io_doc_release` |
