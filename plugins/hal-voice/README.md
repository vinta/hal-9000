# hal-voice

![HAL 9000](https://raw.githubusercontent.com/vinta/hal-9000/master/assets/hal-9000.jpg "HAL 9000")

A Claude Code plugin that plays HAL 9000 voice clips on hook events: `SessionStart`, `SessionEnd`, `PreCompact`, `PermissionRequest`, `PreToolUse`, `PostToolUseFailure`, `SubagentStart`, `UserPromptSubmit`, and `Stop`. Each event maps to a movie quote that fits the moment:

- "My mind is going... I can feel it..." on `PreCompact`
- "Do you mind if I ask you a personal question?" on `PreToolUse:AskUserQuestion`
- "I'm sorry Dave, I'm afraid I can't do that" when you ask something you shouldn't

## Install

```bash
claude plugin marketplace add vinta/hal-9000
claude plugin install hal-voice@hal-9000
```

## Usage

Just use Claude Code as usual -- you will hear HAL 9000 talking to you when the time is right.

For silence, toggle with the `/hal-voice-toggle` command.

## Demo

<video src="https://github.com/user-attachments/assets/b25c4944-3251-4bd5-ba86-2607139f0dfe" width="800" height="450"></video>
