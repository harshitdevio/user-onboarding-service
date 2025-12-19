from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.OTP.service import issue_otp
from app.core.Utils.phone import normalize_phone
from app.core.security.rate_limit import enforce_otp_rate_limit
from app.domain.user.status import OnboardingState
from app.repository.user.pre_user import create_preuser
from app.schemas.User.signup import (
    PhoneSubmitResponse,
    OTPVerifyResponse,
)
from app.services.OTP.verify_otp import verify_otp_flow
from app.services.User.preuser_credentials import (
    set_preuser_password,
    InvalidPreUserState,
    CredentialsAlreadySet,
)

class UserOnboardingError(Exception):
    pass


class PasswordAlreadySet(UserOnboardingError):
    pass


class InvalidOnboardingState(UserOnboardingError):
    pass


class UserOnboarding:

    @staticmethod
    async def submit_phone(phone: str) -> PhoneSubmitResponse:
        """
        Step 1–3:
        - Phone submitted
        - Rate-limit gate
        - OTP issued & stored
        """

        normalized_phone = normalize_phone(phone)

        # Step 2: rate-limit
        await enforce_otp_rate_limit(normalized_phone)

        # Step 3: generate + hash + store OTP
        otp = await issue_otp(phone=normalized_phone)

        # (TEMP) You will remove this once SMS is wired
        # print(f"OTP for {normalized_phone}: {otp}")

        return PhoneSubmitResponse(
            phone=normalized_phone,
            status="OTP_SENT",
        )

    @staticmethod
    async def verify_otp(phone: str, otp: str) -> OTPVerifyResponse:
        """
        Step 4: OTP verification
        """

        await verify_otp_flow(phone=phone, otp=otp)

        # OTP valid → orchestration can move to next step
        return OTPVerifyResponse(
            phone=phone,
            status="OTP_VERIFIED",
        )
    
    @staticmethod
    async def verify_otp(
        *,
        db: AsyncSession,
        phone: str,
        otp: str,
    ) -> OTPVerifyResponse:
        """
        Step 4–5:
        - OTP verification
        - PreUser creation (idempotent)
        """

        # Step 4: Redis-based OTP verification
        await verify_otp_flow(phone=phone, otp=otp)

        # Step 5: DB backed PreUser creation
        await create_preuser(
            db=db,
            phone=phone,
        )

        return OTPVerifyResponse(
            phone=phone,
            status=OnboardingState.PREUSER_CREATED,
        )
    

    @staticmethod
    async def set_password(
        *,
        db: AsyncSession,
        phone: str,
        password: str,
    ) -> None:
        """
        Handle password setup after OTP verification.
        """

        try:
            await set_preuser_password(
                db=db,
                phone=phone,
                raw_password=password,
            )
        except CredentialsAlreadySet:
            raise PasswordAlreadySet()
        except InvalidPreUserState:
            raise InvalidOnboardingState()