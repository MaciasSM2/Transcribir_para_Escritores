from logging.config import fileConfig
import os
import sys

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Añadir backend/ al path para importar database y models
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import Base, SQLALCHEMY_DATABASE_URL  # noqa: E402
import models  # noqa: E402, F401  — necesario para que Base.metadata conozca todas las tablas

# Alembic Config object
config = context.config

# Interpretar config de logging del .ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadatos del modelo para autogenerate
target_metadata = Base.metadata

# Sobreescribir sqlalchemy.url con la URL real del proyecto
# (evita duplicar la ruta en alembic.ini)
config.set_main_option("sqlalchemy.url", SQLALCHEMY_DATABASE_URL)


def run_migrations_offline() -> None:
    """Modo offline: emite SQL sin conectar a la BD."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # SQLite no soporta ALTER TABLE nativo; Alembic usa batch_mode
        render_as_batch=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Modo online: conecta a la BD y aplica migraciones."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # SQLite requiere batch_mode para ALTER TABLE
            render_as_batch=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
