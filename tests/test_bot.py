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

@patch("bot.send_discord_message")
@patch("bot.process_jira_event")
def test_jira_webhook_success_with_embed(mock_process_event, mock_send_message, client):
    """Test a successful Jira webhook call that returns an embed."""
    mock_embed = discord.Embed(title="Test Embed")
    mock_process_event.return_value = mock_embed
    
    response = client.post("/webhooks/jira?secret=secret", json={"event": "test"})
    
    assert response.status_code == 200
    assert response.data == b"OK"
    mock_process_event.assert_called_once_with({"event": "test"})
    mock_send_message.assert_called_once_with(embed=mock_embed)

@patch("bot.send_discord_message")
@patch("bot.process_jira_event")
def test_jira_webhook_success_no_embed(mock_process_event, mock_send_message, client):
    """Test a successful Jira webhook call that does not return an embed."""
    mock_process_event.return_value = None
    
    response = client.post("/webhooks/jira?secret=secret", json={"event": "unhandled"})
    
    assert response.status_code == 200
    assert response.data == b"OK"
    mock_process_event.assert_called_once_with({"event": "unhandled"})
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