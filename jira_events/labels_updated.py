import logging
from typing import Optional

import discord

logger = logging.getLogger(__name__)

LABELS_UPDATED_EVENT_TYPES = (
    "jira:issue_labels_changed",
    "issue_labels_changed",
    "labels_changed",
)


def register(registry, register_classifier=None) -> None:
    registry.register(LABELS_UPDATED_EVENT_TYPES, handle_labels_updated)
    if register_classifier:
        register_classifier(classify_labels_updated)


def classify_labels_updated(data: dict) -> Optional[str]:
    """
    Attempts to determine if an update payload represents label changes.
    To be implemented with actual detection logic.
    """
    return None


def handle_labels_updated(data: dict, event_type=None) -> Optional[discord.Embed]:
    """
    Formats a Discord Embed for issue label change events.
    Implementation pending.
    """
    logger.debug("Labels update handler not implemented yet.")
    return None
