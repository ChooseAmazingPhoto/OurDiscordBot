import discord
from datetime import datetime

def process_jira_event(data):
    """
    Routes the Jira webhook payload to the appropriate formatting function
    based on the event type.
    """
    event_type = data.get('webhookEvent')

    if event_type == 'jira:issue_created':
        return format_issue_created_embed(data)
    # --- Future event handlers will go here ---
    # elif event_type == 'jira:issue_updated':
    #     return format_issue_updated_embed(data)
    # elif event_type == 'comment_created':
    #     return format_comment_created_embed(data)
    
    # Return None if the event is not one we handle
    print(f"Ignoring unhandled Jira event: {event_type}")
    return None

def format_issue_created_embed(data):
    """
    Formats a Discord Embed for a 'jira:issue_created' event.
    """
    try:
        issue = data['issue']
        issue_key = issue['key']
        summary = issue['fields']['summary']
        reporter = issue['fields']['reporter']['displayName']
        issue_type = issue['fields']['issuetype']['name']
        priority = issue['fields']['priority']['name']
        
        # Construct the user-friendly issue URL from the API 'self' link
        base_url = issue['self'].split('/rest/api')[0]
        issue_url = f"{base_url}/browse/{issue_key}"

        embed = discord.Embed(
            title=f"[{issue_key}] New Issue Created",
            description=summary,
            url=issue_url,
            color=discord.Color.green()  # Green for new items
        )
        
        embed.add_field(name="Type", value=issue_type, inline=True)
        embed.add_field(name="Priority", value=priority, inline=True)
        embed.add_field(name="Reporter", value=reporter, inline=False)
        
        # Try to parse the timestamp and add it
        try:
            created_timestamp = issue['fields']['created']
            # Timestamps from Jira are in ISO 8601 format, e.g., '2023-10-27T05:26:31.230+0000'
            # discord.py's fromisoformat doesn't handle the timezone offset well, so we split it.
            embed.timestamp = datetime.fromisoformat(created_timestamp.split('.')[0])
        except Exception as e:
            print(f"Could not parse timestamp: {e}")


        # Set a footer with the project name
        project_name = issue['fields']['project']['name']
        embed.set_footer(text=f"Project: {project_name}")

        return embed

    except KeyError as e:
        print(f"Error parsing Jira 'issue_created' payload: Missing key {e}")
        return None
