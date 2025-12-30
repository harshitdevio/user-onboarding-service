from app.core.redis import redis_client
from app.auth.OTP.otp_exceptions import (
    OTPExpired,
    OTPInvalid,
)
from app.core.security.verify_rate_limit import enforce_otp_verify_rate_limit
from app.core.security.hashing.otp import verify_otp as crypto_verify_otp


async def verify_otp_flow(*, phone: str, otp: str) -> None:
    """
    Full OTP verification flow:

    1. Fetch stored hash
    2. Compare OTP
    3. On success: cleanup keys
    4. On failure: apply rate-limit
    """

    redis_key = f"otp:verify:{phone}"
    stored_hash = await redis_client.get(redis_key)

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
        fail_key = f"otp:verify:fail:{phone}"
        lock_key = f"otp:verify:lock:{phone}"

        await redis_client.delete(redis_key)
        await redis_client.delete(fail_key)
        await redis_client.delete(lock_key)

        return  # success, orchestration layer can continue

    # FAILURE: enforce verification rate-limit
    await enforce_otp_verify_rate_limit(phone)

    raise OTPInvalid("Incorrect OTP provided.")
