# OurDiscordBot

A minimal Discord bot starter that demonstrates both a classic prefix command and a modern slash command. The project uses `discord.py`, loads secrets from environment variables, and is ready for deployment on platforms such as Railway.

## Features
- `!ping` prefix command that replies with `pong!`
- `/hello` slash command that greets the invoking user
- Automatic slash command tree sync on startup
- Loads `DISCORD_TOKEN` from environment variables (via `.env` locally)
- Opt-in message content intent enabled for compatibility with prefix commands

## Requirements
- Python 3.10+
- `discord.py`, `python-dotenv`, `requests` (installed from `requirements.txt`)
- A Discord bot application with the **Message Content Intent** enabled

## Local Setup
1. Create a virtual environment:
   ```powershell
   python -m venv .venv
   .venv\Scripts\activate
   ```
2. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
3. Create a `.env` file (not committed to git) and add your bot token:
   ```env
   DISCORD_TOKEN=your-bot-token-here
   ```
4. Run the bot:
   ```powershell
   python bot.py
   ```
5. Invite the bot to a server using the OAuth2 URL from the Discord Developer Portal (include the `applications.commands` scope to use slash commands).

## Slash Commands
- On the first startup the bot syncs the slash command definition with Discord. This can take up to a minute before the command appears in your server.
- Slash command code lives in `bot.py` under `@bot.tree.command`. Add additional commands there and call `await bot.tree.sync()` after modifying them.

## Deployment (Railway example)
1. Push the repository to GitHub (omit `.env`, already ignored).
2. Create a new Railway project and connect the repository.
3. Set the environment variable `DISCORD_TOKEN` in the Railway dashboard.
4. Deploy; Railway boots the container and the bot logs in using the provided token.

## Troubleshooting
- **Missing DISCORD_TOKEN environment variable**: ensure the variable is set in `.env` locally or in your hosting provider's environment settings.
- **Message content warning**: verify Message Content Intent is enabled in the Discord Developer Portal for the bot.

## License
This project is released under the [MIT License](LICENSE).
