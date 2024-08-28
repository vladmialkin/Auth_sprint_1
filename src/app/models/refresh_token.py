import datetime

from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import DateTime, String

from app.common.constance import LARGE_STRING_LENGTH
from app.models.base import Base


class RefreshToken(Base):
    token: Mapped[str] = mapped_column(String(LARGE_STRING_LENGTH))
    expiration_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    UniqueConstraint("token")
