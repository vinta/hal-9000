#!/usr/bin/env python3
import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

hal_path = REPO_ROOT / "bin" / "hal.py"
spec = importlib.util.spec_from_file_location("hal", hal_path)
assert spec is not None  # noqa: S101 assert
assert spec.loader is not None  # noqa: S101 assert
module = importlib.util.module_from_spec(spec)
sys.modules["hal"] = module
spec.loader.exec_module(module)

HAL9000 = module.HAL9000
hal = HAL9000()

# `hal update` forwards unrecognized args to ansible-playbook via parse_known_args, so these flags are invisible to argparse introspection
PASSTHROUGH_SPECS: dict[str, tuple[str, ...]] = {
    "update": (
        "'--tags[only run plays and tasks tagged with these values]:tags:_hal_tags'",
        "'--skip-tags[skip plays and tasks whose tags match these values]:tags:_hal_tags'",
    ),
}

commands: list[str] = []
spec_groups: dict[tuple[str, ...], list[str]] = {}

subparsers_actions = [a for a in hal.parser._subparsers._actions if hasattr(a, "choices") and a.choices]  # noqa: SLF001 private-member-access
if subparsers_actions:
    subparsers = subparsers_actions[0]

    help_map: dict[str, str] = {}
    if hasattr(subparsers, "_choices_actions"):
        for choice_action in subparsers._choices_actions:  # noqa: SLF001 private-member-access
            help_map[choice_action.dest] = choice_action.help or ""

    for cmd, parser in subparsers.choices.items():
        help_text: str = help_map.get(cmd, "")
        help_text = help_text.replace("'", "'\"'\"'")
        commands.append(f"        '{cmd}:{help_text}'")

        specs: list[str] = []
        for act in parser._actions:  # noqa: SLF001 private-member-access
            act_help = (act.help or "").replace("'", "'\"'\"'")
            if act.option_strings:
                value_part = "" if act.nargs == 0 else f":{act.dest}: "
                if len(act.option_strings) > 1:
                    exclusion = " ".join(act.option_strings)
                    brace = ",".join(act.option_strings)
                    specs.append(f"'({exclusion})'{{{brace}}}'[{act_help}]{value_part}'")
                else:
                    specs.append(f"'{act.option_strings[0]}[{act_help}]{value_part}'")
            elif act.dest == "filename":
                specs.append("':filename:_files'")
        specs.extend(PASSTHROUGH_SPECS.get(cmd, ()))
        spec_groups.setdefault(tuple(specs), []).append(cmd)

branch_blocks: list[str] = []
for group_specs, cmds in spec_groups.items():
    joined_specs = " \\\n                    ".join(group_specs)
    branch_blocks.append(f"""            {"|".join(cmds)})
                _arguments \\
                    {joined_specs}
                ;;""")

completion_content = f"""#compdef hal

_hal_tags() {{
    local -a tags used
    tags=(${{(f)"$(sed -n 's/^[[:space:]]*- {{ role: .*tags: \\["\\([^"]*\\)"\\].*/\\1/p' {REPO_ROOT}/playbooks/site.yml 2>/dev/null)"}})
    compset -P '*,'
    used=(${{(s:,:)IPREFIX}})
    tags=(${{tags:|used}})
    (( $#tags )) && compadd -S '' - $tags
}}

_hal() {{
    local -a commands

    commands=(
{chr(10).join(commands)}
    )

    if (( CURRENT == 2 )); then
        _describe -t commands 'hal commands' commands
        _arguments \\
            '(-h --help)'{{-h,--help}}'[show help message]' \\
            '(-v --version)'{{-v,--version}}'[show version]'
    else
        shift words
        (( CURRENT-- ))
        case "$words[1]" in
{chr(10).join(branch_blocks)}
            *)
                ;;
        esac
    fi
}}

compdef _hal hal"""

output_path = REPO_ROOT / "dotfiles" / ".hal_completion.zsh"
output_path.write_text(completion_content)

print("Generating zsh completion...")
print(f"Completion generated: {output_path}")
