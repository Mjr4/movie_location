from logging.config import fileConfig

from sqlalchemy import create_engine, pool

from alembic import context
from app import config as app_config
from app.models import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name, disable_existing_loggers=False)

target_metadata = Base.metadata

# sqlalchemy.url puede fijarse por código (tests); si no, se usa el DATABASE_URL de la app.
url = config.get_main_option("sqlalchemy.url") or app_config.DATABASE_URL

# SQLite no soporta la mayoría de ALTER TABLE: batch recrea la tabla para aplicarlos.
context_options = dict(target_metadata=target_metadata, render_as_batch=True, compare_type=True)


def run_migrations_offline() -> None:
    context.configure(url=url, literal_binds=True, dialect_opts={"paramstyle": "named"}, **context_options)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_engine(url, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(connection=connection, **context_options)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
