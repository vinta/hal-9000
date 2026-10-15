import json
import subprocess
import sys

from .conftest import GUARD_PATH


class TestCheck:
    def test_denied_home_prefix(self, guard):
        assert guard.check(f"cat {guard.HOME}/.ssh/id_rsa") == f"{guard.HOME}/.ssh"

    def test_tilde_expansion(self, guard):
        assert guard.check("cat ~/.aws/config") == f"{guard.HOME}/.aws"

    def test_home_var_normalization(self, guard):
        assert guard.check("ls $HOME/.gnupg") == f"{guard.HOME}/.gnupg"
        assert guard.check("ls ${HOME}/.kube") == f"{guard.HOME}/.kube"

    def test_etc_prefix(self, guard):
        assert guard.check("cat /etc/passwd") == "/etc/"

    def test_etc_without_trailing_slash(self, guard):
        assert guard.check("ls /etc") == "/etc/"

    def test_etc_lookalike_allowed(self, guard):
        assert guard.check("cat /etcetera/notes.txt") is None

    def test_prefix_boundary_is_respected(self, guard):
        """A longer name that merely starts with a denied one is not blocked."""
        assert guard.check(f"ls {guard.HOME}/.configuration/app") is None

    def test_history_file_in_home(self, guard):
        assert guard.check("cat ~/.zsh_history") == "~/*_history"
        assert guard.check("tail $HOME/.bash_history") == "~/*_history"

    def test_history_file_outside_home_root_allowed(self, guard):
        assert guard.check(f"cat {guard.HOME}/project/chat_history.py") is None
        assert guard.check("cat /var/log/app_history") is None

    def test_backslash_in_assignment_value(self, guard):
        assert guard.check(r'RE=\d+; grep "$RE" notes.txt') is None

    def test_benign_commands_allowed(self, guard):
        assert guard.check("ls -la") is None
        assert guard.check(f"cat {guard.HOME}/project/notes.txt") is None


class TestHookProcessContract:
    """End-to-end cases pinning the stdin/stdout hook protocol."""

    def test_denied_command_emits_ask_json(self):
        hook_input = json.dumps({"tool_input": {"command": "cat ~/.ssh/id_rsa"}})
        result = subprocess.run(  # noqa: S603 PLW1510 subprocess-without-shell-equals-true subprocess-run-without-check
            [sys.executable, str(GUARD_PATH)],
            input=hook_input,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert output["hookSpecificOutput"]["permissionDecision"] == "ask"
        assert output["hookSpecificOutput"]["hookEventName"] == "PreToolUse"

    def test_benign_command_emits_nothing(self):
        hook_input = json.dumps({"tool_input": {"command": "ls -la"}})
        result = subprocess.run(  # noqa: S603 PLW1510 subprocess-without-shell-equals-true subprocess-run-without-check
            [sys.executable, str(GUARD_PATH)],
            input=hook_input,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert result.stdout == ""
