import logging
from typing import Optional

import discord

logger = logging.getLogger(__name__)

ISSUE_REOPENED_EVENT_TYPES = (
    "jira:issue_reopened",
    "issue_reopened",
    "issue_reopen",
)


def register(registry, register_classifier=None) -> None:
    registry.register(ISSUE_REOPENED_EVENT_TYPES, handle_issue_reopened)
    if register_classifier:
        register_classifier(classify_issue_reopened)


def classify_issue_reopened(data: dict) -> Optional[str]:
    """
    Attempts to determine if an update payload represents an issue being reopened.
    To be implemented with actual detection logic.
    """
    return None


def handle_issue_reopened(data: dict, event_type=None) -> Optional[discord.Embed]:
    """
    Formats a Discord Embed for issue reopen events.
    Implementation pending.
    """
    logger.debug("Issue reopened handler not implemented yet.")
    return None
