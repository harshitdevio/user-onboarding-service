from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.User.pre_user import PreUser
from app.domain.user.status import OnboardingState
from app.repository.user.pre_user import PreUserRepository

async def create_preuser(
        *,
        db: AsyncSession,
        phone: str,
    ) -> PreUser:
        """
        Create or update a PreUser after OTP verification.

        Idempotent by phone.
        Safe to call multiple times.
        """

        repo = PreUserRepository()

        return await repo.upsert_by_phone(
            db,
            phone=phone,
            onboarding_state=OnboardingState.OTP_VERIFIED,
        )
