"""AgentOS"""

from pathlib import Path

from agno.os import AgentOS

from agents.knowledge_agent import knowledge_agent
from agents.mcp_agent import mcp_agent

os_config_path = str(Path(__file__).parent.joinpath("config.yaml"))

# Create the AgentOS
agent_os = AgentOS(
    id="agentos-railway",
    agents=[knowledge_agent, mcp_agent],
    # Configuration for the AgentOS
    config=os_config_path,
)
app = agent_os.get_app()

if __name__ == "__main__":
    # Serve the application
    agent_os.serve(app="main:app", reload=True)
