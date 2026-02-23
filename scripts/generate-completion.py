#!/usr/bin/env python3
import importlib.machinery
import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

hal_path = REPO_ROOT / "bin" / "hal"
loader = importlib.machinery.SourceFileLoader("hal", str(hal_path))
spec = importlib.util.spec_from_file_location("hal", hal_path, loader=loader)
assert spec is not None  # noqa: S101 assert
assert spec.loader is not None  # noqa: S101 assert
module = importlib.util.module_from_spec(spec)
sys.modules["hal"] = module
spec.loader.exec_module(module)

HAL9000 = module.HAL9000  # type: ignore[attr-defined]
hal = HAL9000()

commands = []
file_commands = []

subparsers_actions = [a for a in hal.parser._subparsers._actions if hasattr(a, "choices") and a.choices]  # noqa: SLF001 private-member-access
if subparsers_actions:
    subparsers = subparsers_actions[0]

    help_map = {}
    if hasattr(subparsers, "_choices_actions"):
        for choice_action in subparsers._choices_actions:  # noqa: SLF001 private-member-access
            help_map[choice_action.dest] = choice_action.help or ""

    for cmd, parser in subparsers.choices.items():
        help_text = help_map.get(cmd, "")
        help_text = help_text.replace("'", "'\"'\"'")
        commands.append(f"        '{cmd}:{help_text}'")

        for act in parser._actions:  # noqa: SLF001 private-member-access
            if hasattr(act, "dest") and act.dest == "filename":
                file_commands.append(cmd)
                break

completion_content = f"""#compdef hal

_hal() {{
    local -a commands

    # Commands extracted from hal script
    commands=(
{chr(10).join(commands)}
    )

    if (( CURRENT == 2 )); then
        # First argument - show commands and options
        _describe -t commands 'hal commands' commands
        _arguments \\
            '(-h --help)'{{-h,--help}}'[show help message]' \\
            '(-v --version)'{{-v,--version}}'[show version]'
    else
        # Additional arguments based on command
        case "$words[2]" in"""

if file_commands:
    completion_content += f"\n            {'|'.join(file_commands)})"
    completion_content += """
                _files
                ;;"""

completion_content += """
            *)
                # No special completion for other commands
                ;;
        esac
    fi
}

compdef _hal hal"""

output_path = REPO_ROOT / "dotfiles" / ".hal_completion.zsh"
output_path.write_text(completion_content)

print("Generating zsh completion...")
print(f"Completion generated: {output_path}")
print("Run 'hal sync' to update your local completion.")
