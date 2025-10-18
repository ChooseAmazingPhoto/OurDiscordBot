import logging
from typing import Optional

import discord

logger = logging.getLogger(__name__)

COMMENT_CREATED_EVENT_TYPES = (
    "comment_created",
    "jira:issue_comment_added",
    "jira:issue_comment_created",
)


def register(registry, register_classifier=None) -> None:
    registry.register(COMMENT_CREATED_EVENT_TYPES, handle_comment_created)


def handle_comment_created(data: dict, event_type=None) -> Optional[discord.Embed]:
    """
    Formats a Discord Embed for comment creation events.
    Implementation pending.
    """
    logger.debug("Comment creation handler not implemented yet.")
    return None
