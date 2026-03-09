from sqlalchemy.orm import Session
from . import models, schemas


# ── Movies ────────────────────────────────────────────────────────────────────

def get_movies(db: Session, genre: str | None = None, skip: int = 0, limit: int = 100):
    q = db.query(models.Movie)
    if genre:
        q = q.filter(models.Movie.genre.ilike(f"%{genre}%"))
    return q.offset(skip).limit(limit).all()


def get_movie(db: Session, movie_id: int):
    return db.query(models.Movie).filter(models.Movie.id == movie_id).first()


def create_movie(db: Session, movie: schemas.MovieCreate):
    db_movie = models.Movie(**movie.model_dump())
    db.add(db_movie)
    db.commit()
    db.refresh(db_movie)
    return db_movie


def update_movie(db: Session, movie_id: int, movie: schemas.MovieUpdate):
    db_movie = get_movie(db, movie_id)
    if not db_movie:
        return None
    for key, value in movie.model_dump(exclude_unset=True).items():
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
    skip: int = 0,
    limit: int = 100,
):
    q = db.query(models.Location)
    if city:
        q = q.filter(models.Location.city.ilike(f"%{city}%"))
    if country:
        q = q.filter(models.Location.country.ilike(f"%{country}%"))
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
