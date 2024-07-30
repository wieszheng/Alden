#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Version  : Python 3.12
@Time     : 2024/7/13 17:50
@Author   : wiesZheng
@Software : PyCharm
"""
import asyncio
import random
import uuid

from fastapi import APIRouter, File, UploadFile
from starlette.exceptions import WebSocketException
from starlette.websockets import WebSocket

from app.commons.client import MiNiOClient

router = APIRouter(prefix="", tags=["公共"])
minio_C = MiNiOClient()


@router.websocket("/ws", name="系统信息")
async def get_system_info(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            data = {
                "usage": {
                    "cpu": f"{random.random() * 100: .2}",
                    "memory": f"{random.random() * 100: .2}",
                    "disk": f"{random.random() * 100: .2}",
                },
                "performance": {
                    "rps": f"{random.random() * random.randint(1, 50): .2}",
                    "time": f"{random.random() * random.randint(1, 50): .2}",
                    "user": f"{random.randint(1, 50)}",
                },
            }
            await asyncio.sleep(1)
            await ws.send_json(data)
    except WebSocketException:
        await ws.close()


@router.post("/upload", summary="上传文件")
async def upload_file(file: UploadFile = File(..., description="上传的文件")):
    # 生成随机文件名
    random_suffix = str(uuid.uuid4()).replace('-', '')
    object_name = f"{random_suffix}.{file.filename.split('.')[-1]}"
    minio_C.upload_file(object_name, file.file,
                        content_type=file.content_type)

    url = minio_C.pre_signature_get_object_url(object_name)
    return {"code": 0, "msg": "上传成功", "url": url}
