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
| `db/session.py` | `get_postgres_db()` helper for database connections |
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
    # Context options (all agents use these)
    add_datetime_to_context=True,
    add_history_to_context=True,
    read_chat_history=True,
    num_history_runs=5,
    markdown=True,
    # Optional: Enable agentic memory for user preferences
    enable_agentic_memory=True,
)

if __name__ == "__main__":
    my_agent.print_response("Hello!", stream=True)
```

### Database

- Use `get_postgres_db()` from `db` module
- **Important**: The `contents_table` parameter is only needed when the database is provided to a Knowledge base as a `contents_db`. If your agent doesn't use a Knowledge base, just use `get_postgres_db()` without arguments.

```python
# Agent WITH a Knowledge base - specify contents_table
agent_db = get_postgres_db(contents_table="my_agent_contents")
knowledge = Knowledge(
    vector_db=PgVector(
        db_url=db_url,
        table_name="my_agent_vectors",  # Vector embeddings table
        search_type=SearchType.hybrid,
        embedder=OpenAIEmbedder(id="text-embedding-3-small"),
    ),
    contents_db=agent_db,  # <-- contents_table stores document contents
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
3. Add quick prompts to `app/config.yaml` using the agent's `id`

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
- `DB_DRIVER` - Database driver (default: `postgresql+psycopg`)
- `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASS`, `DB_DATABASE`
- `DATA_DIR` - DuckDB storage location (default: `/data`)
- `RUNTIME_ENV` - Set to `dev` for auto-reload

## Ports

- API: 8000 (both Dockerfile and railway.json)
- Database: 5432

## Data Storage

| Agent | Storage | Table/Location |
|-------|---------|----------------|
| Pal | DuckDB (user data) | `/data/pal.db` |
| Pal | PostgreSQL (vector embeddings) | `pal_knowledge` |
| Pal | PostgreSQL (document contents) | `pal_contents` |
| Knowledge Agent | PostgreSQL (vector embeddings) | `knowledge_agent_docs` |
| Knowledge Agent | PostgreSQL (document contents) | `knowledge_agent_contents` |
| All | PostgreSQL | Session/memory tables (automatic) |

---

## Agno Framework Reference

### Model Providers

Agno supports 40+ model providers. Common options:

```python
# OpenAI (default in this project)
from agno.models.openai import OpenAIResponses
model = OpenAIResponses(id="gpt-5.2")

# Anthropic Claude
from agno.models.anthropic import Claude
model = Claude(id="claude-sonnet-4-5")

# Google Gemini
from agno.models.google import Gemini
model = Gemini(id="gemini-2.0-flash")

# Local models via Ollama
from agno.models.ollama import Ollama
model = Ollama(id="llama3")

# AWS Bedrock
from agno.models.aws import BedrockChat
model = BedrockChat(id="anthropic.claude-3-sonnet-20240229-v1:0")

# Azure OpenAI
from agno.models.azure import AzureOpenAI
model = AzureOpenAI(id="gpt-4", azure_endpoint="...", api_version="...")
```

### Knowledge & RAG

#### Search Types

```python
from agno.vectordb.pgvector import SearchType

SearchType.vector   # Semantic similarity search
SearchType.keyword  # Exact word/phrase matching
SearchType.hybrid   # Combined vector + keyword (recommended)
```

#### Knowledge Base Setup

```python
from agno.knowledge import Knowledge
from agno.knowledge.embedder.openai import OpenAIEmbedder
from agno.vectordb.pgvector import PgVector, SearchType

knowledge = Knowledge(
    name="My Knowledge Base",
    vector_db=PgVector(
        db_url=db_url,
        table_name="my_vectors",
        search_type=SearchType.hybrid,
        embedder=OpenAIEmbedder(id="text-embedding-3-small"),
    ),
    contents_db=get_postgres_db(contents_table="my_contents"),
    max_results=10,
)

# Load documents
knowledge.insert(name="Doc Name", url="https://example.com/doc.md")
knowledge.insert(name="Local File", path="/path/to/file.pdf")

# Use in agent
agent = Agent(
    knowledge=knowledge,
    search_knowledge=True,  # Enable automatic knowledge search
    ...
)
```

#### Supported Vector Databases

PgVector (used here), ChromaDB, LanceDB, Pinecone, Qdrant, Weaviate, Milvus, Redis, MongoDB, and 15+ others.

### Memory & Learning

#### Memory Types

- **User Memory**: Unstructured observations about users
- **User Profile**: Structured facts about users
- **Entity Memory**: Facts about companies, projects, people
- **Session Context**: Goals, plans, progress for active sessions

#### Learning Machines

For agents that learn and improve over time:

```python
from agno.learn import (
    LearningMachine,
    LearningMode,
    LearnedKnowledgeConfig,
    UserMemoryConfig,
    UserProfileConfig,
)

agent = Agent(
    learning=LearningMachine(
        knowledge=my_knowledge_base,
        user_profile=UserProfileConfig(mode=LearningMode.AGENTIC),
        user_memory=UserMemoryConfig(mode=LearningMode.AGENTIC),
        learned_knowledge=LearnedKnowledgeConfig(mode=LearningMode.AGENTIC),
    ),
    ...
)
```

#### Simple Agentic Memory

For basic user preference tracking without a full knowledge base:

```python
agent = Agent(
    enable_agentic_memory=True,
    ...
)
```

### Tools

#### Built-in Tools

```python
# DuckDB for structured data
from agno.tools.duckdb import DuckDbTools
tools = [DuckDbTools(db_path="/data/my.db")]

# Web search
from agno.tools.duckduckgo import DuckDuckGoTools
tools = [DuckDuckGoTools()]

# File operations
from agno.tools.file import FileTools
tools = [FileTools()]

# Many more: Slack, Gmail, GitHub, Linear, etc.
# See: https://docs.agno.com/tools/toolkits
```

#### MCP Tools (Model Context Protocol)

Connect to external MCP servers:

```python
from agno.tools.mcp import MCPTools

# Remote MCP server
tools = [MCPTools(url="https://mcp.example.com/mcp")]

# Local MCP server (stdio)
tools = [MCPTools(command="npx @modelcontextprotocol/server-filesystem /path")]

# Multiple MCP servers
tools = [
    MCPTools(url="https://mcp.exa.ai/mcp?exaApiKey=..."),
    MCPTools(url="https://docs.agno.com/mcp"),
]
```

#### Custom Tools

```python
from agno.tools import tool

@tool
def my_custom_tool(query: str) -> str:
    """Search for something.

    Args:
        query: The search query.

    Returns:
        Search results as a string.
    """
    # Implementation
    return f"Results for: {query}"

agent = Agent(tools=[my_custom_tool], ...)
```

### Agent Configuration Options

| Option | Type | Description |
|--------|------|-------------|
| `id` | str | Unique identifier (used in config.yaml) |
| `name` | str | Display name |
| `model` | Model | Language model to use |
| `db` | PostgresDb | Database for persistence |
| `instructions` | str | System prompt |
| `tools` | list | Available tools |
| `knowledge` | Knowledge | Knowledge base for RAG |
| `search_knowledge` | bool | Auto-search knowledge base |
| `learning` | LearningMachine | Learning configuration |
| `enable_agentic_memory` | bool | Track user preferences |
| `add_datetime_to_context` | bool | Include current time |
| `add_history_to_context` | bool | Include chat history |
| `read_chat_history` | bool | Load previous messages |
| `num_history_runs` | int | Number of history runs to include |
| `markdown` | bool | Format responses as markdown |

### AgentOS Configuration

```python
from agno.os import AgentOS

agent_os = AgentOS(
    name="My AgentOS",
    agents=[agent1, agent2],
    teams=[team1],           # Optional: multi-agent teams
    workflows=[workflow1],   # Optional: sequential workflows
    knowledge=[kb1, kb2],    # Optional: shared knowledge bases
    db=get_postgres_db(),
    config="path/to/config.yaml",
    tracing=True,            # Enable distributed tracing
    enable_mcp_server=True,  # Expose as MCP server
)
```

### Hooks (Pre/Post Processing)

```python
from agno.os import AgentOS
from agno.os.hooks import hook

@hook
async def log_request(request):
    """Pre-execution hook."""
    print(f"Request: {request}")
    return request

@hook
async def log_response(response):
    """Post-execution hook."""
    print(f"Response: {response}")
    return response

agent_os = AgentOS(
    pre_hooks=[log_request],
    post_hooks=[log_response],
    run_hooks_in_background=True,  # Non-blocking execution
    ...
)
```

### Security

#### JWT Authentication

```python
from agno.os.security import JWTAuth

agent_os = AgentOS(
    auth=JWTAuth(
        secret="your-secret-key",
        algorithm="HS256",
    ),
    ...
)
```

#### RBAC Scopes

- `agents:read` - Read all agents
- `agents:<id>:run` - Run specific agent
- `agent_os:admin` - Full admin access

### Documentation Links

**LLM-friendly documentation (for fetching):**
- https://docs.agno.com/llms.txt - Concise overview of Agno framework
- https://docs.agno.com/llms-full.txt - Complete Agno documentation

**Web documentation:**
- [Agno Docs](https://docs.agno.com)
- [AgentOS Introduction](https://docs.agno.com/agent-os/introduction)
- [Tools & Integrations](https://docs.agno.com/tools/toolkits)
- [Model Providers](https://docs.agno.com/models)
- [Knowledge & RAG](https://docs.agno.com/knowledge)
- [MCP Integration](https://docs.agno.com/tools/mcp)
