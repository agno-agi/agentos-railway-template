"""
Web Agent (Context Mode: Agent)
-------------------------------

Searches the web using Parallel MCP via a WebContextProvider in default
(agent) mode. The context provider wraps the MCP tools behind a sub-agent,
so the main agent sees a single `query_web` tool.

This pattern isolates tool complexity: the sub-agent handles pagination,
retries, and Parallel-specific quirks. The main agent stays focused on
user intent.

No API key required — Parallel MCP is free at search.parallel.ai/mcp.

Run:
    python -m agents.web_agent
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
    mode=ContextMode.agent,
    model=OpenAIResponses(id="gpt-5.2"),
)

# ---------------------------------------------------------------------------
# Agent Instructions
# ---------------------------------------------------------------------------
instructions = """\
You are a web research assistant. You search the web to find current information.

## How You Work

1. Use `query_web` to search for information
2. Synthesize results into a clear answer
3. Cite your sources with URLs

## Guidelines

- Be direct and concise
- Prefer recent, authoritative sources
- If you can't find what the user needs, say so and suggest alternatives
"""

# ---------------------------------------------------------------------------
# Create Agent
# ---------------------------------------------------------------------------
web_agent = Agent(
    id="web-agent",
    name="Web Agent",
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
    web_agent.print_response("What are the latest developments in AI agents?", stream=True)
