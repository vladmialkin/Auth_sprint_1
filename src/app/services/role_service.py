from sqlalchemy.ext.asyncio import AsyncSession

from app.repository.role import role_repository


async def delete_role(session: AsyncSession, role_id: str) -> bool:
    role_obj = await role_repository.get(session, **{"id": role_id})

    if role_obj is None:
        return False

    await role_repository.delete(session, role_obj)

    return True


async def update_role(session: AsyncSession, role_id: str, data: dict):
    role_odj = await role_repository.get(session, **{"id": role_id})

    if role_odj is None:
        return False

    role_updated = await role_repository.update(session, role_odj, data)

    return role_updated
