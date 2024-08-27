from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base
from sqlalchemy.types import Text, DateTime
import datetime


class RefreshToken(Base):
    __tablename__ = 'refresh_token'
    token: Mapped[str] = mapped_column(Text)
    expiration_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    UniqueConstraint('token')
