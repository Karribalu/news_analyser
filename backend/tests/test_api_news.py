"""Tests for GET /api/news."""
from unittest.mock import patch

from app.schemas import Article

_ARTICLE = Article(
    title="Test Title",
    description="Test Desc",
    url="https://example.com/1",
    source="Test Source",
    published_at="2024-01-01T00:00:00Z",
)


def test_search_news_success(client):
    with patch("app.api.news.fetch_articles", return_value=[_ARTICLE]):
        resp = client.get("/api/news?q=python")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["articles"]) == 1
    assert data["articles"][0]["title"] == "Test Title"
    assert data["articles"][0]["url"] == "https://example.com/1"


def test_search_news_default_max_results(client):
    with patch("app.api.news.fetch_articles", return_value=[]) as mock_fn:
        resp = client.get("/api/news?q=python")
    assert resp.status_code == 200
    mock_fn.assert_called_once_with("python", 10)


def test_search_news_custom_max_results(client):
    with patch("app.api.news.fetch_articles", return_value=[]) as mock_fn:
        resp = client.get("/api/news?q=ai&max_results=5")
    assert resp.status_code == 200
    mock_fn.assert_called_once_with("ai", 5)


def test_search_news_empty_results(client):
    with patch("app.api.news.fetch_articles", return_value=[]):
        resp = client.get("/api/news?q=xyzzy")
    assert resp.status_code == 200
    assert resp.json() == {"articles": []}


# --- Validation errors (422) ---

def test_search_news_missing_query_param(client):
    resp = client.get("/api/news")
    assert resp.status_code == 422


def test_search_news_empty_query_string(client):
    resp = client.get("/api/news?q=")
    assert resp.status_code == 422


def test_search_news_query_too_long(client):
    resp = client.get(f"/api/news?q={'a' * 201}")
    assert resp.status_code == 422


def test_search_news_max_results_too_low(client):
    resp = client.get("/api/news?q=test&max_results=0")
    assert resp.status_code == 422


def test_search_news_max_results_too_high(client):
    resp = client.get("/api/news?q=test&max_results=21")
    assert resp.status_code == 422


# --- Upstream error propagation ---

def test_search_news_value_error_returns_500(client):
    with patch("app.api.news.fetch_articles", side_effect=ValueError("GNEWS_API_KEY not set")):
        resp = client.get("/api/news?q=test")
    assert resp.status_code == 500
    assert "GNEWS_API_KEY not set" in resp.json()["detail"]


def test_search_news_generic_error_returns_502(client):
    with patch("app.api.news.fetch_articles", side_effect=RuntimeError("network down")):
        resp = client.get("/api/news?q=test")
    assert resp.status_code == 502
    assert "News API error" in resp.json()["detail"]
