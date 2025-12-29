from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date

from app.services.OTP.issue_otp import issue_otp
from app.core.Utils.phone import normalize_phone
from app.domain.user.status import OnboardingState
from app.domain.user.preuser_onboarding import create_preuser
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
from app.services.User.preuser_profile import (
    complete_basic_profile,
    ProfileAlreadyCompleted,
    InvalidPreUserState as ProfileInvalidState,
)
from app.domain.risks.evaluate import evaluate_risk
from app.repository.user.pre_user import PreUserRepository

from app.services.account.create_limited_account import (
    create_limited_account,
    RiskNotApproved,
)
from app.services.kyc.submit_kyc import submit_kyc, KYCAlreadySubmitted
from app.services.kyc.verify_kyc import approve_kyc, reject_kyc
from app.services.account.upgrade import upgrade_account_to_full
from app.domain.auth.otp_purpose import OTPPurpose


class UserOnboardingError(Exception):
    pass


class PasswordAlreadySet(UserOnboardingError):
    pass


class InvalidOnboardingState(UserOnboardingError):
    pass


class ProfileAlreadyCompletedError(UserOnboardingError):
    pass


class UserOnboarding:

    @staticmethod
    async def submit_phone(phone: str) -> PhoneSubmitResponse:
        """
        Step 1–3:
        - Phone submitted
        - OTP issued & stored
        """

        normalized_phone = normalize_phone(phone)

        await issue_otp(
            phone=normalized_phone,
            purpose=OTPPurpose.SIGNUP,
        )

        return PhoneSubmitResponse(
            phone=normalized_phone,
            status="OTP_SENT",
        )

    @staticmethod
    async def verify_otp_and_create_preuser(
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

        await verify_otp_flow(
            phone=phone,
            otp=otp,
            purpose=OTPPurpose.SIGNUP,
        )

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
        Step 6:
        - Set password after OTP verification
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

    @staticmethod
    async def complete_basic_profile(
        *,
        db: AsyncSession,
        phone: str,
        first_name: str,
        last_name: str,
        date_of_birth: date,
        address: str,
    ) -> None:
        """
        Step 7:
        - Complete basic profile details
        """

        try:
            await complete_basic_profile(
                db=db,
                phone=phone,
                first_name=first_name,
                last_name=last_name,
                date_of_birth=date_of_birth,
                address=address,
            )
        except ProfileAlreadyCompleted:
            raise ProfileAlreadyCompletedError()
        except ProfileInvalidState:
            raise InvalidOnboardingState()

    @staticmethod
    async def evaluate_risk(
        *,
        db: AsyncSession,
        phone: str,
        otp_retry_count: int,
    ) -> str:
        """
        Step 8:
        - Evaluate onboarding risk
        """

        repo = PreUserRepository()
        preuser = await repo.get_by_phone(db, phone)

        return await evaluate_risk(
            preuser=preuser,
            otp_retry_count=otp_retry_count,
            db=db,
        )

    @staticmethod
    async def create_limited_account(
        *,
        db: AsyncSession,
        user,
    ) -> None:
        """
        Step 9:
        - Create LIMITED account after risk approval
        """

        try:
            await create_limited_account(
                db=db,
                user=user,
            )
        except RiskNotApproved:
            raise InvalidOnboardingState()

    @staticmethod
    async def submit_kyc(
        *,
        db: AsyncSession,
        user,
        document_type: str,
        document_number: str,
    ) -> None:
        """
        Step 10:
        - Store KYC submission
        """

        try:
            await submit_kyc(
                db=db,
                user=user,
                document_type=document_type,
                document_number=document_number,
            )
        except KYCAlreadySubmitted:
            raise InvalidOnboardingState()

        user.onboarding_state = OnboardingState.KYC_SUBMITTED
        await db.commit()

    @staticmethod
    async def approve_kyc(
        *,
        db: AsyncSession,
        user,
        admin_id: str = "system",
    ) -> None:
        await approve_kyc(
            db=db,
            user=user,
            admin_id=admin_id,
        )

    @staticmethod
    async def reject_kyc(
        *,
        db: AsyncSession,
        user,
        admin_id: str = "system",
    ) -> None:
        await reject_kyc(
            db=db,
            user=user,
            admin_id=admin_id,
        )

    @staticmethod
    async def upgrade_to_full(
        *,
        db: AsyncSession,
        account,
    ) -> None:
        """
        Step 12:
        - Upgrade account to FULL tier
        """
        await upgrade_account_to_full(db=db, account=account)
