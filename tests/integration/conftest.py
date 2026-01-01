import asyncio
import pytest
from uuid import uuid4
from app.db.models.User.user_core import User
from app.db.models.User.user_auth import UserAuth
from httpx import AsyncClient
from fastapi import FastAPI
from redis.asyncio import Redis

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.main import app as fastapi_app
from app.db.base import Base
import app.core.redis

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

@pytest.fixture
async def redis_test():
    client = Redis.from_url("redis://localhost:6380", decode_responses=True)
    await client.flushall()
    yield client
    await client.flushall()
    await client.aclose()

from unittest.mock import patch

@pytest.fixture(autouse=True)
async def patch_redis_client_global(redis_test):
    """
    Patch the global redis_client with the test-scoped redis_test client.
    This ensures app code uses the test redis and the correct event loop.
    """
    with patch("app.core.redis.redis_client", redis_test):
        yield


@pytest.fixture
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

@pytest.fixture(autouse=True)
async def prepare_database(test_engine):
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

@pytest.fixture
async def async_db(test_engine):
    async_session = async_sessionmaker(test_engine, class_=AsyncSession)

    async with async_session() as session:
        trans = await session.begin()
        try:
            yield session
        finally:
            if trans.is_active:
                await trans.rollback()

   
@pytest.fixture
async def test_user(async_db):
    user = User(
        id=uuid4(),
        email="test@example.com",
    )
    async_db.add(user)
    await async_db.flush()

    auth = UserAuth(
        user_id=user.id,
        hashed_password="fakehashed",
    )
    async_db.add(auth)

    await async_db.commit()
    await async_db.refresh(user)
    return user



# FastAPI App + Override get_db
@pytest.fixture()
async def integration_app(async_db) -> FastAPI:
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


@pytest.fixture(autouse=True)
async def clean_state(async_db: AsyncSession):
    """
    Runs before & after each test.
    Ensures no leftover state leaks.
    Especially important in Fintech systems.
    """
    try:
        yield
    finally:
        await async_db.rollback()
        async_db.expire_all()


@pytest.fixture(autouse=True)
async def patch_redis_client_global(redis_test):
    """
    Patch the global redis_client with the test-scoped redis_test client.
    """
    await redis_test.flushdb()
    with patch("app.core.redis.redis_client", redis_test):
        yield
    await redis_test.flushdb()

@pytest.fixture(autouse=True)
async def ensure_redis(patch_redis_client_global):
    pass


@pytest.fixture
def mock_sms_provider():
    """
    Mock external SMS side-effect.
    OTP logic must still execute.
    """
    with patch("app.interegation.SMS.console.ConsoleSMSProvider.send") as mock_send:
        yield mock_send