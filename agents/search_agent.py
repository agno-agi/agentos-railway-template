"""
Search Agent
------------

Web search using context provider in agent mode.

Run:
    python -m agents.search_agent
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
    model=OpenAIResponses(id="gpt-5.5"),
)

# ---------------------------------------------------------------------------
# Agent Instructions
# ---------------------------------------------------------------------------
instructions = """\
You are a web search assistant. Search the web for current information.

Be direct and concise. Prefer recent, authoritative sources.
If you can't find what the user needs, say so.
"""

# ---------------------------------------------------------------------------
# Create Agent
# ---------------------------------------------------------------------------
search_agent = Agent(
    id="search-agent",
    name="Search Agent",
    model=OpenAIResponses(id="gpt-5.5"),
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
    search_agent.print_response("What are the latest developments in AI agents?", stream=True)
