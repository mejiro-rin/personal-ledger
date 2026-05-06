from __future__ import annotations

from decimal import Decimal
from sqlmodel import Session

from models.account import Account, AccountCreate, AccountRead, AccountUpdate
from repositories.account import AccountRepository
from exceptions.service_exceptions import ResourceNotFoundError, DuplicateNameError, InvalidDecimalError


def _validate_decimal_places(value: Decimal, field_name: str, max_places: int = 2) -> None:
    """校验金额字段是否符合最大小数位数要求"""
    if value.as_tuple().exponent < -max_places:
        raise InvalidDecimalError(field_name, max_places)


class AccountService:

    def __init__(self):
        self.repo = AccountRepository()

    def get_by_id(self, session: Session, id: int) -> AccountRead:
        account = self.repo.get_by_id(session, id)
        if account is None:
            raise ResourceNotFoundError("Account", id)
        return AccountRead.model_validate(account)

    def list(self, session: Session, offset: int = 0, limit: int = 100) -> list[AccountRead]:
        accounts = self.repo.list(session, offset=offset, limit=limit)
        return [AccountRead.model_validate(a) for a in accounts]

    def create(self, session: Session, obj_in: AccountCreate) -> AccountRead:
        # 名称唯一性校验。同分类下不允许名称重复。
        existing = self.repo.get_by_name_and_type(session, obj_in.name, obj_in.account_type)
        if existing is not None:
            raise DuplicateNameError("Account", obj_in.name)
        _validate_decimal_places(obj_in.balance, "余额")
        account = Account.model_validate(obj_in)
        account = self.repo.create(session, account)
        session.commit()
        return AccountRead.model_validate(account)

    def update(self, session: Session, id: int, obj_in: AccountUpdate) -> AccountRead:
        account = self.repo.get_by_id(session, id)
        if account is None:
            raise ResourceNotFoundError("Account", id)
        if obj_in.name is not None:
            existing = self.repo.get_by_name(session, obj_in.name)
            if existing is not None and existing.id != id:
                raise DuplicateNameError("Account", obj_in.name)
        if obj_in.balance is not None:
            _validate_decimal_places(obj_in.balance, "余额")
        update_data = obj_in.model_dump(exclude_unset=True)
        account.sqlmodel_update(update_data)
        account = self.repo.update(session, account)
        session.commit()
        return AccountRead.model_validate(account)

    def delete(self, session: Session, id: int) -> None:
        account = self.repo.get_by_id(session, id)
        if account is None:
            raise ResourceNotFoundError("Account", id)
        self.repo.delete(session, account)
        session.commit()