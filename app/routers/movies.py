from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from ..database import get_db
from .. import crud, schemas

router = APIRouter(prefix="/movies", tags=["movies"])


@router.get("/", response_model=list[schemas.MovieRead])
def list_movies(title: Optional[str] = None, genre: Optional[str] = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_movies(db, title=title, genre=genre, skip=skip, limit=limit)


@router.post("/", response_model=schemas.MovieRead, status_code=201)
def create_movie(movie: schemas.MovieCreate, db: Session = Depends(get_db)):
    return crud.create_movie(db, movie)


@router.get("/{movie_id}", response_model=schemas.MovieRead)
def get_movie(movie_id: int, db: Session = Depends(get_db)):
    db_movie = crud.get_movie(db, movie_id)
    if not db_movie:
        raise HTTPException(status_code=404, detail="Película no encontrada")
    return db_movie


@router.put("/{movie_id}", response_model=schemas.MovieRead)
def update_movie(movie_id: int, movie: schemas.MovieUpdate, db: Session = Depends(get_db)):
    db_movie = crud.update_movie(db, movie_id, movie)
    if not db_movie:
        raise HTTPException(status_code=404, detail="Película no encontrada")
    return db_movie


@router.delete("/{movie_id}", response_model=schemas.MovieRead)
def delete_movie(movie_id: int, db: Session = Depends(get_db)):
    db_movie = crud.delete_movie(db, movie_id)
    if not db_movie:
        raise HTTPException(status_code=404, detail="Película no encontrada")
    return db_movie
