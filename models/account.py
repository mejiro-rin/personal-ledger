from sqlmodel import SQLModel, Field, Relationship, Integer, Column
from typing import TYPE_CHECKING
from decimal import Decimal
import enum
from datetime import datetime
from .base import ReadModel, CreateModel, UpdateModel

if TYPE_CHECKING:
    from .transaction import Transaction


class AccountType(str, enum.Enum):
    cash = "cash"           # 现金
    alipay = "alipay"       # 支付宝
    wechat = "wechat"       # 微信
    bank_card = "bank"      # 银行卡
    credit_card = "credit"  # 信用卡
    other = "other"         # 其他账户


class Account(SQLModel, table=True):
    """Account 建表模型"""
    __tablename__ = "accounts"

    id: int | None = Field(
        default=None,
        sa_column=Column(Integer, primary_key=True, autoincrement=True)
    )
    name: str = Field(index=True)
    account_type: AccountType
    balance: Decimal = Field(default=Decimal("0.0"))
    currency: str = Field(default="CNY")
    note: str | None = Field(default=None)
    created_at: int = Field(default_factory=lambda: int(datetime.now().strftime("%Y%m%d%H%M%S")))

    transactions: list["Transaction"] = Relationship(
        back_populates="account",
        sa_relationship_kwargs={"foreign_keys": "[Transaction.account_id]"}
    )

"""======== Schema Models ========"""

class AccountCreate(CreateModel):
    """Account 创建模型"""
    name: str
    account_type: AccountType
    balance: Decimal
    currency: str
    note : str | None

class AccountRead(ReadModel):
    """Account 读取模型"""
    id: int
    name: str
    account_type: AccountType
    balance: Decimal
    currency: str
    note: str | None
    created_at: int

class AccountUpdate(UpdateModel):
    """Account 更新模型"""
    name: str | None = None
    account_type: AccountType | None = None
    balance: Decimal | None = None
    currency: str | None = None
    note: str | None = None