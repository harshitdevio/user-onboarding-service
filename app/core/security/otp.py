from typing import Final
import secrets

DEFAULT_OTP_LENGTH: Final[int] = 6

def generate_otp(length: int = DEFAULT_OTP_LENGTH) -> str:
    if length <= 0:
        raise ValueError("length must be > 0")
    upper = 10 ** length
    value = secrets.randbelow(upper) 
    return str(value).zfill(length)

OTP_EXPIRY: Final[int] = 300
OTP_MAX_REQUESTS: Final[int] = 3

OTP_VERIFY_MAX_ATTEMPTS: Final[int] = 5
OTP_VERIFY_WINDOW: Final[int] = 15 * 60
OTP_LOCKOUT_TTL: Final[int] = 60 * 60

OTP_RESEND_COOLDOWN = 30

OTP_MAX_IN_WINDOW = 3
OTP_WINDOW = 5 * 60

OTP_DAILY_LIMIT = 10
OTP_DAILY_TTL = 24 * 60 * 60
