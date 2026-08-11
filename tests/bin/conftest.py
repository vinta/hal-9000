import importlib.util
import sys
from pathlib import Path

import pytest


@pytest.fixture
def hal_module():
    """Import bin/hal.py as a module."""
    hal_path = Path(__file__).resolve().parent.parent.parent / "bin" / "hal.py"
    spec = importlib.util.spec_from_file_location("hal", hal_path)
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
