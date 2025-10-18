"""Application bootstrap utilities."""

from __future__ import annotations

import logging
import threading
from typing import Optional, Tuple

import discord

from .discord_client import DiscordNotifier, create_bot
from .http_app import create_flask_app
from .jira_handler import process_jira_event
from .settings import Settings

logger = logging.getLogger(__name__)


def build_runtime(
    settings: Optional[Settings] = None,
) -> Tuple[Settings, discord.Client, DiscordNotifier, "Flask"]:
    """Create settings, Discord client, notifier, and Flask app."""
    from flask import Flask  # Imported lazily to avoid eager dependency at import time

    resolved_settings = settings or Settings.from_env()
    client, notifier = create_bot(resolved_settings)
    app = create_flask_app(
        jira_secret=resolved_settings.jira_webhook_secret,
        process_event=process_jira_event,
        notifier=notifier,
    )
    return resolved_settings, client, notifier, app


def run_bot() -> None:
    """Launch the Flask webhook receiver and Discord client."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    settings, client, notifier, app = build_runtime()
    missing = settings.requires_secrets()
    if missing:
        print(f"FATAL: Missing required environment variables: {', '.join(missing)}")
        return

    if settings.discord_bot_token is None:
        print("FATAL: Discord bot token missing.")
        return

    def run_flask():
        logger.info("Starting Flask server on port %s", settings.port)
        app.run(host="0.0.0.0", port=settings.port)

    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    logger.info("Flask server thread started.")

    try:
        client.run(settings.discord_bot_token)
    except discord.errors.LoginFailure:
        print("FATAL: Improper Discord bot token has been passed.")
    except Exception as exc:  # pragma: no cover - safety net
        print(f"An error occurred while running the bot: {exc}")
