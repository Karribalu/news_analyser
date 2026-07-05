from app.models import Analysis
from app.main import app
from app.database import Base, get_db
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import pytest
import os
from datetime import datetime, timezone

# Must be set before any app module is imported so pydantic-settings picks
# them up and SQLAlchemy creates a SQLite engine instead of PostgreSQL.
os.environ["DATABASE_URL"] = "sqlite:///./test_news_analyzer.db"
os.environ["GNEWS_API_KEY"] = "test_gnews_key"
os.environ["OPENAI_API_KEY"] = "test_openai_key"
os.environ["GNEWS_BASE_URL"] = "https://gnews.io/api/v4/search"
os.environ["CORS_ORIGINS"] = "http://localhost:3000"


TEST_DATABASE_URL = "sqlite:///./test_news_analyzer.db"
test_engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture
def db_session():
    """Fresh SQLite DB for every test."""
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db_session):
    """TestClient with the DB dependency overridden to use the test session."""
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def sample_article():
    return {
        "title": "Test Article Title",
        "description": "Test article description",
        "url": "https://example.com/test-article",
        "source": "Test Source",
        "published_at": "2024-01-01T00:00:00Z",
    }


@pytest.fixture
def persisted_analysis(db_session, sample_article):
    """Insert one Analysis row into the test DB and return the ORM object."""
    analysis = Analysis(
        article_url=sample_article["url"],
        article_title=sample_article["title"],
        article_description=sample_article["description"],
        article_source=sample_article["source"],
        article_published_at=sample_article["published_at"],
        summary="Test summary",
        sentiment="neutral",
        created_at=datetime.now(timezone.utc),
    )
    db_session.add(analysis)
    db_session.commit()
    db_session.refresh(analysis)
    return analysis
