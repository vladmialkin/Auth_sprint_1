from sqlalchemy import Column, ForeignKey, Table, UniqueConstraint, func
from sqlalchemy.types import DateTime

from app.models.base import Base, mapper_registry

user_role = Table(
    "user_role",
    Base.metadata,
    Column("user_id", ForeignKey("user.id"), primary_key=True),
    Column("role_id", ForeignKey("role.id"), primary_key=True),
    Column("created_at", DateTime(timezone=False), server_default=func.now()),
    UniqueConstraint("user_id", "role_id"),
)


class UserRole:
    pass


mapper_registry.map_imperatively(UserRole, user_role)
