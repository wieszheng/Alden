#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Version  : Python 3.12
@Time     : 2024/7/2 22:51
@Author   : wiesZheng
@Software : PyCharm
"""
import uvicorn
from config import Settings

if __name__ == "__main__":
    uvicorn.run("main:alden",
                host=Settings.APP_HOST,
                port=Settings.APP_PORT,
                reload=True,
                forwarded_allow_ips="*",
                access_log=False)
