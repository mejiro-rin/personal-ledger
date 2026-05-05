from typing import cast
from sqlmodel import Session, select

from models.account import Account, AccountType
from .base import BaseRepository as BaseRepo


class AccountRepository(BaseRepo[Account]):
    """Account 仓库类，提供账户相关的 CRUD 操作"""
    def __init__(self):
        super().__init__(Account)

    # def get_by_id(self, session: Session, id: int) -> Account | None:
    #     return super().get_by_id(session, id)

    def get_by_name(self, session: Session, name: str) -> Account | None:
        statement = select(Account).where(Account.name == name)
        return cast(Account | None, session.exec(statement).first())

    def get_by_name_and_type(self, session: Session, name: str, account_type: AccountType) -> Account | None:
        statement = select(Account).where(
            Account.name == name,
            Account.account_type == account_type
        )
        return cast(Account | None, session.exec(statement).first())

    # def create(self, session: Session, new_obj: Account) -> Account:
    #     return super().create(session, new_obj)

    # def update(self, session: Session, up_obj: Account) -> Account:
    #     return super().update(session, up_obj)


    def list(self, session: Session, *, offset: int = 0, limit: int = 100) -> list[Account]:
        return super().list(session, offset=offset, limit=limit)


