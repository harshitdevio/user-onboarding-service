from __future__ import annotations

from passlib.context import CryptContext
from passlib.exc import UnknownHashError
from typing import Final

from .base import get_pepper

_secret_context: Final = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
    argon2__type="ID",
    argon2__memory_cost=65536,  # 64 MB
    argon2__time_cost=3,
    argon2__parallelism=2,
    argon2__hash_len=32,
    argon2__salt_size=16,
)

def hash_secret(secret: str) -> str:
    """
    Hash a server-issued secret (refresh token, device key, backup code).
    Uses Argon2id + pepper.
    """
    if not secret:
        raise ValueError("Secret cannot be empty")

    peppered = f"{secret}::{get_pepper()}"
    return _secret_context.hash(peppered)

def verify_secret(secret: str, hashed: str) -> bool:
    """
    Verify a server-issued secret against a stored hash.
    Returns True if valid, False otherwise.
    """
    if not secret or not hashed:
        return False

    try:
        peppered = f"{secret}::{get_pepper()}"
        return _secret_context.verify(peppered, hashed)
    except UnknownHashError:
        return False
    

def needs_rehash(hashed: str) -> bool:
    """
    Check if a stored secret hash needs upgrading.
    Useful when security parameters change.
    """
    return _secret_context.needs_update(hashed)