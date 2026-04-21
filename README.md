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

### Deploy to Railway via GitHub UI

If you want to deploy directly from the Railway dashboard instead of the CLI, use this exact flow.

#### 1. Create the AgentOS service from GitHub

1. In Railway, click `New` -> `Deploy from GitHub repo`.
2. Select this repository.
3. If the template files are already at the repo root, leave `Root Directory` empty.
4. If this code is inside a larger repo or monorepo, set `Root Directory` to `agentos-railway`.

Railway builds from the source directory root. If the `Dockerfile` is not at that root, deployment fails unless you point Railway to the correct directory.

#### 2. Add PostgreSQL to the same Railway project

1. Click `New` -> `Database` -> `PostgreSQL`.
2. Wait for provisioning to finish.
3. Rename the database service to something simple like `postgres` if you want cleaner variable references.

Railway exposes `PGHOST`, `PGPORT`, `PGUSER`, `PGPASSWORD`, `PGDATABASE`, and `DATABASE_URL` automatically for the database service.

#### 3. Fill the `Settings` tab for the AgentOS service

Use these values:

| Section | Field | What to fill |
|--------|-------|--------------|
| Source | Source Repo | The GitHub repo you selected |
| Source | Root Directory | Leave empty if the template is at repo root. Use `agentos-railway` only if the template is nested inside a larger repo |
| Networking | Public Networking | Add `HTTP Proxy` |
| Networking | HTTP target/internal port | `8000` |
| Deploy | Pre-deploy Command | Leave empty |
| Deploy | Custom Start Command | Leave empty |
| Deploy | Healthcheck Path | `/health` |
| Deploy | Restart Policy | `On Failure` |
| Deploy | Restart retries | `10` |
| Deploy | Replicas | `1` |

Do not add `TCP Proxy` for the API service. This container exposes HTTP only.

#### 4. Fill the `Variables` tab for the AgentOS service

Add these variables:

```dotenv
OPENAI_API_KEY=sk-...
DB_DRIVER=postgresql+psycopg
WAIT_FOR_DB=True
PORT=8000
WHATSAPP_ENABLED=false
DB_HOST=${{postgres.PGHOST}}
DB_PORT=${{postgres.PGPORT}}
DB_USER=${{postgres.PGUSER}}
DB_PASS=${{postgres.PGPASSWORD}}
DB_DATABASE=${{postgres.PGDATABASE}}
```

Important:

- Replace `postgres` in `${{postgres.PGHOST}}` with the exact Railway service name of your PostgreSQL service.
- The Railway variables UI autocompletes references. Use the autocomplete instead of typing these references manually.
- `OPENAI_API_KEY` is the only required secret for the default template.
- `PORT=8000` keeps the HTTP proxy, healthcheck, and the container aligned.

Optional model provider variables:

```dotenv
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
```

Only add the WhatsApp variables if you are enabling the WhatsApp interface:

```dotenv
WHATSAPP_ENABLED=true
WHATSAPP_ACCESS_TOKEN=...
WHATSAPP_PHONE_NUMBER_ID=...
WHATSAPP_VERIFY_TOKEN=...
WHATSAPP_APP_SECRET=...
```

If `WHATSAPP_ENABLED=true` and one of those values is missing, the container now fails fast on startup instead of booting with a broken webhook configuration.

#### 5. Deploy and validate

1. Click `Deploy`.
2. Open the generated Railway domain.
3. Check:
   - `https://<your-domain>/health`
   - `https://<your-domain>/docs`
4. In `os.agno.com`, connect the deployment using the live Railway URL.

#### 6. Where each value comes from

| Value | Where you get it |
|-------|-------------------|
| `OPENAI_API_KEY` | OpenAI Platform dashboard |
| `DB_*` variables | Railway Postgres reference variables |
| `PORT` | Fixed manually to `8000` for this container |
| `Healthcheck Path` | This repo exposes `/health` |
| `Custom Start Command` | Leave blank because the container starts AgentOS by default |
| `WHATSAPP_*` variables | Meta Developers -> your app -> WhatsApp -> API Setup |

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
| `WHATSAPP_ENABLED` | No | `false` | Enables the live WhatsApp interface. Leave disabled for local tests/dev. |
| `WHATSAPP_ACCESS_TOKEN` | No | - | Meta WhatsApp Cloud API access token. Required only when `WHATSAPP_ENABLED=true`. |
| `WHATSAPP_PHONE_NUMBER_ID` | No | - | Meta WhatsApp phone number id. Required only when `WHATSAPP_ENABLED=true`. |
| `WHATSAPP_VERIFY_TOKEN` | No | - | Webhook verification token. Required only when `WHATSAPP_ENABLED=true`. |
| `WHATSAPP_APP_SECRET` | No | - | Meta app secret for webhook signature validation. Required only when `WHATSAPP_ENABLED=true`. |
| `WHATSAPP_SKIP_SIGNATURE_VALIDATION` | No | `false` | Local-only escape hatch when testing webhooks without `WHATSAPP_APP_SECRET`. |
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
