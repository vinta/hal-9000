import importlib.util
from pathlib import Path

import pytest

GUARD_PATH = Path(__file__).resolve().parent.parent.parent / "dotfiles" / ".claude" / "hooks" / "guard-bash-paths.py"
EGRESS_GUARD_PATH = GUARD_PATH.with_name("guard-network-egress.py")


@pytest.fixture
def guard():
    spec = importlib.util.spec_from_file_location("guard_bash_paths", GUARD_PATH)
    assert spec is not None
    assert spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def egress_guard():
    spec = importlib.util.spec_from_file_location("guard_network_egress", EGRESS_GUARD_PATH)
    assert spec is not None
    assert spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod
