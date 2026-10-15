import json
import runpy
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / ".claude/skills/publish-plugins/scripts/check_skill_descriptions_sync.py"
DESCRIPTION = 'Answers "what\'s different?" quickly'


@pytest.fixture(scope="module")
def check():
    return runpy.run_path(str(SCRIPT))["check"]


@pytest.fixture
def repo(tmp_path):
    skill = tmp_path / "skills/difference"
    (skill / "agents").mkdir(parents=True)
    (skill / "SKILL.md").write_text("# Difference\n", encoding="utf-8")
    (skill / "agents/openai.yaml").write_text(
        f"interface:\n  short_description: {json.dumps(DESCRIPTION)}\n",
        encoding="utf-8",
    )
    (tmp_path / "README.md").write_text(f"- [difference](skills/difference/SKILL.md): {DESCRIPTION}\n", encoding="utf-8")
    (tmp_path / "skills/README.md").write_text(f"- [difference](difference/SKILL.md): {DESCRIPTION}\n", encoding="utf-8")
    return tmp_path


def test_matching_descriptions_with_yaml_quoting(check, repo):
    assert check(repo) == []


@pytest.mark.parametrize("readme", ["README.md", "skills/README.md"])
@pytest.mark.parametrize("replacement", ["Different description", ""])
def test_each_readme_must_include_matching_description(check, repo, readme, replacement):
    path = repo / readme
    path.write_text(path.read_text(encoding="utf-8").replace(DESCRIPTION, replacement) if replacement else "", encoding="utf-8")

    problems = check(repo)

    assert problems
    assert any(readme in problem and "difference" in problem for problem in problems)


@pytest.mark.parametrize("contents", [None, "interface:\n  display_name: Difference\n", 'interface:\n  short_description: "unterminated\n'])
def test_missing_or_invalid_metadata_is_reported(check, repo, contents):
    path = repo / "skills/difference/agents/openai.yaml"
    if contents is None:
        path.unlink()
    else:
        path.write_text(contents, encoding="utf-8")

    problems = check(repo)

    assert problems
    assert any("skills/difference/agents/openai.yaml" in problem for problem in problems)
    if contents and "display_name" in contents:
        assert any("short_description" in problem for problem in problems)


def test_description_in_other_section_does_not_satisfy_interface(check, repo):
    (repo / "skills/difference/agents/openai.yaml").write_text(
        f"interface:\n  display_name: Difference\nother:\n  short_description: {json.dumps(DESCRIPTION)}\n",
        encoding="utf-8",
    )

    problems = check(repo)

    assert any("skills/difference/agents/openai.yaml" in problem and "short_description" in problem for problem in problems)
