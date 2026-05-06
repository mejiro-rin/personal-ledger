from typing import TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship, Integer, Column
from .transaction_tag import TransactionTag
from .base import ReadModel, CreateModel, UpdateModel


if TYPE_CHECKING:
    from .transaction import Transaction


class Tag(SQLModel, table=True):
    """标签建表模型"""
    __tablename__ = "tags"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)

    transactions: list["Transaction"] = Relationship(
        back_populates="tags", link_model=TransactionTag
    )

class TagCreate(CreateModel):
    name: str

class TagUpdate(UpdateModel):
    name: str | None = None

class TagRead(ReadModel):
    id: int
    name: str