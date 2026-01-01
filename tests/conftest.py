import os
import time
import asyncio
import pytest
import docker
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

from httpx import AsyncClient
from fastapi import FastAPI

from dotenv import load_dotenv

from app.core.config import settings
from app.db.base import Base
import app.db.models  # noqa: F401
from app.main import app as fastapi_app

load_dotenv()

POSTGRES_USER = os.getenv("TEST_POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("TEST_POSTGRES_PASSWORD", "postgres")
POSTGRES_DB = os.getenv("TEST_POSTGRES_DB", "finguard_test")
POSTGRES_PORT = 5433

ADMIN_DB_URL = (
    f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
    f"@localhost:{POSTGRES_PORT}/postgres"
)

TEST_DB_URL = (
    f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
    f"@localhost:{POSTGRES_PORT}/{POSTGRES_DB}"
)

@pytest.fixture(scope="session")
def postgres_container():
    client = docker.from_env()

    container = client.containers.run(
        image="postgres:16",
        name="finguard-test-postgres",
        environment={
            "POSTGRES_USER": POSTGRES_USER,
            "POSTGRES_PASSWORD": POSTGRES_PASSWORD,
        },
        ports={"5432/tcp": POSTGRES_PORT},
        detach=True,
        remove=True,
    )

    time.sleep(5)

    yield

    container.stop()

@pytest.fixture(scope="session")
async def test_engine(postgres_container):
    admin_engine = create_async_engine(
        ADMIN_DB_URL,
        isolation_level="AUTOCOMMIT",
        future=True,
    )

    async with admin_engine.connect() as conn:
        result = await conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :db"),
            {"db": POSTGRES_DB},
        )
        exists = result.scalar()

        if not exists:
            await conn.execute(text(f'CREATE DATABASE "{POSTGRES_DB}"'))

    await admin_engine.dispose()

    engine = create_async_engine(
        TEST_DB_URL,
        echo=False,
        future=True,
        pool_pre_ping=True,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()

@pytest.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    async_session = sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        yield session


@pytest.fixture
def override_app(db_session):
    app = fastapi_app

    async def _override_get_db():
        async with db_session as s:
            yield s

    app.dependency_overrides.clear()
    app.dependency_overrides[settings.get_db_dependency] = _override_get_db

    yield app

    app.dependency_overrides.clear()


@pytest.fixture
async def client(override_app: FastAPI):
    async with AsyncClient(
        app=override_app,
        base_url="http://test",
        follow_redirects=True,
    ) as ac:
        yield ac

@pytest.fixture(autouse=True)
def set_test_pepper(monkeypatch):
    monkeypatch.setenv("PASSWORD_PEPPER", "test-pepper-secret")
