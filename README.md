# AgentOS Railway Template

A complete agent platform you can run on Railway. Everything runs in your cloud, behind your auth, with your data in your database.

The template ships with five Claude Code prompts to:

1. **Create** a new agent.
2. **Extend** an agent. You steer, Claude executes.
3. **Improve** an agent. Claude probes its own `INSTRUCTIONS` and edits until it passes.
4. **Hill-climb** failing evals.
5. **Review** the repo for drift between docs, code, and config.

The platform has five parts:

1. **Runtime.** FastAPI + AgentOS (`app/main.py`).
2. **Storage.** PostgreSQL + pgvector (sessions, memory, knowledge, traces).
3. **Connectors.** MCP servers and toolkits (`agno.tools.*`).
4. **Interfaces.** Slack is already wired. Discord, Telegram, and custom UIs via [agno interfaces](https://docs.agno.com/agent-os/interfaces/overview?utm_source=github&utm_medium=example-repo&utm_campaign=agent-platform&utm_content=agent-platform&utm_term=railway).
5. **Infrastructure.** Docker locally, Railway in production. 

> **TL;DR.** Run locally in four lines. Ship to Railway with one script. Iterate on agents from Claude Code. The rest of this doc is the long form.

## Step 1: Run locally

> **Prerequisite:** [Docker](https://www.docker.com/get-started/) installed and running.

```sh
git clone https://github.com/agno-agi/agentos-railway-template.git agent-platform
cd agent-platform

cp example.env .env
# Edit .env and set OPENAI_API_KEY

docker compose up -d --build
```

Confirm AgentOS is live at [http://localhost:8000/docs](http://localhost:8000/docs).

Connect a UI: open [os.agno.com](https://os.agno.com?utm_source=github&utm_medium=example-repo&utm_campaign=agent-platform&utm_content=agent-platform&utm_term=railway), click **Add OS** → **Local**, enter `http://localhost:8000`, and connect.

## Step 2: Create your first agent

The template ships with two reference agents:

| Agent | Pattern | Tools |
|---|---|---|
| WebSearch | Direct tools | `parallel_search` / `parallel_extract` (needs `PARALLEL_API_KEY`); `web_search` / `web_fetch` keyless |
| CodeSearch | Context provider sub-agent | `query_my_codebase` |

**Direct tools**: the agent sees each tool individually. **Context provider**: the agent sees one `query_<thing>` tool that hands off to a sub-agent. Two patterns to copy from when you build your own.

To create a new agent, open [Claude Code](https://claude.ai/code) in this repo and paste:

```
Run docs/create-new-agent.md in a new branch
```

Claude asks a few questions, generates the agent file in `agents/`, registers it in `app/main.py`, adds prompts to `app/config.yaml`, restarts the container, and smoke-tests via cURL. The container restart is needed because uvicorn's reloader doesn't reliably pick up newly-registered modules. Usually 5-10 minutes for a simple agent.

## Step 3: Test

Chat with your agents at [os.agno.com](https://os.agno.com?utm_source=github&utm_medium=example-repo&utm_campaign=agent-platform&utm_content=agent-platform&utm_term=railway). Run realistic prompts. Try edge cases. Watch the traces and sessions in the UI.

For a quick sanity check from the terminal:

```sh
curl -X POST http://localhost:8000/agents/<agent-id>/runs \
  -F "message=hello" \
  -F "user_id=me" \
  -F "stream=false"
```

## Step 4: Iterate

Two recursive loops for two different patterns:

1. [`docs/extend-agent.md`](docs/extend-agent.md). When you have a specific change in mind (new tool, tighter rule, better tone). You direct, Claude executes.
2. [`docs/improve-agent.md`](docs/improve-agent.md). When the agent feels off but you can't pinpoint why. Claude derives probes from the agent's `INSTRUCTIONS`, runs them against the live container, judges responses, and edits until it passes.

Both run in Claude Code against `http://localhost:8000` with hot-reload, so edits land in ~2 seconds. No rebuild, no restart.

Pick the loop that matches how the agent feels right now. Use both over time.

## Step 5: Lock in behavior with evals

The extend and improve loops are fast iteration. Evals are the regression suite that runs the same prompts against your agents on a schedule and tells you when behavior drifts.

The eval surface is two files: [`evals/cases.py`](evals/cases.py) (declarative cases) and [`evals/__main__.py`](evals/__main__.py) (runner). Evals use agno's built-in [`AgentAsJudgeEval`](https://docs.agno.com/evals/agent-as-judge?utm_source=github&utm_medium=example-repo&utm_campaign=agent-platform&utm_content=agent-platform&utm_term=railway) (LLM judge against a rubric, binary pass/fail) and/or [`ReliabilityEval`](https://docs.agno.com/evals/reliability?utm_source=github&utm_medium=example-repo&utm_campaign=agent-platform&utm_content=agent-platform&utm_term=railway) (tool-call assertion). No custom DSL, no separate harness. Agno primitives directly.

```bash
python -m evals                # run the suite (concise)
python -m evals -v             # stream the full agent run with rich panels
python -m evals --case <name>  # run one case
```

Results log to Postgres via `db=eval_db`. Connect your AgentOS at [os.agno.com](https://os.agno.com?utm_source=github&utm_medium=example-repo&utm_campaign=agent-platform&utm_content=agent-platform&utm_term=railway) to see eval history over time.

Run [`docs/eval-and-improve.md`](docs/eval-and-improve.md) in Claude Code to run the suite, diagnose failures, and fix in scope.

## Step 6: Run on Railway

Requires the [Railway CLI](https://docs.railway.com/cli#installing-the-cli) and `railway login`.

### 6.1 Set up your production env

```sh
cp .env .env.production
# Edit .env.production with production values
```

The deploy scripts read `.env.production` first and fall back to `.env`. This lets you keep separate values for local and production: different OpenAI keys, production-only credentials, a different Slack workspace. `.env.production` is gitignored.

### 6.2 Deploy

```sh
./scripts/railway/up.sh
```

This provisions Postgres and the app service on the same private network.

### 6.3 Your first deploy will fail by design

Token-Based Authorization is on by default. Without `JWT_VERIFICATION_KEY`, the app refuses to serve traffic. The platform's job is to keep your data off the public web, so the safe default is "refuse to start."

Token-Based Auth gives you three things:

1. **No public access.** The server rejects requests without a valid token.
2. **Per-request identity.** Middleware parses the token and injects `user_id`, `session_id`, and custom claims into your endpoints. Each request is tied to a user and session.
3. **Granular permissions.** User tokens can run an agent and view their own sessions. Admin tokens read everyone's sessions and test any agent.

### 6.4 Get your verification key

> **Heads up.** Live connections at os.agno.com are a paid feature. Use coupon code `PLATFORM30` for a one-month free trial. Cancel before the trial ends if you don't want to be charged.

1. Open [os.agno.com](https://os.agno.com?utm_source=github&utm_medium=example-repo&utm_campaign=agent-platform&utm_content=agent-platform&utm_term=railway), click **Add OS** → **Live**, enter your Railway domain, and connect.
2. Enable **Token Based Authorization**.
3. Paste the public key into `.env.production` (full PEM block, no surrounding quotes):

```sh
JWT_VERIFICATION_KEY=-----BEGIN PUBLIC KEY-----
MIIBIjANBgkq...
-----END PUBLIC KEY-----
```

### 6.5 Sync env and verify

While `.env.production` is open, point the in-cluster scheduler at your public Railway domain so cron triggers can reach AgentOS:

```sh
# .env.production
AGENTOS_URL=https://<your-app>.up.railway.app
```

Then push every variable to Railway:

```sh
./scripts/railway/env-sync.sh
```

Railway auto-deploys when env values change. Watch the logs and confirm the platform is serving:

```sh
railway logs --service agent-os
```

Once you see successful requests, AgentOS will connect through your Railway domain and you're live.

### 6.6 Redeploy after code changes

For one-off updates from your machine:

```sh
./scripts/railway/redeploy.sh
```

To auto-deploy on every push to `main`:

1. Open the Railway dashboard, your project, the agent-os service, **Settings**.
2. Under **Source**, click **Connect Repo** and pick your repo.
3. Set the deploy branch to `main` and save.

Push to `main` triggers a build and rolling deploy. `./scripts/railway/env-sync.sh` is still how you sync env changes.

### Opting out of JWT (not recommended)

Set `authorization=False` in [`app/main.py`](app/main.py) and redeploy. Use this only inside a private VPC behind another auth layer. Without it, anyone who guesses your Railway domain can read your sessions and run your agents.

### Scaling

The default deploy is two replicas at 4Gi memory and 2 vCPU each (zero-downtime rolling deploys plus basic fault tolerance). Bump `numReplicas` and `limits` in [`railway.json`](railway.json) as your usage grows.

## Extending the platform

### Multi-agent teams and workflows

For most things one agent is enough. When it isn't:

- **[Multi-agent teams](https://docs.agno.com/teams/overview?utm_source=github&utm_medium=example-repo&utm_campaign=agent-platform&utm_content=agent-platform&utm_term=railway).** Coordinate (a leader plans and synthesizes), route (a router picks the right specialist), or broadcast (run everyone in parallel). Use when the right specialist isn't known up front.
- **[Agentic workflows](https://docs.agno.com/workflows/overview?utm_source=github&utm_medium=example-repo&utm_campaign=agent-platform&utm_content=agent-platform&utm_term=railway).** Deterministic step-by-step pipelines. Use when a process needs to run the same way every time.

Rule of thumb: agents for open questions, teams for routing, workflows for processes.

### Scheduled tasks

`scheduler=True` is on in [`app/main.py`](app/main.py). Schedule any agent or workflow on a cron:

- **Maintenance.** Purge sessions older than 90 days. Vacuum tables.
- **Proactive runs.** Every weekday morning, summarize overnight news for your portfolio and send to Slack.
- **Periodic re-evaluation.** Wrap the eval suite as a scheduled workflow to catch behavior drift before users do.

See [agno scheduler docs](https://docs.agno.com/agent-os/scheduler?utm_source=github&utm_medium=example-repo&utm_campaign=agent-platform&utm_content=agent-platform&utm_term=railway) for the cron API.

### Interfaces

Agents land where work happens. Slack, Discord, Telegram, custom UIs in your product.

**Slack** is pre-wired. Set `SLACK_BOT_TOKEN` and `SLACK_SIGNING_SECRET` in your env and the interface lights up automatically. See [`app/main.py`](app/main.py):

```python
interfaces: list = []
if SLACK_BOT_TOKEN and SLACK_SIGNING_SECRET:
    from agno.os.interfaces.slack import Slack

    interfaces.append(
        Slack(
            agent=code_search,
            streaming=True,
            token=SLACK_BOT_TOKEN,
            signing_secret=SLACK_SIGNING_SECRET,
            resolve_user_identity=True,
        )
    )
```

Swap the `agent=` arg to route Slack to a different agent. For the Slack-side app setup, see the [agno Slack interface docs](https://docs.agno.com/agent-os/interfaces/overview?utm_source=github&utm_medium=example-repo&utm_campaign=agent-platform&utm_content=agent-platform&utm_term=railway).

For Discord, Telegram, WhatsApp, or a custom UI, mirror the same conditional with the relevant interface from agno. See the [agno interfaces guide](https://docs.agno.com/agent-os/interfaces/overview?utm_source=github&utm_medium=example-repo&utm_campaign=agent-platform&utm_content=agent-platform&utm_term=railway).

### Tools and MCP servers

The WebSearch agent in [`agents/web_search.py`](agents/web_search.py) shows the MCPTools pattern (URL plus transport). Copy it to wire any MCP server.

For built-in toolkits, agno ships 100+. A typical wire-up is three lines:

```python
from agno.tools.linear import LinearTools

linear_agent = Agent(
    id="linear",
    model=default_model(),
    tools=[LinearTools()],
    instructions="You triage issues in Linear.",
    db=get_postgres_db(),
)
```

See [agno tools](https://docs.agno.com/tools/toolkits?utm_source=github&utm_medium=example-repo&utm_campaign=agent-platform&utm_content=agent-platform&utm_term=railway) for the full catalog.

## Environment variables

`compose.yaml` sets the dev defaults (`RUNTIME_ENV=dev`, `AGNO_DEBUG=True`, `WAIT_FOR_DB=True`) so local Docker runs hot-reload and skips JWT. Production reads everything from `.env.production` via `./scripts/railway/env-sync.sh`.

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | yes | none | OpenAI key for models and embeddings. |
| `RUNTIME_ENV` | no | `prd` | `dev` enables hot-reload and disables JWT. Compose sets this to `dev` for local. |
| `JWT_VERIFICATION_KEY` | prd | none | Public key from os.agno.com. Required when `RUNTIME_ENV=prd`. |
| `AGENTOS_URL` | no | `http://127.0.0.1:8000` | Scheduler base URL. Set to your Railway domain in production. |
| `PARALLEL_API_KEY` | no | none | Authenticates the WebSearch Agent's Parallel SDK / MCP connection. |
| `SLACK_BOT_TOKEN` / `SLACK_SIGNING_SECRET` | no | none | Both must be set to enable the Slack interface. |
| `DB_HOST` / `DB_PORT` / `DB_USER` / `DB_PASS` / `DB_DATABASE` | no | matches compose | Postgres connection. |
| `DB_DRIVER` | no | `postgresql+psycopg` | SQLAlchemy driver. |
| `PORT` | no | `8000` | API server port. |
| `AGNO_DEBUG` | no | `False` | If `True`, agno emits verbose debug logs. Compose sets this for dev. |
| `WAIT_FOR_DB` | no | `False` | If `True`, the entrypoint blocks on the DB before starting. Compose sets this. |

## Learn more

- [Agno documentation](https://docs.agno.com?utm_source=github&utm_medium=example-repo&utm_campaign=agent-platform&utm_content=agent-platform&utm_term=railway)
- [AgentOS introduction](https://docs.agno.com/agent-os/introduction?utm_source=github&utm_medium=example-repo&utm_campaign=agent-platform&utm_content=agent-platform&utm_term=railway)
- [Agno on GitHub](https://github.com/agno-agi/agno). Drop a star if this is useful.
