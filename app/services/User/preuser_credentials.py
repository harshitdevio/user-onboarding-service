from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security.hashing.password import PasswordHasher
from app.db.enums import PreUserOnboardingState
from app.db.models.User.pre_user import PreUser
from app.repository.user.pre_user import PreUserRepository


class PreUserCredentialError(Exception):
    """Base exception for PreUser credential operations."""


class InvalidPreUserState(PreUserCredentialError):
    """Raised when credentials are set in an invalid onboarding state."""


class CredentialsAlreadySet(PreUserCredentialError):
    """Raised when credentials are already present for a PreUser."""


async def set_preuser_password(
    *,
    db: AsyncSession,
    phone: str,
    raw_password: str,
) -> PreUser:
    """
    Set the password for a PreUser after OTP verification.

    Rules:
    - OTP must already be verified
    - Password can be set only once at this stage
    - On success, onboarding state transitions to CREDENTIALS_SET
    """

    repo = PreUserRepository()
    hasher = PasswordHasher()

    # Fetch PreUser
    preuser = await repo.get_by_phone(db, phone)

    # State guard
    if preuser.onboarding_state != PreUserOnboardingState.OTP_VERIFIED:
        raise InvalidPreUserState(
            f"Cannot set password in state {preuser.onboarding_state}"
        )

    # Write-once guard
    if preuser.hashed_password:
        raise CredentialsAlreadySet("Password already set for this user")
    hashed_password = hasher.hash(raw_password)

    await repo.update_profile(
        db,
        preuser_id=preuser.id,
        profile_data={
            "hashed_password": hashed_password,
            "onboarding_state": PreUserOnboardingState.CREDENTIALS_SET,
        },
    )

    return await repo.get(db, preuser.id)
