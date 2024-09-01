import datetime
import uuid
from functools import lru_cache

from sqlalchemy import insert, select
from sqlalchemy import update as sqlalchemy_update

from app.models.schema_validation.user_schema import UserInDB, RefreshTokenInDB
from app.api.deps import Session
from app.models.user import User


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

    async def get_user_by_id(self, user_id: str) -> UserInDB:
        """if exist return UserInDB else None"""
        try:
            query = select(User).where(User.id == user_id)
            res = await self.session.execute(statement=query)
            user = res.scalar()
        except:
            user = None
        return user

    async def get_refresh_token(self, user_id, user_agent) -> RefreshTokenInDB | None:
        return RefreshTokenInDB(
            id=uuid.uuid4(),
            token='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJiODNkMzRkMS1lMmU3LTQ5NDQtYTQwYS02MjJmZTk1YTRlMjAiLCJpYXQiOjE3MjUyMjIwMDQsIm5iZiI6MTcyNTIyMjAwNCwianRpIjoiNWZiYzNmN2QtYmFjZC00YjczLTlhYjgtYzgxMTE2MWMyMWVjIiwiZXhwIjoxNzI1MjIzODA0LCJ0eXBlIjoicmVmcmVzaCJ9.niIq315MjUdRH8_f86Tx8MEW4XBepsJzzDk1XcDWyqI',
            expiration_date=datetime.datetime.now() - datetime.timedelta(minutes=30),
            created_at=datetime.datetime.now(),
            updated_at=datetime.datetime.now()
        )

    async def update(self, table_to_update, cls_id, **kwargs):
        query = (
            sqlalchemy_update(table_to_update)
            .where(table_to_update.id == cls_id)
            .values(**kwargs)
        )
        await self.session.execute(query)
        await self.session.commit()
        return table_to_update

    async def update_refresh_token(self, table, user_id, user_agent, **kwargs):
        pass

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
