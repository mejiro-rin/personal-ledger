import enum
from typing import TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship, Column, Integer
from .base import ReadModel, CreateModel, UpdateModel

if TYPE_CHECKING:
    from .transaction import Transaction


class CategoryType(str, enum.Enum):
    """分类类型"""
    INCOME = "income"
    EXPENSE = "expense"


class Category(SQLModel, table=True):
    """分类建表模型"""
    __tablename__ = "categories"

    id: int | None = Field(
        default=None,
        sa_column=Column(Integer, primary_key=True, autoincrement=True)
    )
    name: str = Field(index=True)
    category_type: CategoryType
    parent_id: int = Field(default=0, foreign_key="categories.id")

    transactions: list["Transaction"] = Relationship(back_populates="category")

"""======== Schema Models ========"""

class CategoryCreate(CreateModel):
    """分类创建模型"""
    name: str
    category_type: CategoryType
    parent_id: int = 0

class CategoryRead(ReadModel):
    """分类读取模型"""
    id: int
    name: str
    category_type: CategoryType
    parent_id: int

class CategoryUpdate(UpdateModel):
    """分类更新模型"""
    name: str | None = None
    category_type: CategoryType | None = None
    parent_id: int | None = None