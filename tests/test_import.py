import pytest
from sqlalchemy.exc import OperationalError

from app import config, crud, models

URL = "/import/movies"


def loc(lat=10.0, lon=20.0, name="Loc", city="City", country="Country", source_text=None):
    return {"name": name, "city": city, "country": country, "latitude": lat, "longitude": lon, "source_text": source_text}


def mov(imdb="tt0000001", title="Movie", year=2000, directors=("Dir",), genres=("Gen",), locations=()):
    return {"imdb_id": imdb, "title": title, "year": year, "directors": list(directors),
            "genres": list(genres), "locations": list(locations)}


def post(client, *movies):
    return client.post(URL, json={"movies": list(movies)})


def db_counts(db):
    return {m.__tablename__: db.query(m).count() for m in (models.Movie, models.Location, models.MovieLocation)}


def test_creates_movies_locations_and_associations(client, db):
    r = post(
        client,
        mov("tt1", locations=[loc(1, 1, name="A", source_text="raw A"), loc(2, 2, name="B")]),
        mov("tt2", title="Other", locations=[]),
    )

    assert r.status_code == 200
    assert r.json() == {
        "movies_created": 2, "movies_updated": 0, "locations_created": 2,
        "locations_updated": 0, "associations_created": 2, "associations_existing": 0,
    }
    movie = client.get("/movies/").json()[0]
    assert movie["directors"][0]["name"] == "Dir" and movie["genres"][0]["name"] == "Gen"
    assert db.query(models.Location).filter_by(name="A").one().source_text == "raw A"


def test_movie_with_empty_locations(client, db):
    r = post(client, mov(locations=[]))

    assert r.status_code == 200
    assert r.json()["movies_created"] == 1 and r.json()["associations_created"] == 0
    assert db_counts(db) == {"movies": 1, "locations": 0, "movie_location": 0}


def test_resend_same_payload_is_idempotent(client, db):
    payload = [mov("tt1", locations=[loc(1, 1), loc(2, 2)]), mov("tt2", locations=[loc(1, 1)])]
    post(client, *payload)
    before = db_counts(db)

    r = post(client, *payload)

    assert r.status_code == 200
    assert r.json() == {
        "movies_created": 0, "movies_updated": 2, "locations_created": 0,
        "locations_updated": 3, "associations_created": 0, "associations_existing": 3,
    }
    assert db_counts(db) == before


def test_existing_records_are_updated_but_source_text_is_kept(client, db):
    post(client, mov("tt1", title="Old", year=1990, directors=["D1"], genres=["G1"],
                     locations=[loc(1, 1, name="Old", city="Old", country="Old", source_text="first")]))

    r = post(client, mov("tt1", title="New", year=2001, directors=["D2"], genres=["G2", "G3"],
                         locations=[loc(1, 1, name="New", city=None, country="NewC", source_text="second")]))

    assert r.json()["movies_updated"] == 1 and r.json()["locations_updated"] == 1
    movie = db.query(models.Movie).filter_by(imdb_id="tt1").one()
    assert (movie.title, movie.year) == ("New", 2001)
    assert [d.name for d in movie.directors] == ["D2"]
    assert sorted(g.name for g in movie.genres) == ["G2", "G3"]
    location = db.query(models.Location).one()
    assert (location.name, location.city, location.country) == ("New", None, "NewC")
    assert location.source_text == "first"


def test_associations_are_additive_and_keep_scene_data(client, db):
    post(client, mov("tt1", locations=[loc(1, 1)]))
    link = db.query(models.MovieLocation).one()
    link.scene_description, link.notes = "escena", "nota"
    db.commit()

    post(client, mov("tt1", locations=[loc(2, 2)]))

    assert db.query(models.MovieLocation).count() == 2
    kept = db.query(models.MovieLocation).filter_by(location_id=link.location_id).one()
    assert (kept.scene_description, kept.notes) == ("escena", "nota")


def test_same_coordinates_within_batch_reuse_the_location(client, db):
    r = post(client, mov("tt1", locations=[loc(5, 5, name="First")]), mov("tt2", locations=[loc(5, 5, name="Second")]))

    assert r.json()["locations_created"] == 1 and r.json()["locations_updated"] == 1
    assert r.json()["associations_created"] == 2
    assert db.query(models.Location).one().name == "Second"


def test_repeated_imdb_id_within_batch_is_processed_in_order(client, db):
    r = post(client, mov("tt1", title="First"), mov("tt1", title="Second"))

    assert r.json()["movies_created"] == 1 and r.json()["movies_updated"] == 1
    assert db.query(models.Movie).one().title == "Second"


def test_invalid_item_returns_400_with_path_and_persists_nothing(client, db):
    r = post(client, mov("tt1", locations=[loc(1, 1)]), mov("tt2", locations=[loc(lat=999)]))

    assert r.status_code == 400
    assert "movies.1.locations.0.latitude" in [e["field"] for e in r.json()["errors"]]
    assert db_counts(db) == {"movies": 0, "locations": 0, "movie_location": 0}


@pytest.mark.parametrize("field", ["latitude", "longitude"])
def test_coordinates_are_required_and_not_null(client, field):
    for bad in ({field: None}, {}):
        item = loc()
        if bad:
            item.update(bad)
        else:
            del item[field]
        r = post(client, mov(locations=[item]))
        assert r.status_code == 400
        assert f"movies.0.locations.0.{field}" in [e["field"] for e in r.json()["errors"]]


def test_imdb_id_is_required(client):
    item = mov()
    del item["imdb_id"]
    assert post(client, item).status_code == 400
    assert post(client, mov(imdb="")).status_code == 400


def test_failure_mid_batch_rolls_back_everything(client, db, monkeypatch):
    calls = []

    def flaky_genre(session, name):
        calls.append(name)
        if len(calls) == 2:
            raise OperationalError("stmt", {}, Exception("boom"))
        return crud_get_or_create_genre(session, name)

    crud_get_or_create_genre = crud.get_or_create_genre
    monkeypatch.setattr(crud, "get_or_create_genre", flaky_genre)

    r = post(client, mov("tt1", genres=["G1"], locations=[loc(1, 1)]), mov("tt2", genres=["G2"], locations=[loc(2, 2)]))

    assert r.status_code == 503
    assert db_counts(db) == {"movies": 0, "locations": 0, "movie_location": 0}


def test_batch_size_limit(client):
    ok = [mov(f"tt{i}") for i in range(config.MAX_IMPORT_BATCH)]
    assert post(client, *ok).status_code == 200
    assert post(client, *ok, mov("tt-extra")).status_code == 400


def test_requires_api_key(anon_client, db):
    r = anon_client.post(URL, json={"movies": [mov()]})

    assert r.status_code == 401
    assert db_counts(db) == {"movies": 0, "locations": 0, "movie_location": 0}
