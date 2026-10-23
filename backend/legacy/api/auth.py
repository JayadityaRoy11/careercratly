from fastapi import APIRouter, HTTPException, Request, Response, status
from sqlalchemy.exc import IntegrityError

from app.api.deps import CurrentUser, DbSession
from app.core.config import settings
from app.core.openapi import ERROR_RESPONSES
from app.core.rate_limit import limiter
from app.schemas.auth import (
    AuthResponse,
    TokenPair,
    TokenRefresh,
    UserLogin,
    UserPublic,
    UserRegister,
)
from app.services.auth import (
    authenticate_user,
    get_user_by_email,
    issue_token_pair,
    register_user,
    rotate_refresh_token,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a candidate or recruiter",
    description="Create an account. Returns the user profile plus access and refresh JWTs.",
    responses={409: ERROR_RESPONSES[409], 422: ERROR_RESPONSES[422]},
)
async def register(payload: UserRegister, session: DbSession) -> AuthResponse:
    existing = await get_user_by_email(session, str(payload.email))
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    try:
        user = await register_user(session, payload)
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        ) from None

    return AuthResponse(user=UserPublic.model_validate(user), tokens=issue_token_pair(user))


@router.post(
    "/login",
    response_model=AuthResponse,
    summary="Log in",
    description="Exchange email and password for JWTs. Rate limited per client IP.",
    responses={401: ERROR_RESPONSES[401], 429: ERROR_RESPONSES[429], 422: ERROR_RESPONSES[422]},
)
@limiter.limit(settings.login_rate_limit)
async def login(
    request: Request, response: Response, payload: UserLogin, session: DbSession
) -> AuthResponse:
    user = await authenticate_user(session, str(payload.email), payload.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    return AuthResponse(user=UserPublic.model_validate(user), tokens=issue_token_pair(user))


@router.post(
    "/refresh",
    response_model=TokenPair,
    summary="Refresh access token",
    description="Issue a new access and refresh pair from a valid refresh token.",
    responses={401: ERROR_RESPONSES[401]},
)
async def refresh(payload: TokenRefresh, session: DbSession) -> TokenPair:
    try:
        user = await rotate_refresh_token(session, payload.refresh_token)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        ) from None
    return issue_token_pair(user)


@router.get(
    "/me",
    response_model=UserPublic,
    summary="Current user",
    description="Return the profile for the Bearer access token.",
    responses={401: ERROR_RESPONSES[401]},
)
async def me(current_user: CurrentUser) -> UserPublic:
    return UserPublic.model_validate(current_user)
