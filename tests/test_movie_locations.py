from .conftest import make_movie, make_location


def _create_both(client):
    movie_id = make_movie(client).json()["id"]
    loc_id = make_location(client).json()["id"]
    return movie_id, loc_id


def test_create_movie_location(client):
    movie_id, loc_id = _create_both(client)
    r = client.post("/movie-locations/", json={"movie_id": movie_id, "location_id": loc_id})
    assert r.status_code == 201
    assert r.json()["movie_id"] == movie_id
    assert r.json()["location_id"] == loc_id


def test_create_movie_location_with_scene(client):
    movie_id, loc_id = _create_both(client)
    r = client.post(
        "/movie-locations/",
        json={"movie_id": movie_id, "location_id": loc_id, "scene_description": "Opening scene"},
    )
    assert r.status_code == 201
    assert r.json()["scene_description"] == "Opening scene"


def test_create_movie_location_invalid_movie(client):
    loc_id = make_location(client).json()["id"]
    r = client.post("/movie-locations/", json={"movie_id": 9999, "location_id": loc_id})
    assert r.status_code == 404
    assert "9999" in r.json()["detail"]


def test_create_movie_location_invalid_location(client):
    movie_id = make_movie(client).json()["id"]
    r = client.post("/movie-locations/", json={"movie_id": movie_id, "location_id": 9999})
    assert r.status_code == 404
    assert "9999" in r.json()["detail"]


def test_create_movie_location_duplicate(client):
    movie_id, loc_id = _create_both(client)
    client.post("/movie-locations/", json={"movie_id": movie_id, "location_id": loc_id})
    r = client.post("/movie-locations/", json={"movie_id": movie_id, "location_id": loc_id})
    assert r.status_code == 409


def test_list_movie_locations(client):
    movie_id, loc_id = _create_both(client)
    client.post("/movie-locations/", json={"movie_id": movie_id, "location_id": loc_id})
    r = client.get("/movie-locations/")
    assert r.status_code == 200
    assert len(r.json()) == 1


def test_delete_movie_location(client):
    movie_id, loc_id = _create_both(client)
    ml_id = client.post("/movie-locations/", json={"movie_id": movie_id, "location_id": loc_id}).json()["id"]
    r = client.delete(f"/movie-locations/{ml_id}")
    assert r.status_code == 200
    assert client.get("/movie-locations/").json() == []


def test_delete_movie_location_not_found(client):
    r = client.delete("/movie-locations/9999")
    assert r.status_code == 404
