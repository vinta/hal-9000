#!/usr/bin/env python3
"""Check that skill UI descriptions match both README skill lists."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]


def read_description(path: Path) -> object:
    in_interface = False
    for line in path.read_text().splitlines():
        if line and not line[0].isspace() and not line.startswith("#"):
            in_interface = line == "interface:"
        if in_interface and line.startswith("  short_description:"):
            # shortcut: descriptions use JSON-compatible quoted strings, use a YAML parser if the format changes
            return json.loads(line.partition(":")[2].strip())
    return None


def check(root: Path) -> list[str]:
    problems = []
    readmes = {}
    for path in (root / "README.md", root / "skills/README.md"):
        try:
            readmes[path] = path.read_text()
        except OSError as error:
            problems.append(f"{path.relative_to(root)}: cannot read README ({error}); restore the skill list")

    for skill in sorted((root / "skills").glob("*/SKILL.md")):
        metadata_path = skill.parent / "agents/openai.yaml"
        relative = metadata_path.relative_to(root)
        try:
            description = read_description(metadata_path)
        except (OSError, json.JSONDecodeError) as error:
            problems.append(f"{relative}: cannot read interface.short_description ({error}); use a single-line double-quoted string")
            continue
        if not isinstance(description, str) or not description.strip():
            problems.append(f"{relative}: interface.short_description must be a non-empty string; copy the README description")
            continue

        for readme, text in readmes.items():
            link = skill.relative_to(readme.parent).as_posix()
            entries = re.findall(rf"^- \[[^\]\n]+\]\({re.escape(link)}\): (.+)$", text, re.MULTILINE)
            if len(entries) != 1:
                problems.append(f"{readme.relative_to(root)}: expected one description for {link}, found {len(entries)}; fix the skill list entry")
            elif entries[0] != description:
                problems.append(f"{relative}: short_description differs from {readme.relative_to(root)}; set it to {entries[0]!r} and keep both READMEs in sync")

    return problems


def main() -> int:
    problems = check(REPO_ROOT)
    for problem in problems:
        print(problem)
    if problems:
        return 1
    print("Skill short descriptions match README.md and skills/README.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
