import pytest

from app import config
from .conftest import make_movie, make_location


WRITE_REQUESTS = [
    ("post", "/movies/", {"title": "X", "year": 2020}),
    ("put", "/movies/1", {"title": "Y"}),
    ("delete", "/movies/1", None),
    ("post", "/locations/", {"name": "L", "country": "Argentina"}),
    ("put", "/locations/1", {"name": "L2"}),
    ("delete", "/locations/1", None),
    ("post", "/movie-locations/", {"movie_id": 1, "location_id": 1}),
    ("delete", "/movie-locations/1", None),
]


@pytest.mark.parametrize("method,path,body", WRITE_REQUESTS)
def test_write_without_key_is_rejected(anon_client, method, path, body):
    r = getattr(anon_client, method)(path, **({"json": body} if body is not None else {}))
    assert r.status_code == 401


@pytest.mark.parametrize("method,path,body", WRITE_REQUESTS)
def test_write_with_wrong_key_is_rejected(anon_client, method, path, body):
    kwargs = {"headers": {"X-API-Key": "wrong"}}
    if body is not None:
        kwargs["json"] = body
    r = getattr(anon_client, method)(path, **kwargs)
    assert r.status_code == 401


def test_rejected_write_does_not_modify_data(client, anon_client):
    movie_id = make_movie(client).json()["id"]
    assert anon_client.delete(f"/movies/{movie_id}").status_code == 401
    assert client.get(f"/movies/{movie_id}").status_code == 200


def test_reads_are_public(client, anon_client):
    movie_id = make_movie(client).json()["id"]
    location_id = make_location(client).json()["id"]
    client.post("/movie-locations/", json={"movie_id": movie_id, "location_id": location_id})

    assert anon_client.get("/movies/").status_code == 200
    assert anon_client.get(f"/movies/{movie_id}").status_code == 200
    assert anon_client.get(f"/movies/{movie_id}/locations").status_code == 200
    assert anon_client.get("/locations/").status_code == 200
    assert anon_client.get(f"/locations/{location_id}").status_code == 200
    assert anon_client.get("/movie-locations/").status_code == 200


def test_valid_key_allows_write(anon_client):
    r = anon_client.post(
        "/movies/", json={"title": "X", "year": 2020}, headers={"X-API-Key": "test-key"}
    )
    assert r.status_code == 201


def test_multiple_keys_are_supported(anon_client, monkeypatch):
    monkeypatch.setattr(config, "API_KEYS", {"old-key", "new-key"})
    for key in ("old-key", "new-key"):
        r = anon_client.post(
            "/movies/", json={"title": f"M-{key}", "year": 2020}, headers={"X-API-Key": key}
        )
        assert r.status_code == 201


def test_no_configured_keys_fails_closed(anon_client, monkeypatch):
    monkeypatch.setattr(config, "API_KEYS", set())
    # ni la ausencia de key ni una key vacía deben pasar
    assert anon_client.post("/movies/", json={"title": "X", "year": 2020}).status_code == 401
    r = anon_client.post(
        "/movies/", json={"title": "X", "year": 2020}, headers={"X-API-Key": ""}
    )
    assert r.status_code == 401
