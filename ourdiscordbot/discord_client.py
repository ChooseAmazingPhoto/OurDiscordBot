"""Discord client factories and helpers."""

from __future__ import annotations

import asyncio
import logging
from typing import Optional

import aiohttp
import discord

from .settings import Settings

logger = logging.getLogger(__name__)


class DiscordNotifier:
    """Thin wrapper that schedules messages on the Discord client's loop."""

    def __init__(self, client: discord.Client, channel_id: Optional[int]) -> None:
        self._client = client
        self._channel_id = channel_id

    @property
    def channel_id(self) -> Optional[int]:
        return self._channel_id

    def send(
        self, *, content: Optional[str] = None, embed: Optional[discord.Embed] = None
    ) -> bool:
        if self._channel_id is None:
            logger.error("Cannot send Discord message; channel id not configured.")
            return False

        loop = getattr(self._client, "loop", None)
        if loop is None or not loop.is_running():
            logger.warning("Discord client loop not running; skipping message.")
            return False

        channel = self._client.get_channel(self._channel_id)
        if not channel:
            logger.error(
                "Discord channel %s not cached; unable to send message.",
                self._channel_id,
            )
            return False

        try:
            asyncio.run_coroutine_threadsafe(
                channel.send(content=content, embed=embed),
                loop,
            )
            return True
        except Exception as exc:  # pragma: no cover - safety net
            logger.exception("Failed to dispatch message to Discord: %s", exc)
            return False


def create_bot(settings: Settings) -> tuple[discord.Client, DiscordNotifier]:
    """Instantiate the Discord client with event handlers."""
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)
    notifier = DiscordNotifier(client, settings.discord_channel_id)

    @client.event
    async def on_ready():  # type: ignore[no-redef]
        logger.info("Logged in as %s", client.user)
        if notifier.channel_id:
            logger.info(
                "Ready to send notifications to channel ID: %s", notifier.channel_id
            )
        else:
            logger.warning(
                "Discord channel ID missing; outbound notifications disabled."
            )

    @client.event
    async def on_message(message: discord.Message):  # type: ignore[no-redef]
        if message.author == client.user:
            return

        if message.content.startswith("!health"):
            await _respond_with_health(message, settings.port)

    return client, notifier


async def _respond_with_health(message: discord.Message, port: int) -> None:
    """Execute the local health check and respond in Discord."""
    url = f"http://localhost:{port}/health"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                body = await response.text()
                if response.status == 200 and body == "OK":
                    text = (
                        ":white_check_mark: **Web Server Status: Online**\n"
                        f"Health check endpoint `{url}` is responding correctly."
                    )
                elif response.status == 200:
                    text = (
                        ":warning: **Web Server Status: Unexpected Response**\n"
                        f"Endpoint returned: `{body}`"
                    )
                else:
                    text = (
                        ":x: **Web Server Status: Error**\n"
                        f"Endpoint returned status code: `{response.status}`"
                    )
    except aiohttp.ClientError as exc:
        text = (
            ":x: **Web Server Status: Unreachable**\n"
            f"Could not connect to `{url}`. The server might be down.\n`{exc}`"
        )
    except Exception as exc:  # pragma: no cover - unexpected path
        text = ":x: **An unexpected error occurred during health check:**\n" f"`{exc}`"

    await message.channel.send(text)
