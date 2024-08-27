from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Boolean, DateTime, Text, LargeBinary

from app.models.role import Role
from app.models.base import Base
import datetime


class User(Base):
    email: Mapped[str] = mapped_column(Text(254),unique=True)
    password: Mapped[str] = mapped_column(Text(254))
    salt: Mapped[bytes] = mapped_column(LargeBinary(512))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_staff: Mapped[bool] = mapped_column(Boolean, default=False)
    is_super_user: Mapped[bool] = mapped_column(Boolean, default=False)
    last_login: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    roles: Mapped[list[Role]] = relationship("Role", secondary="user_role", back_populates="users")
