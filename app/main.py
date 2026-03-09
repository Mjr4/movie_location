from fastapi import FastAPI

from .database import engine
from .models import Base
from .routers import movies, locations, movie_locations

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Movie Locations API")

app.include_router(movies.router)
app.include_router(locations.router)
app.include_router(movie_locations.router)


@app.get("/")
def read_root():
    return {"message": "Movie Locations API", "docs": "/docs"}
