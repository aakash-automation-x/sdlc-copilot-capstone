import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# DR-004, DR-005: default to SQLite for local development; override with
# DATABASE_URL in production to target PostgreSQL.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./carportal.db")

# check_same_thread is a SQLite-only argument; skip it for other dialects.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Yield a database session and guarantee cleanup on exit - FR-001."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
