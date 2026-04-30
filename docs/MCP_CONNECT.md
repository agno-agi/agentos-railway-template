# Connecting MCP Servers

AgentOS can connect to any [Model Context Protocol](https://modelcontextprotocol.io) server. Each server exposes tools that your agent can use.

## Why MCP?

- **No custom code** — any MCP server works out of the box
- **Tool discovery** — tools are discovered from the server at connect time
- **Graceful degradation** — a crashed server doesn't take down your agent

## Quick Start: Web Search

The starter template uses Parallel MCP for web search. It's free and requires no API key:

```python
from agno.context.web.parallel_mcp import ParallelMCPBackend
from agno.context.web.provider import WebContextProvider

web_context = WebContextProvider(
    backend=ParallelMCPBackend(),  # Free at search.parallel.ai/mcp
    model=your_model,
)

agent = Agent(
    tools=web_context.get_tools,
    # ...
)
```

## Adding Other MCP Servers

Use `MCPContextProvider` to add any MCP server:

### stdio (local subprocess)

```python
from agno.context.mcp import MCPContextProvider

linear_context = MCPContextProvider(
    server_name="linear",
    transport="stdio",
    command="npx",
    args=["-y", "@linear/mcp"],
    env={"LINEAR_API_KEY": getenv("LINEAR_API_KEY", "")},
    model=your_model,
)
```

### streamable-http (hosted)

```python
github_context = MCPContextProvider(
    server_name="github",
    transport="streamable-http",
    url="https://mcp.github.com/mcp",
    headers={"Authorization": f"Bearer {getenv('GITHUB_TOKEN', '')}"},
    model=your_model,
)
```

### sse

```python
notion_context = MCPContextProvider(
    server_name="notion",
    transport="sse",
    url="https://mcp.notion.so/sse",
    model=your_model,
)
```

## Context Modes

Control how tools are exposed to your agent:

### Default (agent mode)

Wraps tools behind a sub-agent. Your agent sees one `query_<server_name>` tool:

```python
MCPContextProvider(
    server_name="linear",
    mode=ContextMode.default,  # or omit — this is the default
    # ...
)
```

**Use when:** Server has many tools, cryptic names, or names that collide with other servers.

### Tools mode

Flattens tools directly onto your agent:

```python
from agno.context.mode import ContextMode

MCPContextProvider(
    server_name="time",
    mode=ContextMode.tools,
    # ...
)
```

**Use when:** Server has few, distinctively-named tools (cheaper, no sub-agent overhead).

## Constructor Parameters

| Parameter | Required | Description |
|---|---|---|
| `server_name` | yes | Derives `id=mcp_<server_name>` and tool names |
| `transport` | yes | `"stdio"`, `"sse"`, or `"streamable-http"` |
| `command` | stdio | Executable (`npx`, `uvx`, `python`, ...) |
| `args` | stdio (optional) | CLI args as a list |
| `env` | stdio (optional) | Env vars for the subprocess |
| `url` | sse / streamable-http | Server URL |
| `headers` | sse / streamable-http (optional) | HTTP headers dict |
| `timeout_seconds` | optional | Connect + read timeout (default 30) |
| `mode` | optional | `ContextMode.default` or `ContextMode.tools` |

## stdio Executables

`command` must be on `PATH` inside the runtime. The Docker image includes Python tooling (`uv`, `uvx`, `python`).

**Node-based servers** (`npx @something/mcp`) need Node installed. Add to your Dockerfile:

```dockerfile
RUN apt-get update && apt-get install -y nodejs npm
```

## Debugging

Check if the MCP server connected:

```bash
curl -sS http://localhost:8000/contexts | jq '.[] | select(.id | startswith("mcp_"))'
```

Expected output:
```json
{ "id": "mcp_linear", "name": "linear", "ok": true, "detail": "mcp: linear (12 tools)" }
```

If `ok: false`, check:
- **stdio**: Is `command` on `PATH` inside the container?
- **HTTP**: Is the URL reachable? Are headers correct?
