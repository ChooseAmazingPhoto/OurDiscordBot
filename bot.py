import os
import sys

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

MISSING_TOKEN_MESSAGE = (
    "Missing DISCORD_TOKEN environment variable. "
    "Set it in your deployment settings or .env file."
)


def get_token() -> str:
    token = os.getenv("DISCORD_TOKEN")
    if token is None:
        raise RuntimeError(MISSING_TOKEN_MESSAGE)
    return token


intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    if not getattr(bot, "synced", False):
        await bot.tree.sync()
        bot.synced = True
    print(f"Bot is online: {bot.user}")


@bot.command()
async def ping(ctx):
    await ctx.send("pong!")


@bot.tree.command(name="hello", description="Say hello with a slash command")
async def hello(interaction: discord.Interaction):
    greeting = f"Hello, {interaction.user.mention}!"
    await interaction.response.send_message(greeting)


def main() -> None:
    try:
        token = get_token()
    except RuntimeError as exc:
        sys.stderr.write(f"{exc}\n")
        sys.exit(1)

    bot.run(token)


if __name__ == "__main__":
    main()
