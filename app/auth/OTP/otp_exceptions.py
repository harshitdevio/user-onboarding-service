class OTPRateLimitExceeded(Exception):
    """Raised when the user exceeds the allowed OTP request limit."""

class OTPException(Exception):
    """Base OTP exception."""

class OTPTooManyRequests(OTPException):
    """Raised when user requests OTP too frequently."""

class OTPLocked(OTPException):
    """Raised when phone is temporarily locked due to too many failed verifications."""

class OTPExpired(OTPException):
    """Raised when OTP has expired."""

class OTPMismatch(OTPException):
    """Raised when OTP does not match."""

class OTPRateLimitExceeded(Exception):
    """Raised when the user exceeds the allowed OTP request limit."""
    pass

class OTPVerificationLocked(Exception):
    """Raised when phone is temporarily locked due to too many failed verifications."""
    pass


class OTPVerificationAttemptsExceeded(Exception):
    """Raised when user exceeds the allowed OTP verification attempts."""
    pass

class OTPInvalid(Exception):
    """Raised when OTP does not match the stored hash."""
    pass