from typing import Generic, TypeVar, Type, Optional, cast
from sqlmodel import SQLModel, Session, select

# SQLModel 类型变量，限定为 SQLModel 或其子类
SQLModelType = TypeVar("SQLModelType", bound=SQLModel)


class BaseRepository(Generic[SQLModelType]):
    """
    具有常见 CRUD 操作的通用存储库。
    查询只提供主键方法，其余由子类添加。
    方法期望调用者（服务层或API 层）。
    存储库返回 SQLModel 实例。
    """

    def __init__(self, model: Type[SQLModelType]):
        # SQLModel 类型
        self.model = model

    def get_by_id(self, session: Session, id: int) -> SQLModelType | None:
        """
        通过主键查询方法
        :param session: 数据库会话
        :param id: 主键 ID
        :return: 模型实例或 None
        """
        # 使用 getattr 避免有关 SQLModelType 属性的静态类型投诉
        statement = select(self.model).where(getattr(self.model, "id") == id)  # type: ignore[arg-type]
        result = session.exec(statement).first()
        return cast(Optional[SQLModelType], result)

    def list(self, session: Session, *, offset: int = 0, limit: int = 100) -> list[SQLModelType]:
        """
        分页查询模型实例列表。
        :param session: 数据库会话
        :param offset: 查询偏移量
        :param limit: 返回数量上限
        :return: SQLModel 类型的模型实例列表
        """
        statement = select(self.model).offset(offset).limit(limit)
        results = session.exec(statement).all()
        return cast(list[SQLModelType], results)

    def create(self, session: Session, new_obj: SQLModelType) -> SQLModelType:
        """
        创建方法
        :param session: 数据库会话
        :param new_obj: 要创建的模型实例
        :return: 创建后的 SQLModel 模型实例
        """
        session.add(new_obj)
        session.flush()
        session.refresh(new_obj)
        return new_obj

    # def update(self, session: Session, db_obj: SQLModelType, updates: dict) -> SQLModelType:
    #     """
    #     更新方法，使用字典更新模型实例的属性。
    #     仅更新提供的非 None 字段。
    #     :param session:
    #     :param db_obj:
    #     :param updates:
    #     :return:
    #     """
    #     for key, value in updates.items():
    #         if value is not None and hasattr(db_obj, key):
    #             setattr(db_obj, key, value)
    #     session.add(db_obj)
    #     session.flush()
    #     session.refresh(db_obj)
    #     return db_obj

    def update(self, session: Session, up_obj: SQLModelType) -> SQLModelType:
        """
        更新方法，直接更新模型实例的属性。
        :param session:
        :param up_obj:
        :return: 更新后的 SQLModel 模型实例
        """
        session.add(up_obj)
        session.flush()
        session.refresh(up_obj)
        return up_obj

    def delete(self, session: Session, db_obj: SQLModelType) -> None:
        """
        删除方法
        :param session:
        :param db_obj:
        :return:
        """
        session.delete(db_obj)
        session.flush()
