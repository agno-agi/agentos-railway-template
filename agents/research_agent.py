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
    model=OpenAIResponses(id="gpt-5.5"),
)

# ---------------------------------------------------------------------------
# Agent Instructions
# ---------------------------------------------------------------------------
instructions = """\
You are a web research assistant. Search and fetch pages for in-depth research.

Be direct and concise. Search first, then fetch specific pages for details.
Prefer recent, authoritative sources.
"""

# ---------------------------------------------------------------------------
# Create Agent
# ---------------------------------------------------------------------------
research_agent = Agent(
    id="research-agent",
    name="Research Agent",
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
    research_agent.print_response("Search for recent news about OpenAI", stream=True)
