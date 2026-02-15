# AgentOS Railway Template

Deploy a multi-agent system to production on Railway.

[What is AgentOS?](https://docs.agno.com/agent-os/introduction) · [Agno Docs](https://docs.agno.com) · [Discord](https://agno.com/discord)

## What's Included

| Agent | Pattern | Description |
|-------|---------|-------------|
| **Scout** | S3 Browsing + Learning | Enterprise knowledge agent for document stores |
| **Pal** | Learning + Tools | Your AI-powered second brain |
| Knowledge Agent | RAG | Answers questions from a knowledge base |
| MCP Agent | Tool Use | Connects to external services via MCP |

**Scout** is your enterprise librarian -- it navigates document stores, reads full documents, extracts answers, and remembers where things are. **Pal** (Personal Agent that Learns) is your AI-powered second brain -- it researches, captures, organizes, connects, and retrieves your personal knowledge.

## Quick Start

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop)
- [OpenAI API key](https://platform.openai.com/api-keys)

### 1. Clone and configure
```sh
git clone https://github.com/agno-agi/agentos-railway-template.git agentos-railway
cd agentos-railway

cp example.env .env
# Add your OPENAI_API_KEY to .env
```

### 2. Start locally
```sh
docker compose up -d --build
```

- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **Database**: localhost:5432

### 3. Connect to control plane

1. Open [os.agno.com](https://os.agno.com)
2. Click "Add OS" → "Local"
3. Enter `http://localhost:8000`

## Deploy to Railway

### Prerequisites

- [Railway CLI](https://docs.railway.com/guides/cli)
- `OPENAI_API_KEY` set in your environment

### Deploy

```sh
railway login
./scripts/railway_up.sh
```

The script provisions PostgreSQL, configures environment variables, and deploys your application. If you have a Railway Bucket named "storage" in the project, credentials are wired automatically.

### Connect to control plane

1. Open [os.agno.com](https://os.agno.com)
2. Click "Add OS" → "Live"
3. Enter your Railway domain

### Manage deployment

```sh
railway logs --service agent_os      # View logs
railway open                         # Open dashboard
railway up --service agent_os -d     # Update after changes
```

To stop services:
```sh
railway down --service agent_os
railway down --service pgvector
```

---

## The Agents

### Scout (Enterprise Knowledge Agent)

Your enterprise librarian. Scout navigates document stores (Railway Buckets), reads full documents, extracts the actual answer, and remembers where things are so repeated questions get faster, more accurate answers.

**What Scout can find:**

| Source | Contents |
|--------|----------|
| **company-docs** | HR policies, benefits guide, employee handbook |
| **engineering-docs** | Architecture docs, deployment runbooks, incident response |
| **data-exports** | Monthly metrics, reports, data exports |

**Try it:**
```
What is our PTO policy?
Find the deployment runbook
What is the incident response process?
How do I request access to production systems?
```

**How it works:**
- **S3 Tools** navigate buckets, list files, search content, and read documents
- **Two knowledge systems**: static (source registry, intent routing) + dynamic (learned discoveries)
- **Intent routing** maps questions to the right document before searching
- **Exa search** provides web research fallback (requires `EXA_API_KEY`)

**Storage:** Railway Bucket (S3-compatible). Works out of the box with a public demo bucket. Link your own Railway Bucket for write access and custom documents.

### Pal (Personal Agent that Learns)

Your AI-powered second brain. Pal researches, captures, organizes, connects, and retrieves your personal knowledge - so nothing useful is ever lost.

**What Pal stores:**

| Type | Examples |
|------|----------|
| **Notes** | Ideas, decisions, snippets, learnings |
| **Bookmarks** | URLs with context - why you saved it |
| **People** | Contacts - who they are, how you know them |
| **Meetings** | Notes, decisions, action items |
| **Projects** | Goals, status, related items |
| **Research** | Findings from web search, saved for later |

**Try it:**
```
Note: decided to use Postgres for the new project - better JSON support
Bookmark https://www.ashpreetbedi.com/articles/lm-technical-design - great intro
Research event sourcing patterns and save the key findings
What notes do I have?
What do I know about event sourcing?
```

**How it works:**
- **DuckDB** stores your actual data (notes, bookmarks, people, etc.)
- **Learning system** remembers schemas and research findings
- **Exa search** powers web research, company lookup, and people search

**Data persistence:** Pal stores structured data in DuckDB at `/data/pal.db`. This persists across container restarts.

### Knowledge Agent

Answers questions using a vector knowledge base (RAG pattern).

**Try it:**
```
What is Agno?
How do I create my first agent?
What documents are in your knowledge base?
```

**Load documents:**
```sh
# Local
docker exec -it agentos-api python -m agents.knowledge_agent

# Railway
railway run python -m agents.knowledge_agent
```

### MCP Agent

Connects to external tools via the Model Context Protocol.

**Try it:**
```
What tools do you have access to?
Search the docs for how to use LearningMachine
Find examples of agents with memory
```

---

## Project Structure
```
├── agents/
│   ├── scout.py             # Enterprise knowledge agent (S3 browsing)
│   ├── pal.py               # Personal second brain agent
│   ├── knowledge_agent.py   # RAG agent
│   └── mcp_agent.py         # MCP tools agent
├── app/
│   ├── main.py              # AgentOS entry point
│   └── config.yaml          # Quick prompts config
├── storage/
│   ├── client.py            # S3 client (Railway Buckets / any S3-compatible)
│   └── tools.py             # S3 browsing toolkit for agents
├── infra/
│   └── settings.py          # Infrastructure defaults (bucket, region)
├── db/
│   ├── session.py           # PostgreSQL database helpers
│   └── url.py               # Connection URL builder
├── scripts/                 # Helper scripts
├── compose.yaml             # Docker Compose config
├── Dockerfile
├── railway.json             # Railway config
└── pyproject.toml           # Dependencies
```

---

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
    agents=[pal, knowledge_agent, mcp_agent, my_agent],
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

### Scale on Railway

Edit `railway.json`:
```json
{
  "deploy": {
    "numReplicas": 2
  }
}
```

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
| `EXA_API_KEY` | No | - | Exa API key for web research (Pal + Scout) |
| `S3_BUCKET` | No | `agno-scout-public` | Railway Bucket name (auto-set when bucket is linked) |
| `S3_REGION` | No | `us-east-1` | Bucket region |
| `S3_ENDPOINT` | No | - | Bucket endpoint (auto-set for Railway Buckets) |
| `S3_ACCESS_KEY_ID` | No | - | Bucket access key (enables write access) |
| `S3_SECRET_ACCESS_KEY` | No | - | Bucket secret key (enables write access) |
| `PORT` | No | `8000` | API server port |
| `DB_HOST` | No | `localhost` | Database host |
| `DB_PORT` | No | `5432` | Database port |
| `DB_USER` | No | `ai` | Database user |
| `DB_PASS` | No | `ai` | Database password |
| `DB_DATABASE` | No | `ai` | Database name |
| `DATA_DIR` | No | `/data` | Directory for DuckDB storage |
| `RUNTIME_ENV` | No | `prd` | Set to `dev` for auto-reload |

---

## Learn More

- [Agno Documentation](https://docs.agno.com)
- [AgentOS Documentation](https://docs.agno.com/agent-os/introduction)
- [Tools & Integrations](https://docs.agno.com/tools/toolkits)
- [Discord Community](https://agno.com/discord)