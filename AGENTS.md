# AGENTS.md

macOS dev environment automation: dotfiles, AI agent configs, skills, and dev stacks.

## Commands

Use `make help` to find targets and `hal --help` for CLI usage. When a matching Makefile target exists, use it to run the required tools and flags together.

## Gotchas

- Edit managed home-directory files in `dotfiles/`; `dotfiles/hal_dotfiles.json` maps them to their destinations under `~/`.
- Edit skills in `skills/`. The `hal-9000` Claude Code marketplace installs the published GitHub version, so local edits do not update that installed plugin. Distribution commands are in [README.md](README.md#skills).
- Keep the `hal-skills` skill lists in `skills/.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` synchronized. Both copies are intentional: Claude Code reads the first for author and skill count; `npx skills` needs the second to group skills because it only looks for a root `plugin.json`.
- Regenerate generated artifacts with their repo command. After changing `bin/hal.py`, run `make hal-completion` to update zsh completion.

## External Tool Documentation

When looking up tool behavior or configuration, use `find-docs` or an available documentation/web fetch tool.

### Context7 Library IDs

Use these pre-resolved IDs with `find-docs`. Pass the matching ID directly to `npx ctx7@latest docs <libraryId> "<query>"`, skipping library resolution. If an ID no longer resolves, look it up again with `find-docs`.

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

### Documentation Links

Fetch the relevant official page when changing prompts or configuration:

- [GPT-6 prompting guidance](https://developers.openai.com/api/docs/guides/latest-model?model=gpt-6-astra#prompting-best-practices).
- [GPT-5.6 prompting guidance](https://developers.openai.com/api/docs/guides/prompt-guidance-gpt-5p6) when targeting GPT-5.6.
- [Codex configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference).
