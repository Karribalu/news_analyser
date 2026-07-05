"""Tests for POST /api/analysis, GET /api/analysis, DELETE /api/analysis/{id}."""
from datetime import datetime, timezone
from unittest.mock import patch

from app.models import Analysis
from app.schemas import Sentiment

_AI_RESULT = {"summary": "A concise summary.", "sentiment": Sentiment.Positive}


# ---------------------------------------------------------------------------
# POST /api/analysis
# ---------------------------------------------------------------------------

def test_analyze_new_article_creates_and_returns_201(client, sample_article):
    with patch("app.api.analysis.analyze_article", return_value=_AI_RESULT):
        resp = client.post("/api/analysis", json={"article": sample_article})
    assert resp.status_code == 201
    data = resp.json()
    assert data["summary"] == "A concise summary."
    assert data["sentiment"] == "positive"
    assert data["article_url"] == sample_article["url"]
    assert "id" in data


def test_analyze_cached_article_skips_openai(client, sample_article, persisted_analysis):
    with patch("app.api.analysis.analyze_article") as mock_ai:
        resp = client.post("/api/analysis", json={"article": sample_article})
    mock_ai.assert_not_called()
    assert resp.status_code == 201
    assert resp.json()["id"] == persisted_analysis.id


def test_analyze_invalid_body_returns_422(client):
    resp = client.post("/api/analysis", json={"article": {}})
    assert resp.status_code == 422


def test_analyze_missing_body_returns_422(client):
    resp = client.post("/api/analysis", json={})
    assert resp.status_code == 422


def test_analyze_openai_config_error_returns_500(client, sample_article):
    with patch("app.api.analysis.analyze_article", side_effect=ValueError("OPENAI_API_KEY")):
        resp = client.post("/api/analysis", json={"article": sample_article})
    assert resp.status_code == 500
    assert "OPENAI_API_KEY" in resp.json()["detail"]


def test_analyze_openai_generic_error_returns_502(client, sample_article):
    with patch("app.api.analysis.analyze_article", side_effect=RuntimeError("API down")):
        resp = client.post("/api/analysis", json={"article": sample_article})
    assert resp.status_code == 502
    assert "OpenAI API error" in resp.json()["detail"]


# ---------------------------------------------------------------------------
# GET /api/analysis
# ---------------------------------------------------------------------------

def test_list_analysis_empty(client):
    resp = client.get("/api/analysis")
    assert resp.status_code == 200
    assert resp.json() == []


def test_list_analysis_returns_persisted_record(client, persisted_analysis):
    resp = client.get("/api/analysis")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["id"] == persisted_analysis.id
    assert data[0]["article_url"] == persisted_analysis.article_url
    assert data[0]["summary"] == "Test summary"
    assert data[0]["sentiment"] == "neutral"


def test_list_analysis_returns_multiple_records(client, db_session):
    for i in range(3):
        db_session.add(Analysis(
            article_url=f"https://example.com/{i}",
            article_title=f"Title {i}",
            summary=f"Summary {i}",
            sentiment="neutral",
            created_at=datetime.now(timezone.utc),
        ))
    db_session.commit()

    resp = client.get("/api/analysis")
    assert resp.status_code == 200
    assert len(resp.json()) == 3


# ---------------------------------------------------------------------------
# DELETE /api/analysis/{id}
# ---------------------------------------------------------------------------

def test_delete_analysis_success(client, persisted_analysis):
    resp = client.delete(f"/api/analysis/{persisted_analysis.id}")
    assert resp.status_code == 200
    assert resp.json() == {"message": "Analysis deleted"}


def test_delete_analysis_removes_from_list(client, persisted_analysis):
    client.delete(f"/api/analysis/{persisted_analysis.id}")
    resp = client.get("/api/analysis")
    assert resp.json() == []


def test_delete_analysis_not_found_returns_404(client):
    resp = client.delete("/api/analysis/9999")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Analysis not found"
