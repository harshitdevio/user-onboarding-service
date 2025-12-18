from __future__ import annotations

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security.hashing.password import PasswordHasher
from app.core.security.hashing.pin import hash_pin
from app.db.models.User.pre_user import PreUser


_password_hasher = PasswordHasher()


async def set_password(
    *,
    db: AsyncSession,
    preuser_id: int,
    password: str,
) -> None:
    """
    Hash and persist a login password for a PreUser.

    Password hashing uses the dedicated PasswordHasher (Argon2id + pepper).
    Validation and policy enforcement must occur upstream.
    """

    hashed_password = _password_hasher.hash(password)

    result = await db.execute(
        update(PreUser)
        .where(PreUser.id == preuser_id)
        .values(hashed_password=hashed_password)
    )

    if result.rowcount != 1:
        raise ValueError(f"PreUser {preuser_id} not found")

    await db.commit()


async def set_pin(
    *,
    db: AsyncSession,
    preuser_id: int,
    pin: str,
) -> None:
    """
    Hash and persist a transaction PIN for a PreUser.

    PIN hashing uses a dedicated Argon2id configuration with a
    separate peppering policy.
    """

    hashed_pin = hash_pin(pin)

    result = await db.execute(
        update(PreUser)
        .where(PreUser.id == preuser_id)
        .values(hashed_pin=hashed_pin)
    )

    if result.rowcount != 1:
        raise ValueError(f"PreUser {preuser_id} not found")

    await db.commit()
