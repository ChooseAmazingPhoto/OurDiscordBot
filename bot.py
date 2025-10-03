import os
import sys

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

if TOKEN is None:
    sys.stderr.write("Missing DISCORD_TOKEN environment variable. Set it in your deployment settings or .env file.\n")
    sys.exit(1)

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
    await interaction.response.send_message(f"Hello, {interaction.user.mention}!")

bot.run(TOKEN)
