"""Flask application factory."""

from __future__ import annotations

import logging
from typing import Callable, Optional

import discord
from flask import Flask, abort, request

from .discord_client import DiscordNotifier

logger = logging.getLogger(__name__)

EmbedFactory = Callable[[dict], Optional[discord.Embed]]


def create_flask_app(
    *,
    jira_secret: Optional[str],
    process_event: EmbedFactory,
    notifier: DiscordNotifier,
) -> Flask:
    """Create and configure the Flask app used for webhook ingestion."""
    app = Flask(__name__)

    @app.route("/health")
    def health_check():
        return "OK", 200

    @app.route("/webhooks/jira", methods=["POST"])
    def jira_webhook():
        auth_token = request.args.get("secret")
        if not jira_secret or auth_token != jira_secret:
            logger.warning(
                "Invalid secret provided for Jira webhook. Provided: %s", auth_token
            )
            abort(403)

        raw_data = request.get_data(as_text=True)
        logger.info("Received Jira webhook payload: %s", raw_data)

        try:
            data = request.get_json()
        except Exception as exc:
            logger.error("Failed to parse JSON from Jira webhook: %s", exc)
            abort(400, description="Could not parse JSON payload.")

        if data and "issue" in data:
            issue_key = data.get("issue", {}).get("key")
            logger.info("Processing Jira event for issue: %s", issue_key)
        else:
            logger.warning("Jira webhook payload did not contain issue data.")

        embed = process_event(data)
        if isinstance(embed, discord.Embed):
            notifier.send(embed=embed)
            logger.info("Successfully sent Jira notification to Discord.")

        return "OK", 200

    return app
