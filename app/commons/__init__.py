# !/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@Version  : Python 3.12
@Time     : 2024/7/8 12:34
@Author   : wiesZheng
@Software : PyCharm
"""
import threading
from typing import Generic, Optional, TypeVar, List

from pydantic import BaseModel

T = TypeVar("T")


class SingletonMetaCls(type):
    """ 单例元类 """
    _instance_lock = threading.Lock()

    def __init__(cls, *args, **kwargs):
        cls._instance = None
        super().__init__(*args, **kwargs)

    def _init_instance(cls, *args, **kwargs):
        if cls._instance:
            # 存在实例对象直接返回，减少锁竞争，提高性能
            return cls._instance

        with cls._instance_lock:
            if cls._instance is None:
                cls._instance = super().__call__(*args, **kwargs)
        return cls._instance

    def __call__(cls, *args, **kwargs):
        reinit = kwargs.pop("reinit", True)
        instance = cls._init_instance(*args, **kwargs)
        if reinit:
            # 重新初始化单例对象属性
            instance.__init__(*args, **kwargs)
        return instance


class R(BaseModel, Generic[T]):
    code: int
    data: T
    message: str

    @staticmethod
    def success(message: str = "success", data: T = None) -> "R":
        return R(code=200, message=message, data=data)

    @staticmethod
    def fail(code: int = 400, message: str = "fail", data: T = None) -> "R":
        return R(code=code, message=message, data=data)

    # @validator('error', always=True)
    # def check_consistency(cls, v, values):
    #     if v is not None and values['data'] is not None:
    #         raise ValueError('must not provide both data and error')
    #     if v is None and values.get('data') is None:
    #         raise ValueError('must provide data or error')
    #     return v
