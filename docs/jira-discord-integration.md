# Jira to Discord Integration Guide

This guide explains how to connect Jira Automation to the OurDiscordBot webhook and validate the end-to-end flow.

## Prerequisites

- OurDiscordBot deployed and reachable over HTTPS.
- Environment variables configured on the target host:
  - `DISCORD_BOT_TOKEN`
  - `DISCORD_CHANNEL_ID`
  - `JIRA_WEBHOOK_SECRET`
- Jira project admin rights to create Automation rules.

## 1. Obtain the Webhook URL

1. Deploy the repository (Railway, Fly.io, etc.).
2. Record the public hostname, for example `https://our-discord-bot.up.railway.app`.
3. Construct the webhook URL:
   ```
   https://our-discord-bot.up.railway.app/webhooks/jira?secret=<JIRA_WEBHOOK_SECRET>
   ```
   Replace `<JIRA_WEBHOOK_SECRET>` with the exact value configured in your deployment.

## 2. Create a Jira Automation Rule

1. Navigate to **Project settings → Automation**.
2. Click **Create rule** and choose a trigger:
   - Issue created (supported by the bot)
   - Issue transitioned (status updates are supported)
   - Field value changed (useful for assignee or due date changes)
3. Add an action **Send web request**.
4. Configure the request:
   - **Webhook URL**: the URL from step 1.
   - **Method**: `POST`
   - **Headers**: `Content-Type: application/json`
   - **Body**: select *Custom data* and paste JSON tailored to the event. Example for “Issue created”:
     ```json
     {
       "webhookEvent": "jira:issue_created",
       "webhookEventCreated": "{{now}}",
       "user": {
         "displayName": "{{initiator.displayName}}"
       },
       "issue": {
         "self": "{{issue.url}}",
         "id": "{{issue.id}}",
         "key": "{{issue.key}}",
         "fields": {
           "summary": "{{issue.summary}}",
           "issuetype": { "name": "{{issue.issueType.name}}" },
           "priority": { "name": "{{issue.priority.name}}" },
           "status": { "name": "{{issue.status.name}}" },
           "reporter": { "displayName": "{{issue.reporter.displayName}}" },
           "assignee": { "displayName": "{{issue.assignee.displayName}}" },
           "project": { "name": "{{issue.project.name}}" },
           "labels": "{{issue.labels.join(\", \")}}",
           "created": "{{issue.created}}"
         }
       }
     }
     ```
5. Save and enable the rule.

## 3. Verify Locally Before Deploying

1. Run the bot locally (`python bot.py`). Ensure `PORT` matches the value Jira will hit (defaults to `8080`).
2. Use the HTML tester (`docs/jira_webhook_tester.html`) or a simple `curl` command:
   ```bash
   curl -X POST "http://localhost:8080/webhooks/jira?secret=secret" \
        -H "Content-Type: application/json" \
        -d @payload.json
   ```
3. Check the terminal output for log lines indicating payload reception and Discord delivery attempts.

## 4. Debugging Checklist

| Symptom | Suggested Checks |
| --- | --- |
| `403 Forbidden` | The `secret` query parameter does not match `JIRA_WEBHOOK_SECRET`. |
| `400 Bad Request` | Jira sent malformed JSON or an empty body. Enable the Automation “Send web request” sample data option to compare payloads. |
| No Discord message | Verify the bot is online, has access to the guild/channel, and that `DISCORD_CHANNEL_ID` is a valid text channel ID. |
| Wrong fields | Compare your Automation payload with the templates in `jira_smart_templates/` and confirm the handler supports that event. |

## 5. Updating the Integration

- Extend Automation rules to trigger on additional events (e.g. due date changes) as new handlers are implemented.
- Keep payloads minimal but include the fields that handlers expect (summary, project, assignee, priority, changelog items, etc.).
- Run `python -m pytest` before deploying to ensure the registry and classifier logic remains stable.

## 6. Useful Resources

- [Jira Smart Templates](../jira_smart_templates) – Example payloads and desired Discord embed structures.
- [Runtime Architecture](JiraEventHandlingArchitecture.md) – Detailed explanation of how the bot processes events.
- [Jira Webhook Tester](JiraWebhookTester.md) – Instructions for the HTML tool that simulates Automation payloads.
