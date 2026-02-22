"""Tests for bin/hal security hardening."""

import importlib.machinery
import importlib.util
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
