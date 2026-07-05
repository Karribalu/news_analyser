"""Tests for AnalysisRepository (database layer)."""
from datetime import datetime, timezone

import pytest

from app.models import Analysis
from app.repositories.analysis import AnalysisRepository
from app.schemas import Article, Sentiment


@pytest.fixture
def repo(db_session) -> AnalysisRepository:
    return AnalysisRepository(db_session)


@pytest.fixture
def article() -> Article:
    return Article(
        title="Repository Test Article",
        description="Some description",
        url="https://example.com/repo-test",
        source="Test Source",
        published_at="2024-06-01",
    )


def _insert(db_session, url: str, title: str = "Title", summary: str = "Summary") -> Analysis:
    row = Analysis(
        article_url=url,
        article_title=title,
        summary=summary,
        sentiment="neutral",
        created_at=datetime.now(timezone.utc),
    )
    db_session.add(row)
    db_session.commit()
    db_session.refresh(row)
    return row


# ---------------------------------------------------------------------------
# create
# ---------------------------------------------------------------------------

def test_create_returns_analysis_with_id(repo, article):
    result = repo.create(article, "A summary", Sentiment.Positive)
    assert result.id is not None
    assert result.article_url == article.url
    assert result.article_title == article.title
    assert result.article_description == article.description
    assert result.article_source == article.source
    assert result.summary == "A summary"
    assert result.sentiment == Sentiment.Positive


def test_create_persists_to_db(repo, db_session, article):
    created = repo.create(article, "Summary", Sentiment.Neutral)
    fetched = db_session.query(Analysis).filter_by(id=created.id).first()
    assert fetched is not None
    assert fetched.article_url == article.url


# ---------------------------------------------------------------------------
# get_by_url
# ---------------------------------------------------------------------------

def test_get_by_url_returns_existing_row(repo, db_session):
    row = _insert(db_session, "https://example.com/abc")
    result = repo.get_by_url("https://example.com/abc")
    assert result is not None
    assert result.id == row.id


def test_get_by_url_returns_none_for_missing(repo):
    result = repo.get_by_url("https://nonexistent.example.com/xyz")
    assert result is None


# ---------------------------------------------------------------------------
# get_by_id
# ---------------------------------------------------------------------------

def test_get_by_id_returns_existing_row(repo, db_session):
    row = _insert(db_session, "https://example.com/id-test")
    result = repo.get_by_id(row.id)
    assert result is not None
    assert result.article_url == "https://example.com/id-test"


def test_get_by_id_returns_none_for_missing(repo):
    result = repo.get_by_id(99999)
    assert result is None


# ---------------------------------------------------------------------------
# list_all
# ---------------------------------------------------------------------------

def test_list_all_returns_empty_list(repo):
    assert repo.list_all() == []


def test_list_all_returns_all_rows(repo, db_session):
    _insert(db_session, "https://example.com/1")
    _insert(db_session, "https://example.com/2")
    _insert(db_session, "https://example.com/3")
    results = repo.list_all()
    assert len(results) == 3


def test_list_all_ordered_by_created_at_desc(repo, db_session):
    from datetime import timedelta  # only used here
    base = datetime(2024, 1, 1, tzinfo=timezone.utc)
    for i in range(3):
        row = Analysis(
            article_url=f"https://example.com/order-{i}",
            article_title=f"Title {i}",
            summary=f"Summary {i}",
            sentiment="neutral",
            created_at=base + timedelta(hours=i),
        )
        db_session.add(row)
    db_session.commit()

    results = repo.list_all()
    timestamps = [r.created_at for r in results]
    assert timestamps == sorted(timestamps, reverse=True)


# ---------------------------------------------------------------------------
# delete
# ---------------------------------------------------------------------------

def test_delete_removes_row(repo, db_session):
    row = _insert(db_session, "https://example.com/delete-me")
    repo.delete(row)
    assert repo.get_by_url("https://example.com/delete-me") is None


def test_delete_does_not_affect_other_rows(repo, db_session):
    keep = _insert(db_session, "https://example.com/keep")
    remove = _insert(db_session, "https://example.com/remove")
    repo.delete(remove)
    assert repo.get_by_url("https://example.com/keep") is not None
