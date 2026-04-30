"""
Web Tools Agent (Context Mode: Tools)
-------------------------------------

Searches the web using Parallel MCP via a WebContextProvider in tools
mode. Unlike the default agent mode, tools mode flattens the MCP tools
(`web_search`, `web_fetch`) directly onto this agent.

Use this pattern when:
- You want fewer LLM hops (no sub-agent overhead)
- The tools have distinct, non-colliding names
- You want fine-grained control over tool orchestration

No API key required — Parallel MCP is free at search.parallel.ai/mcp.

Run:
    python -m agents.web_tools_agent
"""

from agno.agent import Agent
from agno.context.mode import ContextMode
from agno.context.web.parallel_mcp import ParallelMCPBackend
from agno.context.web.provider import WebContextProvider
from agno.models.openai import OpenAIResponses

from db import get_postgres_db

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------
agent_db = get_postgres_db()

web_context = WebContextProvider(
    backend=ParallelMCPBackend(),
    mode=ContextMode.tools,
    model=OpenAIResponses(id="gpt-5.2"),
)

# ---------------------------------------------------------------------------
# Agent Instructions
# ---------------------------------------------------------------------------
instructions = """\
You are a web research assistant with direct access to web tools.

## Your Tools

- `web_search`: Search the web for information
- `web_fetch`: Fetch and read the contents of a URL

## How You Work

1. Use `web_search` to find relevant URLs
2. Use `web_fetch` to read page contents when needed
3. Synthesize results into a clear answer
4. Cite your sources with URLs

## Guidelines

- Be direct and concise
- Search first, then fetch specific pages for details
- Prefer recent, authoritative sources
- If you can't find what the user needs, say so
"""

# ---------------------------------------------------------------------------
# Create Agent
# ---------------------------------------------------------------------------
web_tools_agent = Agent(
    id="web-tools-agent",
    name="Web Tools Agent",
    model=OpenAIResponses(id="gpt-5.2"),
    db=agent_db,
    tools=web_context.get_tools(),
    instructions=web_context.instructions() + "\n\n" + instructions,
    enable_agentic_memory=True,
    add_datetime_to_context=True,
    add_history_to_context=True,
    read_chat_history=True,
    num_history_runs=5,
    markdown=True,
)

if __name__ == "__main__":
    web_tools_agent.print_response("Search for recent news about OpenAI", stream=True)
