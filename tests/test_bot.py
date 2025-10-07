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


def test_get_channel_id_returns_int(monkeypatch):
    monkeypatch.setenv("DISCORD_JIRA_CHANNEL_ID", "1234567890")
    bot_module = reload_bot()
    assert bot_module.get_channel_id() == 1234567890


def test_get_channel_id_requires_integer(monkeypatch):
    monkeypatch.setenv("DISCORD_JIRA_CHANNEL_ID", "not-a-number")
    bot_module = reload_bot()
    with pytest.raises(RuntimeError):
        bot_module.get_channel_id()


def test_authorize_request_valid():
    headers = {"Authorization": "Bearer secret"}
    assert bot.authorize_request(headers, "secret") is True


def test_authorize_request_invalid_scheme():
    headers = {"Authorization": "Basic secret"}
    assert bot.authorize_request(headers, "secret") is False


def test_sanitize_payload_coerces_none():
    payload = {
        "issueKey": "PROJ-2",
        "summary": None,
        "status": None,
        "event": None,
        "link": None,
        "triggeredBy": None,
        "timestamp": None,
    }
    sanitized = bot.sanitize_payload(payload)
    assert sanitized["summary"] == ""
    assert sanitized["event"] == ""


def test_format_notification_truncates(monkeypatch):
    issue_key = "PROJ-1"
    payload = {
        "issueKey": issue_key,
        "summary": "A" * 2100,
        "status": "In Progress",
        "event": "Updated",
        "link": "https://example.com",
        "triggeredBy": "User",
        "timestamp": "2024-01-01T00:00:00Z",
    }
    message = bot.format_notification(payload)
    assert len(message) <= 2000
    assert message.startswith(f"**{issue_key}**")


def test_main_exits_when_token_missing(monkeypatch, capsys):
    monkeypatch.delenv("DISCORD_TOKEN", raising=False)
    monkeypatch.setenv("DISCORD_JIRA_CHANNEL_ID", "123456")
    monkeypatch.setenv("JIRA_WEBHOOK_TOKEN", "secret")
    bot_module = reload_bot()

    with pytest.raises(SystemExit) as excinfo:
        bot_module.main()

    assert excinfo.value.code == 1
    assert "Missing DISCORD_TOKEN" in capsys.readouterr().err
