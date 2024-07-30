#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Version  : Python 3.12
@Time     : 2024/7/20 17:56
@Author   : wiesZheng
@Software : PyCharm
"""
from collections.abc import Callable
from typing import TypeVar

Transaction = TypeVar("Transaction", bool, Callable)

transaction: Transaction = True
if callable(transaction):
    print("hello world")