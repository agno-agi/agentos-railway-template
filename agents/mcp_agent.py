"""
MCP Agent
=========

An agent that uses MCP tools to answer questions.

Run:
    python -m agents.mcp_agent
"""

from agno.agent import Agent
from agno.models.openai import OpenAIResponses
from agno.tools.mcp import MCPTools

from db.session import get_postgres_db

# ============================================================================
# Setup
# ============================================================================
agent_db = get_postgres_db()

# ============================================================================
# Agent Instructions
# ============================================================================
instructions = """\
You are a helpful assistant with access to external tools via MCP (Model Context Protocol).

## How You Work

1. Understand what the user needs
2. Use your tools to find information or take action
3. Provide clear answers based on tool results
4. If a tool can't help, say so and suggest alternatives

## Guidelines

- Be direct and concise
- Explain what you're doing when using tools
- Provide code examples when asked
- If you're unsure which tool to use, ask for clarification
"""

# ============================================================================
# Create Agent
# ============================================================================
mcp_agent = Agent(
    id="mcp-agent",
    name="MCP Agent",
    model=OpenAIResponses(id="gpt-5.2"),
    db=agent_db,
    tools=[MCPTools(url="https://docs.agno.com/mcp")],
    instructions=instructions,
    enable_agentic_memory=True,
    add_datetime_to_context=True,
    add_history_to_context=True,
    num_history_runs=5,
    markdown=True,
)

if __name__ == "__main__":
    mcp_agent.cli_app(stream=True)
