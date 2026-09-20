from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

from .config import MAX_IMPORT_BATCH


# ── Location ──────────────────────────────────────────────────────────────────

class LocationBase(BaseModel):
    name: str
    location_type: Optional[str] = None  # exterior / interior / mixto (no siempre disponible: ver locaciones geocodificadas)
    city: Optional[str] = None  # el geocoding a veces solo resuelve país/región, sin ciudad
    country: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    description: Optional[str] = None


class LocationCreate(LocationBase):
    pass


class LocationUpdate(BaseModel):
    name: Optional[str] = None
    location_type: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    description: Optional[str] = None


class LocationRead(LocationBase):
    id: int
    created_at: datetime
    movies: list["MovieSummary"] = []

    model_config = {"from_attributes": True}


# ── Director / Genre ──────────────────────────────────────────────────────────

class DirectorRead(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class GenreRead(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


# ── Movie ─────────────────────────────────────────────────────────────────────

class MovieBase(BaseModel):
    title: str
    year: int
    directors: list[str] = []
    genres: list[str] = []
    imdb_id: Optional[str] = None


class MovieCreate(MovieBase):
    pass


class MovieUpdate(BaseModel):
    title: Optional[str] = None
    year: Optional[int] = None
    directors: Optional[list[str]] = None
    genres: Optional[list[str]] = None
    imdb_id: Optional[str] = None


class MovieSummary(BaseModel):
    """Vista liviana de Movie (con directors/genres ya resueltos) para anidar en Location/MovieLocation sin recursión."""
    id: int
    title: str
    year: int
    imdb_id: Optional[str] = None
    directors: list[DirectorRead] = []
    genres: list[GenreRead] = []

    model_config = {"from_attributes": True}


class MovieRead(MovieSummary):
    created_at: datetime
    locations: list[LocationRead] = []

    model_config = {"from_attributes": True}


# ── MovieLocation ─────────────────────────────────────────────────────────────

class MovieLocationCreate(BaseModel):
    movie_id: int
    location_id: int
    scene_description: Optional[str] = None
    notes: Optional[str] = None


class MovieLocationRead(MovieLocationCreate):
    id: int
    created_at: datetime
    movie: Optional[MovieSummary] = None
    location: Optional[LocationBase] = None

    model_config = {"from_attributes": True}


# ── Import (carga masiva desde el pipeline) ──────────────────────────────────

class ImportLocation(BaseModel):
    name: str
    city: Optional[str] = None
    country: str
    latitude: float = Field(ge=-90, le=90)  # clave natural junto con longitude
    longitude: float = Field(ge=-180, le=180)
    source_text: Optional[str] = None  # solo se escribe al insertar; no se expone en LocationRead


class ImportMovie(BaseModel):
    imdb_id: str = Field(min_length=1)  # clave natural de movies
    title: str
    year: int
    directors: list[str] = []
    genres: list[str] = []
    locations: list[ImportLocation] = []


class ImportRequest(BaseModel):
    movies: list[ImportMovie] = Field(max_length=MAX_IMPORT_BATCH)


class ImportResult(BaseModel):
    movies_created: int
    movies_updated: int
    locations_created: int
    locations_updated: int
    associations_created: int
    associations_existing: int
