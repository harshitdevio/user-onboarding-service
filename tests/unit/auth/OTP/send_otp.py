import pytest
from unittest.mock import AsyncMock, MagicMock

from app.auth.OTP.service import send_otp
from app.auth.OTP.otp_exceptions import OTPRateLimitExceeded
from app.core.security.otp import OTP_EXPIRY


@pytest.mark.asyncio
async def test_send_otp_success(mocker):
    phone = "+91 9876543210"
    normalized_phone = "+919876543210"
    fixed_otp = "123456"

    # Mocks
    mocker.patch(
        "app.auth.OTP.service.normalize_phone",
        return_value=normalized_phone
    )
    mocker.patch(
        "app.auth.OTP.service.enforce_otp_rate_limit",
        new=AsyncMock()
    )
    mocker.patch(
        "app.auth.OTP.service.generate_otp",
        return_value=fixed_otp
    )

    redis_set = mocker.patch(
        "app.auth.OTP.service.redis_client.set",
        new=AsyncMock()
    )

    sms_send = mocker.patch(
        "app.auth.OTP.service.ConsoleSMSProvider.send",
        new=AsyncMock()
    )

    result = await send_otp(phone)

    assert result is True
    redis_set.assert_called_once_with(
        f"otp:{normalized_phone}",
        fixed_otp,
        ex=OTP_EXPIRY,
    )
    sms_send.assert_called_once()



@pytest.mark.asyncio
async def test_send_otp_rate_limit_exceeded(mocker):
    phone = "+91 9876543210"

    mocker.patch(
        "app.auth.OTP.service.normalize_phone",
        return_value=phone
    )

    mocker.patch(
        "app.auth.OTP.service.enforce_otp_rate_limit",
        new=AsyncMock(side_effect=OTPRateLimitExceeded())
    )

    redis_set = mocker.patch(
        "app.auth.OTP.service.redis_client.set",
        new=AsyncMock()
    )

    sms_send = mocker.patch(
        "app.auth.OTP.service.ConsoleSMSProvider.send",
        new=AsyncMock()
    )

    with pytest.raises(OTPRateLimitExceeded):
        await send_otp(phone)

    redis_set.assert_not_called()
    sms_send.assert_not_called()


