from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from .database import engine
from .models import Base
from .routers import movies, locations, movie_locations

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Movie Locations API")

#TODO: actualizar para prod
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    return JSONResponse(
        status_code=409,
        content={"detail": "El recurso ya existe o viola una restricción de unicidad"},
    )


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError):
    return JSONResponse(
        status_code=503,
        content={"detail": "Error en la base de datos, intente nuevamente"},
    )


app.include_router(movies.router)
app.include_router(locations.router)
app.include_router(movie_locations.router)


@app.get("/")
def read_root():
    return {"message": "Movie Locations API", "docs": "/docs"}
