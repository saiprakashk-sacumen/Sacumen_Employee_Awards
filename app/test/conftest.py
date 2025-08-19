from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db import Base
import pytest
from fastapi.testclient import TestClient
import sys
from unittest.mock import MagicMock

# Mock AI first
mock_sentiment = MagicMock()
mock_sentiment.analyze_nomination.return_value = {"score": 0.9, "label": "POSITIVE"}
sys.modules["app.ai.sentiment"] = mock_sentiment

# In-memory SQLite for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables in memory
Base.metadata.create_all(bind=engine)

# Import app after mocking AI
from app.main import app, get_db

# Override get_db for tests
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c
