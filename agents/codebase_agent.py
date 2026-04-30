"""
Codebase Agent
--------------

Answers questions about this codebase.

Run:
    python -m agents.codebase_agent
"""

from pathlib import Path

from agno.agent import Agent
from agno.context.mode import ContextMode
from agno.context.workspace import WorkspaceContextProvider
from agno.models.openai import OpenAIResponses

from db import get_postgres_db

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------
agent_db = get_postgres_db()

REPO_ROOT = Path(__file__).resolve().parents[1]

workspace_context = WorkspaceContextProvider(
    root=REPO_ROOT,
    mode=ContextMode.tools,
)

# ---------------------------------------------------------------------------
# Agent Instructions
# ---------------------------------------------------------------------------
instructions = """\
You are a codebase assistant. Answer questions about this repository.

Be direct and specific. Quote relevant code when it helps.
If you can't find something, say so.
"""

# ---------------------------------------------------------------------------
# Create Agent
# ---------------------------------------------------------------------------
codebase_agent = Agent(
    id="codebase-agent",
    name="Codebase Agent",
    model=OpenAIResponses(id="gpt-5.5"),
    db=agent_db,
    tools=workspace_context.get_tools(),
    instructions=workspace_context.instructions() + "\n\n" + instructions,
    enable_agentic_memory=True,
    add_datetime_to_context=True,
    add_history_to_context=True,
    read_chat_history=True,
    num_history_runs=5,
    markdown=True,
)

if __name__ == "__main__":
    codebase_agent.print_response("What agents are available in this project?", stream=True)
