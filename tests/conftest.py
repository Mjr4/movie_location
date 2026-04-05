import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import get_db
from app.models import Base

SQLALCHEMY_TEST_URL = "sqlite://"  # in-memory

engine = create_engine(
    SQLALCHEMY_TEST_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,  # todas las conexiones usan el mismo in-memory DB
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db):
    def override_get_db():
        try:
            yield db
        except Exception:
            db.rollback()
            raise

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ── Factories ─────────────────────────────────────────────────────────────────

def make_movie(client, **kwargs):
    data = {"title": "Test Movie", "year": 2020, "director": "Director", "genre": "Drama", **kwargs}
    return client.post("/movies/", json=data)


def make_location(client, **kwargs):
    data = {
        "name": "Test Location",
        "location_type": "exterior",
        "city": "Buenos Aires",
        "country": "Argentina",
        **kwargs,
    }
    return client.post("/locations/", json=data)
