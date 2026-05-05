from .base import ReadModel, CreateModel, UpdateModel
from sqlmodel import SQLModel, Field


class TransactionTag(SQLModel, table=True):
    __tablename__ = "transaction_tags"

    transaction_id: int = Field(
        foreign_key="transactions.id", primary_key=True
    )
    tag_id: int = Field(
        foreign_key="tags.id", primary_key=True
    )
