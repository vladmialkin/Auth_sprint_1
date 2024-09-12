from sqlalchemy import desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Session
from app.repository.base import SQLAlchemyRepository


class SessionRepository(SQLAlchemyRepository[Session]):
    async def get_history(self, db_session: AsyncSession, **attrs) -> list[Session]:
        return await self.filter_with_orderby(db_session, "created_at", desc, **attrs)


session_repository = SessionRepository(Session)
