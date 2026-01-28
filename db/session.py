"""
Database Session
================

Database connection and session management.
"""

from typing import Generator

from agno.db.postgres import PostgresDb
from sqlalchemy.engine import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from db.url import get_db_url

# ============================================================================
# Database Setup
# ============================================================================
db_url: str = get_db_url()
db_engine: Engine = create_engine(db_url, pool_pre_ping=True)
SessionLocal: sessionmaker[Session] = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)


# ============================================================================
# Database Helpers
# ============================================================================
def get_postgres_db(id: str = "postgres-db") -> PostgresDb:
    """Create a PostgresDb instance."""
    return PostgresDb(id=id, db_url=db_url)


def get_db() -> Generator[Session, None, None]:
    """Dependency to get a database session."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
