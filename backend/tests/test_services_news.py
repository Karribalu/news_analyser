"""Tests for app.services.news.fetch_articles."""
from unittest.mock import MagicMock, patch

import httpx
import pytest

from app.services.news import fetch_articles


ITEM = {
    "title": "Breaking News",
    "description": "Something happened.",
    "url": "https://news.example.com/1",
    "source": {"name": "CNN"},
    "publishedAt": "2024-01-01T10:00:00Z",
}


def test_fetch_articles_returns_articles():
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"articles": [ITEM]}

    with patch("app.services.news.httpx.get", return_value=mock_resp):
        articles = fetch_articles("python", max_results=5)

    assert len(articles) == 1
    assert articles[0].title == "Breaking News"
    assert articles[0].url == "https://news.example.com/1"
    assert articles[0].source == "CNN"
    assert articles[0].published_at == "2024-01-01T10:00:00Z"


def test_fetch_articles_passes_correct_params():
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"articles": []}

    with patch("app.services.news.httpx.get", return_value=mock_resp) as mock_get:
        fetch_articles("test query", max_results=7)

    params = mock_get.call_args.kwargs["params"]
    assert params["q"] == "test query"
    assert params["max"] == 7
    assert params["lang"] == "en"


def test_fetch_articles_source_as_plain_string():
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"articles": [{**ITEM, "source": "BBC"}]}

    with patch("app.services.news.httpx.get", return_value=mock_resp):
        articles = fetch_articles("test")

    assert articles[0].source == "BBC"


def test_fetch_articles_empty_response():
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"articles": []}

    with patch("app.services.news.httpx.get", return_value=mock_resp):
        articles = fetch_articles("nothing")

    assert articles == []


def test_fetch_articles_multiple_articles():
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"articles": [{**ITEM, "url": f"https://example.com/{i}"} for i in range(3)]}

    with patch("app.services.news.httpx.get", return_value=mock_resp):
        articles = fetch_articles("multi")

    assert len(articles) == 3


def test_fetch_articles_raises_when_no_base_url(monkeypatch):
    monkeypatch.setattr("app.services.news.settings.gnews_base_url", "")
    with pytest.raises(ValueError, match="GNEWS_BASE_URL"):
        fetch_articles("test")


def test_fetch_articles_raises_when_no_api_key(monkeypatch):
    monkeypatch.setattr("app.services.news.settings.gnews_api_key", "")
    with pytest.raises(ValueError, match="GNEWS_API_KEY"):
        fetch_articles("test")


def test_fetch_articles_propagates_http_errors():
    with patch("app.services.news.httpx.get", side_effect=httpx.ConnectError("refused")):
        with pytest.raises(httpx.ConnectError):
            fetch_articles("test")


def test_fetch_articles_calls_raise_for_status():
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"articles": []}

    with patch("app.services.news.httpx.get", return_value=mock_resp):
        fetch_articles("test")

    mock_resp.raise_for_status.assert_called_once()
