from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..auth import require_api_key
from ..database import get_db
from .. import crud, schemas

router = APIRouter(prefix="/import", tags=["import"], dependencies=[Depends(require_api_key)])


@router.post("/movies", response_model=schemas.ImportResult)
def import_movies(payload: schemas.ImportRequest, db: Session = Depends(get_db)):
    return crud.import_movies(db, payload.movies)
