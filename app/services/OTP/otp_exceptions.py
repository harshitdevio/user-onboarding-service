class OTPRateLimitExceeded(Exception):
    """Raised when the user exceeds the allowed OTP request limit."""

class OTPException(Exception):
    """Base OTP exception."""

class OTPTooManyRequests(OTPException):
    """Raised when user requests OTP too frequently."""

class OTPLocked(OTPException):
    """Raised when phone is temporarily locked due to too many failed verifications."""

class OTPExpired(OTPException):
    """Raised when OTP has expired or does not exist in Redis."""

class OTPMismatch(OTPException):
    """Raised when OTP does not match."""

class OTPInvalid(Exception):
    """Raised when OTP does not match the stored hash."""
    pass