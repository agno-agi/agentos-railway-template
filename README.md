# AgentOS on Railway

An agent platform you build, improve, and run using coding agents.

The platform runs in your cloud, behind your auth, with all your data stored in your database. Because trace data, agent code, system logs, and the iteration tool all live in one place, coding agents like Claude Code can read, update, and improve the platform end-to-end.

## Built for coding agents

This codebase is designed primarily for coding agents. It comes with five prompts that cover the full agent development lifecycle:

1. **Create.** Claude asks a few questions, scaffolds the agent file, registers it in `app/main.py`, adds quick prompts to `app/config.yaml`, restarts the container, and smoke-tests via cURL. Usually 5-10 minutes for a simple agent.
2. **Improve.** Hardens and fine-tunes your agent based on its existing spec. Claude derives probes from the agent's `INSTRUCTIONS`, runs them against the live container, judges the responses, and edits until they pass. No input from you.
3. **Extend.** Add a new feature to an agent. You direct, Claude executes. Add tools, refine prompts, fix bugs. The Agno docs MCP is loaded so toolkit research is grounded in the real API.
4. **Hill Climb.** Claude runs the eval suite, diagnoses failures, and fixes what's in scope. Stops when all cases pass.
5. **Review.** Claude sweeps the repo for drift between docs, code, and config. Auto-fixes mechanical drift like stale paths and missing env vars; flags anything bigger.

3 of 5 run autonomously with no input needed from you.

## Own the stack

The auto-improvement loop is possible because we own the full stack. From start to end:

1. **Runtime.** The server that runs your agents. FastAPI running Agno AgentOS (see `app/main.py`).
2. **Storage.** Sessions, memory, knowledge, and traces all stored in PostgreSQL + pgvector.
3. **Connectors.** Hundreds of toolkits and MCP servers available via Agno to connect agents to external tools.
4. **Interfaces.** Expose agents in Slack, Discord, Telegram. Slack is already wired (see `app/main.py`). Discord, Telegram, and custom UIs can be added using [Agno interfaces](https://docs.agno.com/agent-os/interfaces/overview?utm_source=github&utm_medium=example-repo&utm_campaign=agent-platform&utm_content=agent-platform&utm_term=railway).
5. **Infrastructure.** Docker locally, Railway in production.

## Get Started

### Step 1: Run locally

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

### Step 2: Create your first agent

Open [Claude Code](https://claude.ai/code) in this repo and paste:

```
Run docs/create-new-agent.md in a new branch
```

Claude asks a few questions, generates the agent file in `agents/`, registers it in `app/main.py`, adds prompts to `app/config.yaml`, restarts the container, and smoke-tests via cURL. The container restart is needed because uvicorn's reloader doesn't reliably pick up newly-registered modules. Usually 5-10 minutes for a simple agent.

Two reference agents ship in the template for you to study and copy from:

| Agent | Pattern | Tools |
|---|---|---|
| WebSearch | Direct tools | `parallel_search` / `parallel_extract` (needs `PARALLEL_API_KEY`); `web_search` / `web_fetch` keyless |
| CodeSearch | Context provider sub-agent | `query_my_codebase` |

**Direct tools**: the agent sees each tool individually. **Context provider**: the agent sees one `query_<thing>` tool that hands off to a sub-agent. Two patterns to copy from when you build your own.

### Step 3: Chat with your agent

Chat with your agents at [os.agno.com](https://os.agno.com?utm_source=github&utm_medium=example-repo&utm_campaign=agent-platform&utm_content=agent-platform&utm_term=railway). Run realistic prompts. Try edge cases. Watch the traces and sessions in the UI.

For a quick sanity check from the terminal:

```sh
curl -X POST http://localhost:8000/agents/<agent-id>/runs \
  -F "message=hello" \
  -F "user_id=me" \
  -F "stream=false"
```

### Step 4: Improve your agent

To improve your agents, use one of these recursive loops:

1. [`docs/improve-agent.md`](docs/improve-agent.md). Hardens and fine-tunes your agent based on its existing spec. Claude derives probes from the agent's `INSTRUCTIONS`, runs them against the live container, judges responses, and edits until it passes.

2. [`docs/extend-agent.md`](docs/extend-agent.md). Add a new feature to an agent. You direct, Claude executes. Add tools, refine prompts, fix bugs. The Agno docs MCP is loaded so toolkit research is grounded in the real API.

Both run in Claude Code against `http://localhost:8000` with hot-reload.

### Step 5: Lock in behavior with evals

The extend and improve loops are great for improving the agents. Evals are the regression suite that makes sure your agent continues to perform as designed.

The eval surface is two files: [`evals/cases.py`](evals/cases.py) (declarative cases) and [`evals/__main__.py`](evals/__main__.py) (runner). Evals use Agno's built-in [`AgentAsJudgeEval`](https://docs.agno.com/evals/agent-as-judge?utm_source=github&utm_medium=example-repo&utm_campaign=agent-platform&utm_content=agent-platform&utm_term=railway) (LLM judge against a rubric, binary pass/fail) and/or [`ReliabilityEval`](https://docs.agno.com/evals/reliability?utm_source=github&utm_medium=example-repo&utm_campaign=agent-platform&utm_content=agent-platform&utm_term=railway) (tool-call assertion).

```bash
python -m evals                # run the suite (concise)
python -m evals -v             # stream the full agent run with rich panels
python -m evals --case <name>  # run one case
```

Results log to Postgres via `db=eval_db`. Connect your AgentOS at [os.agno.com](https://os.agno.com?utm_source=github&utm_medium=example-repo&utm_campaign=agent-platform&utm_content=agent-platform&utm_term=railway) to see eval history over time.

Run [`docs/eval-and-improve.md`](docs/eval-and-improve.md) in Claude Code to run the suite, diagnose failures, and fix in scope.

## Run in production

You can run the platform anywhere that supports containerized images.

For the lightest lift, the codebase comes with one-command-deploy scripts to run the platform on Railway.

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

See [Agno scheduler docs](https://docs.agno.com/agent-os/scheduler?utm_source=github&utm_medium=example-repo&utm_campaign=agent-platform&utm_content=agent-platform&utm_term=railway) for the cron API.

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

Swap the `agent=` arg to route Slack to a different agent. For the Slack-side app setup, see the [Agno Slack interface docs](https://docs.agno.com/agent-os/interfaces/overview?utm_source=github&utm_medium=example-repo&utm_campaign=agent-platform&utm_content=agent-platform&utm_term=railway).

For Discord, Telegram, WhatsApp, or a custom UI, mirror the same conditional with the relevant interface from Agno. See the [Agno interfaces guide](https://docs.agno.com/agent-os/interfaces/overview?utm_source=github&utm_medium=example-repo&utm_campaign=agent-platform&utm_content=agent-platform&utm_term=railway).

### Tools and MCP servers

The WebSearch agent in [`agents/web_search.py`](agents/web_search.py) shows the MCPTools pattern (URL plus transport). Copy it to wire any MCP server.

For built-in toolkits, Agno ships 100+. A typical wire-up is three lines:

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

See [Agno tools](https://docs.agno.com/tools/toolkits?utm_source=github&utm_medium=example-repo&utm_campaign=agent-platform&utm_content=agent-platform&utm_term=railway) for the full catalog.

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
| `AGNO_DEBUG` | no | `False` | If `True`, Agno emits verbose debug logs. Compose sets this for dev. |
| `WAIT_FOR_DB` | no | `False` | If `True`, the entrypoint blocks on the DB before starting. Compose sets this. |

## Learn more

- [Agno documentation](https://docs.agno.com?utm_source=github&utm_medium=example-repo&utm_campaign=agent-platform&utm_content=agent-platform&utm_term=railway)
- [AgentOS introduction](https://docs.agno.com/agent-os/introduction?utm_source=github&utm_medium=example-repo&utm_campaign=agent-platform&utm_content=agent-platform&utm_term=railway)
- [Agno on GitHub](https://github.com/agno-agi/agno). Drop a star if this is useful.