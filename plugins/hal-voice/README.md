# hal-voice

Claude Code plugin that plays HAL 9000 voice clips on hook events: `SessionStart`, `SessionEnd`, `PreCompact`, `PermissionRequest`, `PreToolUse`, `PostToolUseFailure`, `SubagentStart`, `UserPromptSubmit`, and `Stop`. Each event maps to a movie quote that fits the moment ("My mind is going..." on `PreCompact`).

## Install

```bash
claude plugin marketplace add vinta/hal-9000
claude plugin install hal-voice@hal-9000
```

## Usage

Just use Claude Code as usual -- you will hear HAL 9000 talking to you when the time is right.

For silence, toggle with the `/hal-voice-toggle` command.

## Configuration

Settings live in `${PLUGIN_ROOT}/config.json`:

| Key                          | Default | Description                              |
| ---------------------------- | ------- | ---------------------------------------- |
| `enabled`                    | `true`  | Master on/off switch                     |
| `volume`                     | `0.5`   | Playback volume (0.0--1.0)               |
| `debounce_seconds`           | `5`     | Minimum gap between any two clips        |
| `replay_suppression_seconds` | `3`     | Cooldown before the same clip can repeat |

## Demo

<video src="https://github.com/user-attachments/assets/b25c4944-3251-4bd5-ba86-2607139f0dfe" width="800" height="450"></video>
