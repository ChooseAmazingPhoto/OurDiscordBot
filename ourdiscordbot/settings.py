"""Configuration helpers for the bot runtime."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Settings:
    """Container for application configuration values."""

    discord_bot_token: Optional[str]
    discord_channel_id: Optional[int]
    jira_webhook_secret: Optional[str]
    port: int

    @staticmethod
    def _parse_channel_id(raw_value: Optional[str]) -> Optional[int]:
        if not raw_value:
            return None
        try:
            return int(raw_value.strip())
        except (TypeError, ValueError):
            return None

    @classmethod
    def from_env(cls) -> "Settings":
        """Load settings from environment variables."""
        port_value = os.getenv("PORT", "8080")
        try:
            port = int(port_value)
        except (TypeError, ValueError):
            port = 8080

        return cls(
            discord_bot_token=os.getenv("DISCORD_BOT_TOKEN"),
            discord_channel_id=cls._parse_channel_id(os.getenv("DISCORD_CHANNEL_ID")),
            jira_webhook_secret=os.getenv("JIRA_WEBHOOK_SECRET"),
            port=port,
        )

    def requires_secrets(self) -> list[str]:
        """List missing critical configuration keys."""
        missing: list[str] = []
        if not self.discord_bot_token:
            missing.append("DISCORD_BOT_TOKEN")
        if self.discord_channel_id is None:
            missing.append("DISCORD_CHANNEL_ID")
        if not self.jira_webhook_secret:
            missing.append("JIRA_WEBHOOK_SECRET")
        return missing
