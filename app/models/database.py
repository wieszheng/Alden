#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Version  : Python 3.12
@Time     : 2024/7/16 23:15
@Author   : wiesZheng
@Software : PyCharm
"""
from sqlalchemy import INT, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models import BaseOrmTableWithTS


class Database(BaseOrmTableWithTS):
    __tablename__ = "alden_database_info"

    env: Mapped[int] = mapped_column(INT, nullable=False)
    name: Mapped[str] = mapped_column(String(24), nullable=False)
    host: Mapped[str] = mapped_column(String(64), nullable=False)
    port: Mapped[int] = mapped_column(INT, nullable=False)
    username: Mapped[str] = mapped_column(String(36), nullable=False)
    password: Mapped[str] = mapped_column(String(64), nullable=False)
    database: Mapped[str] = mapped_column(String(36), nullable=False)
    sql_type: Mapped[int] = mapped_column(INT, nullable=False, comment="0: mysql 1: postgresql 2: mongo")
    # env_info: Environment
