from pydantic import BaseModel, Field

class SetPasswordRequest(BaseModel):
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="User account password",
    )
