#!/usr/bin/env python3
"""Check that the hal-skills skill list matches across both manifests and the skills/ directory."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
MARKETPLACE = REPO_ROOT / ".claude-plugin" / "marketplace.json"
PLUGIN = REPO_ROOT / "skills" / ".claude-plugin" / "plugin.json"
PLUGIN_NAME = "hal-skills"


def marketplace_skills() -> set[str]:
    entries = json.loads(MARKETPLACE.read_text())["plugins"]
    entry = next(e for e in entries if e["name"] == PLUGIN_NAME)
    return set(entry.get("skills", []))


def plugin_skills() -> set[str]:
    return set(json.loads(PLUGIN.read_text()).get("skills", []))


def skills_on_disk() -> set[str]:
    return {f"./{path.parent.name}" for path in (REPO_ROOT / "skills").glob("*/SKILL.md")}


def main() -> int:
    on_disk = skills_on_disk()
    in_marketplace = marketplace_skills()
    in_plugin = plugin_skills()

    problems = {
        f"missing from {MARKETPLACE.relative_to(REPO_ROOT)}": (on_disk | in_plugin) - in_marketplace,
        f"missing from {PLUGIN.relative_to(REPO_ROOT)}": (on_disk | in_marketplace) - in_plugin,
        "listed in a manifest but not on disk": (in_marketplace | in_plugin) - on_disk,
    }

    for label, paths in problems.items():
        for path in sorted(paths):
            print(f"{label}: {path}")

    if any(problems.values()):
        return 1

    print(f"{len(on_disk)} skills listed in both manifests")
    return 0


if __name__ == "__main__":
    sys.exit(main())
