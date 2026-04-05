from .conftest import make_location, make_movie


def test_create_location(client):
    r = make_location(client)
    assert r.status_code == 201
    assert r.json()["city"] == "Buenos Aires"


def test_list_locations(client):
    make_location(client, name="Loc A")
    make_location(client, name="Loc B")
    r = client.get("/locations/")
    assert r.status_code == 200
    assert len(r.json()) == 2


def test_filter_by_country(client):
    make_location(client, name="Coliseo", city="Roma", country="Italia")
    make_location(client, name="Torre Eiffel", city="Paris", country="Francia")
    r = client.get("/locations/?country=italia")
    assert r.status_code == 200
    assert len(r.json()) == 1
    assert r.json()[0]["country"] == "Italia"


def test_filter_by_city(client):
    make_location(client, name="Loc A", city="Buenos Aires", country="Argentina")
    make_location(client, name="Loc B", city="Córdoba", country="Argentina")
    r = client.get("/locations/?city=buenos")
    assert r.status_code == 200
    assert len(r.json()) == 1


def test_location_includes_movies(client):
    movie_id = make_movie(client).json()["id"]
    loc_id = make_location(client).json()["id"]
    client.post("/movie-locations/", json={"movie_id": movie_id, "location_id": loc_id})
    r = client.get(f"/locations/{loc_id}")
    assert len(r.json()["movies"]) == 1


def test_get_location_not_found(client):
    r = client.get("/locations/9999")
    assert r.status_code == 404


def test_update_location(client):
    loc_id = make_location(client).json()["id"]
    r = client.put(f"/locations/{loc_id}", json={"city": "Rosario"})
    assert r.status_code == 200
    assert r.json()["city"] == "Rosario"


def test_update_location_not_found(client):
    r = client.put("/locations/9999", json={"city": "Rosario"})
    assert r.status_code == 404


def test_delete_location(client):
    loc_id = make_location(client).json()["id"]
    r = client.delete(f"/locations/{loc_id}")
    assert r.status_code == 200
    assert client.get(f"/locations/{loc_id}").status_code == 404


def test_delete_location_not_found(client):
    r = client.delete("/locations/9999")
    assert r.status_code == 404
