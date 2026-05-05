from typing import List, cast
from sqlmodel import Session, select

from models.category import Category
from .base import BaseRepository


class CategoryRepository(BaseRepository[Category]):
    """Category 仓库类，提供账户相关的 CRUD 操作"""
    def __init__(self):
        super().__init__(Category)

    def get_by_id(self, session: Session, id: int) -> Category | None:
        return super().get_by_id(session, id)

    def get_by_parent_id(self, session: Session, parent_id: int) -> list[Category]:
        statement = select(Category).where(Category.parent_id == parent_id)
        return cast(list[Category], session.exec(statement).all())

    def create(self, session: Session, new_obj: Category) -> Category:
        return super().create(session, new_obj)

    def update(self, session: Session, db_obj: Category) -> Category:
        return super().update(session, db_obj)

    def list(self, session: Session, *, offset: int = 0, limit: int = 100) -> List[Category]:
        return super().list(session, offset=offset, limit=limit)


