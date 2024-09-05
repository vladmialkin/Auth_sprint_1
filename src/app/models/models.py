from datetime import datetime
from uuid import UUID as PY_UUID

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    String,
    Table,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, mapper_registry
from app.models.constance import (
    EMAIL_STR_LEN,
    NAME_STR_LEN,
    PASSWORD_STR_LEN,
    REFRESH_TOKEN_STR_LEN,
    SALT_STR_LEN,
    USER_AGENT_STR_LEN,
)

user_role = Table(
    "userrole",
    Base.metadata,
    Column("user_id", ForeignKey("user.id"), primary_key=True),
    Column("role_id", ForeignKey("role.id"), primary_key=True),
)


class UserRole:
    pass


mapper_registry.map_imperatively(UserRole, user_role)


class User(Base):
    username: Mapped[str] = mapped_column(String(NAME_STR_LEN), unique=True)
    password: Mapped[str] = mapped_column(String(PASSWORD_STR_LEN))
    email: Mapped[str | None] = mapped_column(
        String(EMAIL_STR_LEN), unique=True
    )
    salt: Mapped[str] = mapped_column(String(SALT_STR_LEN))
    is_active: Mapped[bool] = mapped_column(default=True)
    is_stuff: Mapped[bool] = mapped_column(default=False)
    is_superuser: Mapped[bool] = mapped_column(default=False)
    last_login: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), server_default=func.now()
    )

    roles: Mapped[list["Role"]] = relationship(
        "Role", secondary=user_role, back_populates="users"
    )
    sessions: Mapped[list["Session"]] = relationship(
        "Session", back_populates="user"
    )


class Role(Base):
    name: Mapped[UUID] = mapped_column(String(NAME_STR_LEN))

    users: Mapped[list[User]] = relationship(
        "User", secondary=user_role, back_populates="roles"
    )


class RefreshToken(Base):
    token: Mapped[str] = mapped_column(String(REFRESH_TOKEN_STR_LEN))
    expiration_date: Mapped[datetime] = mapped_column(DateTime(timezone=False))

    session: Mapped["Session"] = relationship(
        "Session", back_populates="refresh_token"
    )


class Session(Base):
    user_id: Mapped[PY_UUID] = mapped_column(ForeignKey("user.id"))
    refresh_token_id: Mapped[PY_UUID] = mapped_column(
        ForeignKey("refreshtoken.id")
    )
    user_agent: Mapped[str | None] = mapped_column(String(USER_AGENT_STR_LEN))

    user: Mapped[User] = relationship("User", back_populates="sessions")
    refresh_token: Mapped[RefreshToken] = relationship(
        "RefreshToken", back_populates="session"
    )
