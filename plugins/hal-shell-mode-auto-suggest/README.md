# Claude Code Shell Mode Auto-suggest

Suggests the `!` shell command Claude's last reply asks you to run, Tab to take.

## Installation

```bash
claude plugin install hal-shell-mode-auto-suggest --marketplace vinta/hal-9000
```

Then restart Claude Code.

## Usage

Just use Claude Code as usual. When Claude's reply tells you to run a `!` command yourself, that command shows up as the dim suggestion in the prompt box. Press Tab to take it, then Enter to run it. If the reply names several, you get the first one. Resuming a session whose last reply named a `!` command brings it up too.

In the Claude desktop app, the plugin does nothing, since the app already offers the reply's `!` command to run.
