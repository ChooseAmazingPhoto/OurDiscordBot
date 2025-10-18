import logging
from typing import Optional

import discord

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
    To be implemented with actual detection logic.
    """
    return None


def handle_assignee_changed(data: dict, event_type=None) -> Optional[discord.Embed]:
    """
    Formats a Discord Embed for issue assignee change events.
    Implementation pending.
    """
    logger.debug("Assignee change handler not implemented yet.")
    return None
