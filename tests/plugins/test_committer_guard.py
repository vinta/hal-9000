import importlib.util
import io
import json
from pathlib import Path

import pytest


@pytest.fixture(scope="module")
def guard():
    spec = importlib.util.spec_from_file_location(
        "guard_committer_bash",
        Path(__file__).resolve().parent.parent.parent / "plugins" / "hal-skills" / "hooks" / "guard-committer-bash.py",
    )
    assert spec is not None
    assert spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestAllowed:
    @pytest.mark.parametrize(
        "command",
        [
            "git status",
            "git diff HEAD",
            "git diff --stat",
            "git log --oneline -5",
            "git show HEAD",
            "git branch --show-current",
            "git add dotfiles/.claude/CLAUDE.md",
            "git restore --staged file.py",
            "git rm --cached secrets.env",
            "git stash push --keep-index -m 'temp: unstaged changes'",
            "git stash pop",
            'git commit -m "docs: tune rules"',
            "cd /usr/local/hal-9000 && git status && git diff",
            'git commit -m "feat: support a && b > c || d"',
            "git commit -m 'msg with `backticks` and $(subshell) single-quoted'",
            "git status\ngit diff",
        ],
    )
    def test_allows(self, guard, command):
        assert guard.check(command) is None


class TestDenied:
    @pytest.mark.parametrize(
        ("command", "fragment"),
        [
            ("sed -i '' 's/foo/bar/' file.py", "not a git command"),
            ("echo done", "not a git command"),
            ("python3 script.py", "not a git command"),
            ("git apply --cached /tmp/patch.diff", "git apply"),
            ("git apply /tmp/patch.diff", "git apply"),
            ("git checkout -- file.py", "not in the committer allowlist"),
            ("git reset --hard HEAD", "not in the committer allowlist"),
            ("git push origin main", "not in the committer allowlist"),
            ("git mv old.py new.py", "not in the committer allowlist"),
            ("git config user.email x@y.z", "not in the committer allowlist"),
            ("git restore file.py", "--staged"),
            ("git restore --staged --worktree file.py", "--staged"),
            ("git rm file.py", "git rm"),
            ("git add -f build/artifact.bin", "git add -f"),
            ('git commit --amend -m "reword"', "amend"),
            ('git commit --no-verify -m "skip hooks"', "amend or skip hooks"),
            ("git branch -D feature", "read-only"),
            ("git diff > /tmp/patch.diff", "redirection"),
            ("git apply --cached < patch.diff", "redirection"),
            ("git commit -m $(cat msg.txt)", "command substitution"),
            ('git commit -m "msg $(cat msg.txt)"', "command substitution"),
            ("git commit -m `cat msg.txt`", "backticks"),
            ('git commit -m "msg `cat msg.txt`"', "backticks"),
            ("git log | head -5", "pipes"),
            ("git status & git diff", "pipes and background"),
            ("git status && sed -i '' 's/a/b/' f.py", "not a git command"),
            ("cd /repo; rm -rf .git", "not a git command"),
        ],
    )
    def test_denies(self, guard, command, fragment):
        reason = guard.check(command)
        assert reason is not None
        assert fragment in reason


class TestAgentScoping:
    def test_ignores_other_agents(self, guard, capsys, monkeypatch):
        payload = json.dumps(
            {
                "tool_name": "Bash",
                "tool_input": {"command": "rm -rf /"},
                "agent_type": "Explore",
            }
        )
        monkeypatch.setattr("sys.stdin", io.StringIO(payload))
        guard.main()
        assert capsys.readouterr().out == ""

    def test_ignores_main_thread(self, guard, capsys, monkeypatch):
        payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": "rm -rf /"}})
        monkeypatch.setattr("sys.stdin", io.StringIO(payload))
        guard.main()
        assert capsys.readouterr().out == ""

    @pytest.mark.parametrize("agent_type", ["committer", "hal-skills:committer"])
    def test_denies_for_committer(self, guard, capsys, monkeypatch, agent_type):
        payload = json.dumps(
            {
                "tool_name": "Bash",
                "tool_input": {"command": "sed -i '' 's/a/b/' file.py"},
                "agent_type": agent_type,
            }
        )
        monkeypatch.setattr("sys.stdin", io.StringIO(payload))
        guard.main()
        output = json.loads(capsys.readouterr().out)
        assert output["hookSpecificOutput"]["permissionDecision"] == "deny"

    def test_allows_for_committer(self, guard, capsys, monkeypatch):
        payload = json.dumps(
            {
                "tool_name": "Bash",
                "tool_input": {"command": "git status"},
                "agent_type": "hal-skills:committer",
            }
        )
        monkeypatch.setattr("sys.stdin", io.StringIO(payload))
        guard.main()
        assert capsys.readouterr().out == ""
