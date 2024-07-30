#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Version  : Python 3.12
@Time     : 2024/7/16 23:22
@Author   : wiesZheng
@Software : PyCharm
"""
from sqlalchemy import INT, String, TEXT, BOOLEAN
from sqlalchemy.orm import Mapped, mapped_column

from app.models import BaseOrmTableWithTS


class GConfig(BaseOrmTableWithTS):
    __tablename__ = 'alden_gconfig'

    env: Mapped[int] = mapped_column(INT)
    key: Mapped[str] = mapped_column(String(16))
    value: Mapped[str] = mapped_column(TEXT)
    key_type: Mapped[int] = mapped_column(INT, nullable=False, comment="0: string 1: json 2: yaml")
    enable: Mapped[bool] = mapped_column(BOOLEAN, default=True)
