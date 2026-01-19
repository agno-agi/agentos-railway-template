"""
Database URL
============

Build database connection URL from environment variables.
"""

from os import getenv


def get_db_url() -> str:
    """Build database URL from environment variables."""
    driver = getenv("DB_DRIVER", "postgresql+psycopg")
    user = getenv("DB_USER", "ai")
    password = getenv("DB_PASS", "ai")
    host = getenv("DB_HOST", "localhost")
    port = getenv("DB_PORT", "5432")
    database = getenv("DB_DATABASE", "ai")

    return f"{driver}://{user}:{password}@{host}:{port}/{database}"
