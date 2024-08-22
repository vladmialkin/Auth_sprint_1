from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Index(Base):
    message: Mapped[str] = mapped_column(String(256), nullable=True)
