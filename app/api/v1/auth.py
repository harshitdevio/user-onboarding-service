from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException

from app.schemas.User.login import RequestOTP, VerifyOTP
from app.orchestration.UserOnboarding import UserOnboarding
from app.auth.OTP.service import send_otp, verify_otp
from app.schemas.User.signup import (
    PhoneSubmitRequest,
    PhoneSubmitResponse,
    OTPVerifyRequest, 
    OTPVerifyResponse, 
    SetPasswordRequest
)
from app.db.session import get_db

from app.orchestration.UserOnboarding import (
    get_verified_phone, 
    PasswordAlreadySet,
    InvalidOnboardingState
)    



router = APIRouter(tags=["Auth"])

@router.post("/send-otp")
async def send_otp_route(payload: RequestOTP):
    await send_otp(payload.phone)
    return {"status": "otp_sent"}

@router.post("/verify-otp")
async def verify_otp_route(payload: VerifyOTP):
    valid = await verify_otp(payload.phone, payload.otp)

    if not valid:
        return {"valid": False}
    return {"valid": True}

@router.post("/signup/phone", response_model=PhoneSubmitResponse)
async def submit_phone(payload: PhoneSubmitRequest):
    return await UserOnboarding.submit_phone(payload.phone)


@router.post("/signup/verify-otp", response_model=OTPVerifyResponse)
async def verify_otp_endpoint(payload: OTPVerifyRequest):
    return await UserOnboarding.verify_otp(
        phone=payload.phone,
        otp=payload.otp,
    )

@router.post("/signup/set-password", status_code=204)
async def set_signup_password(
    payload: SetPasswordRequest,
    db: AsyncSession = Depends(get_db),
    phone: str = Depends(get_verified_phone),  # OTP context
):
    try:
        await UserOnboarding.set_password(
            db=db,
            phone=phone,
            password=payload.password,
        )
    except PasswordAlreadySet:
        raise HTTPException(409, "Password already set")
    except InvalidOnboardingState:
        raise HTTPException(409, "Invalid onboarding state")
