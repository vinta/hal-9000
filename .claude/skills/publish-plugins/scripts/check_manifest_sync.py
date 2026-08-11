#!/usr/bin/env python3
"""Check that every plugin's marketplace entry and its own plugin.json agree, and that both describe what is on disk."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[4]
MARKETPLACE = REPO_ROOT / ".claude-plugin" / "marketplace.json"

# Fields the marketplace entry owns on its own, so plugin.json never carries them.
MARKETPLACE_ONLY_FIELDS = {"source", "category", "tags", "strict", "defaultEnabled"}

# Fields whose values are paths inside the plugin.
COMPONENT_PATH_FIELDS = {"skills", "commands", "agents", "workflows", "hooks", "mcpServers", "lspServers", "outputStyles"}


def load(path: Path) -> Any:  # noqa: ANN401 manifests are free-form JSON
    return json.loads(path.read_text())


def comparable(value: Any) -> Any:  # noqa: ANN401 manifest values are free-form JSON
    """Order-insensitive view of a field, so a reordered list is not a mismatch."""
    if isinstance(value, list):
        return sorted(json.dumps(item, sort_keys=True) for item in value)
    return value


def declared_paths(manifest: dict[str, Any], field: str) -> list[str]:
    """Component fields hold a path, a list of paths, or inline config that declares no path at all."""
    value = manifest.get(field)
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [item for item in value if isinstance(item, str)]
    return []


def check_fields(entry: dict[str, Any], manifest: dict[str, Any], relative: Path) -> list[str]:
    """Both manifests have to declare the same fields with the same values, apart from the ones with a single home."""
    name = entry["name"]
    single_home = MARKETPLACE_ONLY_FIELDS | {"version"}
    shared = sorted((set(entry) | set(manifest)) - single_home)

    problems = [f"{name}: version lives in {relative} only, drop it from the marketplace entry"] if "version" in entry else []
    problems += [f"{name}: {field} belongs in the marketplace entry, not {relative}" for field in sorted(set(manifest) & MARKETPLACE_ONLY_FIELDS)]
    problems += [f"{name}: {field} is in {relative} but missing from the marketplace entry" for field in shared if field not in entry]
    problems += [f"{name}: {field} is in the marketplace entry but missing from {relative}" for field in shared if field not in manifest]
    problems += [
        f"{name}: {field} differs between the marketplace entry and {relative}" for field in shared if field in entry and field in manifest and comparable(entry[field]) != comparable(manifest[field])
    ]
    return problems


def check_paths_exist(entry: dict[str, Any], manifest: dict[str, Any], base: Path) -> list[str]:
    """Every component path either manifest declares has to exist."""
    name = entry["name"]
    problems = []

    for field in sorted(COMPONENT_PATH_FIELDS):
        for source, paths in (("the marketplace entry", declared_paths(entry, field)), (f"{name}'s plugin.json", declared_paths(manifest, field))):
            problems += [f"{name}: {field} in {source} points at {path}, which does not exist" for path in paths if not (base / path).exists()]

    return problems


def check_skills_listed(entry: dict[str, Any], manifest: dict[str, Any], base: Path) -> list[str]:
    """A skill directory sitting in the plugin root has to appear in both skill lists."""
    on_disk = {f"./{path.parent.name}" for path in base.glob("*/SKILL.md")}
    if not on_disk:
        return []

    name = entry["name"]
    return [f"{name}: {path} is missing from a skill list" for path in sorted(on_disk - (set(declared_paths(entry, "skills")) & set(declared_paths(manifest, "skills"))))]


def main() -> int:
    entries = load(MARKETPLACE)["plugins"]
    problems = []

    for entry in entries:
        base = REPO_ROOT / entry["source"]
        manifest_path = base / ".claude-plugin" / "plugin.json"
        if not manifest_path.exists():
            problems.append(f"{entry['name']}: no plugin manifest at {manifest_path.relative_to(REPO_ROOT)}")
            continue

        manifest = load(manifest_path)
        problems += check_fields(entry, manifest, manifest_path.relative_to(REPO_ROOT))
        problems += check_paths_exist(entry, manifest, base)
        problems += check_skills_listed(entry, manifest, base)

    for problem in problems:
        print(problem)

    if problems:
        return 1

    print(f"{len(entries)} plugins: marketplace entries and plugin manifests agree")
    return 0


if __name__ == "__main__":
    sys.exit(main())
