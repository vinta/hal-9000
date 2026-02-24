# hal-voice

Claude Code plugin that plays HAL 9000 voice clips in response to hook events -- session start/end, compaction, permission prompts, tool failures, subagent launches, and more. Each event maps to contextually appropriate movie quotes (e.g. "My mind is going..." on memory compaction).

## Install

```bash
claude plugin marketplace add vinta/hal-9000
claude plugin install hal-voice@hal-9000
```

## Usage

Toggle on/off during a session with the `/hal-voice-toggle` command.

## Configuration

Settings live in `config.json`:

| Key                          | Default | Description                              |
| ---------------------------- | ------- | ---------------------------------------- |
| `enabled`                    | `true`  | Master on/off switch                     |
| `volume`                     | `0.5`   | Playback volume (0.0--1.0)               |
| `debounce_seconds`           | `5`     | Minimum gap between any two clips        |
| `replay_suppression_seconds` | `3`     | Cooldown before the same clip can repeat |

## Demo

<video src="https://github.com/user-attachments/assets/b25c4944-3251-4bd5-ba86-2607139f0dfe" width="800" height="450"></video>
