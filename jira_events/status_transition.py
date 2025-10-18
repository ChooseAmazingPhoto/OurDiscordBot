import logging
from typing import Optional, Tuple

import discord
from discord.utils import escape_markdown, format_dt

from .common import build_issue_url, parse_jira_datetime

logger = logging.getLogger(__name__)

STATUS_TRANSITION_EVENT_TYPES = (
    "jira:issue_status_changed",
    "issue_status_changed",
    "issue_status_transitioned",
)


def register(registry, register_classifier=None) -> None:
    registry.register(STATUS_TRANSITION_EVENT_TYPES, handle_status_transition)
    if register_classifier:
        register_classifier(classify_status_transition)


def classify_status_transition(data: dict) -> Optional[str]:
    """
    Attempts to determine if an update payload represents a status change.
    """
    change, _ = _extract_status_change(data)
    if change:
        return "jira:issue_status_changed"
    return None


def handle_status_transition(data: dict, event_type=None) -> Optional[discord.Embed]:
    """
    Formats a Discord Embed for issue status transition events.
    """
    issue = data.get("issue")
    if not issue:
        logger.debug("No issue found in payload; cannot format status transition.")
        return None

    fields = issue.get("fields", {})
    change, audit_info = _extract_status_change(data)
    if not change:
        logger.debug("Status change not detected in payload.")
        return None

    issue_key = issue.get("key", "UNKNOWN-ISSUE")
    summary = _format_summary(fields.get("summary"))
    issue_url = build_issue_url(issue)

    embed = discord.Embed(
        title=f"[{issue_key}] Status Updated",
        description=summary,
        color=_status_color(change.get("toString")),
    )
    if issue_url:
        embed.url = issue_url

    project = fields.get("project") or {}
    project_name = project.get("name", "Unknown Project")
    embed.set_author(name=project_name, url=issue_url or discord.Embed.Empty)

    from_value = _normalize_status_label(change.get("fromString"))
    to_value = _normalize_status_label(change.get("toString"))

    embed.add_field(name="From", value=from_value, inline=True)
    embed.add_field(name="To", value=to_value, inline=True)
    embed.add_field(
        name="Changed by", value=_resolve_actor(data, audit_info), inline=True
    )

    priority = (fields.get("priority") or {}).get("name")
    assignee_info = fields.get("assignee") or {}
    assignee = assignee_info.get("displayName") or assignee_info.get("name")

    footer_parts = []
    if priority:
        footer_parts.append(f"Priority: {escape_markdown(priority)}")
    if assignee:
        footer_parts.append(f"Assignee: {escape_markdown(assignee)}")

    timestamp = (
        (audit_info or {}).get("created")
        or data.get("timestamp")
        or data.get("webhookEventCreated")
    )
    parsed_timestamp = parse_jira_datetime(timestamp)
    if parsed_timestamp:
        embed.timestamp = parsed_timestamp
        footer_parts.append(f"Updated {format_dt(parsed_timestamp, 'R')}")

    if footer_parts:
        embed.set_footer(text=" | ".join(footer_parts))

    return embed


def _extract_status_change(data: dict) -> Tuple[Optional[dict], Optional[dict]]:
    changelog = data.get("changelog") or (data.get("issue") or {}).get("changelog")
    if not changelog:
        return None, None

    items = changelog.get("items")
    if isinstance(items, list):
        for item in items:
            if _is_status_field(item):
                return item, changelog

    histories = changelog.get("histories")
    if isinstance(histories, list):
        for history in histories:
            for item in history.get("items", []):
                if _is_status_field(item):
                    audit = {
                        "created": history.get("created"),
                        "author": history.get("author"),
                    }
                    return item, audit

    return None, changelog if changelog else None


def _is_status_field(item: dict) -> bool:
    field = (item.get("field") or "").lower()
    field_id = (item.get("fieldId") or "").lower()
    return field == "status" or field_id == "status"


def _normalize_status_label(value: Optional[str]) -> str:
    if value:
        return escape_markdown(value)
    return "Unknown"


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


def _status_color(status: Optional[str]) -> discord.Color:
    normalized = (status or "").lower()
    palette = {
        "to do": discord.Color.from_rgb(148, 163, 184),
        "selected for development": discord.Color.from_rgb(96, 165, 250),
        "in progress": discord.Color.from_rgb(234, 179, 8),
        "in review": discord.Color.from_rgb(249, 115, 22),
        "blocked": discord.Color.from_rgb(220, 38, 38),
        "done": discord.Color.from_rgb(34, 197, 94),
        "closed": discord.Color.from_rgb(22, 163, 74),
    }
    return palette.get(normalized, discord.Color.blurple())


def _format_summary(summary) -> str:
    if isinstance(summary, str) and summary.strip():
        return f"> {escape_markdown(summary.strip())}"
    return "> No summary provided."
