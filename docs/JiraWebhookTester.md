# Jira Webhook Tester Guide

The HTML tester (`docs/jira_webhook_tester.html`) simulates Jira Automation requests so you can validate the webhook locally or against a deployed instance.

## Usage
1. Open the HTML file in a modern browser (no build step required).
2. Enter your application base URL (e.g. `https://your-app.up.railway.app`). The tester appends `/webhooks/jira` automatically.
3. Provide the webhook secret if your deployment requires it (recommended). This becomes the `secret` query parameter.
4. Choose a canned event type and populate quick fields such as issue key and summary. Click **Rebuild Payload** to regenerate the JSON body.
5. Inspect or edit the generated JSON. You can paste in real payloads from Jira if desired.
6. Click **Send to Railway** (or your target base URL). The tool issues a `POST` request and prints the HTTP status code and body in the lower console.

## Troubleshooting
- `403 Forbidden` - Verify that the provided secret matches the `JIRA_WEBHOOK_SECRET` configured on the server.
- `400 Bad Request` - The payload is not valid JSON. Use a JSON formatter or copy a known working template from `jira_smart_templates/`.
- No Discord notification - Confirm the bot is running, connected to the correct guild, and that `DISCORD_CHANNEL_ID` references a text channel the bot can access.
- Browser network errors - The tester runs client-side. If CORS is disabled on the target environment, run the tester locally via `python -m http.server` and proxy traffic through a tool like `ngrok`.

## Tips
- Keep a library of sample payloads for different Jira events. You can build them from the templates in `jira_smart_templates/`.
- When testing locally, start the bot (`python bot.py`) and watch the terminal logs for immediate feedback.
- Use the developer tools Network tab to inspect request and response headers if the tester output is insufficient.
