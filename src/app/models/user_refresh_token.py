from sqlalchemy import Column, ForeignKey, Table, UniqueConstraint

from app.models.base import Base, mapper_registry

user_refresh_token = Table(
    "user_refresh_token",
    Base.metadata,
    Column("user_id", ForeignKey("user.id"), primary_key=True),
    Column("refresh_token_id", ForeignKey("refreshtoken.id"), primary_key=True),
    UniqueConstraint("user_id", "refresh_token_id"),
)


class UserRefreshToken:
    pass


mapper_registry.map_imperatively(UserRefreshToken, user_refresh_token)
