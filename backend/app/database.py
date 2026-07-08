"""
Database connection.

SQLAlchemy needs three things:
  - An engine: the actual connection to Postgres
  - A SessionLocal factory: creates individual DB sessions per request
  - A Base class: all our models will inherit from this so SQLAlchemy
    knows to manage their tables

We use python-dotenv to load the DATABASE_URL from the .env file rather
than hardcoding credentials.
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# The engine is the core interface to the database.
# pool_pre_ping=True means SQLAlchemy tests connections before using them
# — useful so stale connections don't cause silent failures.
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Each request gets its own session (a unit of work with the DB).
# autocommit=False: we control when changes are committed.
# autoflush=False: changes aren't sent to the DB until we flush or commit.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# All models inherit from Base. SQLAlchemy uses this to track what tables exist.
Base = declarative_base()


def get_db():
    """
    FastAPI dependency that provides a database session per request.

    Using 'yield' makes this a context manager — the session is always
    closed after the request finishes, even if an exception was raised.
    FastAPI calls this automatically when a route lists it as a dependency.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()