import pytest
from httpx import AsyncClient

from app.main import app
from app.db.session import get_db
from app.main import app
from app.db.session import get_db
from app.core.redis import redis_client
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession



@pytest.fixture
async def db_session(test_engine):
    """
    Provides a real async DB session using the TEST database.
    """
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session


@pytest.fixture(autouse=True)
async def e2e_db_cleaner(db_session):
    """
    Ensure DB state is rolled back between E2E tests.
    """
    try:
        yield
    finally:
        await db_session.rollback()
        db_session.expire_all()


@pytest.fixture
async def e2e_client(override_app):
    """
    Async HTTP client bound to the FastAPI app with overrides.
    """
    async with AsyncClient(
        app=override_app,
        base_url="http://test",
        follow_redirects=True,
    ) as client:
        yield client


@pytest.fixture(autouse=True)
def mock_otp_generator(mocker):
    """
    Mock OTP generation to have deterministic OTPs in tests.
    """
    mocker.patch(
        "app.services.OTP.issue_otp.generate_otp",
        return_value="123456",
    )


@pytest.fixture
def mock_sms_provider(mocker):
    """
    Mock SMS provider so OTP sending does not hit real infra.
    """
    mocker.patch(
        "app.auth.OTP.service.send_otp",
        return_value=True,
    )


@pytest.fixture(autouse=True)
async def flush_redis():
    """
    Ensure Redis is clean before each E2E test.
    """
    await redis_client.flushdb()
    yield
