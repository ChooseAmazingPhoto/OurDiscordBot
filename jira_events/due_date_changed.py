import logging
from typing import Optional

import discord

logger = logging.getLogger(__name__)

DUE_DATE_CHANGED_EVENT_TYPES = (
    "jira:issue_due_date_changed",
    "issue_due_date_changed",
    "due_date_changed",
)


def register(registry, register_classifier=None) -> None:
    registry.register(DUE_DATE_CHANGED_EVENT_TYPES, handle_due_date_changed)
    if register_classifier:
        register_classifier(classify_due_date_changed)


def classify_due_date_changed(data: dict) -> Optional[str]:
    """
    Attempts to determine if an update payload represents a due date change.
    To be implemented with actual detection logic.
    """
    return None


def handle_due_date_changed(data: dict, event_type=None) -> Optional[discord.Embed]:
    """
    Formats a Discord Embed for issue due date change events.
    Implementation pending.
    """
    logger.debug("Due date change handler not implemented yet.")
    return None
