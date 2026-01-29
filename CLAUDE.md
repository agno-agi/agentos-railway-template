# CLAUDE.md

This file provides context for Claude Code when working with this repository.

## Project Overview

AgentOS - A multi-agent system built on the Agno framework, deployable to Railway.

## Architecture

```
AgentOS (app/main.py)
├── Pal Agent (agents/pal.py)           # Personal second brain with learning
├── Knowledge Agent (agents/knowledge_agent.py)  # RAG-based Q&A
└── MCP Agent (agents/mcp_agent.py)     # External tools via MCP
```

All agents share:
- PostgreSQL database (pgvector) for persistence
- OpenAI GPT-5.2 model
- Chat history and context management

## Key Files

| File | Purpose |
|------|---------|
| `app/main.py` | AgentOS entry point, registers all agents |
| `app/config.yaml` | Quick prompts for each agent |
| `agents/*.py` | Individual agent implementations |
| `db/session.py` | `get_postgres_db(contents_table=...)` helper |
| `db/url.py` | Builds database URL from environment |
| `compose.yaml` | Local development with Docker |
| `railway.json` | Railway deployment config |

## Development Setup

### Virtual Environment

Use the venv setup script to create the development environment:

```bash
./scripts/venv_setup.sh
source .venv/bin/activate
```

### Format & Validation

Always run format and lint checks using the venv Python interpreter:

```bash
source .venv/bin/activate && ./scripts/format.sh
source .venv/bin/activate && ./scripts/validate.sh
```

## Conventions

### Agent Pattern

All agents follow this structure:

```python
from agno.agent import Agent
from agno.models.openai import OpenAIResponses
from db import get_postgres_db

agent_db = get_postgres_db()

instructions = """..."""

my_agent = Agent(
    id="my-agent",
    name="My Agent",
    model=OpenAIResponses(id="gpt-5.2"),
    db=agent_db,
    instructions=instructions,
    add_datetime_to_context=True,
    add_history_to_context=True,
    read_chat_history=True,
    num_history_runs=5,
    markdown=True,
)

if __name__ == "__main__":
    my_agent.print_response("Hello!", stream=True)
```

### Database

- Use `get_postgres_db()` from `db` module
- **Important**: The `contents_table` parameter is only needed when the database is provided to a Knowledge base as a contents_db. If your agent doesn't use a Knowledge base, just use `get_postgres_db()` without arguments.

```python
# Agent WITH a Knowledge base - specify contents_table
agent_db = get_postgres_db(contents_table="my_agent_contents")
knowledge = Knowledge(
    vector_db=PgVector(...),
    contents_db=agent_db,  # <-- contents_table is used here
)

# Agent WITHOUT a Knowledge base - no contents_table needed
agent_db = get_postgres_db()
```

- Knowledge bases use PgVector with `SearchType.hybrid`
- Embeddings use `text-embedding-3-small`

### Imports

```python
# Database
from db import db_url, get_postgres_db

# Agents (import directly from module)
from agents.pal import pal
from agents.knowledge_agent import knowledge_agent
from agents.mcp_agent import mcp_agent
```

## Adding a New Agent

1. Create `agents/new_agent.py` following the agent pattern above
2. Register in `app/main.py`:
   ```python
   from agents.new_agent import new_agent

   agent_os = AgentOS(
       agents=[pal, knowledge_agent, mcp_agent, new_agent],
       ...
   )
   ```
3. Add quick prompts to `app/config.yaml`

## Commands

```bash
# Setup virtual environment
./scripts/venv_setup.sh
source .venv/bin/activate

# Local development with Docker
docker compose up -d --build

# Test individual agents
python -m agents.pal
python -m agents.mcp_agent

# Load documents into knowledge agent
python -m agents.knowledge_agent

# Format & validation (run from activated venv)
./scripts/format.sh
./scripts/validate.sh

# Deploy to Railway
./scripts/railway_up.sh
```

## Environment Variables

Required:
- `OPENAI_API_KEY`

Optional:
- `EXA_API_KEY` - Enables Pal's web research tools
- `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASS`, `DB_DATABASE`
- `DATA_DIR` - DuckDB storage location (default: `/data`)
- `RUNTIME_ENV` - Set to `dev` for auto-reload

## Ports

- API: 8000 (both Dockerfile and railway.json)
- Database: 5432

## Data Storage

| Agent | Storage | Location |
|-------|---------|----------|
| Pal | DuckDB (user data) | `/data/pal.db` |
| Pal | PostgreSQL (learnings) | `pal_knowledge` table |
| Knowledge Agent | PostgreSQL | `knowledge_agent_docs` table |
| All | PostgreSQL | Session/memory tables (automatic) |
