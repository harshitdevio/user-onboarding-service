import pytest
from unittest.mock import AsyncMock, patch
from app.services.OTP.otp_service import send_otp, generate_otp


OTP_EXPIRY = 300       
OTP_MAX_REQUESTS = 3   

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


@pytest.mark.asyncio
async def test_send_otp_subsequent_request_within_limit():
    phone = "9999999999"

    mock_redis = AsyncMock()
    mock_redis.incr.return_value = 2 
    mock_redis.set.return_value = True

    with patch("app.services.User.otp_service.generate_otp", return_value="654321"):
        with patch("app.services.User.otp_service.redis_client", mock_redis):

            result = await send_otp(phone)

            assert result is True

            mock_redis.incr.assert_called_once_with(f"otp_count:{phone}")

            mock_redis.expire.assert_not_called()

            mock_redis.set.assert_called_once_with(
                f"otp:{phone}",
                "654321",
                ex=OTP_EXPIRY
            )


@pytest.mark.asyncio
async def test_send_otp_exceeds_rate_limit():
    phone = "9999999999"

    mock_redis = AsyncMock()
    mock_redis.incr.return_value = OTP_MAX_REQUESTS + 1  

    with patch("app.services.User.otp_service.generate_otp", return_value="111111"):
        with patch("app.services.User.otp_service.redis_client", mock_redis):

            with pytest.raises(Exception) as exc:
                await send_otp(phone)

            assert "Too many OTP requests" in str(exc.value)

            mock_redis.incr.assert_called_once_with(f"otp_count:{phone}")

            mock_redis.expire.assert_not_called()
            mock_redis.set.assert_not_called()

def test_generate_otp_format():
    otp = generate_otp()

    assert isinstance(otp, str)
    assert otp.isdigit()
    assert len(otp) == 6