import pytest
from unittest.mock import AsyncMock

from app.auth.OTP.service import verify_otp
from app.auth.OTP.otp_exceptions import (
    OTPLocked,
    OTPExpired,
    OTPMismatch,
)
from app.core.security.otp import OTP_VERIFY_MAX_ATTEMPTS
from app.domain.auth.otp_purpose import OTPPurpose
from app.core.security.otp_keys import _otp_key, _fail_key, _lock_key

@pytest.mark.asyncio
async def test_verify_otp_locked_phone_raises(mocker):
    phone = "+919876543210"

    mocker.patch("app.auth.OTP.service.normalize_phone", return_value=phone)
    mocker.patch("app.auth.OTP.service.redis_client.exists", new=AsyncMock(return_value=True))

    with pytest.raises(OTPLocked):
        await verify_otp(phone, "123456", purpose=OTPPurpose.SIGNUP)

@pytest.mark.asyncio
async def test_verify_otp_expired_or_missing(mocker):
    phone = "+919876543210"

    mocker.patch("app.auth.OTP.service.normalize_phone", return_value=phone)
    mocker.patch("app.auth.OTP.service.redis_client.get", new=AsyncMock(return_value=None))
    mocker.patch("app.auth.OTP.service.enforce_otp_verify_rate_limit", new=AsyncMock())

    with pytest.raises(OTPExpired):
        await verify_otp(phone, "123456", purpose=OTPPurpose.SIGNUP)

@pytest.mark.asyncio
async def test_verify_otp_incorrect_otp(mocker):
    phone = "+919876543210"
    saved_hash = "hashed_otp"

    mocker.patch("app.auth.OTP.service.normalize_phone", return_value=phone)
    mocker.patch("app.auth.OTP.service.redis_client.get", new=AsyncMock(return_value=saved_hash))
    mocker.patch("app.auth.OTP.service.crypto_verify_otp", return_value=False)
    mocker.patch("app.auth.OTP.service.enforce_otp_verify_rate_limit", new=AsyncMock())

    with pytest.raises(OTPMismatch):
        await verify_otp(phone, "999999", purpose=OTPPurpose.SIGNUP)

@pytest.mark.asyncio
async def test_verify_otp_success(mocker):
    phone = "+919876543210"
    otp = "123456"
    stored_hash = "hashed_otp"

    mocker.patch("app.auth.OTP.service.normalize_phone", return_value=phone)
    mocker.patch("app.auth.OTP.service.redis_client.get", new=AsyncMock(return_value=stored_hash))
    mocker.patch("app.auth.OTP.service.crypto_verify_otp", return_value=True)
    redis_delete = mocker.patch("app.auth.OTP.service.redis_client.delete", new=AsyncMock())
    mocker.patch("app.auth.OTP.service.enforce_otp_verify_rate_limit", new=AsyncMock())

    result = await verify_otp(phone, otp, purpose=OTPPurpose.SIGNUP)
    assert result is True
    redis_delete.assert_any_call(_otp_key(phone, OTPPurpose.SIGNUP))
    redis_delete.assert_any_call(_fail_key(phone, OTPPurpose.SIGNUP))
    redis_delete.assert_any_call(_lock_key(phone, OTPPurpose.SIGNUP))

@pytest.mark.asyncio
async def test_verify_otp_clears_failed_attempts_on_success(mocker):
    phone = "+919876543210"
    stored_hash = "hashed_otp"

    mocker.patch("app.auth.OTP.service.normalize_phone", return_value=phone)
    mocker.patch("app.auth.OTP.service.redis_client.get", new=AsyncMock(return_value=stored_hash))
    mocker.patch("app.auth.OTP.service.crypto_verify_otp", return_value=True)
    redis_delete = mocker.patch("app.auth.OTP.service.redis_client.delete", new=AsyncMock())
    mocker.patch("app.auth.OTP.service.enforce_otp_verify_rate_limit", new=AsyncMock())

    await verify_otp(phone, "123456", purpose=OTPPurpose.SIGNUP)
    redis_delete.assert_any_call(_fail_key(phone, OTPPurpose.SIGNUP))

@pytest.mark.asyncio
async def test_verify_otp_deletes_otp_after_success(mocker):
    phone = "+919876543210"
    stored_hash = "hashed_otp"

    mocker.patch("app.auth.OTP.service.normalize_phone", return_value=phone)
    mocker.patch("app.auth.OTP.service.redis_client.get", new=AsyncMock(return_value=stored_hash))
    mocker.patch("app.auth.OTP.service.crypto_verify_otp", return_value=True)
    redis_delete = mocker.patch("app.auth.OTP.service.redis_client.delete", new=AsyncMock())
    mocker.patch("app.auth.OTP.service.enforce_otp_verify_rate_limit", new=AsyncMock())

    await verify_otp(phone, "123456", purpose=OTPPurpose.SIGNUP)
    redis_delete.assert_any_call(_otp_key(phone, OTPPurpose.SIGNUP))

@pytest.mark.asyncio
async def test_verify_otp_eventually_locks_after_max_attempts(mocker):
    phone = "+919876543210"
    stored_hash = "hashed_otp"

    mocker.patch("app.auth.OTP.service.normalize_phone", return_value=phone)
    mocker.patch("app.auth.OTP.service.redis_client.get", new=AsyncMock(return_value=stored_hash))
    mocker.patch("app.auth.OTP.service.crypto_verify_otp", return_value=False)
    mocker.patch("app.auth.OTP.service.enforce_otp_verify_rate_limit", new=AsyncMock())

    with pytest.raises(OTPMismatch):
        await verify_otp(phone, "000000", purpose=OTPPurpose.SIGNUP)
