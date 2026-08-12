import importlib.util
from pathlib import Path

import pytest


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None
    assert spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


PLUGINS_DIR = Path(__file__).resolve().parent.parent.parent / "plugins"


@pytest.fixture
def hal():
    return load_module("hal_voice", PLUGINS_DIR / "hal-voice" / "scripts" / "hal-voice.py")


@pytest.fixture
def statusline():
    return load_module("hal_statusline", PLUGINS_DIR / "hal-statusline" / "hal-statusline.py")


@pytest.fixture
def autorename(tmp_path, monkeypatch):
    mod = load_module("hal_session_auto_rename", PLUGINS_DIR / "hal-session-auto-rename" / "scripts" / "hal-session-auto-rename.py")
    monkeypatch.setattr(mod, "STATE_DIR", tmp_path / "state")
    # The developer shell exports this, and inheriting it would flip every test into refresh mode
    monkeypatch.delenv("HAL_SESSION_AUTO_RENAME_REFRESH_EVERY_N_PROMPTS", raising=False)
    return mod
