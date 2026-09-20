import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import config
from app.main import app
from app.database import get_db
from app.models import Base

SQLALCHEMY_TEST_URL = "sqlite://"  # in-memory
TEST_API_KEY = "test-key"

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


@pytest.fixture(autouse=True)
def api_keys(monkeypatch):
    monkeypatch.setattr(config, "API_KEYS", {TEST_API_KEY})


@pytest.fixture
def _override_db(db):
    def override_get_db():
        try:
            yield db
        except Exception:
            db.rollback()
            raise

    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def client(_override_db):
    """Cliente autenticado: envía X-API-Key en todas las requests."""
    with TestClient(app, headers={"X-API-Key": TEST_API_KEY}) as c:
        yield c


@pytest.fixture
def anon_client(_override_db):
    """Cliente sin credenciales, para verificar que las escrituras se rechazan."""
    with TestClient(app) as c:
        yield c


# ── Factories ─────────────────────────────────────────────────────────────────

def make_movie(client, **kwargs):
    data = {"title": "Test Movie", "year": 2020, "directors": ["Director"], "genres": ["Drama"], **kwargs}
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
