# AgentOS Railway Template

Deploy a multi-agent system on Railway.

## What's Included

| Agent | Pattern | Description |
|-------|---------|-------------|
| Knowledge Agent | Agentic RAG | Answers questions from a knowledge base. |
| MCP Agent | MCP Tool Use | Connects to external services via MCP. |

## Get Started

```sh
# Clone the repo
git clone https://github.com/agno-agi/agentos-railway-template.git agentos-railway
cd agentos-railway

# Add OPENAI_API_KEY
cp example.env .env
# Edit .env and add your key

# Start the application
docker compose up -d --build

# Load documents for the knowledge agent
docker exec -it agentos-api python -m agents.knowledge_agent
```

Confirm AgentOS is running at [http://localhost:8000/docs](http://localhost:8000/docs).

### Connect to the Web UI

1. Open [os.agno.com](https://os.agno.com) and login
2. Add OS → Local → `http://localhost:8000`
3. Click "Connect"

## Deploy to Railway

Requires:
- [Railway CLI](https://docs.railway.com/guides/cli)
- `OPENAI_API_KEY` set in your environment

```sh
railway login

./scripts/railway_up.sh
```

The script provisions PostgreSQL, configures environment variables, and deploys your application.

### Connect to the Web UI

1. Open [os.agno.com](https://os.agno.com)
2. Click "Add OS" → "Live"
3. Enter your Railway domain

### Manage deployment

```sh
railway logs --service agent-os      # View logs
railway open                         # Open dashboard
railway up --service agent-os -d     # Update after changes
```

To stop services:
```sh
railway down --service agent-os
railway down --service pgvector
```

## The Agents

### Knowledge Agent

Answers questions using hybrid search over a vector database (Agentic RAG).

**Load documents:**

```sh
# Local
docker exec -it agentos-api python -m agents.knowledge_agent

# Railway
railway run python -m agents.knowledge_agent
```

**Try it:**

```
What is Agno?
How do I create my first agent?
What documents are in your knowledge base?
```

### MCP Agent

Connects to external tools via the Model Context Protocol.

**Try it:**

```
What tools do you have access to?
Search the docs for how to use LearningMachine
Find examples of agents with memory
```

## Common Tasks

### Add your own agent

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
    name="AgentOS",
    agents=[knowledge_agent, mcp_agent, my_agent],
    ...
)
```

3. Restart: `docker compose restart`

### Add tools to an agent

Agno includes 100+ tool integrations. See the [full list](https://docs.agno.com/tools/toolkits).

```python
from agno.tools.slack import SlackTools
from agno.tools.google_calendar import GoogleCalendarTools

my_agent = Agent(
    ...
    tools=[
        SlackTools(),
        GoogleCalendarTools(),
    ],
)
```

### Add dependencies

1. Edit `pyproject.toml`
2. Regenerate requirements: `./scripts/generate_requirements.sh`
3. Rebuild: `docker compose up -d --build`

### Use a different model provider

1. Add your API key to `.env` (e.g., `ANTHROPIC_API_KEY`)
2. Update agents to use the new provider:

```python
from agno.models.anthropic import Claude

model=Claude(id="claude-sonnet-4-5")
```
3. Add dependency: `anthropic` in `pyproject.toml`

---

## Local Development

For development without Docker:

```sh
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Setup environment
./scripts/venv_setup.sh
source .venv/bin/activate

# Start PostgreSQL (required)
docker compose up -d agentos-db

# Run the app
python -m app.main
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | Yes | - | OpenAI API key |
| `PORT` | No | `8000` | API server port |
| `DB_HOST` | No | `localhost` | Database host |
| `DB_PORT` | No | `5432` | Database port |
| `DB_USER` | No | `ai` | Database user |
| `DB_PASS` | No | `ai` | Database password |
| `DB_DATABASE` | No | `ai` | Database name |
| `RUNTIME_ENV` | No | `prd` | Set to `dev` for auto-reload |

## Learn More

- [Agno Documentation](https://docs.agno.com)
- [AgentOS Documentation](https://docs.agno.com/agent-os/introduction)
- [Agno Discord](https://agno.com/discord)
