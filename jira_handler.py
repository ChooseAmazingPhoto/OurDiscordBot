import logging
from typing import Optional

import discord

from jira_events import classify_issue_update, registry

logger = logging.getLogger(__name__)


def process_jira_event(data: dict) -> Optional[discord.Embed]:
    """
    Routes the Jira webhook payload to the appropriate formatting function
    based on the inferred event type.
    """
    event_type = _determine_event_type(data)
    if not event_type:
        logger.info("Ignoring unhandled Jira event: None")
        return None

    embed = registry.dispatch(event_type, data)
    if embed:
        return embed

    logger.info(
        "Ignoring unhandled Jira event: %s (registered events: %s)",
        event_type,
        ", ".join(registry.known_events()) or "none",
    )
    return None


def _determine_event_type(data):
    """
    Attempts to determine the Jira event type from varying webhook payloads.
    """
    if not isinstance(data, dict):
        return None

    event_keys = (
        "webhookEvent",
        "issue_event_type_name",
        "event_type",
        "eventType",
    )

    for key in event_keys:
        if key in data and data[key]:
            normalized = _normalize_event_type(key, data[key])
            if normalized == "jira:issue_updated":
                specific = classify_issue_update(data)
                return specific or normalized
            return normalized

    if "comment" in data:
        return "comment_created"

    issue = data.get("issue")
    if issue:
        changelog = data.get("changelog") or issue.get("changelog")
        if changelog:
            specific = classify_issue_update(data)
            if specific:
                return specific

            histories = changelog.get("histories") or []
            total = changelog.get("total")
            if histories or (isinstance(total, int) and total > 0):
                return "jira:issue_updated"
        return "jira:issue_created"

    return None


def _normalize_event_type(source_key, value):
    """
    Normalizes different representations of event type values.
    """
    if not isinstance(value, str):
        return None

    event_type = value.strip()
    if not event_type:
        return None

    lowered = event_type.lower()

    if source_key == "issue_event_type_name" and not lowered.startswith("jira:"):
        if lowered.startswith("issue_"):
            return f"jira:{lowered}"

    return lowered
