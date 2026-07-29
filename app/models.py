from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Table, UniqueConstraint
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()


movie_director = Table(
    "movie_director",
    Base.metadata,
    Column("movie_id", Integer, ForeignKey("movies.id"), primary_key=True),
    Column("director_id", Integer, ForeignKey("directors.id"), primary_key=True),
)

movie_genre = Table(
    "movie_genre",
    Base.metadata,
    Column("movie_id", Integer, ForeignKey("movies.id"), primary_key=True),
    Column("genre_id", Integer, ForeignKey("genres.id"), primary_key=True),
)


class Director(Base):
    __tablename__ = "directors"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, index=True)

    movies = relationship("Movie", secondary=movie_director, back_populates="directors")


class Genre(Base):
    __tablename__ = "genres"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, index=True)

    movies = relationship("Movie", secondary=movie_genre, back_populates="genres")


class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True)
    title = Column(String, index=True)  # no único: distintas películas (remakes, etc.) pueden compartir título
    year = Column(Integer)
    imdb_id = Column(String, unique=True, index=True, nullable=True)  # clave natural real
    created_at = Column(DateTime, default=datetime.utcnow)

    directors = relationship("Director", secondary=movie_director, back_populates="movies")
    genres = relationship("Genre", secondary=movie_genre, back_populates="movies")

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
    source_text = Column(String, nullable=True)  # string crudo (uno de los orígenes); ya no es único porque varios strings distintos pueden geocodificar al mismo lugar
    created_at = Column(DateTime, default=datetime.utcnow)

    # clave natural real: coordenadas resueltas por geocoding (varios source_text distintos
    # pueden apuntar al mismo lugar real, ej. "London, UK" y "London, UK (Studio)"). NULL en
    # ambas columnas no viola la constraint (semántica UNIQUE de SQLite), así que locaciones
    # creadas a mano sin coordenadas siguen sin restricción.
    __table_args__ = (UniqueConstraint("latitude", "longitude", name="uq_location_coords"),)

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
