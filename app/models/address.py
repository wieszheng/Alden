#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Version  : Python 3.12
@Time     : 2024/7/15 22:49
@Author   : wiesZheng
@Software : PyCharm
"""
from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.models import BaseOrmTableWithTS


class Address(BaseOrmTableWithTS):
    __tablename__ = 'address'

    env: Mapped[int] = mapped_column(Integer, nullable=False, comment="环境标识")
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, comment="名称")
    gateway: Mapped[str] = mapped_column(String(50), comment="网关地址")
