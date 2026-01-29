"""
AgentOS
=======

The main entry point for AgentOS.

Run:
    python -m app.main
"""

from os import getenv
from pathlib import Path

from agno.os import AgentOS

from agents.knowledge_agent import knowledge_agent
from agents.mcp_agent import mcp_agent
from agents.pal import pal, pal_knowledge
from db import get_postgres_db

# ============================================================================
# Create AgentOS
# ============================================================================
agent_os = AgentOS(
    name="AgentOS",
    tracing=True,
    db=get_postgres_db(),
    agents=[pal, knowledge_agent, mcp_agent],
    knowledge=[pal_knowledge],
    config=str(Path(__file__).parent / "config.yaml"),
)

app = agent_os.get_app()

if __name__ == "__main__":
    agent_os.serve(
        app="main:app",
        reload=getenv("RUNTIME_ENV", "prd") == "dev",
    )
