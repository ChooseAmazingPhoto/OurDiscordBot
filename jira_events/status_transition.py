import logging
from typing import Optional

import discord

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
    To be implemented with actual detection logic.
    """
    return None


def handle_status_transition(data: dict, event_type=None) -> Optional[discord.Embed]:
    """
    Formats a Discord Embed for issue status transition events.
    Implementation pending.
    """
    logger.debug("Status transition handler not implemented yet.")
    return None
