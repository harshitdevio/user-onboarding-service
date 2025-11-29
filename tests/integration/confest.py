import pytest
from httpx import AsyncClient
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app as fastapi_app


@pytest.fixture()
async def integration_db(db_session: AsyncSession):
    yield db_session


@pytest.fixture()
def integration_app() -> FastAPI:
    return fastapi_app

# async client (Real App + Real DB)
@pytest.fixture()
async def integration_client(integration_app: FastAPI):
    async with AsyncClient(
        app=integration_app,
        base_url="http://test",
        follow_redirects=True
    ) as client:
        yield client

# clean DB between tests (specifically for this Fintech)
@pytest.fixture(autouse=True)
async def clean_database(integration_db: AsyncSession):
    """
    Runs before every test.
    Useful in a Fintech system to avoid cross-test data leak.
    Rolls back any open transaction and expires all objects.
    """
    try:
        yield
    finally:
        await integration_db.rollback()
        await integration_db.expire_all()