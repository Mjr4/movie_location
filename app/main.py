from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

app.include_router(movies.router)
app.include_router(locations.router)
app.include_router(movie_locations.router)


@app.get("/")
def read_root():
    return {"message": "Movie Locations API", "docs": "/docs"}
