from functools import lru_cache

from app.models.schema_validation.user_schema import UserInDB
from app.api.deps import Session
from app.models.user import User
from sqlalchemy import insert, select


class PostgresService:
    def __init__(self, session: Session):
        self.session = session

    async def get_user_by_login(self, user_login: str) -> UserInDB | None:
        """if exist return UserInDB else None"""
        try:
            query = select(User).where(User.login == user_login)
            res = await self.session.execute(statement=query)
            user = res.scalar()
        except:
            user = None
        return user

    async def create_user_session(self, user_id, user_agent, token_id) -> None:
        pass

    async def create_refresh_token(self, token_id, token_expired, refresh_token) -> None:
        """
        создает refresh токен
        1. скорей всего нужно id сделать id токена, а не генерировать автоматом
        2. также нужно поступить с created_at
        Эти данные можно спокойно взять из token_claim.
        Мне кажется так будет правильнее.
        """
        pass

    async def get_user_sessions(self, user_id: str):
        """
        может потом надо будет ограничить период, за который пользователь захочет увидеть историю
        например, за месяц или неделю

        это просто идея, пока будем выводить всю историю
        """
        pass


@lru_cache()
def get_postgres_service(session: Session) -> PostgresService:
    return PostgresService(session)
