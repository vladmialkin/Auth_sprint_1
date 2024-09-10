from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.api.deps.session import Session
from app.api.v1.schemas.role import (
    RoleCreateSchema,
    RoleRetrieveSchema,
    RoleUpdateSchema,
    RoleSetRevokeSchema
)
from app.repository.role import role_repository
from app.repository.user_role import user_role_repository
from app.repository.user import user_repository
from app.api.deps.roles import ForAdminOnly


router = APIRouter()


@router.post("/")
async def create_role(
    session: Session,
    data: RoleCreateSchema,
    _: ForAdminOnly
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
async def delete_role(
    session: Session,
    role_id: UUID,
    _: ForAdminOnly
) -> None:
    """Удаление роли."""

    role = await role_repository.get(session, id=role_id)

    if role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Role not found"
        )

    await role_repository.delete(session, role)


@router.put("/{role_id}")
async def update_role(
    session: Session,
    data: RoleUpdateSchema,
    role_id: UUID,
    _: ForAdminOnly
) -> RoleRetrieveSchema:
    """Изменение роли."""

    role = await role_repository.get(session, id=role_id)

    if role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Role not found"
        )

    new_role = await role_repository.update(session, role, {"name": data.name})

    return new_role


@router.get("/")
async def get_roles(
    session: Session,
    _: ForAdminOnly,
) -> list[RoleRetrieveSchema]:
    """Просмотр всех ролей."""

    return await role_repository.filter(session)


@router.get("/{role_id}")
async def get_role_info(
    session: Session,
    role_id: UUID,
    _: ForAdminOnly
) -> RoleRetrieveSchema:
    """Получение информации о роли."""

    role = await role_repository.get(session, id=role_id)

    if role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Role not found"
        )

    return role


@router.post('/set_role', status_code=status.HTTP_200_OK)
async def set_role(
        session: Session,
        data: RoleSetRevokeSchema,
        _: ForAdminOnly
) -> None:
    """Назначение роли пользователю."""

    role = await role_repository.get(session, name=data.name)

    if role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Role not found"
        )

    user = await user_repository.exists(session, id=data.user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    payload = {
        "user_id": data.user_id,
        "role_id": role.id
    }

    await user_role_repository.create(session, payload)


@router.post('/revoke_role', status_code=status.HTTP_200_OK)
async def revoke_role(
        session: Session,
        data: RoleSetRevokeSchema,
        _: ForAdminOnly
) -> None:
    """Отзыв роли у пользователя."""

    role = await role_repository.get(session, name=data.name)

    if role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Role not found"
        )

    user = await user_repository.exists(session, id=data.user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    payload = {
        "user_id": data.user_id,
        "role_id": role.id
    }

    user_role = await user_role_repository.get(session, **payload)
    await user_repository.delete(session, user_role)
