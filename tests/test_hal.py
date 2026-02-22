"""Tests for bin/hal security hardening."""

import argparse
import importlib.machinery
import importlib.util
import shlex
import sys
from pathlib import Path
from unittest.mock import patch

import pytest


@pytest.fixture
def hal_module():
    """Import bin/hal as a module."""
    hal_path = str(Path(__file__).resolve().parent.parent / "bin" / "hal")
    spec = importlib.util.spec_from_loader(
        "hal",
        loader=importlib.machinery.SourceFileLoader("hal", hal_path),
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["hal"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def hal_instance(hal_module):
    """Create a HAL9000 instance."""
    return hal_module.HAL9000()


class TestValidatePath:
    def test_valid_path_under_home(self, hal_instance):
        home = str(Path.home())
        path = f"{home}/.zshrc"
        hal_instance._validate_path(path)

    def test_valid_path_under_repo_root(self, hal_instance, hal_module):
        path = f"{hal_module.Setting.REPO_ROOT}/dotfiles/.zshrc"
        hal_instance._validate_path(path)

    def test_path_traversal_outside_home(self, hal_instance):
        home = str(Path.home())
        path = f"{home}/../../etc/passwd"
        with pytest.raises(SystemExit):
            hal_instance._validate_path(path)

    def test_path_to_etc(self, hal_instance):
        with pytest.raises(SystemExit):
            hal_instance._validate_path("/etc/crontab")

    def test_path_traversal_in_template_expansion(self, hal_instance):
        with pytest.raises(SystemExit):
            hal_instance._expand_template("{{HOME}}/../../etc/crontab")

    def test_normal_template_expansion(self, hal_instance):
        result = hal_instance._expand_template("{{HOME}}/.zshrc")
        assert result == f"{Path.home()}/.zshrc"


class TestUpdateSanitization:
    def test_extra_args_are_quoted(self, hal_instance):
        """extra_args with shell metacharacters must be quoted."""
        commands_run = []

        def mock_run(command, *, shell=True, verbose=True):  # noqa: ARG001 unused-function-argument
            commands_run.append(command)
            return 0

        def mock_run_with_output(command, *, shell=True, verbose=True, print_output=True):  # noqa: ARG001 unused-function-argument
            commands_run.append(command)
            return 0, b"/opt/homebrew/bin/ansible\n"

        hal_instance._run = mock_run
        hal_instance._run_with_output = mock_run_with_output

        ns = argparse.Namespace(func=hal_instance.update)
        hal_instance.update(ns, extra_args=["--tags", "foo;rm -rf ~"])

        ansible_cmd = next(c for c in commands_run if "ansible-playbook" in c)
        # The dangerous string must be quoted -- bare ;rm should not appear
        assert ";rm" not in ansible_cmd or shlex.quote("foo;rm -rf ~") in ansible_cmd


class TestFileOpsUseStdlib:
    """Verify link() and copy() don't shell out for mkdir/mv/cp."""

    def test_link_no_shell_mkdir(self, hal_instance, tmp_path):
        """link() should use Path.mkdir() not shell mkdir."""
        commands_run = []
        original_run = hal_instance._run

        def tracking_run(command, *, shell=True, verbose=True):
            commands_run.append(command)
            return original_run(command, shell=shell, verbose=verbose)

        hal_instance._run = tracking_run

        test_file = tmp_path / "testfile"
        test_file.write_text("content")

        ns = argparse.Namespace(filename=str(test_file))

        with (
            patch.object(hal_instance, "dotfiles") as mock_dotfiles,
            patch("pathlib.Path.cwd", return_value=tmp_path),
            patch.object(hal_instance, "_validate_path"),
        ):
            mock_dotfiles.find_by_key.return_value = None
            mock_dotfiles.data = {"links": [], "copies": []}
            hal_instance.link(ns)

        mkdir_cmds = [c for c in commands_run if c.startswith("mkdir ")]
        assert len(mkdir_cmds) == 0, f"Should not shell out to mkdir: {mkdir_cmds}"
        mv_cmds = [c for c in commands_run if c.startswith("mv ")]
        assert len(mv_cmds) == 0, f"Should not shell out to mv: {mv_cmds}"

    def test_copy_no_shell_cp(self, hal_instance, tmp_path):
        """copy() should use shutil.copy2() not shell cp."""
        commands_run = []

        def tracking_run(command, *, shell=True, verbose=True):  # noqa: ARG001 unused-function-argument
            commands_run.append(command)
            return 0

        hal_instance._run = tracking_run

        test_file = tmp_path / "testfile"
        test_file.write_text("content")

        ns = argparse.Namespace(filename=str(test_file))

        with (
            patch.object(hal_instance, "dotfiles") as mock_dotfiles,
            patch("pathlib.Path.cwd", return_value=tmp_path),
            patch.object(hal_instance, "_validate_path"),
        ):
            mock_dotfiles.find_by_key.return_value = None
            mock_dotfiles.data = {"links": [], "copies": []}
            hal_instance.copy(ns)

        cp_cmds = [c for c in commands_run if c.startswith("cp ")]
        assert len(cp_cmds) == 0, f"Should not shell out to cp: {cp_cmds}"


class TestUserFilenameValidation:
    def test_link_validates_filename(self, hal_instance, tmp_path):
        ns = argparse.Namespace(filename="../../../etc/passwd")
        with patch("pathlib.Path.cwd", return_value=tmp_path), pytest.raises(SystemExit):
            hal_instance.link(ns)

    def test_copy_validates_filename(self, hal_instance, tmp_path):
        ns = argparse.Namespace(filename="../../../etc/passwd")
        with patch("pathlib.Path.cwd", return_value=tmp_path), pytest.raises(SystemExit):
            hal_instance.copy(ns)


class TestArgParsing:
    def test_unknown_args_rejected_for_link(self, hal_module):
        """Non-update commands should reject unknown arguments."""
        sys.argv = ["hal", "link", "--bogus", "somefile"]
        hal = hal_module.HAL9000()
        with pytest.raises(SystemExit) as exc_info:
            hal.read_lips()
        assert exc_info.value.code == 2  # noqa: PLR2004 argparse-usage-error

    def test_unknown_args_rejected_for_sync(self, hal_module):
        """sync should also reject unknown arguments."""
        sys.argv = ["hal", "sync", "--unknown"]
        hal = hal_module.HAL9000()
        with pytest.raises(SystemExit) as exc_info:
            hal.read_lips()
        assert exc_info.value.code == 2  # noqa: PLR2004 argparse-usage-error
