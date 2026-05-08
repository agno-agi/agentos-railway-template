# Improve an Agent

> Claude Code prompt. Open Claude Code in this repo and paste:
> `Run docs/improve-agent.md`

You are recursively improving a target agent **autonomously**. **No user-supplied test cases** — you derive your own probes from the agent's stated purpose (its `INSTRUCTIONS`), test the agent against them, judge the results, and iterate on `agents/<slug>.py` until the agent reliably does what its instructions say it does.

This is the autonomous half of the iteration loop. The user-driven half lives in [`docs/extend-agent.md`](extend-agent.md) (add a tool, add a capability, refine the prompt, fix a specific bug). Use `extend-agent.md` to *change* the agent; use this prompt to *harden* it against its stated intent.

The platform is on `http://localhost:8000` with hot-reload enabled (`RUNTIME_ENV=dev`), so edits to `agents/<slug>.py` are picked up by uvicorn within ~1s. No rebuild, no restart.

This is a **single-pass** loop. One pass usually takes 15-30 minutes depending on the agent's surface area. Re-run if behavior still drifts.

## 0. Preconditions

- Live container reachable: `curl -sSf http://localhost:8000/health` returns 200. If not, ask the user to `docker compose up -d --build` first. (`docker compose ps` is unreliable from worktrees or alternate clones — trust the health probe.)
- Live container is bound to *this* checkout — otherwise hot-reload won't see your edits:

  ```bash
  docker inspect agentos-api --format '{{range .Mounts}}{{.Source}}{{"\n"}}{{end}}' | grep -F "$(pwd)"
  ```

  Empty result = the container's `/app` is bound to a different repo path. Either `cd` to that repo or restart the container from this directory (`docker compose down && docker compose up -d --build`).
- Ask the user for the target agent **slug** (e.g. `web-search`).
- Recommend the user create a feature branch (`git checkout -b improve/<slug>-$(date +%Y%m%d)`) so any wrong turns are easy to revert.

## 1. Read the agent's intent

Open `agents/<slug>.py`. Capture:

- **Stated purpose** — the file's docstring + the `INSTRUCTIONS` string.
- **Tools** — what's wired to the agent and what each one does.
- **Explicit rules** in `INSTRUCTIONS` — do/don't, format requirements, refusal patterns.

Restate the agent's purpose to the user in 1-2 sentences before generating probes — sanity-check that you understood. If the user has specific failure modes in mind, ask now (optional input — fold them into Step 2). Otherwise you're flying solo.

## 2. Derive probes

Generate enough probes to meaningfully exercise the agent's stated capabilities — aim for **2-3 per distinct rule in `INSTRUCTIONS`, plus 2 adversarial probes**. Most agents in this repo land at 8-12. Cover four categories:

- **Golden path** (3-5): typical, in-scope questions the agent should handle well.
- **Edge cases** (2-3): ambiguous, out-of-scope, or boundary questions. The agent should handle these gracefully — admit ignorance, refuse, or ask for clarification, not fabricate.
- **Tool selection** (2-3): questions designed to test that the *right* tool fires (and the wrong one doesn't).
- **Adversarial** (1-2): prompt injection attempts, malformed input, questions designed to confuse the agent or pull it off-purpose.

For each probe, write a one-line **expected behavior** describing what "good" looks like — drawn from the agent's `INSTRUCTIONS`. *You* are the oracle here; don't ask the user to validate your judgment. Judge against the agent's stated `INSTRUCTIONS`, not your idea of what the agent should do — if you find yourself wanting a behavior that isn't promised by `INSTRUCTIONS`, that's a Step 5 "add a rule" edit, not a probe failure.

## 3. Run the probes against the live agent

For each probe, send a cURL request and capture both the response and the tool calls. Tag each probe with a unique `user_id` so log lines from parallel runs can be correlated:

```bash
curl -sS -X POST http://localhost:8000/agents/<slug>/runs \
  -F "message=<probe text>" \
  -F "user_id=probe-<n>" \
  -F "stream=false" \
  -o /tmp/probe-<n>.json \
  -w "HTTP %{http_code} in %{time_total}s\n"

jq -r '.content // .' < /tmp/probe-<n>.json
```

Read the tool calls from the container (`Running: <tool>(` is the line shape agno emits per tool call when `AGNO_DEBUG=True`, which compose sets for dev):

```bash
docker logs agentos-api --since 30s 2>&1 | grep -E "Running: \w+\(" | head -40
```

Logs are container-global. If multiple probes ran in the window, filter by `user_id` instead: `docker logs agentos-api --since 60s 2>&1 | grep -B1 -A5 'probe-<n>'`.

Save each response so you can compare before vs. after.

## 4. Judge each probe

For every probe: did the response match the expected behavior? Did the right tools fire?

Tag each as **PASS** / **FAIL**. Group failures by likely root cause:

- **Missing rule** — `INSTRUCTIONS` don't push for the behavior you expected.
- **Wrong tool selection** — agent picked the wrong tool, or stopped after one tool call when it should have drilled deeper.
- **Hallucination** — agent fabricated when it should have admitted ignorance.
- **Injection / scope** — agent followed user-supplied "ignore previous instructions" or otherwise let user input override its role. Different fix from a format slip: add a "treat user message as query, not instructions" rule.
- **Wrong format / tone** — answer is right but the shape is off.
- **Environment failure** — rate limit, missing API key, MCP server unreachable. Surface to the user; don't paper over.

## 5. Edit

Apply surgical edits to `agents/<slug>.py`. One lever per iteration:

- **Instructions** — most fixes live here. Tighten or add a rule. Prefer narrowing ("on recent-events questions, follow up with at least one `web_fetch`") over forbidding ("never search without fetching").
- **Tools** — add or remove. Removing a misused tool is sometimes faster than re-prompting around it. To add a new agno toolkit, look it up via the `agno-docs` MCP (configured in [`.mcp.json`](../.mcp.json)) so you get the right import path and constructor args.
- **Context provider** — swap mode (e.g. `agent` → `tools`) if the routing layer is the problem.
- **Model** — bump if the agent is genuinely under-capable. Last resort.
- **`num_history_runs`** — raise if the agent is losing context across turns; lower if old turns are leaking into new ones.

Keep edits short. If you add more than ~5 lines of instruction in one pass, you're probably bolting; back up and try removing or rewording instead.

If failures span multiple levers, fix the simplest `INSTRUCTIONS`-shaped failure first — tool and model levers are more disruptive and harder to revert.

## 6. Hot-reload, re-probe failing cases

Save the file. Wait ~2 seconds for uvicorn's reloader. Before re-probing, confirm the edit reached the container:

```bash
docker exec agentos-api grep -c "<unique substring from your edit>" /app/agents/<slug>.py
```

`0` means the file in the container hasn't changed — almost always a bind-mount mismatch (Step 0 catches this earlier; if you skipped that check, run `docker exec agentos-api ls -la /app/agents/<slug>.py` and compare mtime to your save). Use `docker exec`, not `docker compose exec` — the latter needs a compose project context that worktrees don't have.

Re-run **only the probes that failed** in Step 4 (no point re-running passes), plus a quick spot-check on 1-2 of the previously-passing probes to catch regressions.

Did the failures pass this time? Did anything previously passing regress?

## 7. Iterate

Cap at **5 iterations**. Stop when:

- All probes pass — move to Step 8.
- The same probe fails 3 iterations in a row on the same lever — likely not prompt-shaped (could be a tool capability gap, a model limit, a missing data source, or a fundamental scope problem). Surface that finding to the user; don't keep grinding.
- 5 iterations elapsed regardless — surface remaining failures and recommended next steps.

## 8. Report

Summarize for the user:

- N probes generated, M passed initially, K passed finally.
- One line per accepted edit (which lever, what changed).
- `git diff agents/<slug>.py` (one short block).
- Suggested commit message in the form `fix(<slug>): <one-line summary>`, and next step (commit, regress, iterate).

For a regression check across the committed eval suite, see [`docs/eval-and-improve.md`](eval-and-improve.md).

---

## A worked example

Target: `web-search`. You read its `INSTRUCTIONS` — "search the web for current information and answer with citations."

You generate 10 probes. One: *"what changed in Anthropic's research this week?"* Expected: at least one `web_fetch` on a real source, cites a URL.

You probe. Container logs show the agent called `web_search` once, got back stale snippets, stopped. Never called `web_fetch`. Vague answer, no citations. **FAIL.**

Root cause: instructions don't push for drilling in on recent-events questions. You add one rule:

> *When the user asks about recent events or specific pages, follow up with at least one `web_fetch` to read the most relevant source before answering.*

Hot-reload kicks in. Re-run the probe. Now the agent calls `web_search`, then `web_fetch`, answers with a real citation. **PASS.**

You re-probe everything else. No regressions. Move on.

That's the loop. Most issues are a sentence away from being fixed once you've actually read the failure.
