"""
AgentOS
=======

The main entry point for AgentOS.

Run:
    python -m app.main
"""

from pathlib import Path

from agno.os import AgentOS

from agents.knowledge_agent import knowledge_agent
from agents.mcp_agent import mcp_agent

# ============================================================================
# Create AgentOS
# ============================================================================
agent_os = AgentOS(
    name="AgentOS",
    agents=[knowledge_agent, mcp_agent],
    config=str(Path(__file__).parent / "config.yaml"),
)

app = agent_os.get_app()

if __name__ == "__main__":
    agent_os.serve(app="main:app", reload=True)
