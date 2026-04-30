"""
Research Agent
--------------

Web research using context provider in tools mode.

Run:
    python -m agents.research_agent
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
research_agent = Agent(
    id="research-agent",
    name="Research Agent",
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
    research_agent.print_response("Search for recent news about OpenAI", stream=True)
