from app.domain.auth.otp_purpose import OTPPurpose


def _otp_key(phone: str, purpose: OTPPurpose) -> str:
    """Key for storing the actual OTP hash."""
    return f"otp:{purpose.value}:{phone}"


def _fail_key(phone: str, purpose: OTPPurpose) -> str:
    """Key for counting failed verification attempts."""
    return f"otp_fail:{purpose.value}:{phone}"


def _lock_key(phone: str, purpose: OTPPurpose) -> str:
    """Key for the lockout flag preventing further verification."""
    return f"otp_lock:{purpose.value}:{phone}"
