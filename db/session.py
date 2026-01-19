from typing import Generator

from agno.db.postgres import PostgresDb
from sqlalchemy.engine import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from db.url import get_db_url

# Create SQLAlchemy Engine using a database URL
db_url: str = get_db_url()
db_engine: Engine = create_engine(db_url, pool_pre_ping=True)

# Create a SessionLocal class
# https://fastapi.tiangolo.com/tutorial/sql-databases/#create-a-sessionlocal-class
SessionLocal: sessionmaker[Session] = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)


def get_postgres_db(session_table: str = "agno_sessions", knowledge_table: str = "agno_knowledge") -> PostgresDb:
    """Create a PostgresDb instance with specific table names for agent isolation."""
    return PostgresDb(db_url=db_url, id="agent-os", session_table=session_table, knowledge_table=knowledge_table)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get a database session.

    Yields:
        Session: An SQLAlchemy database session.
    """
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
