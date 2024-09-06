from datetime import datetime
from uuid import UUID

from app.api.v1.schemas.base import Base


class RoleBaseSchema(Base):
    name: str


class RolesSchema(RoleBaseSchema):
    id: UUID
    created_at: datetime


class RoleCreateSchema(RoleBaseSchema): ...


class RoleUpdateSchema(RoleBaseSchema): ...
