"""
Workspace Agent
---------------

Answers questions about this codebase.

Run:
    python -m agents.workspace_agent
"""

from pathlib import Path

from agno.agent import Agent
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
    model=OpenAIResponses(id="gpt-5.2"),
)

# ---------------------------------------------------------------------------
# Agent Instructions
# ---------------------------------------------------------------------------
instructions = """\
You are a codebase assistant. You answer questions about this repository.

## How You Work

1. Use `query_workspace` to search and navigate the codebase
2. Read relevant files to understand the code
3. Explain clearly with code snippets when helpful

## Guidelines

- Be direct and specific
- Quote relevant code when it helps
- Explain architectural decisions when asked
- If you can't find something, say so and suggest where to look
"""

# ---------------------------------------------------------------------------
# Create Agent
# ---------------------------------------------------------------------------
workspace_agent = Agent(
    id="workspace-agent",
    name="Workspace Agent",
    model=OpenAIResponses(id="gpt-5.2"),
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
    workspace_agent.print_response("What agents are available in this project?", stream=True)
