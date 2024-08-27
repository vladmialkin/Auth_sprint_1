from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Text
from app.models.base import Base
from sqlalchemy import ForeignKey


class Session(Base):
    user_id: Mapped[UUID] = mapped_column(ForeignKey('auth.user.id', ondelete='CASCADE'))
    refresh_token_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            column='auth.refresh_token.id',
            ondelete='CASCADE'
        )
    )
    user_agent: Mapped[str] = mapped_column(Text(254), unique=True)
