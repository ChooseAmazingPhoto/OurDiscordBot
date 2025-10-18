import logging
from typing import Optional

import discord
from discord.utils import escape_markdown, format_dt

from .common import build_issue_url, parse_jira_datetime

logger = logging.getLogger(__name__)

ISSUE_CREATED_EVENT_TYPES = (
    "jira:issue_created",
    "issue_created",
    "task_created",
)


def register(registry, register_classifier=None) -> None:
    """
    Registers the handler for issue-created style events.
    """
    registry.register(ISSUE_CREATED_EVENT_TYPES, handle_issue_created)


def handle_issue_created(data: dict) -> Optional[discord.Embed]:
    """
    Formats a Discord Embed for events that signify a new issue being created.
    """
    try:
        issue = data["issue"]
        fields = issue.get("fields", {})
        issue_key = issue.get("key", "UNKNOWN-ISSUE")
        summary = fields.get("summary", "No summary provided.")
        reporter_info = fields.get("reporter") or {}
        issue_type_info = fields.get("issuetype") or {}
        priority_info = fields.get("priority") or {}

        reporter = _format_user(reporter_info) or "Unknown Reporter"
        issue_type = issue_type_info.get("name", "Unknown")
        priority = priority_info.get("name", "Unspecified")
        status_name = (fields.get("status") or {}).get("name")
        assignee = _format_user(fields.get("assignee") or {})

        embed = discord.Embed(
            title=f"[{issue_key}] New Issue Created",
            description=_format_summary(summary),
            color=_color_from_priority(priority),
        )

        issue_url = build_issue_url(issue)
        if issue_url:
            embed.url = issue_url

        project = fields.get("project") or {}
        project_name = project.get("name", "Unknown Project")
        embed.set_author(name=project_name, url=issue_url or discord.Embed.Empty)

        embed.add_field(name="Type", value=_safe_text(issue_type), inline=True)
        if status_name:
            embed.add_field(name="Status", value=_safe_text(status_name), inline=True)
        embed.add_field(name="Priority", value=_safe_text(priority), inline=True)

        embed.add_field(name="Reporter", value=_safe_text(reporter), inline=True)
        embed.add_field(
            name="Assignee", value=_safe_text(assignee or "Unassigned"), inline=True
        )

        labels = fields.get("labels") or []
        if labels:
            embed.add_field(
                name="Labels",
                value=", ".join(_safe_text(label) for label in labels[:10]),
                inline=False,
            )

        created_timestamp = fields.get("created")
        parsed_timestamp = parse_jira_datetime(created_timestamp)
        if parsed_timestamp:
            embed.timestamp = parsed_timestamp
            embed.set_footer(text=f"Created {format_dt(parsed_timestamp, 'R')}")
        else:
            embed.set_footer(text="Created date unavailable")

        return embed

    except KeyError as exc:
        logger.error("Error parsing Jira 'issue_created' payload: Missing key %s", exc)
        return None


def _format_summary(summary: str) -> str:
    text = (
        escape_markdown(summary.strip())
        if isinstance(summary, str) and summary.strip()
        else "No summary provided."
    )
    return f"> {text}"


def _format_user(user_info: dict) -> Optional[str]:
    if not isinstance(user_info, dict):
        return None
    for key in ("displayName", "nickname", "name", "emailAddress"):
        value = user_info.get(key)
        if value:
            return escape_markdown(str(value))
    return None


def _safe_text(value: Optional[str]) -> str:
    if not value:
        return "—"
    return escape_markdown(str(value))


def _color_from_priority(priority: str) -> discord.Color:
    normalized = (priority or "").lower()
    palette = {
        "highest": discord.Color.from_rgb(220, 38, 38),
        "high": discord.Color.from_rgb(249, 115, 22),
        "medium": discord.Color.from_rgb(234, 179, 8),
        "low": discord.Color.from_rgb(34, 197, 94),
        "lowest": discord.Color.from_rgb(79, 70, 229),
    }
    return palette.get(normalized, discord.Color.blurple())
