import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from unittest.mock import patch

import app.core.redis
from app.db.models.User.pre_user import PreUser
from tests.factories.user_factory import create_user

ENDPOINT = "/v1/auth/signup/phone"


@pytest.fixture
def mock_sms_provider():
    """
    Mock external SMS side-effect.
    OTP logic must still execute.
    """
    with patch("app.interegation.SMS.console.ConsoleSMSProvider.send") as mock_send:
        yield mock_send

@pytest.mark.asyncio
async def test_signup_phone_happy_path(
    integration_client: AsyncClient,
    async_db: AsyncSession,
    mock_sms_provider,
):
    """
    Valid phone signup.
    Verifies:
    - HTTP contract
    - Redis OTP side-effect
    - No premature DB persistence
    """
    phone = "9876543210"
    payload = {"phone": phone}

    response = await integration_client.post(ENDPOINT, json=payload)

    assert response.status_code == 200
    body = response.json()

    assert body["phone"] == f"+91{phone}"
    assert body["status"] == "OTP_SENT"

    keys = await app.core.redis.redis_client.keys("otp:verify:signup:*")
    assert any(f"+91{phone}" in key for key in keys)

    stmt = select(PreUser).where(PreUser.phone == f"+91{phone}")
    result = await async_db.execute(stmt)
    assert result.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_signup_phone_existing_user_is_idempotent(
    integration_client: AsyncClient,
    async_db: AsyncSession,
    mock_sms_provider,
):
    """
    Phone already belongs to a User.
    Signup should:
    - still issue OTP
    - NOT create duplicate PreUser rows
    """
    existing_phone = "+919999999999"
    await create_user(async_db, phone=existing_phone)

    result_before = await async_db.execute(select(PreUser))
    preuser_count_before = len(result_before.scalars().all())

    response = await integration_client.post(
        ENDPOINT,
        json={"phone": "9999999999"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "OTP_SENT"

    keys = await app.core.redis.redis_client.keys("otp:verify:signup:*")
    assert any(existing_phone in key for key in keys)

    result_after = await async_db.execute(select(PreUser))
    preuser_count_after = len(result_after.scalars().all())
    assert preuser_count_after == preuser_count_before


@pytest.mark.asyncio
async def test_signup_phone_invalid_phone_rejected(
    integration_client: AsyncClient,
):
    """
    Invalid phone numbers should:
    - fail validation
    - create no Redis or DB side-effects
    """
    invalid_inputs = ["123", "abcdef", "", None]

    for phone in invalid_inputs:
        response = await integration_client.post(
            ENDPOINT,
            json={"phone": phone},
        )

        assert response.status_code == 422

        # No OTPs should exist
        keys = await app.core.redis.redis_client.keys("otp:verify:signup:*")
        assert keys == []


@pytest.mark.asyncio
async def test_signup_phone_is_idempotent_under_repeated_requests(
    integration_client: AsyncClient,
):
    """
    Repeated requests for the same phone should:
    - succeed
    - overwrite / refresh OTP
    - not fail unexpectedly
    """
    phone = "9000000000"
    payload = {"phone": phone}

    for _ in range(5):
        response = await integration_client.post(ENDPOINT, json=payload)
        assert response.status_code == 200

    keys = await app.core.redis.redis_client.keys("otp:verify:signup:*")
    assert any(f"+91{phone}" in key for key in keys)
