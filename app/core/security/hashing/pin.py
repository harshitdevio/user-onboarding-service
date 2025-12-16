from __future__ import annotations

from passlib.context import CryptContext
from passlib.exc import UnknownHashError

from .base import get_pepper, apply_pepper, HashingError

_pin_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
    argon2__type="ID",
    argon2__memory_cost=65536,  # 64 MB
    argon2__time_cost=3,
    argon2__parallelism=2,
    argon2__hash_len=32,
    argon2__salt_size=16,
)

def hash_pin(pin: str) -> str:
    if not pin or not pin.isdigit():
        raise ValueError("PIN must be numeric")

    pepper = get_pepper()
    peppered = apply_pepper(pin, pepper)

    return _pin_context.hash(peppered)
