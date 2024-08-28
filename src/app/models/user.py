import datetime
from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Boolean, DateTime, LargeBinary, String

from app.common.constance import LARGE_STRING_LENGTH, STRING_LENGTH
from app.models.base import Base
from app.models.role import Role


class User(Base):
    email: Mapped[str] = mapped_column(String(STRING_LENGTH), unique=True)
    password: Mapped[str] = mapped_column(String(STRING_LENGTH))
    salt: Mapped[bytes] = mapped_column(LargeBinary(LARGE_STRING_LENGTH))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_staff: Mapped[bool] = mapped_column(Boolean, default=False)
    is_super_user: Mapped[bool] = mapped_column(Boolean, default=False)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    roles: Mapped[list[Role]] = relationship("Role", secondary="user_role", back_populates="users")
