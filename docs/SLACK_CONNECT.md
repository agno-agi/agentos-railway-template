# Connecting to Slack

Your AgentOS can live in Slack as a teammate. Each Slack thread becomes a session with its own conversation context, so follow-ups in the same thread carry forward automatically.

## Prerequisites

- AgentOS running locally or deployed (see the [README](../README.md))
- A Slack workspace with admin privileges
- [ngrok](https://ngrok.com) installed (for local development only)

## Step 1: Get your URL

You need a public URL that Slack can reach.

### Local development

Expose your local server via ngrok:

```bash
ngrok http 8000
```

Copy the `https://` URL from the output — you'll paste it into the manifest next.

### Production

Use your deployed URL (e.g. `https://your-app.railway.app`).

## Step 2: Create a Slack App

1. Go to [api.slack.com/apps](https://api.slack.com/apps)
2. Click **Create New App**
3. Select **From an app manifest**
4. Select your workspace
5. Choose **JSON** and paste the manifest below — replace `https://your-url` with the URL from Step 1
6. Click **Create**

```json
{
    "display_information": {
        "name": "AgentOS",
        "description": "An AI agent that lives in Slack.",
        "background_color": "#000000"
    },
    "features": {
        "app_home": {
            "home_tab_enabled": false,
            "messages_tab_enabled": true,
            "messages_tab_read_only_enabled": false
        },
        "bot_user": {
            "display_name": "AgentOS",
            "always_online": true
        }
    },
    "oauth_config": {
        "scopes": {
            "bot": [
                "app_mentions:read",
                "assistant:write",
                "channels:history",
                "channels:read",
                "chat:write",
                "chat:write.customize",
                "chat:write.public",
                "files:read",
                "files:write",
                "groups:history",
                "groups:read",
                "im:history",
                "im:read",
                "im:write",
                "mpim:read",
                "users:read",
                "users:read.email"
            ]
        }
    },
    "settings": {
        "event_subscriptions": {
            "request_url": "https://your-url/slack/events",
            "bot_events": [
                "app_mention",
                "message.channels",
                "message.groups",
                "message.im"
            ]
        },
        "org_deploy_enabled": false,
        "socket_mode_enabled": false,
        "is_hosted": false,
        "token_rotation_enabled": false
    }
}
```

The manifest configures scopes, events, and app home settings in one shot.

## Step 3: Install to Workspace

After creating the app:

1. Go to **Install App** in the sidebar
2. Click **Install to Workspace**
3. Click **Allow** to authorize

Copy the **Bot User OAuth Token** shown after install — you'll need it next.

## Step 4: Set Environment Variables

Copy the credentials into your `.env`:

```bash
# Bot User OAuth Token (from Step 3)
SLACK_BOT_TOKEN="xoxb-***"

# Signing Secret (Basic Information → App Credentials)
SLACK_SIGNING_SECRET="***"
```

Restart your app to pick up the Slack credentials:

```bash
docker compose up -d
```

## Step 5: Add the Slack Interface

Add the Slack interface to your `app/main.py`:

```python
from os import getenv
from agno.os.interfaces.slack import Slack

# Only instantiate if credentials are set
if getenv("SLACK_BOT_TOKEN") and getenv("SLACK_SIGNING_SECRET"):
    Slack(
        agent=your_agent,  # or agents=[agent1, agent2]
        token=getenv("SLACK_BOT_TOKEN"),
        signing_secret=getenv("SLACK_SIGNING_SECRET"),
        resolve_user_identity=True,
    )
```

## Verify

Two ways to talk to your agent in Slack:

**Direct message** — find your bot under **Apps** in the Slack sidebar and message it directly:

```
hi
what can you do?
```

**In a channel** — invite the bot first, then mention it:

```
/invite @AgentOS
@AgentOS search for the latest AI news
```

Each thread maintains its own conversation context. Follow-up messages in the same thread don't need to mention the bot again.

## How it works

Thread timestamps are used as session IDs, so each Slack thread is an independent conversation with full history. `resolve_user_identity=True` maps Slack user IDs to names so the agent addresses users by name.

The interface is only instantiated when both `SLACK_BOT_TOKEN` and `SLACK_SIGNING_SECRET` are set — leave them unset to run without Slack.
