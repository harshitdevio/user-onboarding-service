from __future__ import annotations

import hmac
import hashlib
import os
from typing import Final

OTP_SECRET_KEY: Final[str | None] = os.getenv("OTP_SECRET_KEY")

if not OTP_SECRET_KEY:
    raise RuntimeError("OTP_SECRET_KEY is not set")

def _normalize_otp(otp: str) -> str:
    """
    Normalize OTP input to avoid subtle mismatches.
    """
    otp = otp.strip()

    if not otp.isdigit():
        raise ValueError("OTP must contain only digits")

    return otp

def hash_otp(*, otp: str, identifier: str) -> str:
    """
    Hash an OTP using HMAC-SHA256.

    identifier:
        A stable, user-specific value (e.g. phone number or user_id).
        Prevents OTP reuse across users.
    """
    otp = _normalize_otp(otp)

    message = f"{identifier}:{otp}".encode("utf-8")
    key = OTP_SECRET_KEY.encode("utf-8")

    digest = hmac.new(
        key=key,
        msg=message,
        digestmod=hashlib.sha256,
    ).hexdigest()

    return digest

def verify_otp(
    *,
    otp: str,
    identifier: str,
    stored_hash: str,
) -> bool:
    """
    Constant-time OTP verification.
    """
    if not otp or not stored_hash:
        return False

    try:
        computed_hash = hash_otp(otp=otp, identifier=identifier)
    except ValueError:
        return False

    return hmac.compare_digest(computed_hash, stored_hash)