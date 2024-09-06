from app.models import Session
from app.repository.base import SQLAlchemyRepository


class SessionRepository(SQLAlchemyRepository[Session]):
    pass


session_repository = SessionRepository(Session)
