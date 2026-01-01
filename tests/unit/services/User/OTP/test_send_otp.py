import pytest
from unittest.mock import AsyncMock, patch
from app.auth.OTP.service import send_otp, generate_otp
from app.domain.auth.otp_purpose import OTPPurpose
from app.core.security.otp_keys import _otp_key
from app.core.security.otp import OTP_EXPIRY, OTP_RESEND_COOLDOWN, OTP_WINDOW, OTP_DAILY_TTL

@pytest.mark.asyncio
async def test_send_otp_first_request():
    phone = "9999999999"
    mock_redis = AsyncMock()
    mock_redis.incr.side_effect = [1, 1, 1]
    mock_redis.expire.return_value = True
    mock_redis.set.return_value = True
    with patch("app.services.OTP.otp_service.generate_otp", return_value="123456"):
        with patch("app.services.OTP.otp_service.redis_client", mock_redis):
            result = await send_otp(phone, purpose=OTPPurpose.SIGNUP)
            assert result is True
            mock_redis.incr.assert_any_call(f"otp:window:{phone}")
            mock_redis.incr.assert_any_call(f"otp:daily:{phone}")
            mock_redis.set.assert_any_call(f"otp:cooldown:{phone}", "1", ex=OTP_RESEND_COOLDOWN)
            mock_redis.set.assert_any_call(_otp_key(phone, OTPPurpose.SIGNUP), "123456", ex=OTP_EXPIRY)

@pytest.mark.asyncio
async def test_send_otp_subsequent_request_within_limit():
    phone = "9999999999"
    mock_redis = AsyncMock()
    mock_redis.incr.side_effect = [2, 2, 2]
    mock_redis.set.return_value = True
    with patch("app.services.OTP.otp_service.generate_otp", return_value="654321"):
        with patch("app.services.OTP.otp_service.redis_client", mock_redis):
            result = await send_otp(phone, purpose=OTPPurpose.SIGNUP)
            assert result is True
            mock_redis.incr.assert_any_call(f"otp:window:{phone}")
            mock_redis.incr.assert_any_call(f"otp:daily:{phone}")
            mock_redis.set.assert_any_call(_otp_key(phone, OTPPurpose.SIGNUP), "654321", ex=OTP_EXPIRY)

@pytest.mark.asyncio
async def test_send_otp_exceeds_rate_limit():
    phone = "9999999999"
    mock_redis = AsyncMock()
    mock_redis.incr.side_effect = [4, 1, 1]
    with patch("app.services.OTP.otp_service.generate_otp", return_value="111111"):
        with patch("app.services.OTP.otp_service.redis_client", mock_redis):
            with pytest.raises(Exception) as exc:
                await send_otp(phone, purpose=OTPPurpose.SIGNUP)
            assert "Too many OTP requests" in str(exc.value)

def test_generate_otp_format():
    otp = generate_otp()
    assert isinstance(otp, str)
    assert otp.isdigit()
    assert len(otp) == 6
