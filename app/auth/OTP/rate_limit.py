from app.core.redis import redis_client
from app.auth.OTP.otp_exceptions import OTPRateLimitExceeded

from app.core.security.otp import (
    OTP_RESEND_COOLDOWN,
    OTP_MAX_IN_WINDOW,
    OTP_WINDOW,
    OTP_DAILY_LIMIT,
    OTP_DAILY_TTL,
)


async def enforce_otp_rate_limit(phone: str) -> None:
    """
    Enforce OTP send rate limits.

    Controls:
    1. Cooldown between OTP sends
    2. Short burst window limit
    3. Daily quota limit

    Notes:
    - This implementation rate-limits by phone number only.
    - In production fintech systems, IP address, device fingerprint,
      and behavioral signals are also incorporated.
    - Operations are not fully atomic; Redis Lua scripting would be
      used in production to avoid race conditions.
    """

    # Cooldown check
    cooldown_key = f"otp:cooldown:{phone}"
    ttl = await redis_client.ttl(cooldown_key)

    if ttl > 0:
        raise OTPRateLimitExceeded(
            f"Please wait {ttl} seconds before requesting another OTP."
        )

    # Burst window check
    window_key = f"otp:window:{phone}"
    window_count = await redis_client.incr(window_key)

    if window_count == 1:
        await redis_client.expire(window_key, OTP_WINDOW)

    if window_count > OTP_MAX_IN_WINDOW:
        raise OTPRateLimitExceeded(
            "Too many OTP requests. Please try again later."
        )

    # Daily quota check
    daily_key = f"otp:daily:{phone}"
    daily_count = await redis_client.incr(daily_key)

    if daily_count == 1:
        await redis_client.expire(daily_key, OTP_DAILY_TTL)

    if daily_count > OTP_DAILY_LIMIT:
        raise OTPRateLimitExceeded(
            "Daily OTP limit reached. Please try again tomorrow."
        )

    # Set cooldown only after all checks pass
    await redis_client.set(
        cooldown_key,
        "1",
        ex=OTP_RESEND_COOLDOWN
    )
