#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Version  : Python 3.12
@Time     : 2024/7/16 23:23
@Author   : wiesZheng
@Software : PyCharm
"""
from sqlalchemy import INT, SMALLINT, VARCHAR
from sqlalchemy.orm import Mapped, mapped_column

from app.models import BaseOrmTableWithTS


class Notification(BaseOrmTableWithTS):
    __tablename__ = "alden_notification"

    msg_type: Mapped[int] = mapped_column(SMALLINT, comment="消息类型 1: 系统消息 2: 其他消息")
    msg_title: Mapped[str] = mapped_column(VARCHAR(32), comment="消息标题", nullable=False)
    msg_content: Mapped[str | None] = mapped_column(VARCHAR(200), comment="消息内容", nullable=True)
    msg_link: Mapped[str | None] = mapped_column(VARCHAR(128), comment="消息链接")
    msg_status: Mapped[int] = mapped_column(SMALLINT, comment="消息状态 1: 未读 2: 已读")
    sender: Mapped[int] = mapped_column(INT, comment="消息发送人, 0则是CPU 非0则是其他用户")
    receiver: Mapped[int | None] = mapped_column(INT, comment="消息接收人, 系统消息则该字段为空")
