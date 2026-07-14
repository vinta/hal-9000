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

    def test_credential_substring_under_home(self, guard):
        assert guard.check(f"cat {guard.HOME}/myapp/credentials.json") == "~/*credential*"

    def test_credential_outside_home_allowed(self, guard):
        assert guard.check("cat /opt/app/credentials.json") is None

    def test_benign_commands_allowed(self, guard):
        assert guard.check("ls -la") is None
        assert guard.check(f"cat {guard.HOME}/project/notes.txt") is None


class TestHookProcessContract:
    """End-to-end cases pinning the stdin/stdout hook protocol."""

    def test_denied_command_emits_deny_json(self):
        hook_input = json.dumps({"tool_input": {"command": "cat ~/.ssh/id_rsa"}})
        result = subprocess.run(  # noqa: S603 PLW1510 subprocess-without-shell-equals-true subprocess-run-without-check
            [sys.executable, str(GUARD_PATH)],
            input=hook_input,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert output["hookSpecificOutput"]["permissionDecision"] == "deny"
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
