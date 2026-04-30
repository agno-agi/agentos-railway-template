# AgentOS Starter Template

[![Deploy on Railway](https://railway.com/button.svg)](https://railway.com/new/template/agentos)

The minimal AgentOS foundation. Three example agents, web search via MCP, and one-script deploy to Railway.

## What's Included

| Agent | Pattern | Description |
|-------|---------|-------------|
| **Web Agent** | Context Provider (agent mode) | Web search via Parallel MCP. Sub-agent wraps the tools — you get one `query_web` tool. |
| **Web Tools Agent** | Context Provider (tools mode) | Same web search, but tools (`web_search`, `web_fetch`) are flattened directly onto the agent. |
| **Workspace Agent** | Context Provider | Answers questions about this codebase. Navigates, searches, and reads files. |

No API keys required except OpenAI — Parallel MCP is free.

## Quick Start

```bash
git clone https://github.com/agno-agi/agentos-railway-template.git starter
cd starter

cp example.env .env
# Set OPENAI_API_KEY in .env

docker compose up -d --build
```

Verify it's running:

```bash
curl http://localhost:8000/health
# {"status":"ok"}
```

### Connect to the Web UI

1. Open [os.agno.com](https://os.agno.com) and log in
2. Click **Add OS** → **Local** → `http://localhost:8000`
3. Click **Connect**

### Try the agents

```
# Web Agent — searches via sub-agent
What are the latest developments in AI agents?

# Web Tools Agent — direct tool access
Search for recent OpenAI news

# Workspace Agent — explores this codebase
What agents are available in this project?
```

## Deploy to Railway

### One-Click Deploy

Click the deploy button at the top of this page, or go to [railway.com/new/template/agentos](https://railway.com/new/template/agentos).

You'll need to provide your `OPENAI_API_KEY`. The template automatically provisions PostgreSQL with pgvector.

### CLI Deploy

For more control, use the Railway CLI:

```bash
# Install Railway CLI: https://docs.railway.app/guides/cli
railway login
./scripts/railway_up.sh
```

The script provisions PostgreSQL, deploys your app, and assigns a public domain (~5 min).

### Sync env vars after changes

```bash
./scripts/railway_env.sh
```

### Redeploy after code changes

```bash
./scripts/railway_redeploy.sh
```

### Connect production to AgentOS UI

1. Open [os.agno.com](https://os.agno.com)
2. Click **Add OS** → **Live**
3. Enter your Railway domain

## Add Your Own Agent

1. Create `agents/my_agent.py`:

```python
from agno.agent import Agent
from agno.models.openai import OpenAIResponses
from db import get_postgres_db

my_agent = Agent(
    id="my-agent",
    name="My Agent",
    model=OpenAIResponses(id="gpt-5.2"),
    db=get_postgres_db(),
    instructions="You are a helpful assistant.",
)
```

2. Register in `app/main.py`:

```python
from agents.my_agent import my_agent

agent_os = AgentOS(
    agents=[web_agent, web_tools_agent, workspace_agent, my_agent],
    # ...
)
```

3. Restart: `docker compose restart`

## Add MCP Servers

See [docs/MCP_CONNECT.md](docs/MCP_CONNECT.md) for the full guide.

Quick example — add Linear:

```python
from agno.context.mcp import MCPContextProvider

linear_context = MCPContextProvider(
    server_name="linear",
    transport="stdio",
    command="npx",
    args=["-y", "@linear/mcp"],
    env={"LINEAR_API_KEY": getenv("LINEAR_API_KEY", "")},
    model=your_model,
)
```

## Connect to Slack

See [docs/SLACK_CONNECT.md](docs/SLACK_CONNECT.md) for the full guide.

## Local Development

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Setup environment
./scripts/venv_setup.sh
source .venv/bin/activate

# Start PostgreSQL
docker compose up -d agentos-db

# Run the app
python -m app.main
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | Yes | — | OpenAI API key |
| `PORT` | No | `8000` | API server port |
| `DB_HOST` | No | `localhost` | Database host |
| `DB_PORT` | No | `5432` | Database port |
| `DB_USER` | No | `ai` | Database user |
| `DB_PASS` | No | `ai` | Database password |
| `DB_DATABASE` | No | `ai` | Database name |
| `DB_DRIVER` | No | `postgresql+psycopg` | SQLAlchemy driver |
| `RUNTIME_ENV` | No | `prd` | Set to `dev` for auto-reload |
| `WAIT_FOR_DB` | No | `False` | Wait for database before starting |
| `AGNO_DEBUG` | No | `False` | Enable Agno debug logging |
| `SLACK_BOT_TOKEN` | No | — | Slack bot token (enables Slack) |
| `SLACK_SIGNING_SECRET` | No | — | Slack signing secret |

## Learn More

- [Agno Documentation](https://docs.agno.com)
- [AgentOS Documentation](https://docs.agno.com/agent-os/introduction)
- [Context Providers Guide](https://docs.agno.com/context/overview)
- [Agno Discord](https://agno.com/discord)
