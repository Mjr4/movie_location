from pydantic import BaseModel
from datetime import datetime
from typing import Optional


# ── Location ──────────────────────────────────────────────────────────────────

class LocationBase(BaseModel):
    name: str
    location_type: str  # exterior / interior / mixto
    city: str
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
    movies: list["MovieBase"] = []

    model_config = {"from_attributes": True}


# ── Movie ─────────────────────────────────────────────────────────────────────

class MovieBase(BaseModel):
    title: str
    year: int
    director: str
    genre: str
    imdb_id: Optional[str] = None


class MovieCreate(MovieBase):
    pass


class MovieUpdate(BaseModel):
    title: Optional[str] = None
    year: Optional[int] = None
    director: Optional[str] = None
    genre: Optional[str] = None
    imdb_id: Optional[str] = None


class MovieRead(MovieBase):
    id: int
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
    movie: Optional[MovieBase] = None
    location: Optional[LocationBase] = None

    model_config = {"from_attributes": True}
