from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.schemas.auth import TokenPair, UserRegister


def issue_token_pair(user: User) -> TokenPair:
    extra = {"role": user.role.value, "email": user.email}
    return TokenPair(
        access_token=create_access_token(user.id, extra_claims=extra),
        refresh_token=create_refresh_token(user.id, extra_claims=extra),
    )


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    result = await session.execute(select(User).where(User.email == email.lower()))
    return result.scalar_one_or_none()


async def get_user_by_id(session: AsyncSession, user_id: UUID) -> User | None:
    result = await session.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def register_user(session: AsyncSession, payload: UserRegister) -> User:
    user = User(
        email=str(payload.email).lower(),
        hashed_password=hash_password(payload.password),
        role=payload.role,
        full_name=payload.full_name.strip(),
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def authenticate_user(session: AsyncSession, email: str, password: str) -> User | None:
    user = await get_user_by_email(session, email)
    if user is None or not verify_password(password, user.hashed_password):
        return None
    return user


async def rotate_refresh_token(session: AsyncSession, refresh_token: str) -> User:
    payload = decode_token(refresh_token, expected_type="refresh")
    user = await get_user_by_id(session, UUID(payload["sub"]))
    if user is None:
        raise ValueError("Invalid token subject")
    return user


def parse_access_subject(access_token: str) -> UUID:
    payload = decode_token(access_token, expected_type="access")
    return UUID(payload["sub"])


__all__ = [
    "authenticate_user",
    "get_user_by_email",
    "get_user_by_id",
    "issue_token_pair",
    "parse_access_subject",
    "register_user",
    "rotate_refresh_token",
]
