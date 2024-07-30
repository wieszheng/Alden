#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Version  : Python 3.12
@Time     : 2024/7/2 22:49
@Author   : wiesZheng
@Software : PyCharm
"""
from fastapi import FastAPI
from app.apis.v1 import v1


async def register_routers(_app: FastAPI):
    _app.include_router(v1, prefix="/api")
