#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Version  : Python 3.12
@Time     : 2024/7/16 23:18
@Author   : wiesZheng
@Software : PyCharm
"""
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.models import BaseOrmTableWithTS


class Environment(BaseOrmTableWithTS):
    __tablename__ = 'alden_environment'

    name: Mapped[str] = mapped_column(String(10))
    remarks: Mapped[str] = mapped_column(String(200))