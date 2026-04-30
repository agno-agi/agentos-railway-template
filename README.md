# AgentOS Starter Template

[![Deploy on Railway](https://railway.com/button.svg)](https://railway.com/new/template/agentos)

The minimal AgentOS foundation. Three example agents, web search via MCP, and one-script deploy to Railway.

This template demonstrates **context providers** — a pattern for exposing information sources to agents without polluting their context with tool-specific quirks. Each provider wraps a source (web search, codebase, MCP server) and exposes it through one or two natural-language tools.

## Quick start

> **Prerequisite:** Docker Desktop installed and running ([install guide](https://docs.docker.com/desktop/)).

```sh
git clone https://github.com/agno-agi/agentos-railway-template.git starter
cd starter

cp example.env .env
# set OPENAI_API_KEY in .env

docker compose up -d --build
```

AgentOS is now running at `http://localhost:8000`.

## Chat with your agents

1. Open [os.agno.com](https://os.agno.com?utm_source=github&utm_medium=starter-template) and log in.
2. Click **Add OS** → **Local** → enter `http://localhost:8000` → **Connect**.
3. Select an agent and start chatting.

Try these prompts:

```
# Search Agent — searches via sub-agent
What are the latest developments in AI agents?

# Research Agent — direct tool access
Search for recent OpenAI news

# Codebase Agent — explores this codebase
What agents are available in this project?
```

## How it works

Each agent uses a **context provider** to access an information source. The provider handles connection, pagination, retries, and source-specific quirks — the agent just calls `query_<source>`.

| Agent | Provider | Mode | Tools |
|-------|----------|------|-------|
| **Search Agent** | `WebContextProvider` | agent | `query_web` |
| **Research Agent** | `WebContextProvider` | tools | `web_search`, `web_fetch` |
| **Codebase Agent** | `WorkspaceContextProvider` | tools | `list_files`, `search_content`, `read_file` |

**Agent mode** wraps tools behind a sub-agent. Your agent sees one `query_<source>` tool — the sub-agent handles the underlying complexity.

**Tools mode** flattens tools directly onto your agent. Cheaper (no sub-agent LLM hop), but tool names must be distinct.

No API keys required except OpenAI — the web backend uses [Parallel MCP](https://search.parallel.ai/mcp), which is free.

## Deploy to Railway

### One-click deploy

Click the deploy button at the top of this README, or go to [railway.com/new/template/agentos](https://railway.com/new/template/agentos).

You'll need to provide your `OPENAI_API_KEY`. The template automatically provisions PostgreSQL with pgvector.

### CLI deploy

**Prereqs:** [Railway CLI](https://docs.railway.app/guides/cli) installed and `railway login` run.

```sh
./scripts/railway_up.sh
```

This provisions PostgreSQL, deploys your app, and assigns a public domain (~5 min).

After code or env changes:

```sh
./scripts/railway_env.sh       # sync .env → Railway
./scripts/railway_redeploy.sh  # push code updates
```

### Connect production to AgentOS

1. Open [os.agno.com](https://os.agno.com)
2. Click **Add OS** → **Live**
3. Enter your Railway domain

### Enable JWT authorization (recommended)

Production endpoints should require authorization. To enable:

1. In AgentOS, enable **Token Based Authorization** for your OS
2. Copy the public key and add to your env:

```sh
JWT_VERIFICATION_KEY=-----BEGIN PUBLIC KEY-----
MIIBIjANBgkq...
-----END PUBLIC KEY-----
```

3. Sync and redeploy:

```sh
./scripts/railway_env.sh
./scripts/railway_redeploy.sh
```

Every API call now runs signed-and-verified. See [AgentOS Security docs](https://docs.agno.com/agent-os/security/overview) for details.

## Add your own agent

1. Create `agents/my_agent.py`:

```python
from agno.agent import Agent
from agno.models.openai import OpenAIResponses
from db import get_postgres_db

my_agent = Agent(
    id="my-agent",
    name="My Agent",
    model=OpenAIResponses(id="gpt-5.4"),
    db=get_postgres_db(),
    instructions="You are a helpful assistant.",
)
```

2. Register in `app/main.py`:

```python
from agents.my_agent import my_agent

agent_os = AgentOS(
    agents=[search_agent, research_agent, codebase_agent, my_agent],
    # ...
)
```

3. Restart: `docker compose restart`

## Add context providers

### MCP servers

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

agent = Agent(
    tools=linear_context.get_tools(),
    instructions=linear_context.instructions(),
    # ...
)
```

### Slack

See [docs/SLACK_CONNECT.md](docs/SLACK_CONNECT.md) for the full guide.

## Local development

```sh
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

## Environment variables

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

## Architecture

Built on [Agno](https://github.com/agno-agi/agno) and [AgentOS](https://docs.agno.com/agent-os/introduction?utm_source=github&utm_medium=starter-template).

- [Agno Documentation](https://docs.agno.com?utm_source=github&utm_medium=starter-template)
- [Context Providers Guide](https://docs.agno.com/context/overview?utm_source=github&utm_medium=starter-template)
- [Agno Discord](https://agno.com/discord)
