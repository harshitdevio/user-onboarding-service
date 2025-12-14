import pytest
from unittest.mock import AsyncMock

from app.auth.OTP.service import verify_otp
from app.auth.OTP.otp_exceptions import (
    OTPLocked,
    OTPExpired,
    OTPMismatch,
)
from app.core.security.otp import OTP_VERIFY_MAX_ATTEMPTS


@pytest.mark.asyncio
async def test_verify_otp_locked_phone_raises(mocker):
    phone = "+919876543210"

    mocker.patch(
        "app.auth.OTP.service.normalize_phone",
        return_value=phone
    )

    mocker.patch(
        "app.auth.OTP.service.is_locked",
        new=AsyncMock(return_value=True)
    )

    redis_get = mocker.patch(
        "app.auth.OTP.service.redis_client.get",
        new=AsyncMock()
    )

    with pytest.raises(OTPLocked):
        await verify_otp(phone, "123456")

    redis_get.assert_not_called()


@pytest.mark.asyncio
async def test_verify_otp_expired_or_missing(mocker):
    phone = "+919876543210"

    mocker.patch(
        "app.auth.OTP.otp_service.normalize_phone",
        return_value=phone
    )

    mocker.patch(
        "app.auth.OTP.otp_service.is_locked",
        new=AsyncMock(return_value=False)
    )

    mocker.patch(
        "app.auth.OTP.otp_service.redis_client.get",
        new=AsyncMock(return_value=None)
    )

    increment_attempts = mocker.patch(
        "app.auth.OTP.otp_service._increment_failed_attempts",
        new=AsyncMock(return_value=1)
    )

    with pytest.raises(OTPExpired):
        await verify_otp(phone, "123456")

    increment_attempts.assert_called_once_with(phone)

@pytest.mark.asyncio
async def test_verify_otp_incorrect_otp(mocker):
    phone = "+919876543210"
    saved_otp = "111111"

    mocker.patch(
        "app.auth.OTP.otp_service.normalize_phone",
        return_value=phone
    )

    mocker.patch(
        "app.auth.OTP.otp_service.is_locked",
        new=AsyncMock(return_value=False)
    )

    mocker.patch(
        "app.auth.OTP.otp_service.redis_client.get",
        new=AsyncMock(return_value=saved_otp)
    )

    increment_attempts = mocker.patch(
        "app.auth.OTP.otp_service._increment_failed_attempts",
        new=AsyncMock(return_value=2)
    )

    with pytest.raises(OTPMismatch) as exc:
        await verify_otp(phone, "999999")

    assert "Attempt 2" in str(exc.value)
    increment_attempts.assert_called_once_with(phone)


@pytest.mark.asyncio
async def test_verify_otp_success(mocker):
    phone = "+919876543210"
    otp = "123456"

    mocker.patch(
        "app.auth.OTP.otp_service.normalize_phone",
        return_value=phone
    )

    mocker.patch(
        "app.auth.OTP.otp_service.is_locked",
        new=AsyncMock(return_value=False)
    )

    mocker.patch(
        "app.auth.OTP.otp_service.redis_client.get",
        new=AsyncMock(return_value=otp)
    )

    redis_delete = mocker.patch(
        "app.auth.OTP.otp_service.redis_client.delete",
        new=AsyncMock()
    )

    clear_attempts = mocker.patch(
        "app.auth.OTP.otp_service._clear_failed_attempts",
        new=AsyncMock()
    )

    result = await verify_otp(phone, otp)

    assert result is True
    redis_delete.assert_called_once_with(f"otp:{phone}")
    clear_attempts.assert_called_once_with(phone)


@pytest.mark.asyncio
async def test_verify_otp_clears_failed_attempts_on_success(mocker):
    phone = "+919876543210"

    mocker.patch(
        "app.auth.OTP.otp_service.normalize_phone",
        return_value=phone
    )
    mocker.patch(
        "app.auth.OTP.otp_service.is_locked",
        new=AsyncMock(return_value=False)
    )
    mocker.patch(
        "app.auth.OTP.otp_service.redis_client.get",
        new=AsyncMock(return_value="000000")
    )

    clear_attempts = mocker.patch(
        "app.auth.OTP.otp_service._clear_failed_attempts",
        new=AsyncMock()
    )

    mocker.patch(
        "app.auth.OTP.otp_service.redis_client.delete",
        new=AsyncMock()
    )

    await verify_otp(phone, "000000")

    clear_attempts.assert_called_once()


@pytest.mark.asyncio
async def test_verify_otp_deletes_otp_after_success(mocker):
    phone = "+919876543210"

    mocker.patch(
        "app.auth.OTP.otp_service.normalize_phone",
        return_value=phone
    )
    mocker.patch(
        "app.auth.OTP.otp_service.is_locked",
        new=AsyncMock(return_value=False)
    )
    mocker.patch(
        "app.auth.OTP.otp_service.redis_client.get",
        new=AsyncMock(return_value="222222")
    )

    redis_delete = mocker.patch(
        "app.auth.OTP.otp_service.redis_client.delete",
        new=AsyncMock()
    )

    mocker.patch(
        "app.auth.OTP.otp_service._clear_failed_attempts",
        new=AsyncMock()
    )

    await verify_otp(phone, "222222")

    redis_delete.assert_called_once_with(f"otp:{phone}")