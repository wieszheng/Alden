#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Version  : Python 3.12
@Time     : 2024/7/16 23:25
@Author   : wiesZheng
@Software : PyCharm
"""
from datetime import datetime

from sqlalchemy import INT, String, TEXT, TIMESTAMP, SMALLINT
from sqlalchemy.orm import Mapped, mapped_column

from app.models import BaseOrmTableWithTS


class OperationLog(BaseOrmTableWithTS):
    __tablename__ = 'alden_operation_log'

    user_id: Mapped[int] = mapped_column(INT, index=True)
    operate_time: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.now())
    title: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(TEXT, comment="操作描述")
    tag: Mapped[str | None] = mapped_column(String(24), comment="操作tag")
    mode: Mapped[int] = mapped_column(SMALLINT, comment="操作类型")
    key: Mapped[int | None] = mapped_column(INT, nullable=True, comment="关键id，可能是目录id，case_id或者其他id")
