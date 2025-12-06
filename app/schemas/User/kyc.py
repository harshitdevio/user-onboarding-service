from pydantic import BaseModel, Field
from datetime import date

class KYCBasicDetails(BaseModel):
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
    dob: date = Field(
        ...,
        description="Date of birth in YYYY-MM-DD format"
    )
    gender: str = Field(
        ...,
        pattern=r"^(male|female|other)$",
        description="Gender as male, female, or other"
    )
    pan_number: str = Field(
        ...,
        pattern=r"^[A-Z]{5}[0-9]{4}[A-Z]$",
        description="Valid PAN format (e.g., ABCDE1234F)"
    )
    address_line1: str = Field(
        ...,
        max_length=200
    )
    address_line2: str = Field(
        None,
        max_length=200
    )
    city: str = Field(
        ...,
        max_length=100
    )
    state: str = Field(
        ...,
        max_length=100
    )
    pincode: str = Field(
        ...,
        pattern=r"^\d{6}$",
        description="6-digit Indian PIN code"
    )
    country: str = Field(
        default="India",
        const=True,
        description="Country fixed as India"
    )
