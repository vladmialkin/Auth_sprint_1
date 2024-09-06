from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Role
from app.repository.base import SQLAlchemyRepository


class RoleRepository(SQLAlchemyRepository[Role]):
    async def get_all(self, session: AsyncSession) -> Sequence[Role]:
        query = select(Role)

        res = (await session.execute(query)).scalars().all()
        return res


role_repository = RoleRepository(Role)
