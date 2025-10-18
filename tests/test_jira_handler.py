import discord
from jira_events import registry
from jira_handler import process_jira_event


def _sample_issue_payload():
    return {
        "issue": {
            "self": "https://example.atlassian.net/rest/api/2/issue/12345",
            "key": "DCBOT-30",
            "fields": {
                "summary": "Example summary",
                "reporter": {"displayName": "Example Reporter"},
                "issuetype": {"name": "Task"},
                "priority": {"name": "Medium"},
                "project": {"name": "Discord Bot"},
                "created": "2025-10-18T11:58:18.965+0800",
            },
        }
    }


def test_process_jira_event_returns_embed_for_issue_created():
    payload = _sample_issue_payload()
    payload["webhookEvent"] = "jira:issue_created"

    embed = process_jira_event(payload)

    assert isinstance(embed, discord.Embed)
    assert embed.title == "[DCBOT-30] New Issue Created"
    assert embed.url == "https://example.atlassian.net/browse/DCBOT-30"


def test_process_jira_event_infers_issue_created_when_event_missing():
    payload = _sample_issue_payload()

    embed = process_jira_event(payload)

    assert isinstance(embed, discord.Embed)
    assert embed.title == "[DCBOT-30] New Issue Created"


def test_process_jira_event_returns_none_for_unregistered_event():
    payload = _sample_issue_payload()
    payload["webhookEvent"] = "jira:issue_deleted"

    embed = process_jira_event(payload)

    assert embed is None


def test_registry_dispatch_passes_event_type():
    sentinel = object()
    captured = {}

    def handler(data, event_type):
        captured["event"] = event_type
        return sentinel

    registry.register(["custom:event"], handler)

    result = registry.dispatch("custom:event", {})

    assert result is sentinel
    assert captured["event"] == "custom:event"
