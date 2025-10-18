# OurDiscordBot

OurDiscordBot bridges Jira and Discord. A Flask webhook receiver accepts Jira events, converts them into rich Discord embeds, and delivers them through a long-lived `discord.py` client. The codebase now exposes clear factories for HTTP and Discord services, making it easy to extend with new events or integrations.

## Highlights
- **Modular runtime** - `ourdiscordbot.runtime.build_runtime()` wires up settings, Flask app, and Discord client without side effects. The executable entry point (`python bot.py`) simply calls `run_bot()`.
- **Typed settings** - `ourdiscordbot.settings.Settings` loads environment variables, validates mandatory secrets, and centralises the listening port.
- **Webhook pipeline** - `ourdiscordbot.http_app.create_flask_app()` verifies the shared secret, logs payloads for observability, and defers formatting to `ourdiscordbot.jira_handler.process_jira_event`.
- **Discord notifier** - `ourdiscordbot.discord_client.DiscordNotifier` encapsulates outbound messaging and keeps health-check handlers close to the client.
- **Event architecture** - Jira events register via `jira_events.registry`. Handlers (e.g. `jira_events.assignee_changed`) render embeds, while classifiers break down `"jira:issue_updated"` into specific intents.
- **Status transitions** - `jira_events.status_transition` now formats embeds that show the previous and new status, the actor, and a relative timestamp.
- **Tests** - `pytest` suites exercise webhook behaviour, runtime dispatch, and embed formatting to prevent regressions.

## Getting Started
1. **Create a virtual environment**
   ```powershell
   python -m venv .venv
   .venv\Scripts\activate
   ```

2. **Install dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

3. **Set mandatory environment variables**
   ```powershell
   $env:DISCORD_BOT_TOKEN="your-discord-token"
   $env:DISCORD_CHANNEL_ID="123456789012345678"
   $env:JIRA_WEBHOOK_SECRET="super-secret"
   # optional
   $env:PORT="8080"
   ```

4. **Run locally**
   ```powershell
   python bot.py
   ```
   The bot starts the Flask webhook server in a background thread and then connects to Discord. Use `http://localhost:8080/health` to verify the HTTP side.

5. **Execute tests**
   ```powershell
   python -m pytest
   ```

## Deploying
1. Push the repository to your hosting provider (Railway, Fly.io, etc.).
2. Configure the same environment variables in your hosting dashboard.
3. Expose HTTPS traffic to `/webhooks/jira`.
4. Point Jira Automation to `https://<public-host>/webhooks/jira?secret=<JIRA_WEBHOOK_SECRET>`.

## Extending Jira Events
1. Create a new module under `jira_events/` and implement `register()`, `handle_*`, and optional classifiers.
2. Import the module in `jira_events/__init__.py` and call its `register()` function.
3. Add test cases under `tests/` that cover both classification and embed rendering.
4. Update documentation where appropriate (see `docs/JiraEventHandlingArchitecture.md` for the reference architecture).

## Troubleshooting
- 403 responses usually mean the `secret` query parameter does not match `JIRA_WEBHOOK_SECRET`.
- If Discord receives no message, confirm the bot has cached the target channel and that `DISCORD_CHANNEL_ID` is a valid integer.
- Run `python -m pytest` before committing to ensure parser and classifier changes remain compatible.

## License
This project remains under the [MIT License](LICENSE).
