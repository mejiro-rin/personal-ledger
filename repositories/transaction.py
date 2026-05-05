from typing import cast
from sqlmodel import Session, select

from models.transaction import Transaction, TransactionType
from .base import BaseRepository


class TransactionRepository(BaseRepository[Transaction]):

    def __init__(self):
        super().__init__(Transaction)

    def get_by_id(self, session: Session, id: int) -> Transaction | None:
        return super().get_by_id(session, id)

    def create(self, session: Session, new_obj: Transaction) -> Transaction:
        return super().create(session, new_obj)

    def update(self, session: Session, up_obj: Transaction) -> Transaction:
        return super().update(session, up_obj)

    def delete(self, session: Session, db_obj: Transaction) -> None:
        super().delete(session, db_obj)

    def list(
        self,
        session: Session,
        *,
        account_id: int | None = None,
        category_id: int | None = None,
        transaction_type: TransactionType | None = None,
        start_occurred_at: int | None = None,
        end_occurred_at: int | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Transaction]:
        """
        交易列表查询，支持多条件过滤和分页
        :param session:
        :param account_id:
        :param category_id:
        :param transaction_type:
        :param start_occurred_at:
        :param end_occurred_at:
        :param offset:
        :param limit:
        :return:
        """
        statement = select(Transaction)
        if account_id is not None:
            statement = statement.where(Transaction.account_id == account_id)
        if category_id is not None:
            statement = statement.where(Transaction.category_id == category_id)
        if transaction_type is not None:
            statement = statement.where(Transaction.transaction_type == transaction_type)
        if start_occurred_at is not None:
            statement = statement.where(Transaction.occurred_at >= start_occurred_at)
        if end_occurred_at is not None:
            statement = statement.where(Transaction.occurred_at <= end_occurred_at)
        statement = statement.offset(offset).limit(limit)
        return cast(list[Transaction], session.exec(statement).all())