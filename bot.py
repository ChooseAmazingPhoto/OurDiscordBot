"""Application entry-point for the Discord + Jira integration."""

from __future__ import annotations

from ourdiscordbot import run_bot
from ourdiscordbot.runtime import build_runtime

_settings, discord_client, notifier, app = build_runtime()
bot = discord_client


def send_discord_message(*, content=None, embed=None):
    """Forward messages to Discord through the shared notifier."""
    return notifier.send(content=content, embed=embed)


if __name__ == "__main__":
    run_bot()
