from typing import Final

from app.core.redis import redis_client
from app.core.securities import generate_otp
from app.interegation.SMS.base import ConsoleSMSProvider
from app.core.Utils.phone import normalize_phone
from app.core.logging import get_logger, _mask_phone
from app.auth.OTP.rate_limit import enforce_otp_rate_limit
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
    OTP_EXPIRY,
    OTP_MAX_REQUESTS,
    OTP_VERIFY_MAX_ATTEMPTS,
)

logger = get_logger(__name__)

async def send_otp(phone: str) -> bool:
    """
    Generate and send a One-Time Password (OTP) to the given phone number.

    Enforces request-level rate limiting to prevent OTP abuse.

    Args:
        phone: Phone number for which the OTP should be generated.

    Raises:
        OTPRateLimitExceeded: If OTP request limit is exceeded.

    Returns:
        True if OTP generation and storage succeeds.
    """
    phone = normalize_phone(phone)
    masked_phone = _mask_phone(phone)

    logger.info("OTP request initiated", extra={"phone": masked_phone})

    try:
        await enforce_otp_rate_limit(phone)
    except OTPRateLimitExceeded:
        logger.warning(
            "OTP rate limit exceeded",
            extra={"phone": masked_phone}
        )
        raise

    otp: str = generate_otp(6)
    otp_key = f"otp:{phone}"

    await redis_client.set(otp_key, otp, ex=OTP_EXPIRY)

    sms_provider = ConsoleSMSProvider()
    await sms_provider.send(phone, "Your OTP is ******")

    logger.info(
        "OTP generated and sent successfully",
        extra={"phone": masked_phone}
    )

    return True


async def verify_otp(phone: str, user_otp: str) -> bool:
    """
    Verify OTP with brute-force protection.

    Raises:
        OTPLocked: If the phone number is locked due to excessive failures.
        OTPExpired: If the OTP is expired or not found.
        OTPMismatch: If the provided OTP is incorrect.

    Returns:
        True if OTP verification succeeds.
    """
    phone = normalize_phone(phone)
    masked_phone = _mask_phone(phone)

    logger.info("OTP verification initiated", extra={"phone": masked_phone})

    if await is_locked(phone):
        logger.warning("OTP verification attempt blocked due to lock", extra={"phone": masked_phone})
        raise OTPLocked("Too many failed verification attempts. Try later.")

    otp_key = f"otp:{phone}"
    saved_otp: str | None = await redis_client.get(otp_key)

    if not saved_otp:
        attempts = await _increment_failed_attempts(phone)
        logger.warning("OTP expired or missing", extra={"phone": masked_phone, "attempts": attempts})
        raise OTPExpired("OTP expired or not found. Request a new OTP.")

    if saved_otp != user_otp:
        attempts: int = await _increment_failed_attempts(phone)
        logger.warning(
            "Incorrect OTP attempt",
            extra={"phone": masked_phone, "attempts": attempts, "max_attempts": OTP_VERIFY_MAX_ATTEMPTS}
        )
        raise OTPMismatch(f"OTP incorrect. Attempt {attempts}/{OTP_VERIFY_MAX_ATTEMPTS}.")

    await redis_client.delete(otp_key)
    await _clear_failed_attempts(phone)

    logger.info("OTP verified successfully", extra={"phone": masked_phone})

    return True