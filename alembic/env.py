import asyncio
import os
from logging.config import fileConfig

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import pool
from alembic import context
from dotenv import load_dotenv

from app.db.base import Base  


load_dotenv() 

# Alembic Config
config = context.config

# Logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Target metadata
target_metadata = Base.metadata

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")


def run_migrations_offline():
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    engine = create_async_engine(
        DATABASE_URL,
        poolclass=pool.NullPool,
    )

    async with engine.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
