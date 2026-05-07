# AgentOS Railway Template

This file is the source of truth for any agent (Claude Code, Codex, others) working in this repo. `CLAUDE.md` is a symlink to this file — edit one, both update.

## Project Overview

A unified agent platform built on [Agno](https://docs.agno.com), shipped as a copy-pasteable starting point. Two reference agents demonstrate the two common shapes for supplying context to an agent. Postgres (pgvector) handles persistence for sessions, memory, and knowledge. Designed to run locally via Docker and deploy to Railway with a single script.

## Architecture

```
AgentOS  (app/main.py)
├── WebSearch  (agents/web_search.py)   — Parallel SDK or keyless MCPTools
└── CodeSearch (agents/code_search.py)  — WorkspaceContextProvider
```

Shared:
- PostgreSQL + pgvector for sessions, memory, knowledge.
- `app.settings.default_model()` returns `OpenAIResponses(id="gpt-5.4")` — bump the model in one place.
- Scheduler enabled by default (`scheduler=True`).
- Slack interface lights up automatically when both `SLACK_BOT_TOKEN` and `SLACK_SIGNING_SECRET` are set.
- JWT auth on whenever `RUNTIME_ENV == "prd"` (so production deploys are gated by default).

## Key Files

| File | Purpose |
|------|---------|
| [`app/main.py`](app/main.py) | AgentOS entrypoint — lifespan hook, conditional Slack, JWT gate. |
| [`app/settings.py`](app/settings.py) | `default_model()` factory. |
| [`app/config.yaml`](app/config.yaml) | Quick prompts per agent (keyed by agent `id`). |
| [`agents/web_search.py`](agents/web_search.py) | Reference agent — direct tools (Parallel SDK or MCP). |
| [`agents/code_search.py`](agents/code_search.py) | Reference agent — context provider. |
| [`db/session.py`](db/session.py) | `get_postgres_db()`, `create_knowledge()`. |
| [`db/url.py`](db/url.py) | Builds the database URL from env. |
| [`evals/cases.py`](evals/cases.py) | Eval cases (each is a `Case` with optional judge + reliability checks). |
| [`evals/__main__.py`](evals/__main__.py) | `python -m evals` runner — wraps agno's `AgentAsJudgeEval` + `ReliabilityEval`. |
| [`compose.yaml`](compose.yaml) | Docker Compose for local development. |
| [`railway.json`](railway.json) | Railway deploy config (Docker + 2 replicas + 4Gi/2vCPU). |

## Development Setup

### Local with Docker

```bash
cp example.env .env
# Edit .env and set OPENAI_API_KEY

docker compose up -d --build
```

Hot-reload watches `agents/`, `app/`, `db/`. Edits land in <2s. `compose.yaml` sets `RUNTIME_ENV=dev`, `AGNO_DEBUG=True`, and `WAIT_FOR_DB=True` so JWT is off and the API blocks on the DB before serving.

### Format & Validate

The format / validate / eval scripts run on the host, so they need a venv. Set one up once:

```bash
./scripts/venv_setup.sh
source .venv/bin/activate
```

Then:

```bash
./scripts/format.sh     # ruff format + import sort
./scripts/validate.sh   # ruff check + mypy (runs both, summarizes)
```

CI installs the same pinned `requirements.txt` and runs the same `scripts/validate.sh` — local and CI never drift.

## Conventions

### Agent pattern

Every agent file has the same shape:

```python
"""
<Title> Agent
=============
"""

from agno.agent import Agent

from app.settings import default_model
from db import get_postgres_db

INSTRUCTIONS = """\
<one short paragraph: what the agent does, which tools it uses, the
rules to follow when answering>
"""

my_agent = Agent(
    id="my-agent",
    name="My Agent",
    model=default_model(),
    db=get_postgres_db(),
    tools=[...],
    instructions=INSTRUCTIONS,
    enable_agentic_memory=True,
    add_datetime_to_context=True,
    add_history_to_context=True,
    num_history_runs=5,
    markdown=True,
)
```

Two patterns to copy from:

- **Direct tools** — see [`agents/web_search.py`](agents/web_search.py). The agent sees each tool individually. Best when the user knows which tools the agent needs.
- **Context provider** — see [`agents/code_search.py`](agents/code_search.py). The agent sees one `query_<thing>` tool that hands off to a sub-agent. Best for one-source agents and when collapsing many tools into one keeps the model focused.

### Database

```python
# Plain agent — sessions, memory, agentic memory live here
from db import get_postgres_db
agent_db = get_postgres_db()

# Agent with a Knowledge base (RAG) — pass through `knowledge=`
from db import create_knowledge
my_kb = create_knowledge("My Knowledge", "my_vectors")
```

Knowledge bases use PgVector with `SearchType.hybrid` and `text-embedding-3-small`. Document contents go into `<table_name>_contents`.

## Adding a new agent

Two options:

1. **Hand it to Claude Code** — paste `Run docs/create-new-agent.md` into a Claude Code session pointed at this repo. Claude asks the user what the agent should do, generates the file, registers it, smoke-tests it.
2. **Do it manually** — create `agents/<slug>.py`, register in `app/main.py`, add prompts to `app/config.yaml`. Then `docker compose restart agentos-api` — uvicorn hot-reload is unreliable for newly-registered modules, so a restart is required for the new agent to load.

## Improving an agent

Run [`docs/improve-agent.md`](docs/improve-agent.md). Single-pass loop: read the agent's `INSTRUCTIONS`, derive probes, run them against the live agent, judge, edit `agents/<slug>.py`, hot-reload, re-probe, iterate. Most fixes are one sentence in the instructions.

## Evals

The eval suite lives in [`evals/`](evals/). Each case wraps agno's [`AgentAsJudgeEval`](https://docs.agno.com/evals/agent-as-judge) (LLM judge against a rubric, binary pass/fail) and/or [`ReliabilityEval`](https://docs.agno.com/evals/reliability) (tool-call assertion). Run with `python -m evals`. Results log to Postgres via `db=eval_db` so history is visible at os.agno.com.

To diagnose failures and fix in scope, run [`docs/eval-and-improve.md`](docs/eval-and-improve.md) in Claude Code.

## Reviewing the repo

Run [`docs/review-and-improve.md`](docs/review-and-improve.md). A recurring sweep that diffs docs against code: every agent registered, every env var documented, every path in a doc still exists, every script behaves as advertised. Auto-fixes mechanical drift; flags anything bigger. Best run before a public-facing release or after a refactor.

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `OPENAI_API_KEY` | yes | — | OpenAI key for models + embeddings. |
| `RUNTIME_ENV` | no | `prd` | `dev` enables hot-reload and disables JWT. Compose sets this to `dev` for local. |
| `JWT_VERIFICATION_KEY` | prd | — | Public key from os.agno.com. Required when `RUNTIME_ENV=prd` and `authorization=True`. |
| `AGENTOS_URL` | no | `http://127.0.0.1:8000` | Scheduler base URL. Set to your Railway domain in production so cron triggers reach AgentOS. |
| `PARALLEL_API_KEY` | no | — | Authenticates the WebSearch Agent's Parallel SDK / MCP connection (raises rate ceiling). |
| `SLACK_BOT_TOKEN` | no | — | Bot token. Set with signing secret to enable Slack interface. |
| `SLACK_SIGNING_SECRET` | no | — | Signing secret. Both must be set for the interface to load. |
| `DB_HOST` / `DB_PORT` / `DB_USER` / `DB_PASS` / `DB_DATABASE` | no | matches compose | Postgres connection. |
| `DB_DRIVER` | no | `postgresql+psycopg` | SQLAlchemy driver. |
| `PORT` | no | `8000` | API server port. |
| `AGNO_DEBUG` | no | `False` | If `True`, agno emits verbose debug logs. Compose sets this for dev. |
| `WAIT_FOR_DB` | no | `False` | If `True`, the entrypoint blocks on the DB before starting. Compose sets this. |

## Ports

- API: `8000`
- Database: `5432`

## Scheduler

`scheduler=True` is on in [`app/main.py`](app/main.py). Hand the scheduler an agent / workflow + a cron expression and it runs in the background. Use it for:

- **Maintenance** — purge old sessions, vacuum tables, rotate trace data.
- **Proactive runs** — every weekday morning, summarize overnight news for your portfolio.
- **Periodic re-evaluation** — run an improve-agent test suite weekly to catch regressions.

See [agno scheduler docs](https://docs.agno.com/agent-os/scheduler) for the cron API.

## Slack

Set `SLACK_BOT_TOKEN` and `SLACK_SIGNING_SECRET` and restart. The default wiring in `app/main.py` routes Slack messages to `code_search` — change the `agent=` arg to point at any other agent. See the [agno Slack interface docs](https://docs.agno.com/agent-os/interfaces/overview) for the Slack-side app setup.

For Discord, Telegram, WhatsApp, and custom UIs, mirror the Slack conditional pattern with the relevant agno interface — see [agno interfaces overview](https://docs.agno.com/agent-os/interfaces/overview).

## Deploying to Railway

```bash
./scripts/railway/up.sh        # provision Postgres + agent-os service
./scripts/railway/env-sync.sh  # sync .env.production (default) or .env
./scripts/railway/redeploy.sh  # redeploy after code changes
```

The first deploy will fail intentionally — JWT auth is on by default and `JWT_VERIFICATION_KEY` isn't set yet. Get the key from os.agno.com (Add OS → Live → Token Based Authorization), put it in `.env.production`, run `./scripts/railway/env-sync.sh`, and Railway auto-redeploys.

The Railway *project* is `agent-platform`; the app *service* is `agent-os`.

## Common Tasks

```bash
# Add a dependency
# 1. Edit pyproject.toml
./scripts/generate_requirements.sh upgrade
docker compose up -d --build

# Build a multi-arch image (maintainer-only)
./scripts/build_image.sh

# Tail Railway logs
railway logs --service agent-os
```

## Documentation Links

- [Agno docs](https://docs.agno.com) — full framework reference.
- [Agno LLM-friendly docs](https://docs.agno.com/llms.txt) — concise overview, good for fetching.
- [AgentOS introduction](https://docs.agno.com/agent-os/introduction).
- [Agno tools / toolkits](https://docs.agno.com/tools/toolkits) — 100+ integrations.
- [Agno model providers](https://docs.agno.com/models) — OpenAI, Anthropic, Google, Ollama, Bedrock, Azure, etc.
- [Agno teams](https://docs.agno.com/teams/overview) — multi-agent routing/coordination.
- [Agno workflows](https://docs.agno.com/workflows/overview) — deterministic step-by-step pipelines.
- [Agno interfaces](https://docs.agno.com/agent-os/interfaces/overview) — Slack, Discord, Telegram, WhatsApp, custom UIs.
