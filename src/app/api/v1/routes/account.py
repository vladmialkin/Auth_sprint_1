from fastapi import APIRouter, HTTPException, status

from app.api.deps import Session

from app.services import role_service
from app.api.v1.schemas.role import (
    RoleCreateSchema,
    RoleUpdateSchema,
    RolesSchema
)
from app.repository.role import role_repository


router = APIRouter()


@router.post("/create")
async def create_role(session: Session, data: RoleCreateSchema) -> RoleUpdateSchema:
    """Создание роли."""

    role = await role_repository.create(session, data={"name": data.name})

    if role is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Role already exists",
        )

    return role


@router.delete("/delete/{role_id}")
async def delete_role(session: Session, role_id: str):
    """Удаление роли."""

    result = await role_service.delete_role(session, role_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    return status.HTTP_200_OK


@router.put("/update/{role_id}")
async def update_role(session: Session, data: RoleUpdateSchema, role_id: str) -> RoleUpdateSchema:
    """Изменение роли."""
    updated_role = await role_service.update_role(session, role_id, data.model_dump())

    if not updated_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )

    return updated_role


@router.get("/roles")
async def get_roles(session: Session) -> list[RolesSchema]:
    """Просмотр всех ролей."""
    roles = await role_repository.get_all(session)
    roles_list = [RolesSchema(**role.to_dict()) for role in roles]

    return roles_list
