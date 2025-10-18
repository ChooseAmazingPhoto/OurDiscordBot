import logging
from typing import Optional, Tuple

import discord
from discord.utils import escape_markdown, format_dt

from .common import build_issue_url, parse_jira_datetime

logger = logging.getLogger(__name__)

ASSIGNEE_CHANGED_EVENT_TYPES = (
    "jira:issue_assignee_changed",
    "issue_assignee_changed",
    "assignee_changed",
)


def register(registry, register_classifier=None) -> None:
    registry.register(ASSIGNEE_CHANGED_EVENT_TYPES, handle_assignee_changed)
    if register_classifier:
        register_classifier(classify_assignee_changed)


def classify_assignee_changed(data: dict) -> Optional[str]:
    """
    Attempts to determine if an update payload represents an assignee change.
    """
    change, _ = _extract_change(data)
    if change:
        return "jira:issue_assignee_changed"
    return None


def handle_assignee_changed(data: dict, event_type=None) -> Optional[discord.Embed]:
    """
    Formats a Discord Embed for issue assignee change events.
    """
    issue = data.get("issue")
    if not issue:
        logger.debug("No issue found in payload; cannot format assignee change.")
        return None

    fields = issue.get("fields", {})
    change, audit_info = _extract_change(data)
    if not change:
        logger.debug("Assignee change not detected in payload.")
        return None

    issue_key = issue.get("key", "UNKNOWN-ISSUE")
    summary = _format_summary(fields.get("summary"))
    issue_url = build_issue_url(issue)

    embed = discord.Embed(
        title=f"[{issue_key}] Assignee Updated",
        description=summary,
        color=discord.Color.from_rgb(59, 130, 246),
    )
    if issue_url:
        embed.url = issue_url

    project_name = (fields.get("project") or {}).get("name", "Unknown Project")
    embed.set_author(name=project_name, url=issue_url or discord.Embed.Empty)

    previous = _derive_user_label(change.get("fromString"))
    new = _derive_user_label(change.get("toString"))
    embed.add_field(name="Previous assignee", value=previous, inline=True)
    embed.add_field(name="New assignee", value=new, inline=True)

    updated_by = _resolve_actor(data, audit_info)
    embed.add_field(name="Updated by", value=updated_by, inline=True)

    footer_entries = []
    priority = (fields.get("priority") or {}).get("name")
    status = (fields.get("status") or {}).get("name")
    if priority:
        footer_entries.append(f"Priority: {escape_markdown(priority)}")
    if status:
        footer_entries.append(f"Status: {escape_markdown(status)}")

    timestamp = (
        (audit_info or {}).get("created")
        or data.get("timestamp")
        or data.get("webhookEventCreated")
    )
    parsed_timestamp = parse_jira_datetime(timestamp)
    if parsed_timestamp:
        embed.timestamp = parsed_timestamp
        footer_entries.append(f"Updated {format_dt(parsed_timestamp, 'R')}")

    if footer_entries:
        embed.set_footer(text=" | ".join(footer_entries))

    return embed


def _extract_change(data: dict) -> Tuple[Optional[dict], Optional[dict]]:
    changelog = data.get("changelog") or (data.get("issue") or {}).get("changelog")
    if not changelog:
        return None, None

    items = changelog.get("items")
    if isinstance(items, list):
        for item in items:
            if _is_assignee_field(item):
                return item, changelog

    histories = changelog.get("histories")
    if isinstance(histories, list):
        for history in histories:
            for item in history.get("items", []):
                if _is_assignee_field(item):
                    audit = {
                        "created": history.get("created"),
                        "author": history.get("author"),
                    }
                    return item, audit

    return None, changelog if changelog else None


def _is_assignee_field(item: dict) -> bool:
    field = (item.get("field") or "").lower()
    field_id = (item.get("fieldId") or "").lower()
    return field == "assignee" or field_id == "assignee"


def _derive_user_label(raw_value: Optional[str]) -> str:
    if raw_value:
        return escape_markdown(raw_value)
    return "Unassigned"


def _resolve_actor(data: dict, audit_info: Optional[dict]) -> str:
    if audit_info and audit_info.get("author"):
        label = audit_info["author"].get("displayName") or audit_info["author"].get(
            "name"
        )
        if label:
            return escape_markdown(str(label))

    user = data.get("user") or {}
    display = user.get("displayName") or user.get("name") or user.get("emailAddress")
    if display:
        return escape_markdown(str(display))

    return "Unknown"


def _format_summary(summary) -> str:
    if isinstance(summary, str) and summary.strip():
        return f"> {escape_markdown(summary.strip())}"
    return "> No summary provided."
