import importlib.util
from pathlib import Path

import pytest


@pytest.fixture
def hal():
    spec = importlib.util.spec_from_file_location(
        "hal_voice",
        Path(__file__).resolve().parent.parent.parent / "plugins" / "hal-voice" / "scripts" / "hal-voice.py",
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod
