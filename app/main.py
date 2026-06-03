from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
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


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    # Extraer detalles del error de validación
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"][1:])  # Ignorar "body"
        errors.append({"field": field, "message": error["msg"]})

    return JSONResponse(
        status_code=400,
        content={"detail": "Validación fallida", "errors": errors},
    )


app.include_router(movies.router)
app.include_router(locations.router)
app.include_router(movie_locations.router)


@app.get("/")
def read_root():
    return {"message": "Movie Locations API", "docs": "/docs"}
