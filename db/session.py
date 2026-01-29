"""
Database Session
================

PostgreSQL database connection for AgentOS.
"""

from agno.db.postgres import PostgresDb

from db.url import db_url


def get_postgres_db(contents_table: str | None = None) -> PostgresDb:
    """Create a PostgresDb instance.

    Args:
        contents_table: Optional table name for storing knowledge contents.

    Returns:
        Configured PostgresDb instance.
    """
    if contents_table:
        return PostgresDb(db_url=db_url, knowledge_table=contents_table)
    return PostgresDb(db_url=db_url)
