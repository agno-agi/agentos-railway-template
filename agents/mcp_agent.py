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
# Setup database and tools
# ============================================================================
agent_db = get_postgres_db()

# ============================================================================
# Agent Instructions
# ============================================================================
instructions = """\
You are a helpful assistant that answers questions using MCP tools.

WORKFLOW
--------
1. Use available tools to find relevant information
2. Provide clear, accurate answers based on what you find
3. If the answer isn't available, say so
4. Include sources when possible

GUIDELINES
----------
- Be concise and direct
- Quote relevant sections when helpful
- If asked for code, provide working examples
- Ask clarifying questions if the query is ambiguous
"""

# ============================================================================
# Create Agent
# ============================================================================
mcp_agent = Agent(
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
