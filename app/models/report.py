#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Version  : Python 3.12
@Time     : 2024/7/16 23:33
@Author   : wiesZheng
@Software : PyCharm
"""
from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import INT, String, TIMESTAMP, SMALLINT, BIGINT
from app.models import BaseOrmTableWithTS


class Report(BaseOrmTableWithTS):
    __tablename__ = 'alden_report'

    executor: Mapped[int] = mapped_column(INT, index=True)
    env: Mapped[int] = mapped_column(INT, nullable=False)
    cost: Mapped[str] = mapped_column(String(8))
    plan_id: Mapped[int | None] = mapped_column(INT, index=True, nullable=True)
    start_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.now(), nullable=False)
    finished_at: Mapped[datetime | None] = mapped_column(TIMESTAMP, default=datetime.now())
    success_count: Mapped[int] = mapped_column(INT, nullable=False, default=0)
    error_count: Mapped[int] = mapped_column(INT, nullable=False, default=0)
    failed_count: Mapped[int] = mapped_column(INT, nullable=False, default=0)
    skipped_count: Mapped[int] = mapped_column(INT, nullable=False, default=0)
    status: Mapped[int] = mapped_column(SMALLINT, nullable=False,
                                        comment="0: pending, 1: running, 2: stopped, 3: finished", index=True)
    mode: Mapped[int] = mapped_column(SMALLINT, default=0, comment="0: 普通, 1: 测试集, 2: pipeline, 3: 其他")
    deleted_at: Mapped[int] = mapped_column(BIGINT, nullable=False, default=0)
