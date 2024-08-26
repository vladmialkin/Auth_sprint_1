from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Text
from app.models.base import Base


class Role(Base):
    name: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
