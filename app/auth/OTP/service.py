from typing import Final

from app.core.redis import redis_client
from app.interegation.SMS.console import ConsoleSMSProvider
from app.core.Utils.phone import normalize_phone
from app.core.security.masking import _mask_phone
from app.core.logging import get_logger
from app.core.security.rate_limit import enforce_otp_rate_limit
from app.core.security.hashing.otp import hash_otp
from app.core.security.hashing.otp import verify_otp as hash_verify_otp
from app.domain.auth.otp_purpose import OTPPurpose
from app.core.security.otp_keys import _otp_key, _fail_key, _lock_key

from app.auth.OTP.bruteforce import (
    is_locked,
    _increment_failed_attempts,
    _clear_failed_attempts,
)
from app.auth.OTP.otp_exceptions import (
    OTPRateLimitExceeded,
    OTPLocked,
    OTPExpired,
    OTPMismatch,
)

from app.core.security.otp import (
    generate_otp,
    OTP_EXPIRY,
    OTP_VERIFY_MAX_ATTEMPTS,
    OTP_LOCKOUT_TTL,
    OTP_VERIFY_WINDOW
)

logger = get_logger(__name__)



async def send_otp(phone: str, purpose: OTPPurpose) -> bool:
    phone = normalize_phone(phone)
    masked_phone = _mask_phone(phone)

    logger.info(
        "OTP request initiated",
        extra={"phone": masked_phone, "purpose": purpose}
    )

    try:
        await enforce_otp_rate_limit(phone)
    except OTPRateLimitExceeded:
        logger.warning(
            "OTP rate limit exceeded",
            extra={"phone": masked_phone, "purpose": purpose}
        )
        raise

    otp: str = generate_otp(6)
    otp_hash: str = hash_otp(
        otp=otp,
        identifier=phone,
    )

    otp_key = _otp_key(phone, purpose)

    await redis_client.set(otp_key, otp_hash, ex=OTP_EXPIRY)

    sms_provider = ConsoleSMSProvider()
    await sms_provider.send(phone, f"Your OTP is {otp}")

    logger.info(
        "OTP generated and sent successfully",
        extra={"phone": masked_phone, "purpose": purpose}
    )

    return True


async def verify_otp(phone: str, user_otp: str, purpose: OTPPurpose) -> bool:
    phone = normalize_phone(phone)
    masked_phone = _mask_phone(phone)

    otp_key = _otp_key(phone, purpose)
    fail_key = _fail_key(phone, purpose)
    lock_key = _lock_key(phone, purpose)

    if await redis_client.exists(lock_key):
        logger.warning(
            "OTP verification blocked due to lockout",
            extra={"phone": masked_phone, "purpose": purpose}
        )
        raise OTPLocked()

    stored_hash = await redis_client.get(otp_key)
    if not stored_hash:
        logger.warning(
            "OTP expired or missing",
            extra={"phone": masked_phone, "purpose": purpose}
        )
        raise OTPExpired()

    if not hash_verify_otp(
        otp=user_otp,
        identifier=phone,
        stored_hash=stored_hash,
    ):
        fail_count = await redis_client.incr(fail_key)
        await redis_client.expire(fail_key, OTP_VERIFY_WINDOW)

        if fail_count >= OTP_VERIFY_MAX_ATTEMPTS:
            await redis_client.set(lock_key, "1", ex=OTP_LOCKOUT_TTL)
            logger.warning(
                "OTP verification failed: lockout triggered",
                extra={"phone": masked_phone, "purpose": purpose}
            )
            raise OTPLocked()

        logger.warning(
            "OTP verification failed",
            extra={
                "phone": masked_phone,
                "purpose": purpose,
                "fail_count": fail_count
            }
        )
        raise OTPMismatch()

    await redis_client.delete(otp_key)
    await redis_client.delete(fail_key)

    logger.info(
        "OTP verified successfully",
        extra={"phone": masked_phone, "purpose": purpose}
    )

    return True
