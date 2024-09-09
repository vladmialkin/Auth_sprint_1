from datetime import UTC, datetime, timedelta
from uuid import UUID

from fastapi_users import BaseUserManager, UUIDIDMixin
from sqlalchemy.orm import joinedload

from app.models import Session, User
from app.repository.refresh_token import refresh_token_repository
from app.repository.session import session_repository
from app.settings.api import settings as api_settings


class UserManager(UUIDIDMixin, BaseUserManager[User, UUID]):
    reset_password_token_secret = api_settings.SECRET_KEY
    verification_token_secret = api_settings.SECRET_KEY

    async def create_session(
        self,
        refresh_token: str,
        user_agent: str,
        user: User,
        refresh_lifetime_seconds: int,
    ):
        stored_refresh_token = await refresh_token_repository.create(
            self.user_db.session,
            data={
                "token": refresh_token,
                "expiration_date": datetime.now(UTC).replace(tzinfo=None)
                + timedelta(seconds=refresh_lifetime_seconds),
            },
            commit=False,
        )
        await session_repository.create(
            self.user_db.session,
            data={
                "user_id": user.id,
                "refresh_token_id": stored_refresh_token.id,
                "user_agent": user_agent,
            },
        )

    async def expire_session(self, user: User, user_agent: str) -> None:
        session: Session = await session_repository.get(
            self.user_db.session,
            user_id=user.id,
            user_agent=user_agent,
            options=[joinedload(Session.refresh_token)],
        )

        await refresh_token_repository.update(
            self.user_db.session,
            session.refresh_token,
            {"expiration_date": datetime.now(UTC).replace(tzinfo=None)},
        )

    async def prolong_session(
        self, user: User, user_agent: str, refresh_lifetime_seconds: int
    ) -> None:
        session: Session = await session_repository.get(
            self.user_db.session,
            user_id=user.id,
            user_agent=user_agent,
            options=[joinedload(Session.refresh_token)],
        )

        await refresh_token_repository.update(
            self.user_db.session,
            session.refresh_token,
            {
                "expiration_date": datetime.now(UTC).replace(tzinfo=None)
                + timedelta(seconds=refresh_lifetime_seconds)
            },
        )
