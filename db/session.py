"""
Database Session
----------------

PostgreSQL database connection for AgentOS.
"""

from agno.db.postgres import PostgresDb

from db.url import db_url

DB_ID = "agentos-db"


def get_postgres_db() -> PostgresDb:
    """Create a PostgresDb instance."""
    return PostgresDb(id=DB_ID, db_url=db_url)
