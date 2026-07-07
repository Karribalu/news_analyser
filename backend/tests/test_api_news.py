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

_SIX_ARTICLES = [
    Article(title=f"Title {i}", url=f"https://example.com/{i}")
    for i in range(1, 7)
]


def test_search_news_success(client):
    with patch("app.api.news.fetch_articles", return_value=([_ARTICLE], 1)):
        resp = client.get("/api/news?q=python")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["articles"]) == 1
    assert data["articles"][0]["title"] == "Test Title"
    assert data["articles"][0]["url"] == "https://example.com/1"
    assert data["total"] == 1
    assert data["page"] == 1
    assert data["total_pages"] == 1


def test_search_news_uses_gnews_total(client):
    """total in response reflects GNews totalArticles, not just returned count."""
    with patch("app.api.news.fetch_articles", return_value=([_ARTICLE], 54904)):
        resp = client.get("/api/news?q=python")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 54904
    assert data["total_pages"] == 54904 // 6 + 1


def test_search_news_passes_page_and_page_size_to_service(client):
    with patch("app.api.news.fetch_articles", return_value=([], 0)) as mock_fn:
        resp = client.get("/api/news?q=python&page=3&page_size=10")
    assert resp.status_code == 200
    mock_fn.assert_called_once_with("python", 3, 10)


def test_search_news_default_page_and_page_size(client):
    with patch("app.api.news.fetch_articles", return_value=([], 0)) as mock_fn:
        resp = client.get("/api/news?q=python")
    assert resp.status_code == 200
    mock_fn.assert_called_once_with("python", 1, 6)


def test_search_news_empty_results(client):
    with patch("app.api.news.fetch_articles", return_value=([], 0)):
        resp = client.get("/api/news?q=xyzzy")
    assert resp.status_code == 200
    data = resp.json()
    assert data["articles"] == []
    assert data["total"] == 0
    assert data["total_pages"] == 1


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


def test_search_news_page_too_low(client):
    resp = client.get("/api/news?q=test&page=0")
    assert resp.status_code == 422


def test_search_news_page_size_too_high(client):
    resp = client.get("/api/news?q=test&page_size=21")
    assert resp.status_code == 422


# --- Upstream error propagation ---

def test_search_news_value_error_returns_500(client):
    with patch("app.api.news.fetch_articles", side_effect=ValueError("GNEWS_API_KEY not set")):
        resp = client.get("/api/news?q=test")
    assert resp.status_code == 500
    assert "GNEWS_API_KEY not set" in resp.json()["detail"]


# --- Headlines ---

def test_get_headlines_success(client):
    with patch("app.api.news.fetch_headlines", return_value=([_ARTICLE], 100)):
        resp = client.get("/api/news/headlines")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 100
    assert data["page"] == 1
    assert data["total_pages"] == 17  # ceil(100/6)
    assert data["articles"][0]["title"] == "Test Title"


def test_get_headlines_passes_page_and_page_size_to_service(client):
    with patch("app.api.news.fetch_headlines", return_value=([], 0)) as mock_fn:
        resp = client.get("/api/news/headlines?page=2&page_size=10")
    assert resp.status_code == 200
    mock_fn.assert_called_once_with("general", 2, 10)


def test_get_headlines_uses_gnews_total(client):
    with patch("app.api.news.fetch_headlines", return_value=(_SIX_ARTICLES, 3000)):
        resp = client.get("/api/news/headlines?page_size=6")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 3000
    assert data["total_pages"] == 500  # 3000/6


def test_get_headlines_page_size_too_high(client):
    resp = client.get("/api/news/headlines?page_size=21")
    assert resp.status_code == 422


def test_get_headlines_value_error_returns_500(client):
    with patch("app.api.news.fetch_headlines", side_effect=ValueError("GNEWS_API_KEY not set")):
        resp = client.get("/api/news/headlines")
    assert resp.status_code == 500


def test_search_news_generic_error_returns_502(client):
    with patch("app.api.news.fetch_articles", side_effect=RuntimeError("network down")):
        resp = client.get("/api/news?q=test")
    assert resp.status_code == 502
    assert "News API error" in resp.json()["detail"]
