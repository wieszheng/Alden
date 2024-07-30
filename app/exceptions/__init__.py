#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Version  : Python 3.12
@Time     : 2024/7/13 23:09
@Author   : wiesZheng
@Software : PyCharm
"""
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.exceptions.exception_handler import (validation_exception_handler, business_exception_handler,
                                              global_exception_handler, authorization_exception_handler,
                                              http_exception_handler)
from app.exceptions.global_exception import AuthorizationException, BusinessException


def register_global_exceptions_handler(_app: FastAPI):
    """创建全局异常处理器"""
    exception_handler_list = [(StarletteHTTPException, http_exception_handler),
                              (RequestValidationError, validation_exception_handler),
                              (AuthorizationException, authorization_exception_handler),
                              (BusinessException, business_exception_handler),
                              (Exception, global_exception_handler)]
    for exception_name, exception_handler in exception_handler_list:
        _app.add_exception_handler(exception_name, exception_handler)
