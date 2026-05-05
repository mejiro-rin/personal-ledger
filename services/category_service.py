from __future__ import annotations

from sqlmodel import Session

from models.category import Category, CategoryCreate, CategoryRead, CategoryUpdate
from repositories.category import CategoryRepository
from exceptions.service_exceptions import ResourceNotFoundError, DuplicateNameError, InvalidOperationError


class CategoryService:

    def __init__(self):
        self.repo = CategoryRepository()

    def get_by_id(self, session: Session, id: int) -> CategoryRead:
        category = self.repo.get_by_id(session, id)
        if category is None:
            raise ResourceNotFoundError("Category", id)
        return CategoryRead.model_validate(category)

    def list(self, session: Session, offset: int = 0, limit: int = 100) -> list[CategoryRead]:
        categories = self.repo.list(session, offset=offset, limit=limit)
        return [CategoryRead.model_validate(c) for c in categories]

    def list_by_parent(self, session: Session, parent_id: int) -> list[CategoryRead]:
        categories = self.repo.get_by_parent_id(session, parent_id)
        return [CategoryRead.model_validate(c) for c in categories]

    def create(self, session: Session, obj_in: CategoryCreate) -> CategoryRead:
        # parent_id 合法性校验（0 表示根分类，无需校验）
        if obj_in.parent_id != 0:
            parent = self.repo.get_by_id(session, obj_in.parent_id)
            if parent is None:
                raise ResourceNotFoundError("Category", obj_in.parent_id)
        category = Category.model_validate(obj_in)
        category = self.repo.create(session, category)
        session.commit()
        return CategoryRead.model_validate(category)

    def update(self, session: Session, id: int, obj_in: CategoryUpdate) -> CategoryRead:
        category = self.repo.get_by_id(session, id)
        if category is None:
            raise ResourceNotFoundError("Category", id)
        # parent_id 合法性校验
        if obj_in.parent_id is not None and obj_in.parent_id != 0:
            if obj_in.parent_id == id:
                raise InvalidOperationError("分类不能将自身设为父分类")
            parent = self.repo.get_by_id(session, obj_in.parent_id)
            if parent is None:
                raise ResourceNotFoundError("Category", obj_in.parent_id)
        update_data = obj_in.model_dump(exclude_unset=True)
        category.sqlmodel_update(update_data)
        category = self.repo.update(session, category)
        session.commit()
        return CategoryRead.model_validate(category)

    def delete(self, session: Session, id: int) -> None:
        category = self.repo.get_by_id(session, id)
        if category is None:
            raise ResourceNotFoundError("Category", id)
        # 有子分类时禁止删除
        children = self.repo.get_by_parent_id(session, id)
        if children:
            raise InvalidOperationError(f"Category (id={id}) 下存在子分类，无法删除")
        self.repo.delete(session, category)
        session.commit()