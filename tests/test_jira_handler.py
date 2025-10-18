import discord
from jira_events import registry
from ourdiscordbot.jira_handler import process_jira_event


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


def _sample_assignee_change_payload():
    payload = _sample_issue_payload()
    payload["webhookEvent"] = "jira:issue_updated"
    payload["user"] = {"displayName": "Automation Bot"}
    payload["changelog"] = {
        "created": "2025-10-18T12:00:00.000+0000",
        "items": [
            {
                "field": "assignee",
                "fromString": "Alice",
                "toString": "Bob",
            }
        ],
    }
    return payload


def _sample_status_change_payload():
    payload = _sample_issue_payload()
    payload["webhookEvent"] = "jira:issue_updated"
    payload["user"] = {"displayName": "QA Analyst"}
    payload["issue"]["fields"]["assignee"] = {"displayName": "Bob"}
    payload["issue"]["fields"]["priority"] = {"name": "High"}
    payload["changelog"] = {
        "created": "2025-10-18T12:05:00.000+0000",
        "items": [
            {
                "field": "status",
                "fromString": "In Progress",
                "toString": "In Review",
            }
        ],
    }
    return payload


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


def test_process_jira_event_formats_assignee_change():
    payload = _sample_assignee_change_payload()

    embed = process_jira_event(payload)

    assert isinstance(embed, discord.Embed)
    assert embed.title == "[DCBOT-30] Assignee Updated"
    field_map = {field.name: field.value for field in embed.fields}
    assert field_map["Previous assignee"] == "Alice"
    assert field_map["New assignee"] == "Bob"
    assert field_map["Updated by"] == "Automation Bot"


def test_assignee_classifier_detects_history_items():
    from jira_events import assignee_changed

    payload = _sample_assignee_change_payload()
    payload["changelog"] = {
        "histories": [
            {
                "created": "2025-10-18T12:00:00.000+0000",
                "author": {"displayName": "Alice"},
                "items": [
                    {
                        "field": "Assignee",
                        "fromString": "Alice",
                        "toString": "Bob",
                    }
                ],
            }
        ]
    }

    result = assignee_changed.classify_assignee_changed(payload)

    assert result == "jira:issue_assignee_changed"


def test_process_jira_event_formats_status_transition():
    payload = _sample_status_change_payload()

    embed = process_jira_event(payload)

    assert isinstance(embed, discord.Embed)
    assert embed.title == "[DCBOT-30] Status Updated"
    field_map = {field.name: field.value for field in embed.fields}
    assert field_map["From"] == "In Progress"
    assert field_map["To"] == "In Review"
    assert field_map["Changed by"] == "QA Analyst"
    assert "Priority" in embed.footer.text
    assert "Assignee" in embed.footer.text


def test_status_classifier_detects_history_items():
    from jira_events import status_transition

    payload = _sample_status_change_payload()
    payload["changelog"] = {
        "histories": [
            {
                "created": "2025-10-18T12:05:00.000+0000",
                "author": {"displayName": "Release Manager"},
                "items": [
                    {
                        "field": "Status",
                        "fromString": "To Do",
                        "toString": "In Progress",
                    }
                ],
            }
        ]
    }

    result = status_transition.classify_status_transition(payload)

    assert result == "jira:issue_status_changed"
