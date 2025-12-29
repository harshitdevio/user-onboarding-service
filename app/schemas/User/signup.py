from pydantic import BaseModel, Field, EmailStr
from app.domain.user.status import OnboardingState


class SignupRequestOTP(BaseModel):
    phone: str = Field(
        ...,
        pattern=r"^(?:\+91)?[6-9]\d{9}$",
        description="User's mobile number with optional +91"
    )


class SignupVerifyOTP(BaseModel):
    phone: str = Field(
        ...,
        pattern=r"^(?:\+91)?[6-9]\d{9}$"
    )
    otp: str = Field(
        ...,
        min_length=6,
        max_length=6,
        pattern=r"^\d{6}$",
        description="6-digit signup OTP"
    )


class SignupProfileDetails(BaseModel):
    first_name: str = Field(
        ...,
        min_length=1,
        max_length=50
    )
    last_name: str = Field(
        ...,
        min_length=1,
        max_length=50
    )
    email: EmailStr = Field(
        ...
    )


class PhoneSubmitRequest(BaseModel):
    phone: str = Field(
        ...,
        description="User phone number in E.164 or local format"
    )


class PhoneSubmitResponse(BaseModel):
    phone: str
    status: str


class OTPVerifyRequest(BaseModel):
    phone: str = Field(
        ...,
        pattern=r"^(?:\+91)?[6-9]\d{9}$",
        description="User's mobile number used for OTP verification"
    )
    otp: str = Field(
        ...,
        min_length=6,
        max_length=6,
        pattern=r"^\d{6}$",
        description="6-digit OTP"
    )


class OTPVerifyResponse(BaseModel):
    phone: str = Field(
        ...,
        pattern=r"^(?:\+91)?[6-9]\d{9}$",
        description="Verified phone number"
    )
    status: OnboardingState = Field(
        ...,
        description="Current onboarding state after OTP verification"
    )
    
class SetPasswordRequest(BaseModel):
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="User password set after successful OTP verification"
    )
