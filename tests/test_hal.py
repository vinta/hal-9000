"""Tests for bin/hal security hardening."""

import argparse
import importlib.machinery
import importlib.util
import shlex
import sys
from pathlib import Path

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
