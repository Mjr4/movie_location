from fastapi.testclient import TestClient

from app import config
from app.main import app


def test_requests_over_the_limit_get_429(anon_client, monkeypatch):
    monkeypatch.setattr(config, "RATE_LIMIT", "3/minute")
    for _ in range(3):
        assert anon_client.get("/movies/").status_code == 200

    r = anon_client.get("/movies/")
    assert r.status_code == 429
    assert "detail" in r.json()
    assert int(r.headers["retry-after"]) > 0


def test_limit_applies_to_writes_and_failed_auth(anon_client, monkeypatch):
    monkeypatch.setattr(config, "RATE_LIMIT", "2/minute")
    for _ in range(2):
        assert anon_client.post("/movies/", json={"title": "X", "year": 2020}).status_code == 401

    assert anon_client.post("/movies/", json={"title": "X", "year": 2020}).status_code == 429


def test_limit_is_per_ip(_override_db, monkeypatch):
    monkeypatch.setattr(config, "RATE_LIMIT", "1/minute")
    with TestClient(app, client=("10.0.0.1", 5000)) as a, TestClient(app, client=("10.0.0.2", 5000)) as b:
        assert a.get("/movies/").status_code == 200
        assert a.get("/movies/").status_code == 429
        assert b.get("/movies/").status_code == 200


def test_429_keeps_cors_headers(anon_client, monkeypatch):
    monkeypatch.setattr(config, "RATE_LIMIT", "1/minute")
    headers = {"Origin": "https://example.com"}
    anon_client.get("/movies/", headers=headers)

    r = anon_client.get("/movies/", headers=headers)
    assert r.status_code == 429
    assert r.headers["access-control-allow-origin"] == "*"
