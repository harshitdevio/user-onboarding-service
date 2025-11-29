import asyncio
import pytest
from httpx import AsyncClient
from fastapi import FastAPI

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.main import app as fastapi_app
from app.db.base import Base
try:
    from app.core.config import settings
except Exception as e:
    print("ERROR importing settings:", e)

# test DB config(Docker Postgres)
TEST_DATABASE_URL = (
    settings.TEST_DATABASE_URL
    if hasattr(settings, "TEST_DATABASE_URL")
    else "postgresql+asyncpg://postgres:postgres@localhost:5433/testdb"
)

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """
    A dedicated engine for integration tests.
    Real Postgres running in Docker.
    """
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
        future=True,
    )
    yield engine
    await engine.dispose()

@pytest.fixture(scope="session", autouse=True)
async def prepare_database(test_engine):
    """
    Drop + create schema at the beginning of the integration test suite.
    Fully isolated from development DB.
    """
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@pytest.fixture
async def async_db(test_engine):
    """
    Provides a fresh SQLAlchemy AsyncSession for each test.
    Uses SAVEPOINT transaction strategy to isolate each test.
    """

    AsyncSessionLocal = sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        autoflush=False,
        expire_on_commit=False,
        autocommit=False,
    )

    async with AsyncSessionLocal() as session:
        trans = await session.begin()  # outer transaction
        try:
            yield session
        finally:
            await trans.rollback()
            await session.close()


# FastAPI App + Override get_db
@pytest.fixture()
def integration_app(async_db) -> FastAPI:
    """
    Provide the real FastAPI app but override the DB dependency
    so routes use this test session.
    """

    def _override_get_db():
        yield async_db

    fastapi_app.dependency_overrides.clear()
    fastapi_app.dependency_overrides[
        settings.DB_DEPENDENCY
        if hasattr(settings, "DB_DEPENDENCY")
        else "get_db"
    ] = _override_get_db

    return fastapi_app


# async http client
@pytest.fixture()
async def integration_client(integration_app: FastAPI):
    async with AsyncClient(
        app=integration_app,
        base_url="http://test",
        follow_redirects=True,
    ) as client:
        yield client
