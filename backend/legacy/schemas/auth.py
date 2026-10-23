from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.user import UserRole


class UserRegister(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "email": "ada@example.com",
                    "password": "password123",
                    "full_name": "Ada Lovelace",
                    "role": "candidate",
                }
            ]
        }
    )

    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    full_name: str = Field(min_length=1, max_length=255)
    role: UserRole


class UserLogin(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{"email": "ada@example.com", "password": "password123"}]
        }
    )

    email: EmailStr
    password: str = Field(min_length=1, max_length=72)


class TokenRefresh(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={"examples": [{"refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}]}
    )

    refresh_token: str = Field(min_length=1)


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: EmailStr
    role: UserRole
    full_name: str
    created_at: datetime


class AuthResponse(BaseModel):
    user: UserPublic
    tokens: TokenPair
