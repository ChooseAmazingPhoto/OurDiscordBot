# Discord Bot Feature Specification v1

This specification describes the high-level goals and current feature set of OurDiscordBot.

## Vision
Deliver actionable project context directly in Discord so that product, engineering, and operations teams can react without leaving the chat client.

## Core Pillars
1. **Notification Hub** - Broadcast relevant Jira events (issue creation, assignee changes, status transitions, upcoming due dates, comments).
2. **Fast Context** - Embed summaries with priority, status, reporter, assignee, and labels. Provide direct links back to Jira for follow-up.
3. **Operational Awareness** - Offer ad-hoc status checks through lightweight commands (currently `!health`, extendable to future queries).
4. **Extensibility** - New events drop in through the registry+classifier pattern; no modification of core routing is required.

## Functional Scope
| Area | Capabilities (v1) | Notes / Next Steps |
| --- | --- | --- |
| Jira Notifications | Issue created (implemented); assignee change (implemented); status transition (implemented); due date, labels, comments (stubs ready for implementation). | Prioritise finishing stub handlers and adding regression tests. |
| Discord Commands | `!health` checks the webhook availability. | Evaluate need for slash commands once webhook coverage stabilises. |
| Delivery | Single channel broadcast defined by `DISCORD_CHANNEL_ID`. | Future iteration: routing by project or priority. |
| Templates | JSON samples stored under `jira_smart_templates/` for use with Jira Automation. | Assess runtime template rendering if non-engineering teammates will maintain messages. |

## Non-Goals (v1)
- Multi-workspace sharding across numerous Discord guilds.
- Persistent storage or analytics beyond Discord message history.
- Automatic slash command sync (classic client only).

## Quality Requirements
- Webhook authentication via shared secret.
- Unit tests covering HTTP routes and event handlers.
- Graceful handling of missing or malformed payload data (log and skip rather than crash).

## Roadmap Ideas
1. Finalise handlers for due-date updates, comments, and labels.
2. Introduce structured logging / Sentry for error visibility in production.
3. Add slash commands for querying assignee workload or outstanding blockers.
4. Support pluggable notification sinks (e.g., other Discord channels or email digests).
