# bot.py
import discord
import os
import threading
from flask import Flask, request, abort
import asyncio
import aiohttp

# --- Local Imports ---
from jira_handler import process_jira_event

# --- Discord Bot Setup ---
intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)

# --- Flask Web Server Setup ---
app = Flask(__name__)

# --- Environment Variables ---
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
DISCORD_CHANNEL_ID = os.getenv("DISCORD_CHANNEL_ID")
JIRA_WEBHOOK_SECRET = os.getenv("JIRA_WEBHOOK_SECRET")

# --- Webhook Handling ---

@app.route("/health")
def health_check():
    """A simple health check endpoint to verify the server is running."""
    return "OK", 200

@app.route("/webhooks/jira", methods=["POST"])
def jira_webhook():
    """
    Receives webhook events from Jira, validates them, and passes them to a handler.
    """
    auth_token = request.args.get("secret")
    if not JIRA_WEBHOOK_SECRET or auth_token != JIRA_WEBHOOK_SECRET:
        print(f"Aborting Jira webhook: Invalid secret. Provided: {auth_token}")
        abort(403)

    data = request.get_json()
    
    # Pass the data to the handler for processing into an embed
    embed = process_jira_event(data)

    # If the handler returns a valid embed object, send it to Discord
    if isinstance(embed, discord.Embed):
        send_discord_message(embed=embed)

    return "OK", 200

def send_discord_message(content=None, embed=None):
    """
    Sends a message or an embed to the configured Discord channel from a synchronous context.
    """
    if not bot.loop.is_running():
        print("Bot loop is not running. Cannot send message.")
        return

    try:
        channel_id = int(DISCORD_CHANNEL_ID)
        channel = bot.get_channel(channel_id)
        if channel:
            asyncio.run_coroutine_threadsafe(channel.send(content=content, embed=embed), bot.loop)
        else:
            print(f"Error: Cannot find channel with ID {channel_id}. Make sure the bot is in that channel.")
    except (ValueError, TypeError):
        print(f"Error: DISCORD_CHANNEL_ID '{DISCORD_CHANNEL_ID}' is not a valid integer.")
    except Exception as e:
        print(f"An unexpected error occurred when sending to Discord: {e}")

# --- Bot Commands and Events ---

@bot.event
async def on_ready():
    """Event handler for when the bot has successfully connected to Discord."""
    print(f"Logged in as {bot.user}")
    print(f"Ready to send notifications to channel ID: {DISCORD_CHANNEL_ID}")

@bot.event
async def on_message(message):
    """Event handler for when a message is sent to a channel."""
    if message.author == bot.user:
        return

    if message.content.startswith('!health'):
        port = int(os.environ.get("PORT", 8080))
        url = f"http://localhost:{port}/health"
        
        response_text = ""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        text = await response.text()
                        if text == "OK":
                            response_text = f":white_check_mark: **Web Server Status: Online**\nHealth check endpoint `{url}` is responding correctly."
                        else:
                            response_text = f":warning: **Web Server Status: Unexpected Response**\nEndpoint returned: `{text}`"
                    else:
                        response_text = f":x: **Web Server Status: Error**\nEndpoint returned status code: `{response.status}`"
        except aiohttp.ClientError as e:
            response_text = f":x: **Web Server Status: Unreachable**\nCould not connect to `{url}`. The server might be down.\n`{e}`"
        except Exception as e:
            response_text = f":x: **An unexpected error occurred during health check:**\n`{e}`"
            
        await message.channel.send(response_text)

# --- Service Execution ---

def run_flask():
    """Runs the Flask app in a separate thread."""
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    if not all([DISCORD_BOT_TOKEN, DISCORD_CHANNEL_ID, JIRA_WEBHOOK_SECRET]):
        print("FATAL: One or more required environment variables are missing.")
    else:
        print("Starting services...")
        flask_thread = threading.Thread(target=run_flask, daemon=True)
        flask_thread.start()
        print("Flask server thread started.")

        try:
            bot.run(DISCORD_BOT_TOKEN)
        except discord.errors.LoginFailure:
            print("FATAL: Improper Discord bot token has been passed.")
        except Exception as e:
            print(f"An error occurred while running the bot: {e}")
