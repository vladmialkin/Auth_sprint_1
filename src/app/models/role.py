from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import String

from app.common.constance import STRING_LENGTH
from app.models.base import Base


class Role(Base):
    name: Mapped[str] = mapped_column(String(STRING_LENGTH), unique=True)
