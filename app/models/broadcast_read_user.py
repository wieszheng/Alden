#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Version  : Python 3.12
@Time     : 2024/7/16 23:08
@Author   : wiesZheng
@Software : PyCharm
"""
from datetime import datetime

from sqlalchemy import String, Integer, INT, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column
from timestamp import timestamp

from app.models import BaseOrmTableWithTS


class BroadcastReadUser(BaseOrmTableWithTS):
    __tablename__ = "alden_broadcast_read_user"

    notification_id: Mapped[int] = mapped_column(
        INT,
        comment="对应消息id",
        index=True
    )
    read_user: Mapped[int] = mapped_column(
        INT,
        comment="已读用户id"
    )
    read_time: Mapped[timestamp] = mapped_column(
        TIMESTAMP,
        default=datetime.now(),
        comment="已读时间"
    )
