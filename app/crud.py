from sqlalchemy.orm import Session
from . import models, schemas


# ── Directors / Genres ────────────────────────────────────────────────────────

def get_or_create_director(db: Session, name: str) -> models.Director:
    director = db.query(models.Director).filter(models.Director.name == name).first()
    if director:
        return director
    director = models.Director(name=name)
    db.add(director)
    db.flush()  # asigna id para poder resolver nombres repetidos dentro del mismo request
    return director


def get_or_create_genre(db: Session, name: str) -> models.Genre:
    genre = db.query(models.Genre).filter(models.Genre.name == name).first()
    if genre:
        return genre
    genre = models.Genre(name=name)
    db.add(genre)
    db.flush()
    return genre


# ── Movies ────────────────────────────────────────────────────────────────────

def get_movies(db: Session, title: str | None = None, genre: str | None = None, skip: int = 0, limit: int = 100):
    q = db.query(models.Movie)
    if title:
        q = q.filter(models.Movie.title.ilike(f"%{title}%"))
    if genre:
        q = q.join(models.Movie.genres).filter(models.Genre.name.ilike(f"%{genre}%")).distinct()
    return q.offset(skip).limit(limit).all()


def get_movie(db: Session, movie_id: int):
    return db.query(models.Movie).filter(models.Movie.id == movie_id).first()


def create_movie(db: Session, movie: schemas.MovieCreate):
    db_movie = models.Movie(title=movie.title, year=movie.year, imdb_id=movie.imdb_id)
    db.add(db_movie)
    db_movie.directors = [get_or_create_director(db, name) for name in movie.directors]
    db_movie.genres = [get_or_create_genre(db, name) for name in movie.genres]
    db.commit()
    db.refresh(db_movie)
    return db_movie


def update_movie(db: Session, movie_id: int, movie: schemas.MovieUpdate):
    db_movie = get_movie(db, movie_id)
    if not db_movie:
        return None
    data = movie.model_dump(exclude_unset=True)
    if "directors" in data:
        db_movie.directors = [get_or_create_director(db, name) for name in data.pop("directors")]
    if "genres" in data:
        db_movie.genres = [get_or_create_genre(db, name) for name in data.pop("genres")]
    for key, value in data.items():
        setattr(db_movie, key, value)
    db.commit()
    db.refresh(db_movie)
    return db_movie


def delete_movie(db: Session, movie_id: int):
    db_movie = get_movie(db, movie_id)
    if not db_movie:
        return None
    db.delete(db_movie)
    db.commit()
    return db_movie


# ── Locations ─────────────────────────────────────────────────────────────────

def get_locations(
    db: Session,
    city: str | None = None,
    country: str | None = None,
    type: str | None = None,
    skip: int = 0,
    limit: int = 100,
):
    # Buscar locaciones con filtros opcionales (city, country, type)
    q = db.query(models.Location)
    if city:
        q = q.filter(models.Location.city.ilike(f"%{city}%"))
    if country:
        q = q.filter(models.Location.country.ilike(f"%{country}%"))
    if type:
        # Filtrar por tipo de locación (exterior, interior, mixto)
        q = q.filter(models.Location.location_type.ilike(f"%{type}%"))
    return q.offset(skip).limit(limit).all()


def get_location(db: Session, location_id: int):
    return db.query(models.Location).filter(models.Location.id == location_id).first()


def create_location(db: Session, location: schemas.LocationCreate):
    db_location = models.Location(**location.model_dump())
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location


def update_location(db: Session, location_id: int, location: schemas.LocationUpdate):
    db_location = get_location(db, location_id)
    if not db_location:
        return None
    for key, value in location.model_dump(exclude_unset=True).items():
        setattr(db_location, key, value)
    db.commit()
    db.refresh(db_location)
    return db_location


def delete_location(db: Session, location_id: int):
    db_location = get_location(db, location_id)
    if not db_location:
        return None
    db.delete(db_location)
    db.commit()
    return db_location


# ── MovieLocations ────────────────────────────────────────────────────────────

def get_movie_locations(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.MovieLocation).offset(skip).limit(limit).all()

def get_locations_by_movie(db: Session, movie_id: int, skip: int = 0, limit: int = 100):
    return (
        db.query(models.Location)
        .join(models.MovieLocation, models.MovieLocation.location_id == models.Location.id)
        .filter(models.MovieLocation.movie_id == movie_id)
        .offset(skip)
        .limit(limit)
        .all()
    )

def create_movie_location(db: Session, data: schemas.MovieLocationCreate):
    db_ml = models.MovieLocation(**data.model_dump())
    db.add(db_ml)
    db.commit()
    db.refresh(db_ml)
    return db_ml


def delete_movie_location(db: Session, movie_location_id: int):
    db_ml = db.query(models.MovieLocation).filter(models.MovieLocation.id == movie_location_id).first()
    if not db_ml:
        return None
    db.delete(db_ml)
    db.commit()
    return db_ml
