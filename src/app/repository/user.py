import secrets
from typing import Any

from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.repository.base import SQLAlchemyRepository
from app.settings.crypt_context import settings as crypt_context_settings


class UserRepository(SQLAlchemyRepository[User]):
    def _set_password(self, password: str) -> str:
        pwd_ctx = CryptContext(
            schemes=crypt_context_settings.SCHEMES,
            deprecated=crypt_context_settings.DEPRECATED,
        )
        salt = secrets.token_urlsafe(16)
        password = pwd_ctx.hash(password + salt)

        return password, salt

    async def create(
        self, session: AsyncSession, data: dict[str, Any], commit: bool = True
    ) -> User:
        data["password"], data["salt"] = self._set_password(data["password"])
        return await super().create(session, data, commit)


user_repository = UserRepository(User)
