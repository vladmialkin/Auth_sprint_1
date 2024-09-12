from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Session
from app.repository.base import SQLAlchemyRepository


class SessionRepository(SQLAlchemyRepository[Session]):
    @staticmethod
    async def get_history(session: AsyncSession) -> list[Session]:
        query = select(Session).order_by(Session.created_at.desc())
        return (await session.execute(query)).scalars().all()


session_repository = SessionRepository(Session)
