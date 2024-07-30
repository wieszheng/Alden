#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Version  : Python 3.12
@Time     : 2024/7/2 23:16
@Author   : wiesZheng
@Software : PyCharm
"""
from fastapi import APIRouter, Depends

from app.crud.auth.user import UserManager
from app.schemas.user import RegisterUserBody, UserIn

router = APIRouter(prefix="/users", tags=["用户接口"])


@router.post("/login", summary="用户登录")
async def login():
    return {"code": 0, "msg": "登录成功"}


@router.post("/register", summary="用户注册")
async def register_user(user_item: RegisterUserBody):
    user = await UserManager().register(user_item)
    return {"code": 0, "msg": "注册成功"}


@router.get("/users", summary="查询用户")
async def users():
    user = await UserManager().get_by_id(id=2)
    print(user)
    return {"code": 0, "msg": "登录成功", "data": "data"}
