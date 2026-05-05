from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from sqlmodel import Session

from models.transaction import Transaction, TransactionCreate, TransactionRead, TransactionUpdate, TransactionType
from models.tag import TagRead
from repositories.transaction import TransactionRepository
from repositories.account import AccountRepository
from repositories.category import CategoryRepository
from repositories.tag import TagRepository
from exceptions.service_exceptions import ResourceNotFoundError, InvalidOperationError, InvalidDecimalError


def _validate_decimal_places(value: Decimal, field_name: str, max_places: int = 2) -> None:
    if value.as_tuple().exponent < -max_places:
        raise InvalidDecimalError(field_name, max_places)


class TransactionService:

    def __init__(self):
        self.repo = TransactionRepository()
        self.account_repo = AccountRepository()
        self.category_repo = CategoryRepository()
        self.tag_repo = TagRepository()

    def _to_read(self, transaction: Transaction) -> TransactionRead:
        """ORM → TransactionRead，手动处理 tags 嵌套"""
        return TransactionRead(
            id=transaction.id,
            account_id=transaction.account_id,
            category_id=transaction.category_id,
            amount=transaction.amount,
            transaction_type=transaction.transaction_type,
            note=transaction.note,
            occurred_at=transaction.occurred_at,
            tags=[TagRead.model_validate(t) for t in transaction.tags],
        )

    def _resolve_tags(self, session: Session, tag_ids: list[int]) -> list:
        """校验并返回 Tag ORM 对象列表"""
        tags = []
        for tag_id in tag_ids:
            tag = self.tag_repo.get_by_id(session, tag_id)
            if tag is None:
                raise ResourceNotFoundError("Tag", tag_id)
            tags.append(tag)
        return tags

    def _apply_balance_change(self, session: Session, account_id: int, amount: Decimal, transaction_type: TransactionType, sign: int) -> None:
        """
        更新账户余额。sign=1 表示正向（创建），sign=-1 表示反向（撤销）。
        INCOME  → balance += amount * sign
        EXPENSE → balance -= amount * sign
        TRANSFER 不影响余额（转账涉及两个账户，由上层业务处理）
        """
        account = self.account_repo.get_by_id(session, account_id)
        if account is None:
            raise ResourceNotFoundError("Account", account_id)
        if transaction_type == TransactionType.INCOME:
            account.balance += amount * sign
        elif transaction_type == TransactionType.EXPENSE:
            account.balance -= amount * sign
        self.account_repo.update(session, account)

    def get_by_id(self, session: Session, id: int) -> TransactionRead:
        transaction = self.repo.get_by_id(session, id)
        if transaction is None:
            raise ResourceNotFoundError("Transaction", id)
        return self._to_read(transaction)

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
    ) -> list[TransactionRead]:
        transactions = self.repo.list(
            session,
            account_id=account_id,
            category_id=category_id,
            transaction_type=transaction_type,
            start_occurred_at=start_occurred_at,
            end_occurred_at=end_occurred_at,
            offset=offset,
            limit=limit,
        )
        return [self._to_read(t) for t in transactions]

    def create(self, session: Session, obj_in: TransactionCreate) -> TransactionRead:
        _validate_decimal_places(obj_in.amount, "金额")
        if obj_in.transaction_type == TransactionType.TRANSFER:
            if not obj_in.transfer_from_account_id or not obj_in.transfer_to_account_id:
                raise InvalidOperationError("转账交易必须指定转出账户和转入账户")
            from_account = self.account_repo.get_by_id(session, obj_in.transfer_from_account_id)
            if from_account is None:
                raise ResourceNotFoundError("Account", obj_in.transfer_from_account_id)
            to_account = self.account_repo.get_by_id(session, obj_in.transfer_to_account_id)
            if to_account is None:
                raise ResourceNotFoundError("Account", obj_in.transfer_to_account_id)
            # 转账不需要分类
            obj_in.category_id = None
            obj_in.account_id = obj_in.transfer_from_account_id  # 用转出账户作为主账户
        else:
            account = self.account_repo.get_by_id(session, obj_in.account_id)
            if account is None:
                raise ResourceNotFoundError("Account", obj_in.account_id)
            # 非转账必须要有分类
            category = self.category_repo.get_by_id(session, obj_in.category_id)
            if category is None:
                raise ResourceNotFoundError("Category", obj_in.category_id)
        tags = self._resolve_tags(session, obj_in.tag_ids)

        # 如果 occurred_at 为 None，自动生成当前时间戳
        if obj_in.occurred_at is None:
            obj_in.occurred_at = int(datetime.now().strftime("%Y%m%d%H%M%S"))

        transaction = Transaction.model_validate(obj_in.model_dump(exclude={"tag_ids"}))
        transaction.tags = tags
        transaction = self.repo.create(session, transaction)

        if obj_in.transaction_type == TransactionType.TRANSFER:
            from_account.balance -= obj_in.amount
            to_account.balance += obj_in.amount
            self.account_repo.update(session, from_account)
            self.account_repo.update(session, to_account)
        else:
            self._apply_balance_change(session, obj_in.account_id, obj_in.amount, obj_in.transaction_type, sign=1)

        session.commit()
        session.refresh(transaction)
        return self._to_read(transaction)

    def update(self, session: Session, id: int, obj_in: TransactionUpdate) -> TransactionRead:
        transaction = self.repo.get_by_id(session, id)
        if transaction is None:
            raise ResourceNotFoundError("Transaction", id)

        if obj_in.amount is not None:
            _validate_decimal_places(obj_in.amount, "金额")

        old_type = transaction.transaction_type
        if old_type == TransactionType.TRANSFER:
            from_account = self.account_repo.get_by_id(session, transaction.transfer_from_account_id)
            to_account = self.account_repo.get_by_id(session, transaction.transfer_to_account_id)
            if from_account and to_account:
                from_account.balance += transaction.amount
                to_account.balance -= transaction.amount
                self.account_repo.update(session, from_account)
                self.account_repo.update(session, to_account)
        else:
            self._apply_balance_change(session, transaction.account_id, transaction.amount, old_type, sign=-1)

        if obj_in.account_id is not None:
            if self.account_repo.get_by_id(session, obj_in.account_id) is None:
                raise ResourceNotFoundError("Account", obj_in.account_id)
        if obj_in.category_id is not None:
            if self.category_repo.get_by_id(session, obj_in.category_id) is None:
                raise ResourceNotFoundError("Category", obj_in.category_id)

        new_type = obj_in.transaction_type or old_type
        if new_type == TransactionType.TRANSFER:
            if obj_in.transfer_from_account_id is not None and obj_in.transfer_to_account_id is not None:
                if not obj_in.transfer_from_account_id or not obj_in.transfer_to_account_id:
                    raise InvalidOperationError("转账交易必须指定转出账户和转入账户")
                from_account = self.account_repo.get_by_id(session, obj_in.transfer_from_account_id)
                if from_account is None:
                    raise ResourceNotFoundError("Account", obj_in.transfer_from_account_id)
                to_account = self.account_repo.get_by_id(session, obj_in.transfer_to_account_id)
                if to_account is None:
                    raise ResourceNotFoundError("Account", obj_in.transfer_to_account_id)
                from_account.balance -= obj_in.amount or transaction.amount
                to_account.balance += obj_in.amount or transaction.amount
                self.account_repo.update(session, from_account)
                self.account_repo.update(session, to_account)
            else:
                from_id = obj_in.transfer_from_account_id or transaction.transfer_from_account_id
                to_id = obj_in.transfer_to_account_id or transaction.transfer_to_account_id
                from_account = self.account_repo.get_by_id(session, from_id)
                to_account = self.account_repo.get_by_id(session, to_id)
                if from_account and to_account:
                    from_account.balance -= obj_in.amount or transaction.amount
                    to_account.balance += obj_in.amount or transaction.amount
                    self.account_repo.update(session, from_account)
                    self.account_repo.update(session, to_account)
        else:
            new_account_id = obj_in.account_id or transaction.account_id
            new_amount = obj_in.amount or transaction.amount
            self._apply_balance_change(session, new_account_id, new_amount, new_type, sign=1)

        tags = self._resolve_tags(session, obj_in.tag_ids)
        transaction.tags = tags

        update_data = obj_in.model_dump(exclude_unset=True, exclude={"tag_ids"})
        transaction.sqlmodel_update(update_data)
        transaction = self.repo.update(session, transaction)

        session.commit()
        session.refresh(transaction)
        return self._to_read(transaction)

    def delete(self, session: Session, id: int) -> None:
        transaction = self.repo.get_by_id(session, id)
        if transaction is None:
            raise ResourceNotFoundError("Transaction", id)

        if transaction.transaction_type == TransactionType.TRANSFER:
            from_account = self.account_repo.get_by_id(session, transaction.transfer_from_account_id)
            to_account = self.account_repo.get_by_id(session, transaction.transfer_to_account_id)
            if from_account and to_account:
                from_account.balance += transaction.amount
                to_account.balance -= transaction.amount
                self.account_repo.update(session, from_account)
                self.account_repo.update(session, to_account)
        else:
            self._apply_balance_change(session, transaction.account_id, transaction.amount, transaction.transaction_type, sign=-1)

        self.repo.delete(session, transaction)
        session.commit()
