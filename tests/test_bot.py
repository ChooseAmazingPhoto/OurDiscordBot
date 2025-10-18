import pytest
import os
import discord
from unittest.mock import patch

# Set environment variables before importing the bot module
os.environ["DISCORD_BOT_TOKEN"] = "test_token"
os.environ["DISCORD_CHANNEL_ID"] = "12345"
os.environ["JIRA_WEBHOOK_SECRET"] = "secret"

from bot import app as flask_app


@pytest.fixture
def client():
    """A test client for the Flask app."""
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        yield client


def test_health_check(client):
    """Test the /health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.data == b"OK"


def test_jira_webhook_unauthorized(client):
    """Test that the Jira webhook returns 403 with an invalid secret."""
    response = client.post("/webhooks/jira?secret=wrong_secret", json={"key": "value"})
    assert response.status_code == 403


def test_jira_webhook_missing_secret(client):
    """Test that the Jira webhook returns 403 with a missing secret."""
    response = client.post("/webhooks/jira", json={"key": "value"})
    assert response.status_code == 403


@patch("bot.notifier.send")
def test_jira_webhook_success_with_embed(mock_send_message, client):
    """Test a successful Jira webhook call that returns an embed."""
    payload = {
        "webhookEvent": "jira:issue_created",
        "issue": {
            "self": "https://example.atlassian.net/rest/api/2/issue/12345",
            "key": "DCBOT-99",
            "fields": {
                "summary": "A brand new issue",
                "reporter": {"displayName": "Example Reporter"},
                "issuetype": {"name": "Task"},
                "priority": {"name": "Medium"},
                "project": {"name": "Discord Bot"},
            },
        },
    }

    response = client.post("/webhooks/jira?secret=secret", json=payload)

    assert response.status_code == 200
    assert response.data == b"OK"
    mock_send_message.assert_called_once()
    _, kwargs = mock_send_message.call_args
    assert isinstance(kwargs["embed"], discord.Embed)


@patch("bot.notifier.send")
def test_jira_webhook_success_no_embed(mock_send_message, client):
    """Test a successful Jira webhook call that does not return an embed."""
    payload = {
        "webhookEvent": "jira:issue_deleted",
        "issue": {
            "self": "https://example.atlassian.net/rest/api/2/issue/12345",
            "key": "DCBOT-99",
            "fields": {"summary": "No longer valid"},
        },
    }

    response = client.post("/webhooks/jira?secret=secret", json=payload)

    assert response.status_code == 200
    assert response.data == b"OK"
    mock_send_message.assert_not_called()


def test_jira_webhook_invalid_json_causes_400(client):
    """
    Test that the Jira webhook returns a 400 Bad Request error
    when the JSON payload is malformed.
    """
    response = client.post(
        "/webhooks/jira?secret=secret",
        data="this is not valid json",
        content_type="application/json",
    )
    assert response.status_code == 400
