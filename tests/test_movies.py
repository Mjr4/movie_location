from .conftest import make_movie


def test_create_movie(client):
    r = make_movie(client)
    assert r.status_code == 201
    assert r.json()["title"] == "Test Movie"


def test_create_movie_duplicate(client):
    # El título ya no es único (puede haber remakes con el mismo nombre);
    # la clave natural real es imdb_id.
    make_movie(client, title="Inception", imdb_id="tt1375666")
    r = make_movie(client, title="Otra película", imdb_id="tt1375666")
    assert r.status_code == 409


def test_list_movies(client):
    make_movie(client, title="Movie A")
    make_movie(client, title="Movie B")
    r = client.get("/movies/")
    assert r.status_code == 200
    assert len(r.json()) == 2


def test_filter_by_title(client):
    make_movie(client, title="The Godfather")
    make_movie(client, title="Goodfellas")
    r = client.get("/movies/?title=godfather")
    assert r.status_code == 200
    assert len(r.json()) == 1
    assert r.json()[0]["title"] == "The Godfather"


def test_filter_by_genre(client):
    make_movie(client, title="Movie A", genres=["Drama"])
    make_movie(client, title="Movie B", genres=["Comedy"])
    r = client.get("/movies/?genre=drama")
    assert r.status_code == 200
    assert all("Drama" in [g["name"] for g in m["genres"]] for m in r.json())


def test_get_movie(client):
    movie_id = make_movie(client).json()["id"]
    r = client.get(f"/movies/{movie_id}")
    assert r.status_code == 200
    assert r.json()["id"] == movie_id


def test_get_movie_not_found(client):
    r = client.get("/movies/9999")
    assert r.status_code == 404


def test_update_movie(client):
    movie_id = make_movie(client).json()["id"]
    r = client.put(f"/movies/{movie_id}", json={"year": 2025})
    assert r.status_code == 200
    assert r.json()["year"] == 2025


def test_update_movie_not_found(client):
    r = client.put("/movies/9999", json={"year": 2025})
    assert r.status_code == 404


def test_delete_movie(client):
    movie_id = make_movie(client).json()["id"]
    r = client.delete(f"/movies/{movie_id}")
    assert r.status_code == 204
    assert client.get(f"/movies/{movie_id}").status_code == 404


def test_delete_movie_not_found(client):
    r = client.delete("/movies/9999")
    assert r.status_code == 404


def test_movie_includes_locations(client):
    from .conftest import make_location
    movie_id = make_movie(client).json()["id"]
    loc_id = make_location(client).json()["id"]
    client.post("/movie-locations/", json={"movie_id": movie_id, "location_id": loc_id})
    r = client.get(f"/movies/{movie_id}")
    assert len(r.json()["locations"]) == 1
