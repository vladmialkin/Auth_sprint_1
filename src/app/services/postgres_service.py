import datetime
import uuid
from functools import lru_cache

from sqlalchemy import insert, select
from sqlalchemy import update as sqlalchemy_update

from app.models.schema_validation.user_schema import UserInDB, RefreshTokenInDB
from app.api.deps import Session
from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.models.user_refresh_token import UserRefreshToken


class PostgresService:
    def __init__(self, session: Session):
        self.session = session

    async def get_user_by_field(self, user_id=None, user_login=None, user_email=None) -> UserInDB | None:
        """if exist return UserInDB else None"""
        try:
            if user_id is not None:
                query = select(User).where(User.id == user_id)
            elif user_login is not None:
                query = select(User).where(User.login == user_login)
            elif user_email is not None:
                query = select(User).where(User.email == user_email)

            res = await self.session.execute(statement=query)
            user = res.scalar()
        except:
            user = None
        return user

    async def get_userid_by_tokenid(self, token_id):
        try:
            query = select(UserRefreshToken).where(UserRefreshToken.refresh_token_id == token_id)
            res = await self.session.execute(statement=query)
            entity = res.scalar()
        except:
            return
        return entity

    async def get_token_by_token(self, token) -> RefreshTokenInDB | None:
        """if exist return UserInDB else None"""
        try:
            query = select(RefreshToken).where(RefreshToken.token == token)
            res = await self.session.execute(statement=query)
            token = res.scalar()
        except:
            token = None
        return token

    async def get_refresh_token_id(self, user_id, user_agent):
        """находим refresh_token_id из табл Session по user_id, user_agent"""
        return uuid.uuid4()

    async def get_by_id(self, table, cls_id):
        try:
            query = select(table).where(table.id == cls_id)
            res = await self.session.execute(statement=query)
            entity = res.scalar()
        except:
            entity = None
        return entity

    async def get_session_info(self, table, cls_id) -> list:
        """получаем инфо по user_id"""

    async def update(self, table_to_update, cls_id, **kwargs):
        query = (
            sqlalchemy_update(table_to_update)
            .where(table_to_update.id == cls_id)
            .values(**kwargs)
        )
        await self.session.execute(query)
        await self.session.commit()
        return table_to_update

    async def create(self, table, **kwargs):
        try:
            query = insert(table).values(**kwargs).returning(table)
            res = (await self.session.execute(query)).scalars().first()
            await self.session.commit()
        except Exception as e:
            print(e)
            return
        return res

    async def create_user(self, data) -> UserInDB | None:
        try:
            query = insert(User).values(**data.model_dump()).returning(User)
            res = (await self.session.execute(query)).scalars().first()
            await self.session.commit()
        except Exception as e:
            print(e)
            return
        return res


@lru_cache()
def get_postgres_service(session: Session) -> PostgresService:
    return PostgresService(session)
