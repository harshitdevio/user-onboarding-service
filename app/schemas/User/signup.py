from pydantic import BaseModel, Field

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
