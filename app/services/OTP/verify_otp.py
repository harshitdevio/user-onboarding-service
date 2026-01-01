import app.core.redis
from app.auth.OTP.otp_exceptions import (
    OTPExpired,
    OTPInvalid,
)
from app.core.security.verify_rate_limit import enforce_otp_verify_rate_limit
from app.core.security.hashing.otp import verify_otp as crypto_verify_otp
from app.domain.auth.otp_purpose import OTPPurpose
from app.core.security.otp_keys import _otp_key, _fail_key, _lock_key

async def verify_otp_flow(*, phone: str, otp: str, purpose: OTPPurpose) -> None:
    """
    Full OTP verification flow:

    1. Fetch stored hash
    2. Compare OTP
    3. On success: cleanup keys
    4. On failure: apply rate-limit
    """

    redis_key = _otp_key(phone, purpose)
    stored_hash = await app.core.redis.redis_client.get(redis_key)

    if not stored_hash:
        # OTP expired or never issued
        raise OTPExpired("OTP has expired. Please request a new one.")

    # Check OTP using cryptographic primitive
    is_valid = crypto_verify_otp(
        otp=otp,
        identifier=phone,
        stored_hash=stored_hash,
    )

    if is_valid:
        # SUCCESS: cleanup
        fail_key = _fail_key(phone, purpose)
        lock_key = _lock_key(phone, purpose)

        await app.core.redis.redis_client.delete(redis_key)
        await app.core.redis.redis_client.delete(fail_key)
        await app.core.redis.redis_client.delete(lock_key)

        return  # success, orchestration layer can continue

    # FAILURE: enforce verification rate-limit
    await enforce_otp_verify_rate_limit(phone, purpose)

    raise OTPInvalid("Incorrect OTP provided.")
