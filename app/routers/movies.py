from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from ..auth import require_api_key
from ..config import MAX_PAGE_SIZE
from ..database import get_db
from .. import crud, schemas

router = APIRouter(prefix="/movies", tags=["movies"])


@router.get("/", response_model=list[schemas.MovieRead])
def list_movies(title: Optional[str] = None, genre: Optional[str] = None, skip: int = 0, limit: int = Query(100, ge=1, le=MAX_PAGE_SIZE), db: Session = Depends(get_db)):
    return crud.get_movies(db, title=title, genre=genre, skip=skip, limit=limit)


@router.post("/", response_model=schemas.MovieRead, status_code=201, dependencies=[Depends(require_api_key)])
def create_movie(movie: schemas.MovieCreate, db: Session = Depends(get_db)):
    return crud.create_movie(db, movie)


@router.get("/{movie_id}", response_model=schemas.MovieRead)
def get_movie(movie_id: int, db: Session = Depends(get_db)):
    db_movie = crud.get_movie(db, movie_id)
    if not db_movie:
        raise HTTPException(status_code=404, detail="Película no encontrada")
    return db_movie

@router.get("/{movie_id}/locations", response_model=list[schemas.LocationRead])
def list_movie_locations(movie_id: int, db: Session = Depends(get_db)):
    movie = crud.get_movie(db, movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Película no encontrada")
    return crud.get_locations_by_movie(db, movie_id)

@router.put("/{movie_id}", response_model=schemas.MovieRead, dependencies=[Depends(require_api_key)])
def update_movie(movie_id: int, movie: schemas.MovieUpdate, db: Session = Depends(get_db)):
    db_movie = crud.update_movie(db, movie_id, movie)
    if not db_movie:
        raise HTTPException(status_code=404, detail="Película no encontrada")
    return db_movie


@router.delete("/{movie_id}", status_code=204, dependencies=[Depends(require_api_key)])
def delete_movie(movie_id: int, db: Session = Depends(get_db)):
    db_movie = crud.delete_movie(db, movie_id)
    if not db_movie:
        raise HTTPException(status_code=404, detail="Película no encontrada")
