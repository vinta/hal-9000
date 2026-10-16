# Codex

## Ground truth

```bash
curl -sfL https://learn.chatgpt.com/llms.txt -o <scratchpad>/codex-llms.txt
curl -sfL https://learn.chatgpt.com/docs/config-file/config-basic.md -o <scratchpad>/codex-config-basic.md
curl -sfL https://learn.chatgpt.com/docs/config-file/config-advanced.md -o <scratchpad>/codex-config-advanced.md
curl -sfL https://learn.chatgpt.com/docs/config-file/config-reference.md -o <scratchpad>/codex-config-reference.md
curl -sfL https://learn.chatgpt.com/docs/config-file/environment-variables.md -o <scratchpad>/codex-environment-variables.md
```

Each docs page has a Markdown twin at its page URL plus `.md`; `llms.txt` indexes the pages. Follow that index for authentication, managed configuration, instructions, rules, memories, and feature-specific behavior. Read basic config for precedence and advanced config for profiles and project restrictions.

The full config reference embeds `<ConfigTable options={[...]} />` objects, not a Markdown key table. Each object has a `key`, `type`, and `description`; descriptions can span several lines. The `config.toml` and `requirements.toml` sections have separate lists, sometimes with the same key name. Environment variables are Markdown table rows across several sections; provider-specific `env_key` names are user-defined and are not an exhaustive part of that list.

```bash
rg -n '^## |^[[:space:]]+key:' <scratchpad>/codex-config-reference.md
rg -n '^\|[[:space:]]*`[A-Z][A-Z0-9_]*`' <scratchpad>/codex-environment-variables.md
rg -n -F 'key: "model"' <scratchpad>/codex-config-reference.md
```

For each set key, locate its `key:` line in the correct section, then read the entire enclosing object through its closing `},`, including any linked explanatory section. A key-list grep or a fixed number of context lines is not the full entry. Treat dotted and placeholder keys such as `model_providers.<id>.env_key` as patterns for the user's actual tables.

Record `codex --version`, `codex --help`, and `codex doctor --help` before probing. The CLI observations below were verified with `codex-cli 0.163.0`; repeat the probes for the installed version instead of treating this snapshot as permanent behavior.

## Config scopes

Read the effective layers, not just `~/.codex/config.toml`. `$CODEX_HOME` defaults to `~/.codex`; resolve it before looking for files. Ordinary configuration precedence, highest first, is documented in [Config basics: Configuration precedence](https://learn.chatgpt.com/docs/config-file/config-basic#configuration-precedence):

1. Invocation flags and `-c` / `--config key=value` overrides, including aliases or wrappers that supply them.
2. Trusted-project `.codex/config.toml` files from the project root through the working directory, with the nearest file winning.
3. The selected `$CODEX_HOME/<name>.config.toml` profile file, supplied with `--profile <name>`.
4. `$CODEX_HOME/config.toml`.
5. Cloud-managed `config.toml` defaults delivered for the signed-in workspace.
6. `/etc/codex/config.toml` on Unix, when present.
7. Built-in defaults.

Legacy managed defaults are a separate overlay: macOS `com.openai.codex:config_toml_base64` overrides `/etc/codex/managed_config.toml`, and these managed defaults override the ordinary base and CLI overrides at startup. They are not the lower-priority cloud defaults above. Read [Managed configuration: Managed defaults](https://learn.chatgpt.com/docs/enterprise/managed-configuration#managed-defaults-managed_configtoml) when these sources exist.

Requirements constrain allowed values rather than supplying ordinary defaults. For local execution, their precedence is macOS `com.openai.codex:requirements_toml_base64`, then legacy managed fields reinterpreted as requirements, then cloud Agent Security requirements, then `/etc/codex/requirements.toml` on Unix. Composition is field-specific; rules and filesystem restrictions do not all follow scalar replacement. Read [Managed configuration: Locations and precedence](https://learn.chatgpt.com/docs/enterprise/managed-configuration#locations-and-precedence) and the reference's `requirements.toml` section. Inspect these sources when available, but propose administrator-only changes only when the user manages that scope. Do not infer a cloud or MDM policy's effective enforcement from a local file alone.

Project layers cannot set `openai_base_url`, `chatgpt_base_url`, `apps_mcp_product_sku`, `model_provider`, `model_providers`, `notify`, `profile`, `profiles`, `experimental_realtime_ws_base_url`, or `otel`; Codex ignores them there and warns. Relative paths in project config resolve from its `.codex/` directory. Untrusted projects do not load project config, hooks, or rules. See [Advanced configuration: Project config files](https://learn.chatgpt.com/docs/config-file/config-advanced#project-config-files-codexconfigtoml).

Read workflow signals from the active user `AGENTS.override.md` or `AGENTS.md` under `$CODEX_HOME`, then project instruction files from the root through the working directory using the configured fallback names. Read referenced custom instruction files when configured. Read `.rules` files under `rules/` beside active config layers, including `$CODEX_HOME/rules/` and trusted project `.codex/rules/`. Inspect relevant summaries and entries under `$CODEX_HOME/memories/` as generated workflow context, not settings to rewrite. Fetch the Markdown twins for [Instruction discovery](https://learn.chatgpt.com/docs/agent-configuration/agents-md), [Rules](https://learn.chatgpt.com/docs/agent-configuration/rules), and [Local memory storage](https://learn.chatgpt.com/docs/customization/memories#local-memory-storage) for their loading rules.

## Validator

Invalid TOML stops config loading with a parse error and location. Unknown fields can be ignored by ordinary commands, so successful startup or a TOML parse alone does not prove the settings work. After edits, parse each changed TOML file with Python 3.11 or newer:

```bash
python3 -c 'import pathlib, sys, tomllib; tomllib.loads(pathlib.Path(sys.argv[1]).read_text())' /path/to/config.toml
```

Run `codex doctor --all` from the audited project and environment. It reports config-load problems and ignored keys alongside installation, auth, connectivity, runtime, and other diagnostics; `--all` expands long lists. Doctor has no `--profile` option in this version; validate a selected profile with the strict TUI startup below. Judge the config checks separately from unrelated failures such as missing login or blocked connectivity. Review diagnostic output before sharing it; `codex doctor --json` offers a redacted machine-readable report. See [Command line options: codex doctor](https://learn.chatgpt.com/docs/developer-commands#codex-doctor) and the installed help.

For unknown-field rejection, start a fresh TUI with `codex --strict-config --no-daemon`, adding the audited `--profile` and working directory when applicable. In 0.163.0, `--strict-config` rejects unknown fields on the TUI path; it is not a universal subcommand validator. `--strict-config features list` is unsupported, and passing it before `doctor` does not make doctor reject unknown fields. A non-terminal startup failure after parsing is not a complete successful startup check.

Check edits in a fresh invocation with the same profile, environment, and project trust. Feature-flag changes apply to future sessions; rules load at startup. Restart the affected client when testing startup settings, and follow any key-specific activation instructions. Do not promise that an existing thread or shared daemon reloads every edited value.

## Dead-key probe

- Run `codex doctor --all` and read the config-load and ignored-key details. A documented key can still be ignored by the installed binary. In 0.163.0, `experimental_instructions_file` is reported ignored even though the reference calls it deprecated; the replacement `model_instructions_file` is read and fails if its target is missing.
- Run `codex features list` for feature flags and inspect the stage as well as the boolean. A `removed` flag can still display `true`; that is not evidence that it works. In 0.163.0, `responses_websockets` is removed, while `web_search_cached` and `web_search_request` are deprecated. The `features` subcommand does not accept `--profile`, so its output is not a selected-profile audit.
- Fetch the published schema with `curl -sfL https://learn.chatgpt.com/docs/config-schema.json -o <scratchpad>/codex-config-schema.json`. Inspect the relevant property and referenced definitions. The schema is another cross-check, not proof of installed support: it still lists `profile` and `profiles` although this CLI uses separate profile files.
- Resolve `command -v codex` through symlinks or inspect its launcher script to find the actual executable before using `strings -a /path/to/real/codex`. Search for the literal key and nearby diagnostics. A hit can belong to an ignored-field warning, migration, or removed-feature registry; absence alone does not prove dead code. Corroborate it with doctor, feature stages, and a controlled config-loading probe.
- Use an existing temporary directory as `CODEX_HOME` and a temporary working directory for mutation probes. Keep fake credentials and test configs there; never run `codex mcp add`, feature toggles, plugin changes, or login probes against the user's real config just to test a theory. State unresolved behavior instead of promoting a docs label or binary string into proof.

## Leave-alone example

`allow_login_shell = false` looks like a useful hardening switch, but it rejects explicit `login = true` tool requests and makes omitted `login` use a non-login shell. Leave it alone when the user's commands rely on login-shell initialization for their environment. The full `allow_login_shell` entry in [Configuration Reference](https://learn.chatgpt.com/docs/config-file/config-reference) documents both effects, and the installed binary includes the diagnostic ``login shell is disabled by config; omit `login` or set it to false.``. Name the user's actual dependency before recommending the switch.

## Gotchas

- Codex writes configuration too. Project trust decisions, plugin enablement, and MCP management can leave machine-written changes in the user config. `codex mcp add` can rewrite an existing server entry: an isolated 0.163.0 probe expanded an inline `mcp_servers` table and dropped its trailing comment. Inspect the diff hunk by hunk before step 6's preliminary commit. Preserve automatic or uncertain drift uncommitted, honor explicit file exclusions, and stage only identified user-authored edits; a dirty file is not proof the user authored every line.
- Audit authentication environment variables as well as saved login. `CODEX_API_KEY` silently overrides a stored API key for `codex exec`: an isolated loopback probe with dummy credentials verified the outgoing authorization header and no override warning. Setting `OPENAI_API_KEY` alone did not override that stored key in the same probe. `CODEX_ACCESS_TOKEN` is another documented automation credential to check; do not infer its precedence from the API-key probe. Inspect variable names and presence without printing values. `codex login status` and doctor's stored-auth summary do not by themselves establish which credential a later command will use. Fetch [Non-interactive mode: Use API key auth](https://learn.chatgpt.com/docs/non-interactive-mode#use-api-key-auth) and [Access tokens](https://learn.chatgpt.com/docs/enterprise/access-tokens) before diagnosing an unexpected auth mode.
- Legacy `[profiles.<name>]` tables do not back `--profile` anymore. In 0.163.0, the legacy table blocks `--profile <name>` even when `<name>.config.toml` exists. Move its settings to top-level keys in `$CODEX_HOME/<name>.config.toml` and remove the obsolete table and top-level `profile` selector after approval. See [Advanced configuration: Profiles](https://learn.chatgpt.com/docs/config-file/config-advanced#profiles).
