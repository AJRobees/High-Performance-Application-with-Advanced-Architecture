"""
Database configuration and session management for the application.

This module creates the SQLAlchemy database engine, configures database
sessions, and provides the database dependency used by the API endpoints.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,DeclarativeBase

from config import PRODUCTS_DATABASE_URL

engine = create_engine(PRODUCTS_DATABASE_URL,
                       connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autoflush= False, autocommit= False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    """
    Provide a database session for API requests.

    Creates a session, yields it for database operations, and closes it
    after the request is completed.
    """
    with SessionLocal() as db:
        yield db