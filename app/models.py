from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()


class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True)
    title = Column(String, unique=True, index=True)
    year = Column(Integer)
    director = Column(String)
    genre = Column(String)
    imdb_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    locations = relationship(
        "Location",
        secondary="movie_location",
        back_populates="movies"
    )


class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True)
    name = Column(String, index=True)
    location_type = Column(String)  # exterior/interior/mixto
    city = Column(String, index=True)
    country = Column(String, index=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    movies = relationship(
        "Movie",
        secondary="movie_location",
        back_populates="locations"
    )


class MovieLocation(Base):
    __tablename__ = "movie_location"

    id = Column(Integer, primary_key=True)
    movie_id = Column(Integer, ForeignKey("movies.id"), index=True)
    location_id = Column(Integer, ForeignKey("locations.id"), index=True)
    scene_description = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (UniqueConstraint("movie_id", "location_id"),)
