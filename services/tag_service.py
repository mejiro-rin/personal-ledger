from __future__ import annotations

from sqlmodel import Session

from models.tag import Tag, TagCreate, TagRead, TagUpdate
from repositories.tag import TagRepository
from exceptions.service_exceptions import ResourceNotFoundError, DuplicateNameError


class TagService:

    def __init__(self):
        self.repo = TagRepository()

    def get_by_id(self, session: Session, id: int) -> TagRead:
        tag = self.repo.get_by_id(session, id)
        if tag is None:
            raise ResourceNotFoundError("Tag", id)
        return TagRead.model_validate(tag)

    def list(self, session: Session, offset: int = 0, limit: int = 100) -> list[TagRead]:
        tags = self.repo.list(session, offset=offset, limit=limit)
        return [TagRead.model_validate(t) for t in tags]

    def create(self, session: Session, obj_in: TagCreate) -> TagRead:
        existing = self.repo.get_by_name(session, obj_in.name)
        if existing is not None:
            raise DuplicateNameError("Tag", obj_in.name)
        tag = Tag.model_validate(obj_in)
        tag = self.repo.create(session, tag)
        session.commit()
        return TagRead.model_validate(tag)

    def update(self, session: Session, id: int, obj_in: TagUpdate) -> TagRead:
        tag = self.repo.get_by_id(session, id)
        if tag is None:
            raise ResourceNotFoundError("Tag", id)
        if obj_in.name is not None:
            existing = self.repo.get_by_name(session, obj_in.name)
            if existing is not None and existing.id != id:
                raise DuplicateNameError("Tag", obj_in.name)
        update_data = obj_in.model_dump(exclude_unset=True)
        tag.sqlmodel_update(update_data)
        tag = self.repo.update(session, tag)
        session.commit()
        return TagRead.model_validate(tag)

    def delete(self, session: Session, id: int) -> None:
        tag = self.repo.get_by_id(session, id)
        if tag is None:
            raise ResourceNotFoundError("Tag", id)
        self.repo.delete(session, tag)
        session.commit()