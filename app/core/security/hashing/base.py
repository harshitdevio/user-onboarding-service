from __future__ import annotations

import os
import hmac
from typing import Final

PEPPER_ENV_KEY: Final[str] = "PASSWORD_PEPPER"

def get_pepper() -> str:
    """
    Load global pepper from environment.
    Intentionally fails hard if missing.
    """
    pepper = os.getenv(PEPPER_ENV_KEY)
    if not pepper:
        raise RuntimeError(
            f"{PEPPER_ENV_KEY} must be set for cryptographic operations"
        )
    return pepper

def apply_pepper(secret: str, pepper: str) -> str:
    """
    Combine secret with pepper using explicit boundary.
    """
    if not secret:
        raise ValueError("Secret cannot be empty")

    return f"{secret}::{pepper}"
