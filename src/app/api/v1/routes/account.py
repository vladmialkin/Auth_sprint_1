from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.api.deps import Session
from app.api.v1.schemas.role import (
    RoleCreateSchema,
    RoleRetrieveSchema,
    RoleUpdateSchema,
)
from app.repository.role import role_repository

router = APIRouter()


@router.post("/")
async def create_role(
    session: Session, data: RoleCreateSchema
) -> RoleRetrieveSchema:
    """Создание роли."""
    is_exist = await role_repository.exists(session, name=data.name)

    if is_exist:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Role already exists",
        )

    return await role_repository.create(session, data={"name": data.name})


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(session: Session, role_id: UUID) -> None:
    """Удаление роли."""

    is_exist = await role_repository.exists(session, id=role_id)

    if not is_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Role not found"
        )

    role = await role_repository.get(session, id=role_id)

    await role_repository.delete(session, role)


@router.put("/{role_id}")
async def update_role(
    session: Session, data: RoleUpdateSchema, role_id: UUID
) -> RoleRetrieveSchema:
    """Изменение роли."""

    is_exist = await role_repository.exists(session, id=role_id)

    if not is_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Role not found"
        )

    role = await role_repository.get(session, id=role_id)
    new_role = await role_repository.update(session, role, {"name": data.name})

    return new_role


@router.get("/")
async def get_roles(session: Session) -> list[RoleRetrieveSchema]:
    """Просмотр всех ролей."""

    return await role_repository.filter(session)


@router.get("/{role_id}")
async def get_role_info(session: Session, role_id: UUID) -> RoleRetrieveSchema:
    """Получение информации о роли."""

    return await role_repository.get(session, id=role_id)
