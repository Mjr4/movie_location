from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from ..auth import require_api_key
from ..config import MAX_PAGE_SIZE
from ..database import get_db
from .. import crud, schemas

router = APIRouter(prefix="/locations", tags=["locations"])


@router.get("/", response_model=list[schemas.LocationRead])
def list_locations(
    city: Optional[str] = None,
    country: Optional[str] = None,
    type: Optional[str] = None,  # Filtro por tipo de locación (exterior/interior/mixto)
    skip: int = 0,
    limit: int = Query(100, ge=1, le=MAX_PAGE_SIZE),
    db: Session = Depends(get_db),
):
    # Retorna listado de locaciones con filtros opcionales
    return crud.get_locations(db, city=city, country=country, type=type, skip=skip, limit=limit)


@router.post("/", response_model=schemas.LocationRead, status_code=201, dependencies=[Depends(require_api_key)])
def create_location(location: schemas.LocationCreate, db: Session = Depends(get_db)):
    return crud.create_location(db, location)


@router.get("/{location_id}", response_model=schemas.LocationRead)
def get_location(location_id: int, db: Session = Depends(get_db)):
    db_location = crud.get_location(db, location_id)
    if not db_location:
        raise HTTPException(status_code=404, detail="Locación no encontrada")
    return db_location


@router.put("/{location_id}", response_model=schemas.LocationRead, dependencies=[Depends(require_api_key)])
def update_location(location_id: int, location: schemas.LocationUpdate, db: Session = Depends(get_db)):
    db_location = crud.update_location(db, location_id, location)
    if not db_location:
        raise HTTPException(status_code=404, detail="Locación no encontrada")
    return db_location


@router.delete("/{location_id}", status_code=204, dependencies=[Depends(require_api_key)])
def delete_location(location_id: int, db: Session = Depends(get_db)):
    db_location = crud.delete_location(db, location_id)
    if not db_location:
        raise HTTPException(status_code=404, detail="Locación no encontrada")
