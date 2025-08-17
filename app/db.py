# app/db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os

# Read DB URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:postgres@db/awards")

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL, echo=True)  # echo=True logs SQL queries

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


# app/db.py (add at the bottom)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

