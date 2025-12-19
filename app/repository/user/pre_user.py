from __future__ import annotations
from typing import Any

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.User.pre_user import PreUser


class PreUserRepository:
    """
    Repository layer for PreUser entity.

    Handles all database operations related to PreUser, including
    CRUD and state management. Designed for async usage with SQLAlchemy.
    """

    async def upsert_by_phone(
        self,
        db: AsyncSession,
        *,
        phone: str,
        onboarding_state: str,
    ) -> PreUser:
        """
        Insert a new PreUser if phone does not exist, otherwise update the onboarding_state.

        Args:
            db (AsyncSession): SQLAlchemy async session.
            phone (str): Phone number of the PreUser.
            onboarding_state (str): Current onboarding state.

        Returns:
            PreUser: The created or updated PreUser instance.
        """
        result = await db.execute(
            select(PreUser).where(PreUser.phone == phone)
        )
        preuser = result.scalar_one_or_none()

        if preuser:
            preuser.onboarding_state = onboarding_state
        else:
            preuser = PreUser(
                phone=phone,
                onboarding_state=onboarding_state,
            )
            db.add(preuser)

        await db.commit()
        await db.refresh(preuser)
        await db.flush()
        return preuser

    async def get_by_phone(self, db: AsyncSession, phone: str) -> PreUser:
        """
        Retrieve a PreUser by phone number.

        Args:
            db (AsyncSession): SQLAlchemy async session.
            phone (str): Phone number to search.

        Returns:
            PreUser: The matching PreUser.

        Raises:
            NoResultFound: If no PreUser exists with the given phone.
        """
        result = await db.execute(
            select(PreUser).where(PreUser.phone == phone)
        )
        return result.scalar_one()

    async def get(self, db: AsyncSession, preuser_id: int) -> PreUser:
        """
        Retrieve a PreUser by primary key ID.

        Args:
            db (AsyncSession): SQLAlchemy async session.
            preuser_id (int): The ID of the PreUser.

        Returns:
            PreUser: The matching PreUser.

        Raises:
            NoResultFound: If no PreUser exists with the given ID.
        """
        result = await db.execute(
            select(PreUser).where(PreUser.id == preuser_id)
        )
        return result.scalar_one()

    async def update_state(
        self,
        db: AsyncSession,
        *,
        preuser_id: int,
        onboarding_state: str,
    ) -> None:
        """
        Update only the onboarding_state of a PreUser.

        Args:
            db (AsyncSession): SQLAlchemy async session.
            preuser_id (int): ID of the PreUser.
            onboarding_state (str): New onboarding state.
        """
        await db.execute(
            update(PreUser)
            .where(PreUser.id == preuser_id)
            .values(onboarding_state=onboarding_state)
        )
        await db.commit()

    async def update_profile(
        self,
        db: AsyncSession,
        preuser_id: int,
        profile_data: dict[str, Any],
    ) -> None:
        """
        Update multiple fields of a PreUser's profile.

        Args:
            db (AsyncSession): SQLAlchemy async session.
            preuser_id (int): ID of the PreUser.
            profile_data (dict[str, Any]): Key-value pairs of fields to update.

        Warning:
            Ensure keys in profile_data match model columns to avoid runtime errors.
        """
        await db.execute(
            update(PreUser)
            .where(PreUser.id == preuser_id)
            .values(**profile_data)
        )
        await db.commit()

