from contextlib import contextmanager
from app.repositories import UserRepository, RoleRepository, UserRoleRepository, SessionRepository, \
    RefreshTokenRepository


class UnitOfWork:
    def __init__(self, session_factory):
        self.session_factory = session_factory
        self._session = None

    @contextmanager
    def start(self):
        self._session = self.session_factory()
        try:
            yield self
            self._session.commit()
        except Exception as e:
            self._session.rollback()
            raise e
        finally:
            self._session.close()

    @property
    def users(self) -> UserRepository:
        return UserRepository(self._session)

    @property
    def user_roles(self) -> UserRoleRepository:
        return UserRoleRepository(self._session)

    @property
    def roles(self) -> RoleRepository:
        return RoleRepository(self._session)

    @property
    def sessions(self) -> SessionRepository:
        return SessionRepository(self._session)

    @property
    def refresh_tokens(self) -> RefreshTokenRepository:
        return RefreshTokenRepository(self._session)
