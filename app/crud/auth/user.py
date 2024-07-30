# !/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@Version  : Python 3.12
@Time     : 2024/7/8 14:03
@Author   : wiesZheng
@Software : PyCharm
"""
from app.crud import BaseManager
from app.models.user import UserModel
from app.schemas.user import RegisterUserBody


class UserManager(BaseManager):
    orm_table = UserModel

    async def get_name_by_email(self, email):
        username = await self.query_one(cols=["username"], conds=[self.orm_table.email == email], flat=True)
        return username

    # @classmethod
    async def register(self, user_item: RegisterUserBody):
        """ 用户注册 """

        user = await self.create(object=user_item)
        return user
