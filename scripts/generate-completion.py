#!/usr/bin/env python
import os
import sys

# Add parent directory to path to import hal
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Read and modify the hal script to work without __file__
hal_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "bin", "hal")
with open(hal_path) as f:
    hal_content = f.read()

# Replace __file__ with the actual path
hal_content = hal_content.replace("__file__", repr(hal_path))

# Execute the modified content in a namespace
namespace = {"__name__": "__hal_module__"}
exec(hal_content, namespace)

# Now we can use HAL9000 from the namespace
HAL9000 = namespace["HAL9000"]
hal = HAL9000()

# Extract commands and their help text
commands = []
file_commands = []

# Find the subparsers action
subparsers_actions = [a for a in hal.parser._subparsers._actions if hasattr(a, "choices") and a.choices]
if subparsers_actions:
    subparsers = subparsers_actions[0]

    # Get help text from _choices_actions
    help_map = {}
    if hasattr(subparsers, "_choices_actions"):
        for choice_action in subparsers._choices_actions:
            help_map[choice_action.dest] = choice_action.help or ""

    for cmd, parser in subparsers.choices.items():
        # Get help text
        help_text = help_map.get(cmd, "")

        # Escape single quotes in help text
        help_text = help_text.replace("'", "'\"'\"'")
        commands.append(f"        '{cmd}:{help_text}'")

        # Check if this command takes filename arguments
        for act in parser._actions:
            if hasattr(act, "dest") and act.dest == "filename":
                file_commands.append(cmd)
                break

# Generate the completion file content
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

# Write the completion file
output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dotfiles", ".hal_completion.zsh")
with open(output_path, "w") as f:
    f.write(completion_content)

print("Generating zsh completion...")
print(f"Completion generated: {output_path}")
print("Run 'hal sync' to update your local completion.")
