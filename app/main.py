"""
AgentOS
-------

The main entry point for AgentOS.

Run:
    python -m app.main
"""

from os import getenv
from pathlib import Path
from typing import Any

from agno.os import AgentOS

from agents.knowledge_agent import knowledge_agent
from agents.mcp_agent import mcp_agent
from app.interfaces import build_interfaces
from db import get_postgres_db

# ---------------------------------------------------------------------------
# Create AgentOS
# ---------------------------------------------------------------------------
agent_os = AgentOS(
    name="AgentOS",
    tracing=True,
    scheduler=True,
    db=get_postgres_db(),
    agents=[knowledge_agent, mcp_agent],
    interfaces=build_interfaces(knowledge_agent),
    config=str(Path(__file__).parent / "config.yaml"),
)

app = agent_os.get_app()


@app.get("/health", tags=["Ops"])
def healthcheck() -> dict[str, Any]:
    """Lightweight liveness endpoint for Railway healthchecks."""

    return {
        "status": "ok",
        "service": "agentos",
        "runtime_env": getenv("RUNTIME_ENV", "prd"),
    }

if __name__ == "__main__":
    agent_os.serve(
        app="main:app",
        reload=getenv("RUNTIME_ENV", "prd") == "dev",
    )
