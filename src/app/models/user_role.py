from sqlalchemy import Column, ForeignKey, Table, UniqueConstraint

from app.models.base import Base, mapper_registry

user_role = Table(
    "user_role",
    Base.metadata,
    Column("user_id", ForeignKey("auth.user.id"), primary_key=True),
    Column("role_id", ForeignKey("auth.role.id"), primary_key=True),
    UniqueConstraint("user_id", "role_id"),
)


class UserRole:
    pass


mapper_registry.map_imperatively(UserRole, user_role)
