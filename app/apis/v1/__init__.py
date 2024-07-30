#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Version  : Python 3.12
@Time     : 2024/7/2 23:15
@Author   : wiesZheng
@Software : PyCharm
"""
from fastapi import APIRouter
from app.apis.v1.auth import user
from app.apis.v1 import common


v1 = APIRouter(prefix="/v1")

RegisterRouterList = [
    user,
    common
]

for item in RegisterRouterList:
    v1.include_router(item.router)
