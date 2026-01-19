"""
Knowledge Agent
===============

An agent that answers questions using a knowledge base.

Run:
    python -m agents.knowledge_agent
"""

from agno.agent import Agent
from agno.knowledge import Knowledge
from agno.knowledge.embedder.openai import OpenAIEmbedder
from agno.models.openai import OpenAIResponses
from agno.vectordb.pgvector import PgVector, SearchType

from db.session import db_url, get_postgres_db

# ============================================================================
# Setup database and knowledge
# ============================================================================
agent_db = get_postgres_db()
knowledge = Knowledge(
    name="Knowledge Base",
    vector_db=PgVector(
        db_url=db_url,
        table_name="knowledge_agent_docs",
        search_type=SearchType.hybrid,
        embedder=OpenAIEmbedder(id="text-embedding-3-small"),
    ),
    max_results=10,
    contents_db=agent_db,
)

# ============================================================================
# Agent Instructions
# ============================================================================
instructions = """\
You are a knowledge assistant that answers questions using the knowledge base.

WORKFLOW
--------
1. Search the knowledge base for relevant information
2. Provide clear, accurate answers based on what you find
3. If the answer isn't in the knowledge base, say so
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
knowledge_agent = Agent(
    name="Knowledge Agent",
    model=OpenAIResponses(id="gpt-5.2"),
    db=agent_db,
    knowledge=knowledge,
    instructions=instructions,
    enable_agentic_memory=True,
    add_datetime_to_context=True,
    add_history_to_context=True,
    num_history_runs=5,
    markdown=True,
)

if __name__ == "__main__":
    knowledge.insert(name="Agno Introduction", url="https://docs.agno.com/introduction.md")
    knowledge.insert(name="Agno Quickstart", url="https://docs.agno.com/get-started/quickstart.md")
