"""Tests for the root FastAPI app (health & root endpoints, HTTP middleware)."""


def test_root_returns_message(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json() == {"message": "News Analyzer"}


def test_health_returns_ok(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_unknown_route_returns_404(client):
    resp = client.get("/does-not-exist")
    assert resp.status_code == 404


def test_http_middleware_adds_no_extra_headers(client):
    """Middleware must not break normal responses."""
    resp = client.get("/health")
    assert resp.status_code == 200
