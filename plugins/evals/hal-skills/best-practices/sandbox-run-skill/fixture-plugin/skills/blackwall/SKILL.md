---
name: blackwall
description: "Run, configure, and debug blackwall, the sandbox for claude, codex, and other dev commands (srt: Seatbelt on macOS, bubblewrap on Linux). Use when the user asks whether this session is sandboxed or what it can read, write, or reach, mentions blackwall, wants a command run sandboxed, or wants the sandbox to reach a path, host, or tool: ~/.blackwall/config.json, .blackwall/config.json, presets, --add-dir, --trust; or wants a blackwall bug report. Also use inside a sandboxed session when a command fails with `Operation not permitted` on a path that exists, `CONNECT tunnel failed, response 403`, ENOTFOUND or `nodename nor servname provided` for every host, a write under /tmp or ~ that fails or vanishes, or blackwall itself refuses with `can't run inside a sandbox`: those are blackwall denials, not project bugs. Not for configuring Claude Code's built-in sandbox or Codex's sandbox_mode."
license: MIT
compatibility: Node.js 22.21+; macOS (Seatbelt) or Linux (bubblewrap)
allowed-tools: Bash(blackwall --print-config:*) Bash(blackwall --print-file-access:*) Bash(blackwall --print-network-access:*) Bash(blackwall --print-env:*) Bash(blackwall --version)
---

# Blackwall

`blackwall <command>` runs the command under [srt](https://github.com/anthropics/sandbox-runtime) with a policy fixed at launch:

- Writes: the current folder, `--add-dir` folders, `/tmp/claude`, `~/.cache-blackwall`. Write-denied even inside those: `~/.blackwall`, `.blackwall`, `.git/hooks`, `.git/config`, `.claude/settings.json`, `.claude/settings.local.json`, `.claude/hooks`, `.mcp.json`, `.claude/commands`, and `.claude/agents` in the current and `--add-dir` folders (srt covers the last three only beneath the current folder, and blackwall's denies in this list also apply at any depth beneath the current and `--add-dir` folders: on Linux, what exists at launch, three folders deep), and srt's own list for the current folder (`.zshrc`, `.gitconfig`, `.vscode`, …), which `blackwall --print-file-access` prints.
- Reads: those folders, the system paths and preset paths in the default config, and `allowRead` entries from the user and project configs. The rest of `~` is invisible.
- Network: only hosts from presets, the `claude` and `codex` adapters, and `network.allowedHosts`, all through srt's proxy. The sandbox has no direct DNS, so a tool that ignores `HTTPS_PROXY` can't resolve any host.

A denial is the policy working. The fix is a grant plus a relaunch, never a retry, a copy into another folder, or `sudo`.

## Inside or outside?

Inside a sandboxed session (`blackwall claude`, `blackwall codex`), `$BLACKWALL_SANDBOX` is `1`.

Inside, `blackwall` is unavailable: every flag, `--version` included, exits 2 with `blackwall: can't run inside a sandbox; run it from a plain terminal`. Diagnose from the error text and the grant list above, read the project's `.blackwall/config.json` if one exists, then hand the user the exact edit and commands. Outside (a plain terminal, or an agent that isn't sandboxed), run the `--print-*` flags and edit the user config yourself.

## Reading a denial

| The command printed | Cause | Grant |
|---|---|---|
| `Operation not permitted` on a path that exists (macOS). On Linux the path reads as missing, or a write succeeds and the file is gone after the run | path outside the read or write grants | `filesystem.allowRead` or `filesystem.allowWrite` for one path; `--add-dir DIR` for a whole folder, read and write |
| `curl: (56) CONNECT tunnel failed, response 403`; git: `unable to access '…': CONNECT tunnel failed, response 403`; Node's `fetch`: `fetch failed` caused by `Request was cancelled.`; Node's `http`: `ERR_PROXY_TUNNEL`, `HTTP/1.1 403 host is not on the allow list`. The 403 status line carries the reason, e.g. `403 host is not on the allow list`, `403 host is on the deny list`, `403 resolved to a listed address`; git and `curl -sS` show only `response 403`, so run `curl -sv https://<host>` to read it | host outside the allowlist, a `deniedHosts` name under `"*"` (preset `local-network` denies `localhost`), an IP literal in loopback, link-local, cloud metadata, this machine's own addresses, or a denied range, or a name resolving into loopback or a denied range (`private-network` ranges) | `network.allowedHosts`, or the preset for that tool; for a local or LAN server, its IP literal or name with the port, e.g. `127.0.0.1:8000` or `localhost:8000` |
| `ENOTFOUND`, `getaddrinfo` failure, `[Errno 8] nodename nor servname provided, or not known`, for allowed hosts too | the tool ignores `HTTPS_PROXY` | make it use the proxy; no config change. curl, git, gh, npm, pip, uv, and urllib honor it already, and so do Node's `fetch` and `http` (22.21+) through the `node` preset's `NODE_USE_ENV_PROXY=1` |
| `blackwall: …/.blackwall/config.json: not trusted. Review it, then run \`blackwall --trust\`` | project config is new or edited | the user reviews it and runs `blackwall --trust` |
| `blackwall: …/.blackwall/.env: loads only with a trusted .blackwall/config.json` | project `.env` without a trusted config | add `.blackwall/config.json` (`{}` is enough), then `--trust` |
| `blackwall: unknown preset <name>`; `blackwall: <file>: unknown key <key>`; `<file>: <path>: <message>` from a bad value (exit 2) | config typo, or an srt setting blackwall doesn't expose | fix the key or value; preset names are under Config |
| `No image found in clipboard. Use ctrl+v to paste images.` after pasting a copied image (macOS) | the sandbox refuses the pasteboard service | preset `clipboard` in the user config; it also lets every sandboxed command read and replace the clipboard |
| A pasted screenshot or image file stays a plain path instead of turning into `[Image #1]` | the file is outside the read grants | preset `screenshots` for the screenshot folder, or `filesystem.allowRead` for another folder |
| `sandbox_apply: Operation not permitted` from `codex` | Seatbelt can't nest | `blackwall codex` already passes `-c sandbox_mode="danger-full-access"`; a codex started from inside another sandboxed command needs the same flag |
| `unshare: unshare failed: Operation not permitted`, or Chromium, Electron, Playwright, rootless podman, or a nested bubblewrap failing to start (Linux); Chromium, Electron, or Playwright dying at launch, headless too, with `bootstrap_check_in …MachPortRendezvousServer.<pid>: Permission denied (1100)` (macOS) | sandboxed commands can't create user namespaces on Linux, or register a Mach service on macOS | none in the config. The user runs that tool outside blackwall |
| git: `could not write config file .git/config: Operation not permitted`. `git remote add`, `git config`, `git branch -m` fail; `git push -u`, `git switch -c` exit 0 but lose the tracking update; `git branch -d` and `-D` exit 0 with the branch deleted but leave its `branch.<name>` section | `.git/config` is write-denied, no grant lifts it | none. The user sets remotes and upstreams on the host; push with `git push origin HEAD`. After deleting a branch that had an upstream, the user runs `git config --remove-section branch.<name>` on the host |

Noise, harmless, the command still ran:

- git: `could not write config file .git/config` and `update of config-file failed` from `git branch -d` or `-D`, even for a branch with no config; the branch is deleted
- `make: error: couldn't create cache file '/var/folders/…/xcrun_db-…' (errno=Operation not permitted)`, same from `xcrun`
- pip: `WARNING: The directory '…/Library/Caches/pip' or its parent directory is not owned or is not writable … The cache has been disabled`

A failure no row explains, a path or host the docs deny that goes through, or a misleading message is a blackwall bug: write a local report as [references/bug-report.md](references/bug-report.md) describes.

## Granting the narrowest thing

1. Confirm the denial: a marker from "Inside or outside?" plus a row above. Then ask whether the task needs the grant at all: writing under the current folder or `$TMPDIR`, or `npx` instead of a global install, needs none.
2. Pick the grant, narrowest first:
   - One run, one folder, read and write: `blackwall --add-dir DIR <command>`. Under `blackwall claude` the folder is also passed to claude as `--add-dir`.
   - One path: `filesystem.allowRead` or `filesystem.allowWrite`. One host: `network.allowedHosts` (`*.example.com` wildcards work). Everything one tool needs: its preset.
   - Per project: `.blackwall/config.json`. Per machine: `~/.blackwall/config.json`. Secrets: `~/.blackwall/.env` or `.blackwall/.env`, never a config file.
   - `"*"` in `allowedHosts`, or `--allow-internet` for one run, opens every public host and public IP literal, not loopback, private ranges, or `localhost`, and `overrideDefaults.filesystem.denyRead` opens every path; propose them only when the user asks for an open sandbox.
   - Credentials under `~/.ssh`, `~/.aws`, `~/.gnupg`, and writes to `~/.claude`, `~/.codex`, `~/.blackwall` are what the sandbox exists to deny: report the need to the user instead of proposing a grant.
3. Deliver. Inside: print the JSON to add, the file it goes in, and the commands, for the user to run outside. Outside: write `~/.blackwall/config.json` yourself; for a project config, write it and leave `blackwall --trust` to the user, who re-runs it after every edit. `--trust` exists so a human reviews the file.
4. Relaunch: config loads at launch, so the user restarts the sandboxed command and reruns what failed. Done when it passes with that grant and nothing broader.

## Config

`~/.blackwall/config.json` and `.blackwall/config.json` take the same keys. Lists from both are added to the defaults. `srt` keys replace their defaults one by one, and `overrideDefaults` replaces the default `presets`, `network`, and `filesystem` values, applied first; for both, the project's wins over the user's. `~` expands.

```json
{
  "network": { "allowedHosts": ["api.example.com", "*.example.com"] },
  "filesystem": { "allowRead": ["~/.npmrc", "/path/to/other/repo"], "allowWrite": [] },
  "srt": { "allowPty": false },
  "overrideDefaults": { "presets": ["agent-files", "github", "git", "local-network", "private-network"] }
}
```

- Presets: `agent-files`, `python`, `node`, `github`, `git`, `pre-commit`, `local-network`, `private-network` are on by default; `tmpdir`, `mac`, `linux` are always on; `clipboard`, `screenshots` are off by default. Each is one tool's hosts, read paths, env vars, shell lines, and macOS services. What each grants: https://github.com/vinta/blackwall#presets
- `filesystem.denyRead` and `denyWrite` take paths too. A relative entry, like `./local`, applies to the current folder and every `--add-dir` folder.
- Dropping `git` from `presets` makes every sandboxed `git` refuse to start when `~/.gitconfig` exists, and opens writes to `.git/hooks` and `.git/config` in `--add-dir` folders.
- `.blackwall/.env` keys override `~/.blackwall/.env` and reach only the sandboxed command.
- Verify outside: `blackwall --print-config claude` (merged config with the launch-time grants), `blackwall --print-file-access claude` (srt's view), `blackwall --print-network-access claude` (hosts it can reach, the names and ranges it refuses, and srt's own refused classes), `blackwall --print-env claude` (env vars blackwall adds, each with its why).

## Run and install

```bash
npm install -g blackwall-sandbox                                   # Node.js 22.21+
sudo apt-get install -y bubblewrap socat ripgrep                   # Linux only
sudo sysctl -w kernel.apparmor_restrict_unprivileged_userns=0      # Ubuntu 24.04+ only
blackwall claude                                                   # or codex, or any command
blackwall --add-dir ../other-repo claude
blackwall --no-config npx some-tool                                # defaults only, ignores every config and .env file
blackwall --self-signed-node claude                                # runs blackwall as node-blackwall, for firewall rules
blackwall --trust                                                  # in the project, after reviewing .blackwall/config.json
```

`blackwall` with no command, or `blackwall --help`, prints the one-line usage. An unknown option is refused with `unknown option`. Exit 2 means a usage or config error.

## Agent-specific behavior

- For config, copied files, plugins, or login under `blackwall claude`, read [references/claude-code.md](references/claude-code.md).
- For config, copied files, command rules, or login under `blackwall codex`, read [references/codex.md](references/codex.md).
