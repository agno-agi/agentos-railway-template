"""
Knowledge Agent
---------------

An agent that answers questions using a knowledge base.

Run:
    python -m agents.knowledge_agent
"""

from agno.agent import Agent
from agno.models.openai import OpenAIResponses

from db import create_knowledge, get_postgres_db

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------
agent_db = get_postgres_db()
knowledge = create_knowledge("Knowledge Agent", "knowledge_agent_docs")

# ---------------------------------------------------------------------------
# Agent Instructions
# ---------------------------------------------------------------------------
instructions = """\
You are a knowledge assistant. You answer questions by searching your knowledge base.

## How You Work

1. Search the knowledge base for relevant information
2. Answer based on what you find
3. Cite your sources
4. If the information isn't in the knowledge base, say so clearly

## Guidelines

- Be direct and concise
- Quote relevant passages when they add value
- Provide code examples when asked
- Don't make up information - only use what's in the knowledge base
"""

# ---------------------------------------------------------------------------
# Create Agent
# ---------------------------------------------------------------------------
knowledge_agent = Agent(
    id="knowledge-agent",
    name="Knowledge Agent",
    model=OpenAIResponses(id="gpt-5.2"),
    db=agent_db,
    knowledge=knowledge,
    instructions=instructions,
    search_knowledge=True,
    enable_agentic_memory=True,
    add_datetime_to_context=True,
    add_history_to_context=True,
    read_chat_history=True,
    num_history_runs=5,
    markdown=True,
)


def load_default_documents() -> None:
    """Load default documents into the knowledge base."""
    knowledge.insert(
        name="Agno Introduction",
        url="https://docs.agno.com/introduction.md",
        skip_if_exists=True,
    )
    knowledge.insert(
        name="Agno First Agent",
        url="https://docs.agno.com/first-agent.md",
        skip_if_exists=True,
    )


if __name__ == "__main__":
    load_default_documents()
