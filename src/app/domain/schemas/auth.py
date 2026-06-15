from typing import Literal

from pydantic import BaseModel, EmailStr, Field, model_validator

UserRole = Literal["buyer", "vendor"]


class RegisterDTO(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role: UserRole = "buyer"
    name: str | None = Field(default=None, max_length=100)
    # Required when role == "vendor": the linked store needs a name.
    store_name: str | None = Field(default=None, max_length=100)

    @model_validator(mode="after")
    def _require_store_name_for_vendor(self) -> "RegisterDTO":
        if self.role == "vendor" and not self.store_name:
            raise ValueError("store_name is required when role is 'vendor'")
        return self


class LoginDTO(BaseModel):
    email: EmailStr
    password: str


class RefreshDTO(BaseModel):
    refresh_token: str


class TokenResponseDTO(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
