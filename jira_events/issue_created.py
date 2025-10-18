import logging
from typing import Optional

import discord

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

        reporter = (
            reporter_info.get("displayName")
            or reporter_info.get("name")
            or reporter_info.get("emailAddress")
            or "Unknown Reporter"
        )
        issue_type = issue_type_info.get("name", "Unknown")
        priority = priority_info.get("name", "Unspecified")

        embed = discord.Embed(
            title=f"[{issue_key}] New Issue Created",
            description=summary,
            color=discord.Color.green(),
        )

        issue_url = build_issue_url(issue)
        if issue_url:
            embed.url = issue_url

        embed.add_field(name="Type", value=issue_type, inline=True)
        embed.add_field(name="Priority", value=priority, inline=True)
        embed.add_field(name="Reporter", value=reporter, inline=False)

        created_timestamp = fields.get("created")
        parsed_timestamp = parse_jira_datetime(created_timestamp)
        if parsed_timestamp:
            embed.timestamp = parsed_timestamp

        project = fields.get("project") or {}
        project_name = project.get("name", "Unknown Project")
        embed.set_footer(text=f"Project: {project_name}")

        return embed

    except KeyError as exc:
        logger.error("Error parsing Jira 'issue_created' payload: Missing key %s", exc)
        return None
