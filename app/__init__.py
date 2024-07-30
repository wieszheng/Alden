#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Version  : Python 3.12
@Time     : 2024/7/2 22:47
@Author   : wiesZheng
@Software : PyCharm
"""
import logging
import os
import sys
from pprint import pformat

from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from loguru._defaults import LOGURU_FORMAT
from loguru import logger
from starlette.staticfiles import StaticFiles

from app.apis.v1 import v1
from app.crud import BaseManager
from app.models import BaseOrmTable, async_engine
from config import Settings, ROOT

alden = FastAPI(
    title=Settings.APP_NAME,
    version=Settings.APP_VERSION,
    docs_url=None)

alden.mount("/static", StaticFiles(directory=f"{ROOT}/static"), name="static")


@alden.get('/docs', include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title=Settings.APP_NAME + " - Swagger UI",
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css"
    )


async def init_create_table():
    # 根据映射创建库表（异步）
    async with async_engine.begin() as conn:
        await conn.run_sync(BaseOrmTable.metadata.create_all)


class InterceptHandler(logging.Handler):

    def emit(self, record: logging.LogRecord):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def format_record(record: dict):
    format_string = LOGURU_FORMAT
    if record["extra"].get("payload") is not None:
        record["extra"]["payload"] = pformat(
            record["extra"]["payload"], indent=4, compact=True, width=88
        )
        format_string += "\n<level>{extra[payload]}</level>"
    format_string += "{exception}\n"
    return format_string


def make_filter(name: str):
    # 过滤操作，当日志要选择对应的日志文件的时候，通过filter进行筛选
    def filter_(record):
        return record["extra"].get("name") == name

    return filter_


def init_logging_old():
    logger_names = ("uvicorn.access", "uvicorn.error", "uvicorn")
    for name in logger_names:
        logging.getLogger(name).handlers = [InterceptHandler()]

    info = os.path.join(Settings.LOG_DIR, f"{Settings.LOG_INFO}.log")
    error = os.path.join(Settings.LOG_DIR, f"{Settings.LOG_ERROR}.log")
    # 配置loguru的日志句柄，sink代表输出的目标
    logger.configure(
        handlers=[
            {"sink": sys.stdout, "level": logging.DEBUG, "format": format_record},
            # {"sink": info, "level": logging.DEBUG, "rotation": "500 MB", "encoding": 'utf-8'},
            # {"sink": error, "level": logging.WARNING, "serialize": True, "rotation": "500 MB", "encoding": 'utf-8'}
        ]
    )
    logger.add(info, enqueue=True, rotation="20 MB", level="DEBUG", encoding='utf-8')
    logger.add(error, enqueue=True, rotation="10 MB", level="WARNING", encoding='utf-8')
    logger.debug('日志系统已加载')

    return logger


def init_logging(logging_conf: dict):
    for log_handler, log_conf in logging_conf.items():
        log_file = log_conf.pop('file', None)
        logger.add(log_file, **log_conf)
