#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Version  : Python 3.12
@Time     : 2024/7/16 23:31
@Author   : wiesZheng
@Software : PyCharm
"""
from sqlalchemy import INT
from sqlalchemy.orm import Mapped, mapped_column

from app.models import BaseOrmTableWithTS


class ProjectRole(BaseOrmTableWithTS):
    __tablename__ = 'alden_project_role'

    user_id: Mapped[int] = mapped_column(INT, index=True)
    project_id: Mapped[int] = mapped_column(INT, index=True)
    project_role: Mapped[int] = mapped_column(INT, index=True)
