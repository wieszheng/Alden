#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Version  : Python 3.12
@Time     : 2024/7/13 20:33
@Author   : wiesZheng
@Software : PyCharm
"""

import traceback

from fastapi.requests import Request
from fastapi.responses import JSONResponse

from fastapi.exceptions import RequestValidationError
from loguru import logger

from app.commons import R
from app.enums.exception import ErrorCodeEnum, HttpResponseEnum
from app.exceptions.global_exception import BusinessException, AuthorizationException
from starlette.exceptions import HTTPException as StarletteHTTPException


# 自定义http异常处理器
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    # res = ResponseDto(code=CodeEnum.HTTP_ERROR.code, msg=HTTP_MSG_MAP.get(exc.status_code, exc.detail))
    # if exc.status_code == 405:
    #     return MethodNotAllowedException()
    # if exc.status_code == 404:
    #     return NotfoundException()
    # elif exc.status_code == 429:
    #     return LimiterResException()
    logger.warning(
        f"Http请求异常\n"
        f"Method\n{request.method}"
        f"URL{request.url}\n"
        f"Headers:{request.headers}\n"
        f"Code:{exc.status_code}\n"
        f"Message:{exc.detail}\n"
    )

    exc_msg = HttpResponseEnum.use_code_get_enum_msg(exc.status_code)

    return JSONResponse(
        status_code=exc.status_code,
        content=R.fail(code=exc.status_code, message=str(exc_msg)).dict()
    )


async def business_exception_handler(request: Request, exc: BusinessException):
    """ 全局业务异常处理 """
    logger.info(
        f"Http请求异常\n"
        f"Method\n{request.method}"
        f"URL{request.url}\n"
        f"Headers:{request.headers}\n"
        f"Code:{exc.code}\n"
        f"Message:{exc.message}\n"
    )
    return JSONResponse(
        status_code=200,
        content=R.fail(code=exc.code, message=str(exc.message)).dict()
    )


async def authorization_exception_handler(request: Request, exc: AuthorizationException):
    """ 认证异常处理 """
    logger.debug('认证失败')
    return JSONResponse(
        status_code=401,
        content=R.fail(code=exc.code, message=str(exc.message)).dict()
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """ 全局捕捉参数验证异常 """
    message = '.'.join([f'{".".join(map(lambda x: str(x), error.get("loc")))}:{error.get("msg")};'
                        for error in exc.errors()])

    logger.warning(message)
    return JSONResponse(
        status_code=200,
        content=R.fail(code=-1, message=str(message)).dict()
    )


async def global_exception_handler(request: Request, exc: Exception):
    """ 全局系统异常处理器 """

    if isinstance(exc, ConnectionError):
        message = f'网络异常, {traceback.format_exc()}'
        error = ErrorCodeEnum.SOCKET_ERR
    # elif isinstance(exc, AuthorizationException):
    #     return await authorization_exception_handler(request, exc)
    else:
        message = f'系统异常, {traceback.format_exc()}'
        error = ErrorCodeEnum.SYSTEM_ERR

    logger.error(message)
    return JSONResponse(
        status_code=200,
        content=R.fail(code=error.code, message=str(message)).dict()
    )
