class Location(Base):
    __tablename__ = "locations"
    
    id: int = Column(Integer, primary_key=True)
    name: str = Column(String, index=True)
    location_type: str = Column(String)  # exterior/interior/mixto
    city: str = Column(String, index=True)
    country: str = Column(String, index=True)
    latitude: float = Column(Float, nullable=True)
    longitude: float = Column(Float, nullable=True)
    description: str = Column(String, nullable=True)
    created_at: DateTime = Column(DateTime, default=datetime.utcnow)
    
    # Relación con películas
    movies = relationship(
        "Movie",
        secondary="movie_location",
        back_populates="locations"
    )


class MovieLocation(Base):
    __tablename__ = "movie_location"
    
    id: int = Column(Integer, primary_key=True)
    movie_id: int = Column(Integer, ForeignKey("movies.id"), index=True)
    location_id: int = Column(Integer, ForeignKey("locations.id"), index=True)
    scene_description: str = Column(String, nullable=True)
    notes: str = Column(Text, nullable=True)
    created_at: DateTime = Column(DateTime, default=datetime.utcnow)
    
    # Índice único para evitar duplicados
    __table_args__ = (UniqueConstraint('movie_id', 'location_id'),)


    # models/movie.py
class Movie(Base):
    __tablename__ = "movies"
    
    id: int = Column(Integer, primary_key=True)
    title: str = Column(String, unique=True, index=True)
    year: int = Column(Integer)
    director: str = Column(String)
    genre: str = Column(String)
    imdb_id: str = Column(String, nullable=True)
    created_at: DateTime = Column(DateTime, default=datetime.utcnow)
    
    # Relación con locaciones
    locations = relationship(
        "Location",
        secondary="movie_location",
        back_populates="movies"
    )