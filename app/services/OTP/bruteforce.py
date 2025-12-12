from redis.asyncio import client as redis_client
from services.OTP.otp_service import OTP_VERIFY_MAX_ATTEMPTS, OTP_VERIFY_WINDOW, OTP_LOCKOUT_TTL
async def _increment_failed_attempts(phone: str) -> int:
    """Increment the failed attempts counter and set expire. If threshold reached, set lock key."""
    attempts_key = f"otp_failed:{phone}"
    lock_key = f"otp_locked:{phone}"

    attempts = await redis_client.incr(attempts_key)
    if attempts == 1:
        await redis_client.expire(attempts_key, OTP_VERIFY_WINDOW)

    if attempts >= OTP_VERIFY_MAX_ATTEMPTS:
        await redis_client.set(lock_key, "1", ex=OTP_LOCKOUT_TTL)

    return attempts

async def _clear_failed_attempts(phone: str) -> None:
    """Clear attempts and lock keys after successful verification."""
    attempts_key = f"otp_failed:{phone}"
    lock_key = f"otp_locked:{phone}"
    # delete both keys if they exist
    await redis_client.delete(attempts_key)
    await redis_client.delete(lock_key)

async def is_locked(phone: str) -> bool:
    """Return whether phone is currently locked from verification attempts."""
    lock_key = f"otp_locked:{phone}"
    val = await redis_client.get(lock_key)
    return bool(val)