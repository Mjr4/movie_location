import sqlite3
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config

ROOT = Path(__file__).resolve().parent.parent
BASELINE = "a442bfbadc16"


@pytest.fixture
def alembic_cfg(tmp_path):
    cfg = Config(str(ROOT / "alembic.ini"))
    cfg.set_main_option("sqlalchemy.url", f"sqlite:///{tmp_path / 'migrations.db'}")
    return cfg, tmp_path / "migrations.db"


def test_migrations_match_models(alembic_cfg):
    cfg, _ = alembic_cfg
    command.upgrade(cfg, "head")
    command.check(cfg)  # falla si los modelos cambiaron sin una migración que lo refleje


def test_adopting_pre_alembic_db_names_coords_constraint(alembic_cfg):
    cfg, db_path = alembic_cfg
    command.upgrade(cfg, BASELINE)

    # Simula una base creada a mano antes de Alembic: UNIQUE (latitude, longitude) sin nombre.
    con = sqlite3.connect(db_path)
    con.execute("INSERT INTO locations (name, latitude, longitude) VALUES ('Paris', 48.85, 2.35)")
    con.execute("PRAGMA writable_schema = ON")
    con.execute(
        "UPDATE sqlite_master SET sql = replace(sql, 'CONSTRAINT uq_location_coords UNIQUE', 'UNIQUE') "
        "WHERE name = 'locations'"
    )
    con.commit()
    con.close()

    command.upgrade(cfg, "head")
    command.check(cfg)

    con = sqlite3.connect(db_path)
    assert con.execute("SELECT name FROM locations").fetchall() == [("Paris",)]
    with pytest.raises(sqlite3.IntegrityError):
        con.execute("INSERT INTO locations (name, latitude, longitude) VALUES ('Dup', 48.85, 2.35)")
    con.close()
