from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import String

from app.common.constance import LARGE_STRING_LENGTH
from app.models.base import Base


class Session(Base):
    user_id: Mapped[UUID] = mapped_column(ForeignKey("auth.user.id"))
    refresh_token_id: Mapped[UUID] = mapped_column(ForeignKey(column="auth.refresh_token.id", ondelete="CASCADE"))
    user_agent: Mapped[str] = mapped_column(String(LARGE_STRING_LENGTH), unique=True)
