from dataclasses import asdict, dataclass
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from uuid import UUID

import jwt
from jwt import PyJWTError
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.repository.refresh_token import refresh_token_repository
from app.repository.session import session_repository
from app.repository.user import user_repository
from app.services.session.exceptions import (
    NotAuthenticatedError,
    UserNotFoundError,
)
from app.settings.crypt_context import settings as crypt_context_settings
from app.settings.jwt import settings as jwt_settings


class TokenType(StrEnum):
    ACCESS = "access"
    REFRESH = "refresh"


@dataclass
class JWTTokenPayload:
    username: str
    user_id: str
    user_agent: str
    exp: datetime
    token_type: TokenType


async def create_session(
    db_session: AsyncSession, username: str, password: str, user_agent: str
) -> tuple[str, str]:
    authenticated = await authenticate_user(db_session, username, password)

    access_token, *_ = create_access_token(
        authenticated.username, authenticated.id, user_agent
    )
    refresh_token, exp = create_refresh_token(
        authenticated.username, authenticated.id, user_agent
    )

    stored_refresh_token = await refresh_token_repository.create(
        db_session,
        data={
            "token": refresh_token,
            "expiration_date": exp,
        },
        commit=False,
    )

    await session_repository.create(
        db_session,
        {
            "user_id": authenticated.id,
            "refresh_token_id": stored_refresh_token.id,
            "user_agent": user_agent,
        },
    )

    return access_token, refresh_token


async def get_user(db_session: AsyncSession, username: str) -> User:
    is_exists = await user_repository.exists(db_session, username=username)

    if not is_exists:
        raise UserNotFoundError

    user = await user_repository.get(db_session, username=username)

    return user


async def authenticate_user(
    db_session: AsyncSession, username: str, password: str
) -> User:
    user = await get_user(db_session, username)

    pwd_ctx = CryptContext(
        schemes=crypt_context_settings.SCHEMES,
        deprecated=crypt_context_settings.DEPRECATED,
    )

    if not pwd_ctx.verify(password + user.salt, user.password):
        raise NotAuthenticatedError

    return user


def create_access_token(
    username: str, user_id: UUID, user_agent: str
) -> tuple[str, datetime]:
    payload = JWTTokenPayload(
        username=username,
        user_id=str(user_id),
        user_agent=user_agent,
        token_type=TokenType.ACCESS,
        exp=datetime.now(UTC).replace(tzinfo=None)
        + timedelta(minutes=jwt_settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    to_encode = asdict(payload)
    encoded_jwt = jwt.encode(
        to_encode,
        jwt_settings.SECRET_KEY,
        algorithm=jwt_settings.ALGORITHM,
    )
    return encoded_jwt, payload.exp


def create_refresh_token(
    username: str, user_id: UUID, user_agent: str
) -> tuple[str, datetime]:
    payload = JWTTokenPayload(
        username=username,
        user_id=str(user_id),
        user_agent=user_agent,
        token_type=TokenType.REFRESH,
        exp=datetime.now(UTC).replace(tzinfo=None)
        + timedelta(minutes=jwt_settings.REFRESH_TOKEN_EXPIRE_MINUTES),
    )
    to_encode = asdict(payload)
    encoded_jwt = jwt.encode(
        to_encode,
        jwt_settings.SECRET_KEY,
        algorithm=jwt_settings.ALGORITHM,
    )
    return encoded_jwt, payload.exp


async def validate_refresh_token(refresh_token: str) -> JWTTokenPayload:
    try:
        payload = jwt.decode(
            refresh_token,
            jwt_settings.SECRET_KEY,
            algorithms=[jwt_settings.ALGORITHM],
        )
    except PyJWTError as e:
        raise NotAuthenticatedError from e

    if payload.get("token_type") != TokenType.REFRESH:
        raise NotAuthenticatedError

    username: str = payload.get("username")
    user_id: str = payload.get("user_id")
    exp: datetime = payload.get("exp")
    user_agent: str = payload.get("user_agent")

    if not username or not user_id:
        raise NotAuthenticatedError

    return JWTTokenPayload(
        username=username,
        user_id=user_id,
        user_agent=user_agent,
        exp=exp,
        token_type=TokenType.REFRESH,
    )


async def refresh_access_token(
    db_session: AsyncSession, refresh_token: str
) -> tuple[str, str]:
    stored_refresh_token = await refresh_token_repository.get(
        db_session, token=refresh_token
    )

    if not stored_refresh_token:
        raise NotAuthenticatedError

    payload = await validate_refresh_token(refresh_token)

    access_token, *_ = create_access_token(
        payload.username, payload.user_id, payload.user_agent
    )
    refresh_token, exp = create_refresh_token(
        payload.username, payload.user_id, payload.user_agent
    )

    # TODO: по user_id и user_agent сходить в Redis
    # и заблеклистить текущий access_token

    await refresh_token_repository.update(
        db_session,
        obj=stored_refresh_token,
        data={
            "token": refresh_token,
            "expiration_date": exp,
        },
    )

    return access_token, refresh_token
