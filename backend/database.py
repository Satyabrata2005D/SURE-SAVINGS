"""
SURE SAVINGS 2.0: Database Engine & Session Management
Supports SQLite for seamless local execution and PostgreSQL via DATABASE_URL.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Database URL configuration (defaults to local SQLite database in project directory)
DB_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(DB_DIR)
DEFAULT_SQLITE_PATH = os.path.join(PROJECT_DIR, "sure_savings.db")
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_SQLITE_PATH}")

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """FastAPI Dependency for database sessions"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
