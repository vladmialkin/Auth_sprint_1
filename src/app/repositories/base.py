from typing import TypeVar, Generic
from sqlalchemy.orm import Session

T = TypeVar('T')


class BaseRepository(Generic[T]):
    def __init__(self, session: Session):
        self.session = session

    def add(self, item: T):
        self.session.add(item)
