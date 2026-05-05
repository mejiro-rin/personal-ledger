from typing import List, cast
from sqlmodel import Session, select

from models.tag import Tag
from .base import BaseRepository as BaseRepo


class TagRepository(BaseRepo[Tag]):
    """Tag 仓库类，提供账户相关的 CRUD 操作"""
    def __init__(self):
        super().__init__(Tag)

    def get_by_id(self, session: Session, id: int) -> Tag | None:
        return super().get_by_id(session, id)

    def get_by_name(self, session: Session, name: str) -> Tag | None:
        statement = select(Tag).where(Tag.name == name)
        return cast(Tag | None, session.exec(statement).first())

    def create(self, session: Session, new_obj: Tag) -> Tag:
        return super().create(session, new_obj)

    def update(self, session: Session, up_obj: Tag) -> Tag:
        return super().update(session, up_obj)

    def list(self, session: Session, *, offset: int = 0, limit: int = 100) -> List[Tag]:
        return super().list(session, offset=offset, limit=limit)


