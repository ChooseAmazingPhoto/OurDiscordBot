import importlib
import sys

import pytest
import bot


def reload_bot():
    return importlib.reload(sys.modules["bot"])


def test_get_token_returns_env_value(monkeypatch):
    monkeypatch.setenv("DISCORD_TOKEN", "test-token")
    bot_module = reload_bot()
    assert bot_module.get_token() == "test-token"


def test_main_exits_when_token_missing(monkeypatch, capsys):
    monkeypatch.delenv("DISCORD_TOKEN", raising=False)
    bot_module = reload_bot()

    with pytest.raises(SystemExit) as excinfo:
        bot_module.main()

    assert excinfo.value.code == 1
    assert "Missing DISCORD_TOKEN" in capsys.readouterr().err
