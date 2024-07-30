#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Version  : Python 3.12
@Time     : 2024/7/2 22:51
@Author   : wiesZheng
@Software : PyCharm
"""
import argparse
import os
import sys
from functools import lru_cache
from typing import ClassVar

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

ROOT = os.path.dirname(os.path.abspath(__file__))


class AppConfigSettings(BaseSettings):
    LOG_DIR: ClassVar = os.path.join(ROOT, 'logs')

    # 服务配置信息
    APP_NAME: str
    APP_VERSION: str
    APP_HOST: str
    APP_PORT: int
    APP_ENV: str

    # 数据库配置
    MYSQL_PROTOCOL: str
    MYSQL_HOST: str
    MYSQL_PORT: int
    MYSQL_USER: str
    MYSQL_PASSWORD: str
    MYSQL_DATABASE: str

    # SalAlchemy配置
    ASYNC_DATABASE_URI: str

    # 日志配置
    LOG_ERROR: str
    LOG_INFO: str
    DEBUG: bool

    # 用户权限
    MEMBER: int
    MANAGER: int
    ADMIN: int

    # jwt配置
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    JWT_EXPIRED: int
    JWT_ISS: str

    # minio
    MINIO_ENDPOINT: str
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_SECURE: bool
    MINIO_BUCKET_NAME: str
    MINIO_BUCKET_ACCESS_KEY: str
    MINIO_BUCKET_SECRET_KEY: str

    # 密码加密配置
    BCRYPT_ROUNDS: int  # bcrypt迭代次数,越大耗时越长(好在python的bcrypt是C库)

    # 日志
    # 项目运行时所有的日志文件
    SERVER_LOG_FILE: str = os.path.join(LOG_DIR, 'server.log')

    # 错误时的日志文件
    ERROR_LOG_FILE: str = os.path.join(LOG_DIR, 'error.log')

    # 项目日志滚动配置（日志文件超过10 MB就自动新建文件扩充）
    LOGGING_ROTATION: str = "10 MB"
    LOGGING_CONF: dict = {
        'server_handler': {
            'file': SERVER_LOG_FILE,
            'level': 'INFO',
            'rotation': LOGGING_ROTATION,
            'backtrace': False,
            'diagnose': False,
        },
        'error_handler': {
            'file': ERROR_LOG_FILE,
            'level': 'ERROR',
            'rotation': LOGGING_ROTATION,
            'backtrace': True,
            'diagnose': True,
        },
    }

    BANNER: str = """
                                      \`-,                             
                                      |   `\                           
                                      |     \                          
                                   __/.- - -.\,__                      
                              _.-'`              `'"'--..,__           
                          .-'`                              `'--.,_    
                       .'`   _                         _ ___       `)  
                     .'   .'` `'-.                    (_`  _`)  _.-'   
                   .'    '--.     '.                 .-.`"`@ .-'""-,   
          .------~'     ,.---'      '-._      _.'   /   `'--':::.-'   
        /`        '   /`  _,..-----.,__ `''''`/    ;__,..--''--'`      
        `'--.,__ '    |-'`             `'---'|     |                   
                `\    \                       \   /                    
                 |     |                       '-'                     
                  \    |                                               
                   `\  |                                               
                     \/  
    
            """


@lru_cache
def getAppConfig():
    """ 获取项目配置 """

    if "uvicorn" in sys.argv[0]:
        return

    parser = argparse.ArgumentParser(description="命令行参数")
    parser.add_argument("--env", type=str, default="", help="运行环境")

    args, unknown = parser.parse_known_args()
    os.environ["APP_ENV"] = args.env

    runenv = os.environ.get("APP_ENV", "")
    envfile = ".env"
    if runenv != "":
        # 当是其他环境时，如测试环境: 加载 .env.test 正式环境: 加载.env.prod
        envfile = f".env.{runenv}"
    load_dotenv(os.path.join(ROOT, "conf", envfile))
    return AppConfigSettings()


Settings = getAppConfig()
