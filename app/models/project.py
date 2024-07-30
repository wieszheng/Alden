#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Version  : Python 3.12
@Time     : 2024/7/16 23:29
@Author   : wiesZheng
@Software : PyCharm
"""
from sqlalchemy import INT, String, BOOLEAN
from sqlalchemy.orm import Mapped, mapped_column

from app.models import BaseOrmTableWithTS


class Project(BaseOrmTableWithTS):
    __tablename__ = 'alden_project'

    name: Mapped[str] = mapped_column(String(16))
    owner: Mapped[int] = mapped_column(INT)
    app: Mapped[str] = mapped_column(String(32))
    private: Mapped[bool] = mapped_column(BOOLEAN, default=False)
    description: Mapped[str | None] = mapped_column(String(200))
    avatar: Mapped[str | None] = mapped_column(String(128), nullable=True)
    dingtalk_url: Mapped[str | None] = mapped_column(String(128), nullable=True)
