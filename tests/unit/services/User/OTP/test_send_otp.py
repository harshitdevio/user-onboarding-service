import pytest
from unittest.mock import AsyncMock, patch
from app.services.User.otp_service import send_otp 

OTP_EXPIRY = 300 
@pytest.mark.asyncio
async def test_send_otp_first_request():
    phone = "9999999999"

    # Mock redis functions
    mock_redis = AsyncMock()
    mock_redis.incr.return_value = 1
    mock_redis.expire.return_value = True
    mock_redis.set.return_value = True
    with patch("app.services.User.otp_service.generate_otp", return_value="123456"):
        with patch("app.services.User.otp_service.redis_client", mock_redis):
            result = await send_otp(phone)

            # Assertions
            assert result is True

            mock_redis.incr.assert_called_once_with(f"otp_count:{phone}")
            mock_redis.expire.assert_called_once_with(f"otp_count:{phone}", OTP_EXPIRY)

            mock_redis.set.assert_called_once_with(
                f"otp:{phone}", "123456", ex=OTP_EXPIRY
            )
