from fastapi import APIRouter, HTTPException, status

from app.api.deps import Session, Token, UserAgent, CurrentUserId
from app.api.v1.schemas.jwt_token import (
    JWTTokenRetrieveSchema,
)
from app.api.v1.schemas.user import (
    UserLoginSchema,
    UserRegiserSchema,
    UserRetrieveSchema,
)
from app.repository.user import user_repository
from app.services.session import (
    create_session,
    refresh_access_token,
)
from app.services.session.exceptions import (
    NotAuthenticatedError,
    UserNotFoundError,
)

router = APIRouter()


@router.post("/register")
async def register(
    session: Session, data: UserRegiserSchema
) -> UserRetrieveSchema:
    """Регистрация нового пользователя."""

    is_exists = await user_repository.exists(session, username=data.username)

    if is_exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this login already exists",
        )

    return await user_repository.create(session, data.model_dump())


@router.post("/login")
async def login(
    session: Session, data: UserLoginSchema, user_agent: UserAgent = None
) -> JWTTokenRetrieveSchema:
    """Авторизация пользователя."""

    try:
        access_token, refresh_token = await create_session(
            session, data.username, data.password, user_agent
        )
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incorrect username",
        ) from e
    except NotAuthenticatedError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        ) from e

    return {"access_token": access_token, "refresh_token": refresh_token}


@router.post("/refresh")
async def refresh(
    session: Session,
    refresh_token: Token,
) -> JWTTokenRetrieveSchema:
    """Обновление токена."""

    try:
        access_token, refresh_token = await refresh_access_token(
            session, refresh_token
        )
    except NotAuthenticatedError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        ) from e

    return {"access_token": access_token, "refresh_token": refresh_token}


@router.get("/some_protected_data")
async def get_protected_data(session: Session, user_id: CurrentUserId) -> dict:
    return {"msg": "protected_data"}
