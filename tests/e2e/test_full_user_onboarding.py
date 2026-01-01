import pytest
from sqlalchemy import select

from app.core.redis import redis_client
from app.db.models.User.user_core import User
from app.db.models.User.pre_user import PreUser

SIGNUP_PHONE = "/v1/auth/signup/phone"
VERIFY_OTP = "/v1/auth/signup/verify-otp"
SET_PASSWORD = "/v1/auth/set-password"


@pytest.mark.asyncio
async def test_user_onboarding_happy_path_e2e(
    e2e_client,
    db_session,
    mock_sms_provider,
):
    """
    E2E: Full user onboarding happy path

    signup phone
        -> OTP issued
        -> OTP verified
        -> password set
        -> user becomes ACTIVE
    """

    raw_phone = "9876543210"
    phone = f"+91{raw_phone}"
    password = "StrongPassword@123"

    signup_resp = await e2e_client.post(
        SIGNUP_PHONE,
        json={"phone": raw_phone},
    )

    assert signup_resp.status_code == 200
    assert signup_resp.json()["status"] == "OTP_SENT"

    otp = "123456"

    verify_resp = await e2e_client.post(
        VERIFY_OTP,
        json={
            "phone": raw_phone,
            "otp": otp,
        },
    )

    assert verify_resp.status_code == 200
    assert verify_resp.json()["verified"] is True

    set_password_resp = await e2e_client.post(
        SET_PASSWORD,
        json={
            "phone": raw_phone,
            "password": password,
        },
    )

    assert set_password_resp.status_code == 200

    result = await db_session.execute(
        select(User).where(User.phone == phone)
    )
    user = result.scalar_one()

    assert user.is_active is True
    assert user.password_hash is not None
    assert user.password_hash != password  # ensure hashing

    result = await db_session.execute(
        select(PreUser).where(PreUser.phone == phone)
    )
    assert result.scalar_one_or_none() is None
