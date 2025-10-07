import asyncio
import logging
import os
import sys
from hmac import compare_digest
from typing import Any, Dict, Mapping, Tuple

import discord
from aiohttp import web
from discord.abc import Messageable
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

MISSING_TOKEN_MESSAGE = (
    "Missing DISCORD_TOKEN environment variable. "
    "Set it in your deployment settings or .env file."
)
MISSING_CHANNEL_MESSAGE = (
    "Missing DISCORD_JIRA_CHANNEL_ID environment variable. "
    "Configure the target Discord channel id for Jira notifications."
)
MISSING_WEBHOOK_SECRET_MESSAGE = (
    "Missing JIRA_WEBHOOK_TOKEN environment variable. "
    "Set a shared secret for authenticating Jira Automation requests."
)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


def get_token() -> str:
    token = os.getenv("DISCORD_TOKEN")
    if token is None:
        raise RuntimeError(MISSING_TOKEN_MESSAGE)
    return token


def get_channel_id() -> int:
    channel_id_str = os.getenv("DISCORD_JIRA_CHANNEL_ID")
    if channel_id_str is None:
        raise RuntimeError(MISSING_CHANNEL_MESSAGE)
    try:
        return int(channel_id_str)
    except ValueError as exc:  # pragma: no cover - user misconfiguration
        raise RuntimeError(
            "DISCORD_JIRA_CHANNEL_ID must be an integer channel id"
        ) from exc


def get_webhook_secret() -> str:
    secret = os.getenv("JIRA_WEBHOOK_TOKEN")
    if secret is None:
        raise RuntimeError(MISSING_WEBHOOK_SECRET_MESSAGE)
    return secret


def get_server_bind() -> Tuple[str, int]:
    host = os.getenv("JIRA_WEB_SERVER_HOST", "0.0.0.0")
    port_raw = os.getenv("JIRA_WEB_SERVER_PORT", "8080")
    try:
        port = int(port_raw)
    except ValueError as exc:  # pragma: no cover - user misconfiguration
        raise RuntimeError("JIRA_WEB_SERVER_PORT must be an integer") from exc
    return host, port


def authorize_request(headers: Mapping[str, str], secret: str) -> bool:
    auth_header = headers.get("Authorization")
    if not auth_header or not secret:
        return False
    scheme, _, token = auth_header.partition(" ")
    if scheme.lower() != "bearer" or not token:
        return False
    return compare_digest(token.strip(), secret)


def _coerce_field(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def sanitize_payload(payload: Dict[str, Any]) -> Dict[str, str]:
    if not isinstance(payload, Mapping):
        raise ValueError("Payload must be a JSON object")

    issue_key = _coerce_field(payload.get("issueKey"))
    if not issue_key:
        raise ValueError("Payload missing issueKey")

    summary = _coerce_field(payload.get("summary"))
    status = _coerce_field(payload.get("status"))
    event = _coerce_field(payload.get("event"))
    link = _coerce_field(payload.get("link"))
    triggered_by = _coerce_field(payload.get("triggeredBy"))
    timestamp = _coerce_field(payload.get("timestamp"))

    return {
        "issueKey": issue_key,
        "summary": summary,
        "status": status,
        "event": event,
        "link": link,
        "triggeredBy": triggered_by,
        "timestamp": timestamp,
    }


def format_notification(payload: Dict[str, str]) -> str:
    title = f"**{payload['issueKey']}** {payload['summary']}".rstrip()

    details = []
    if payload["status"]:
        details.append(f"狀態：{payload['status']}")
    if payload["event"]:
        details.append(f"事件：{payload['event']}")
    if payload["triggeredBy"]:
        details.append(f"觸發者：{payload['triggeredBy']}")
    if payload["timestamp"]:
        details.append(f"時間：{payload['timestamp']}")

    lines = [title]
    if details:
        lines.append(" / ".join(details))
    if payload["link"]:
        lines.append(payload["link"])

    message = "\n".join(lines)
    if len(message) > 2000:
        message = f"{message[:1997]}..."
    return message


async def dispatch_jira_notification(
    bot_client: commands.Bot, channel_id: int, payload: Dict[str, Any]
) -> None:
    sanitized = sanitize_payload(payload)
    message = format_notification(sanitized)

    await bot_client.wait_until_ready()
    channel = bot_client.get_channel(channel_id)
    if channel is None:
        channel = await bot_client.fetch_channel(channel_id)

    if not isinstance(channel, Messageable):  # pragma: no cover - defensive
        raise RuntimeError(
            "Configured channel does not support sending messages"
        )

    try:
        await channel.send(message)
    except discord.HTTPException as exc:
        raise RuntimeError("Failed to send message to Discord") from exc


async def handle_jira_notification(request: web.Request) -> web.Response:
    secret = request.app["jira_secret"]
    channel_id = request.app["channel_id"]

    if not authorize_request(request.headers, secret):
        return web.json_response({"error": "Unauthorized"}, status=401)

    try:
        payload = await request.json()
    except Exception:  # pragma: no cover - aiohttp already normalizes
        return web.json_response({"error": "Invalid JSON payload"}, status=400)

    try:
        await dispatch_jira_notification(bot, channel_id, payload)
    except ValueError as exc:
        logger.warning("Invalid Jira payload: %s", exc)
        return web.json_response({"error": str(exc)}, status=400)
    except RuntimeError as exc:
        logger.exception("Failed to deliver Jira notification")
        return web.json_response({"error": str(exc)}, status=500)

    return web.json_response({"status": "ok"})


def create_app(secret: str, channel_id: int) -> web.Application:
    app = web.Application()
    app["jira_secret"] = secret
    app["channel_id"] = channel_id
    app.router.add_post("/jira/notify", handle_jira_notification)
    return app


async def start_http_server(app: web.Application, host: str, port: int) -> web.AppRunner:
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host=host, port=port)
    await site.start()
    logger.info("HTTP server listening on %s:%s", host, port)
    return runner


async def run_bot() -> None:
    token = get_token()
    channel_id = get_channel_id()
    secret = get_webhook_secret()
    host, port = get_server_bind()

    app = create_app(secret, channel_id)
    runner = await start_http_server(app, host, port)

    try:
        await bot.start(token)
    except asyncio.CancelledError:  # pragma: no cover - shutdown path
        raise
    finally:
        await bot.close()
        await runner.cleanup()


@bot.event
async def on_ready():
    if not getattr(bot, "synced", False):
        await bot.tree.sync()
        bot.synced = True
    logger.info("Bot is online: %s", bot.user)


@bot.command()
async def ping(ctx: commands.Context) -> None:
    await ctx.send("pong!")


@bot.tree.command(name="hello", description="Say hello with a slash command")
async def hello(interaction: discord.Interaction) -> None:
    greeting = f"Hello, {interaction.user.mention}!"
    await interaction.response.send_message(greeting)


def main() -> None:
    try:
        asyncio.run(run_bot())
    except RuntimeError as exc:
        sys.stderr.write(f"{exc}\n")
        sys.exit(1)
    except KeyboardInterrupt:  # pragma: no cover - manual interrupt
        logger.info("Shutdown requested by user")


if __name__ == "__main__":
    main()
