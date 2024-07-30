#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Version  : Python 3.12
@Time     : 2024/7/2 22:50
@Author   : wiesZheng
@Software : PyCharm
"""
from art import text2art
from loguru import logger
from app import alden, init_logging, init_create_table
from app.apis import register_routers
from app.exceptions import register_global_exceptions_handler
from app.middlewares import register_middlewares

from config import Settings

init_logging(Settings.LOGGING_CONF)
logger.success(text2art(Settings.APP_NAME, font='block', chr_ignore=True))
# 注册中间件
register_middlewares(alden)
logger.info("middlewares is register success！！")
# 注册全局异常处理器
register_global_exceptions_handler(alden)
logger.info("global exceptions is register success！！！")


@alden.on_event('startup')
async def startup_event():
    # step3 加载路由
    await register_routers(alden)
    logger.info("routers is register success！！！")

    # step5 初始化数据库，建表
    try:
        await init_create_table()
        logger.info("database and tables created success.        ✔")
    except Exception as e:
        logger.info(f"database and tables  created failed.        ❌")
        raise e


@alden.on_event("shutdown")
async def shutdown_event():
    pass
