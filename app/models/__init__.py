#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Version  : Python 3.12
@Time     : 2024/7/2 22:49
@Author   : wiesZheng
@Software : PyCharm
"""
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, declarative_base
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import (create_async_engine, AsyncSession,
                                    async_sessionmaker)

from config import Settings

# 定义数据库URL
async_database_url = URL.create(Settings.MYSQL_PROTOCOL,
                                Settings.MYSQL_USER,
                                Settings.MYSQL_PASSWORD,
                                Settings.MYSQL_HOST,
                                Settings.MYSQL_PORT,
                                Settings.MYSQL_DATABASE,
                                {"charset": "utf8mb4"})
# 创建异步引擎
async_engine = create_async_engine(async_database_url, echo=True, pool_size=50, pool_recycle=1500)

# 初始化Session工厂
async_session_maker = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    autocommit=False,
    expire_on_commit=False
)


class BaseOrmTable(AsyncAttrs, DeclarativeBase):
    """SQLAlchemy Base ORM Model"""

    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True, comment="主键ID")

    def __repr__(self):
        return str(self.to_dict())

    def to_dict(self, alias_dict: dict = None, exclude_none=True) -> dict:
        """
        数据库模型转成字典
        Args:
            alias_dict: 字段别名字典
                eg: {"id": "user_id"}, 把id名称替换成 user_id
            exclude_none: 默认排查None值
        Returns: dict
        """
        alias_dict = alias_dict or {}
        if exclude_none:
            return {
                alias_dict.get(c.name, c.name): getattr(self, c.name)
                for c in self.__table__.columns
                if getattr(self, c.name) is not None
            }
        else:
            return {alias_dict.get(c.name, c.name): getattr(self, c.name, None) for c in self.__table__.columns}


class TimestampColumns(AsyncAttrs, DeclarativeBase):
    """时间戳相关列"""

    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(default=datetime.now, comment="创建时间")

    updated_at: Mapped[datetime] = mapped_column(default=datetime.now, onupdate=datetime.now, comment="更新时间")

    deleted_at: Mapped[datetime] = mapped_column(nullable=True, comment="删除时间")


class OperatorColumns(AsyncAttrs, DeclarativeBase):
    """操作人相关列"""

    __abstract__ = True

    created_by: Mapped[int] = mapped_column(comment="创建人")

    updated_by: Mapped[int] = mapped_column(comment="更新人")

    deleted_by: Mapped[int] = mapped_column(nullable=True, comment="删除人")


class BaseOrmTableWithTS(BaseOrmTable, TimestampColumns, OperatorColumns):
    __abstract__ = True


'''
          ```python
            {
                "id": 1,
                "name": "John Doe",
                "username": "john_doe",
                "email": "johndoe@example.com",
                "hashed_password": "hashed_password_example",
                "profile_image_url": "https://profileimageurl.com/default.jpg",
                "uuid": "123e4567-e89b-12d3-a456-426614174000",
                "created_at": "2023-01-01T12:00:00",
                "updated_at": "2023-01-02T12:00:00",
                "deleted_at": null,
                "is_deleted": false,
                "is_superuser": false,
                "tier_id": 2,
                "tier_name": "Premium",
                "tier_created_at": "2022-12-01T10:00:00",
                "tier_updated_at": "2023-01-01T11:00:00"
            }
            ```
'''
# 循环依赖, 记得放在下面
from .user import (
    UserModel
)
