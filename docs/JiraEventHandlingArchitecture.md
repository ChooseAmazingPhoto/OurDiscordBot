# Jira Event Handling Architecture

This document explains how Jira webhook payloads move through the codebase and reach Discord.

## Runtime Overview

```
Settings.from_env()
      │
      ▼
create_bot() ──> Discord Client ──> DiscordNotifier.send()
      │                               ▲
      │                               │
      └────── create_flask_app() ─────┘
                      │
                      ▼
              /webhooks/jira (Flask)
                      │
                      ▼
        ourdiscordbot.jira_handler.process_jira_event()
                      │
                      ▼
           jira_events.registry.dispatch()
                      │
                      ▼
     Event handler (e.g. assignee_changed.handle_assignee_changed)
                      │
                      ▼
                discord.Embed message
```

### Key Modules

| Module | Responsibility |
| --- | --- |
| `ourdiscordbot/settings.py` | Loads `DISCORD_BOT_TOKEN`, `DISCORD_CHANNEL_ID`, `JIRA_WEBHOOK_SECRET`, and optional `PORT`. |
| `ourdiscordbot/discord_client.py` | Creates the `discord.Client`, registers `!health`, and exposes `DiscordNotifier.send()`. |
| `ourdiscordbot/http_app.py` | Builds the Flask app, validates the shared secret, logs payloads, and forwards data to the Jira handler. |
| `ourdiscordbot/runtime.py` | Wires settings, client, notifier, and app. `run_bot()` launches Flask in a background thread and then blocks on `discord.Client.run()`. |
| `ourdiscordbot/jira_handler.py` | Infers the event type, routes `"jira:issue_updated"` payloads through classifiers, and dispatches registered handlers. |
| `jira_events/*` | Per-event handlers and classifiers that transform payloads into Discord embeds. |
| `tests/*` | Pytest suites covering HTTP endpoints, event dispatch, and embed formatting. |

## Webhook Flow

1. **Request arrives** at `POST /webhooks/jira?secret=...`. The Flask route immediately rejects calls with missing or mismatched secrets.
2. **Payload is parsed** and logged. Invalid JSON triggers a `400` response.
3. **Event type resolution** happens inside `ourdiscordbot.jira_handler.process_jira_event()`. The helper `_determine_event_type()` inspects `webhookEvent`, `issue_event_type_name`, etc. For `"jira:issue_updated"` the registry runs each classifier until a specific event (e.g. assignee change, status transition) is identified.
4. **Dispatch** uses `jira_events.registry.JiraEventRegistry`, which understands handler signatures and supplies the inferred `event_type` when required.
5. **Handler execution** builds a `discord.Embed`. Handlers add summary fields, timestamps, and colours that make the update actionable. Returning `None` means “ignore this event”.
6. **Delivery** happens through `DiscordNotifier.send()`, which schedules `channel.send(...)` on the Discord client's event loop.

## Adding a New Jira Event

1. Create a module under `jira_events/` (for example `due_date_changed.py`).
2. Implement a `register(registry, register_classifier=None)` function that adds the handler (and optional classifier) to the registry.
3. Write the handler so it returns either a populated `discord.Embed` or `None`.
4. Optionally register a classifier that inspects `data["changelog"]` to narrow `"jira:issue_updated"` payloads.
5. Import the module in `jira_events/__init__.py` and call `register(...)`.
6. Add regression tests under `tests/` that cover both dispatch and embed output.

## Formatting Guidance

- Escape user-provided strings with `discord.utils.escape_markdown`.
- Reuse helpers in `jira_events/common.py` for timestamps and URLs.
- Focus embed fields on actionable data (status, assignee, priority, reporter, labels).
- Set `embed.timestamp` and pair it with `format_dt(..., "R")` in the footer for relative timing.
- Provide fallbacks such as `"Unassigned"` or `"Unknown"` when Jira omits fields.

## Testing Strategy

- `tests/test_bot.py` exercises the Flask webhook, shared-secret enforcement, and JSON parsing while mocking outbound Discord traffic.
- `tests/test_jira_handler.py` verifies registry dispatch as well as embed formatting for issue creation, assignee changes, and status transitions.
- When introducing new handlers, add tests for both the happy path and edge cases (missing changelog data, unexpected field shapes).

## Jira Smart Templates

The `jira_smart_templates/` directory contains reference JSON bodies for Jira Automation. While handlers currently render embeds directly in Python, the templates remain useful when configuring Automation rules or planning template-driven rendering in future iterations.
