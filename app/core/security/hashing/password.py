from __future__ import annotations

from passlib.context import CryptContext
from passlib.exc import UnknownHashError

from security.hashing.base import get_pepper, apply_pepper, HashingError, Hasher


pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
    argon2__type="ID",
    argon2__memory_cost=65536,  # 64 MB
    argon2__time_cost=3,
    argon2__parallelism=1,
    argon2__hash_len=32,
    argon2__salt_size=16,
)


class PasswordHasher(Hasher):

    def __init__(self):
        self._pepper = get_pepper()

    def hash(self, password: str) -> str:
        
        if not password:
            raise HashingError("Password cannot be empty")

        peppered = apply_pepper(password, self._pepper)
        return pwd_context.hash(peppered)
    
    def verify(self, password: str, hashed: str) -> bool:

        if not password or not hashed:
            return False

        try:
            peppered = apply_pepper(password, self._pepper)
            return pwd_context.verify(peppered, hashed)
        except UnknownHashError:
            return False