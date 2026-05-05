from typing import Generator
from sqlmodel import Session, SQLModel, create_engine
from utils.config import settings
from utils.path import paths
from contextlib import contextmanager

from models import Account, Category, Tag, Transaction, TransactionTag

paths.data_dir.mkdir(parents=True, exist_ok=True)
engine = create_engine(f"sqlite:///{paths.db_path}", connect_args={"check_same_thread": False})


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)
    if settings.dev_env:
        print("表建立完成")


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


@contextmanager
def get_session_once():
    session = next(get_session())
    try:
        yield session
    finally:
        session.close()