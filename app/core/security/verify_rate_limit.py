from app.core.redis import redis_client
from app.auth.OTP.otp_exceptions import (
    OTPVerificationLocked,
    OTPVerificationAttemptsExceeded,
)
from app.core.security.otp import (
    OTP_VERIFY_MAX_ATTEMPTS,
    OTP_VERIFY_FAIL_TTL,
    OTP_VERIFY_LOCK_TTL,
)
from app.domain.auth.otp_purpose import OTPPurpose 
from app.auth.OTP.service import _fail_key, _lock_key

async def enforce_otp_verify_rate_limit(identifier: str, purpose: OTPPurpose) -> None:
    """
    Enforce rate-limits for OTP verification attempts.

    - Blocks verification if locked
    - Increments failure count
    - Locks verification after max failures
    """

    lock_key = _lock_key(identifier, purpose)
    fail_key = _fail_key(identifier, purpose)
    # Hard lock check
    if await redis_client.exists(lock_key):
        raise OTPVerificationLocked(
            "OTP verification temporarily locked. Please try again later."
        )

    # Increment failure counter
    attempts = await redis_client.incr(fail_key)

    # Set TTL on first failure
    if attempts == 1:
        await redis_client.expire(fail_key, OTP_VERIFY_FAIL_TTL)

    # Too many failures → lock
    if attempts > OTP_VERIFY_MAX_ATTEMPTS:
        await redis_client.set(
            lock_key,
            "1",
            ex=OTP_VERIFY_LOCK_TTL,
        )
        await redis_client.delete(fail_key)

        raise OTPVerificationAttemptsExceeded(
            "Too many incorrect OTP attempts."
        )
