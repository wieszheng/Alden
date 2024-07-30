#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Version  : Python 3.12
@Time     : 2024/7/3 0:12
@Author   : wiesZheng
@Software : PyCharm
"""
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, Boolean

from app.models import BaseOrmTableWithTS


class UserModel(BaseOrmTableWithTS):
    """ 用户模型 """

    __tablename__ = "alden_user"
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False,
                                          comment="用户名，用于登录")
    nickname: Mapped[Optional[str]] = mapped_column(String(50), comment="昵称，用于显示")
    password: Mapped[str] = mapped_column(String(128), nullable=False, comment="密码，存储为哈希值")
    phone: Mapped[Optional[str]] = mapped_column(String(11), unique=True, comment="手机号码，唯一")
    email: Mapped[Optional[str]] = mapped_column(String(100), unique=True, comment="电子邮箱，唯一")
    avatar: Mapped[Optional[str]] = mapped_column(String(255), comment="头像链接或路径")
    role: Mapped[str] = mapped_column(String(20), default='user', comment="用户角色，默认为'user'")
    last_login_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow,
                                                    comment="最后登录时间，自动更新")
    is_valid: Mapped[bool] = mapped_column(Boolean, default=True, comment="账户是否有效，默认为True")
