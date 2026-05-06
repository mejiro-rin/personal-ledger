import enum
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship, Integer, Column
from .base import ReadModel, CreateModel, UpdateModel
from .transaction_tag import TransactionTag
from .tag import TagRead

if TYPE_CHECKING:
    from .account import Account
    from .category import Category
    from .tag import Tag


class TransactionType(str, enum.Enum):
    """支出类型"""
    INCOME = "income"       # 收入
    EXPENSE = "expense"     # 支出
    TRANSFER = "transfer"   # 转账


class Transaction(SQLModel, table=True):
    """交易记录建表模型"""
    __tablename__ = "transactions"

    id: int | None = Field(default=None, primary_key=True)
    account_id: int = Field(foreign_key="accounts.id")
    category_id: int | None = Field(default=None, foreign_key="categories.id")
    amount: Decimal
    transaction_type: TransactionType
    note: str | None = Field(default=None)
    occurred_at: int = Field(default_factory=lambda: int(datetime.now().strftime("%Y%m%d%H%M%S")))
    tags: list["Tag"] = Relationship(
        back_populates="transactions", link_model=TransactionTag)

    # 转账业务跟随普通记录，需要记录转入转出方向，以此添加额外信息记录
    transfer_from_account_id: int | None = Field(default=None, foreign_key="accounts.id")
    transfer_to_account_id: int | None = Field(default=None, foreign_key="accounts.id")

    account: "Account" = Relationship(
        back_populates="transactions",
        sa_relationship_kwargs={"foreign_keys": "[Transaction.account_id]"}
    )
    category: "Category" = Relationship(back_populates="transactions")

"""======== Schema Models ========"""

class TransactionCreate(CreateModel):
    """交易创建模型"""
    account_id: int
    category_id: int | None = None
    amount: Decimal
    transaction_type: TransactionType
    note: str | None = None
    occurred_at: int | None = None
    tag_ids: list[int] = []
    transfer_from_account_id: int | None = None
    transfer_to_account_id: int | None = None

class TransactionRead(ReadModel):
    """交易读取模型"""
    id: int
    account_id: int
    category_id: int | None = None
    amount: Decimal
    transaction_type: TransactionType
    note: str | None = None
    occurred_at: int
    tags: list[TagRead] = []
    transfer_from_account_id: int | None = None
    transfer_to_account_id: int | None = None

class TransactionUpdate(UpdateModel):
    """交易更新模型"""
    account_id: int | None = None
    category_id: int | None = None
    amount: Decimal | None = None
    transaction_type: TransactionType | None = None
    note: str | None = None
    occurred_at: int | None = None

    tag_ids: list[int] = []
    transfer_from_account_id: int | None = None
    transfer_to_account_id: int | None = None