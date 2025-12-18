from app.core.Utils.phone import normalize_phone
from app.schemas.User.signup import PhoneSubmitResponse
from app.core.security.rate_limit import enforce_otp_rate_limit
from app.auth.OTP.service import issue_otp
from app.schemas.User.signup import OTPVerifyResponse
from app.services.OTP.verify_otp import verify_otp_flow

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


class UserOnboarding:

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