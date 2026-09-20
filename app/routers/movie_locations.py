from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..auth import require_api_key
from ..config import MAX_PAGE_SIZE
from ..database import get_db
from .. import crud, schemas

router = APIRouter(prefix="/movie-locations", tags=["movie-locations"])


@router.get("/", response_model=list[schemas.MovieLocationRead])
def list_movie_locations(skip: int = 0, limit: int = Query(100, ge=1, le=MAX_PAGE_SIZE), db: Session = Depends(get_db)):
    return crud.get_movie_locations(db, skip=skip, limit=limit)


@router.post("/", response_model=schemas.MovieLocationRead, status_code=201, dependencies=[Depends(require_api_key)])
def create_movie_location(data: schemas.MovieLocationCreate, db: Session = Depends(get_db)):
    if not crud.get_movie(db, data.movie_id):
        raise HTTPException(status_code=404, detail=f"Película con id {data.movie_id} no encontrada")
    if not crud.get_location(db, data.location_id):
        raise HTTPException(status_code=404, detail=f"Locación con id {data.location_id} no encontrada")
    return crud.create_movie_location(db, data)


@router.delete("/{movie_location_id}", status_code=204, dependencies=[Depends(require_api_key)])
def delete_movie_location(movie_location_id: int, db: Session = Depends(get_db)):
    db_ml = crud.delete_movie_location(db, movie_location_id)
    if not db_ml:
        raise HTTPException(status_code=404, detail="Asociación no encontrada")
