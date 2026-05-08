# Create a New Agent

> Claude Code prompt. Open Claude Code in this repo and paste:
> `Run docs/create-new-agent.md`

You are creating a new agent in this AgentOS template. The user already has the platform running locally on `http://localhost:8000` (`RUNTIME_ENV=dev`). Uvicorn hot-reloads on edits inside an existing module, but **registering a new agent module requires a container restart** — see Step 6.

## 0. Preconditions

- Live container reachable: `curl -sSf http://localhost:8000/health` returns 200. (`docker compose ps` is unreliable from worktrees or alternate clones — trust the health probe.)

If it isn't reachable, ask the user to run `docker compose up -d --build` and wait for it to come up.

## 1. Ask the user

**Ask via the `AskUserQuestion` tool** for every choice-shaped prompt below — the branching opener, the role pick, the systems multiselect, the agent-idea suggestions, and the **Pattern** pick. It renders click-to-select buttons, much smoother than parsing free-text replies. Use plain prompts only for free-form fields (the recurring-task description, the slug).

Open with a single branching question — don't dump five questions at once:

> Do you have an agent in mind, or would you like a guided experience?

If the user immediately describes a concrete agent ("build me a GitHub PR reviewer"), they've picked the second branch — skip to **Specifics**.

### Guided experience

Ask three light discovery questions in one message:

- What's your role? (engineer, PM, founder, analyst, ops, …)
- What's a recurring task that takes you real time?
- Which systems do you live in day-to-day? (Slack, GitHub, Linear, Notion, your own DB, …)

Use the answers + the `agno-docs` MCP (configured in [`.mcp.json`](../.mcp.json)) to surface **3-5 concrete agent ideas** grounded in real agno toolkits. For each suggestion: a short name, a one-sentence purpose, and the toolkit(s) it would use.

Common starting points: GitHub PR reviewer, Linear triager, knowledge-base Q&A over a `docs/` folder, Slack on-call digest, market-scan / web research.

Once the user picks one, you have name, purpose, and tools settled — only ask for what's still unknown under **Specifics**.

### Specifics

If the user came in with a concrete agent in mind, ask all five below in one consolidated message. If they came through the guided path, only items 2, 4, and 5 are still unknown — the rest are settled. Don't re-ask.

1. **Name and purpose** — what should this agent do? One sentence.
2. **Pattern** — propose the right one with a heuristic, don't make the user choose blind:
   - **Direct tools** (like [`agents/web_search.py`](../agents/web_search.py)): default when the agent uses ≤2 toolkits, or the user explicitly named the tools.
   - **Context provider** (like [`agents/code_search.py`](../agents/code_search.py)): default when the agent queries a single information source through one `query_<thing>` tool, or you're hiding a sub-agent.
3. **Tools / sources** — which MCP servers, toolkits, or context providers? URL of the MCP server if any. (Default: nothing — just chat.)
4. **Required env vars** — for each toolkit chosen, identify the API key(s) it needs (from the toolkit's `Prerequisites` section in agno docs — see Step 2). For each required key, confirm the user has it set in `.env`. If they don't, offer:
   - (a) add it to `.env` now,
   - (b) drop that toolkit and pick something keyless (HackerNews, ArXiv, Wikipedia, DuckDuckGo via WebSearchTools),
   - (c) build anyway and surface the auth error during smoke test.
5. **Slug** — short kebab-case id (e.g. `linear-agent`). Used as the agent's `id`, in URLs, and in `app/config.yaml`. Propose one based on the agent's purpose.

Model defaults to `gpt-5.4` via `app.settings.default_model()` — override only if the user asks.

## 2. Ground the design in agno docs

If the user named any specific toolkit, MCP server, or integration the agent should use (Linear, Stripe, GitHub, Anthropic Claude, etc.), search agno docs **before** writing code:

- Preferred: the `agno-docs` MCP server (configured in [`.mcp.json`](../.mcp.json)) — search for the toolkit / integration name and read the relevant page(s).
- Fallback: fetch <https://docs.agno.com/llms.txt> and search inline for the relevant sections.

For each toolkit, capture four things:

- **Import path** (e.g. `from agno.tools.exa import ExaTools`).
- **Constructor args** that matter for this agent (categories, domains, max_results, etc.).
- **Required env vars** — feed these back into Step 1, item 4.
- **Pip dependencies** — some toolkits need extra packages (`exa-py`, `anthropic`, `firecrawl-py`, `linear-sdk`, …). The toolkit's `Prerequisites` section lists them. Capture now, install in Step 6.

If the toolkit's docs page has no `Prerequisites` or `Authentication` section, the toolkit is keyless and needs no env vars or extra pip deps (e.g. HackerNews, ArXiv, Wikipedia, DuckDuckGo).

Don't guess any of the four. Skip this step entirely if the agent is chat-only with no tools.

## 3. Generate the agent file

Create `agents/<slug>.py` (replacing `-` with `_` for the filename: `agents/linear_agent.py`). Follow the pattern of one of the two reference agents:

- **Direct tools** → mirror [`agents/web_search.py`](../agents/web_search.py).
- **Context provider** → mirror [`agents/code_search.py`](../agents/code_search.py).

Required structure:

```python
"""
<Title>
=======
"""

from agno.agent import Agent

from app.settings import default_model
from db import get_postgres_db

INSTRUCTIONS = """\
<one short paragraph describing the agent's job, tools, and the rules
it should follow when answering>
"""

<slug_underscore> = Agent(
    id="<slug>",
    name="<DisplayName>",
    model=default_model(),
    db=get_postgres_db(),
    tools=[...],                     # or context_provider.get_tools()
    instructions=INSTRUCTIONS,
    enable_agentic_memory=True,
    add_datetime_to_context=True,
    add_history_to_context=True,
    num_history_runs=5,
    markdown=True,
)
```

Notes:

- Don't add a `if __name__ == "__main__":` smoke block — the platform-driven workflow is the smoke test.
- If the agent uses an `MCPTools` instance, pass it through `tools=[mcp_tools]` directly. AgentOS connects/closes MCP servers automatically — don't manage the lifecycle yourself.
- If a context provider needs a model, reuse `default_model()` so the model id stays in one place.

## 4. Register in `app/main.py`

Add the import and append to the `agents=[…]` list:

```python
from agents.<slug_underscore> import <slug_underscore>

agent_os = AgentOS(
    ...
    agents=[web_search, code_search, <slug_underscore>],
    ...
)
```

## 5. Quick prompts

Add three suggested prompts to [`app/config.yaml`](../app/config.yaml) under `chat.quick_prompts`, keyed by the agent's `id`:

```yaml
chat:
  quick_prompts:
    <slug>:
      - "First example prompt"
      - "Second example prompt"
      - "Third example prompt"
```

## 6. Reload the container

After Step 4, **always restart the container** — uvicorn's hot-reload doesn't reliably pick up newly registered modules.

- **No new pip deps** (the common case):

  ```bash
  docker compose restart agentos-api
  ```

- **New pip deps added in Step 2** — update the lockfile and rebuild:

  ```bash
  ./scripts/generate_requirements.sh
  docker compose up -d --build
  ```

Then verify the agent shows up in the registry before smoke-testing:

```bash
curl -s http://localhost:8000/agents | jq -r '.[].id' | grep <slug>
```

If `<slug>` isn't in the list, the restart didn't pick up your edits — jump to Step 8.

## 7. Smoke test

Poll `/health` until the API is back up, then probe the agent with **one of the quick prompts you wrote in Step 5** (so the smoke test exercises what real users will hit). Substitute `<slug>` and the `message=` value before running:

```bash
until curl -sSf http://localhost:8000/health > /dev/null; do sleep 0.5; done

curl -sS -X POST http://localhost:8000/agents/<slug>/runs \
  -F "message=<one of the quick_prompts you just wrote>" \
  -F "user_id=claude-create-agent" \
  -F "stream=false" \
  -o /tmp/agent-out.json \
  -w "HTTP %{http_code} in %{time_total}s\n"

jq -r '.content // .' < /tmp/agent-out.json
```

Pass = `HTTP 200` and a non-empty `.content` field.

Check the container logs to see which tools fired:

```bash
docker logs agentos-api --since 30s 2>&1 | grep -E "Running: \w+\(" | head -40
```

(`Running: <tool>(` is the line shape agno emits per tool call when `AGNO_DEBUG=True`, which compose sets for dev. Without `AGNO_DEBUG`, expect no matches — `HTTP 200` and a non-empty body are then your only signal.)

## 8. If the smoke test fails

- **HTTP 404** — the agent isn't registered, the container wasn't restarted, or your edits aren't reaching the bind-mount. Re-check Step 4 and Step 6. If both look right, run `docker inspect agentos-api --format '{{ range .Mounts }}{{ .Source }} → {{ .Destination }}{{ "\n" }}{{ end }}'` to confirm `/app` is bound to *this* repo's path (a stale clone or a different worktree is a common cause).
- **HTTP 5xx** — read `docker logs agentos-api --tail 50` for the traceback. Most failures are import errors, missing env vars, or a typo in the agent's `tools=` list.
- **Empty response** — check the logs for tool call errors (rate limits, missing API keys, MCP server unreachable). Surface the issue to the user; don't paper over it.
- **Tool not firing when expected** — the instruction prompt isn't strong enough. Tell the user; suggest tightening or running [`docs/improve-agent.md`](improve-agent.md) once the agent is loaded.

Iterate at most 2-3 times on the prompt before stopping and surfacing the question to the user.

## 9. Done

When the smoke test passes:

1. Tell the user the agent's slug. They can chat with it at `https://os.agno.com` (if their OS is connected there) or against `http://localhost:8000` directly for local-only.
2. Suggest the next-step loops:
   - [`docs/extend-agent.md`](extend-agent.md) — user-driven changes (add a tool, refine the prompt, fix a bug).
   - [`docs/improve-agent.md`](improve-agent.md) — autonomous probe-and-harden against the agent's `INSTRUCTIONS`.

A simple agent usually takes 5-10 minutes from "Run docs/create-new-agent.md" to working. More if the user asks for custom tools or an MCP server with auth.
