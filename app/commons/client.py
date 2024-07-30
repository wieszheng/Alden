#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Version  : Python 3.12
@Time     : 2024/7/13 17:18
@Author   : wiesZheng
@Software : PyCharm
"""
from datetime import timedelta
from typing import BinaryIO

from minio import Minio

from config import Settings


class MiNiOClient:
    def __init__(self):
        self.client = Minio(
            endpoint=Settings.MINIO_ENDPOINT,
            access_key=Settings.MINIO_ACCESS_KEY,
            secret_key=Settings.MINIO_SECRET_KEY,
            secure=Settings.MINIO_SECURE

        )
        self.bucket_name = Settings.MINIO_BUCKET_NAME
        self.make_bucket()

    def make_bucket(self):
        """
        创建bucket
        :return:
        """
        if not self.check_bucket():
            return self.client.make_bucket(self.bucket_name)

    def check_bucket(self):
        """
        检查bucket是否存在
        :return:
        """
        return self.client.bucket_exists(self.bucket_name)

    def upload_file(self, object_name: str, data: BinaryIO, part_size=10 * 1024 * 1024, **kwargs):
        """
        上传文件
        :param object_name: 存储的文件路径
        :param data: 文件名称
        :param part_size: 分块上传大小
        :return:
        """
        if "length" not in kwargs:
            # 不指定长度，适用于未知大小的流
            kwargs["length"] = -1
        return self.client.put_object(self.bucket_name, object_name, data, part_size=part_size, **kwargs)

    def upload_file_v2(self, object_name: str, file_path: str):
        """
        上传文件v2
        :param object_name: 存储的文件路径
        :param file_path: 文件路径
        :return:
        """

        return self.client.fput_object(self.bucket_name, object_name=object_name, file_path=file_path)

    def download_file(self, object_name: str, file_name: str):
        """
        下载文件
        :param object_name: 存储路径
        :param file_name: 文件名称
        :return:
        """
        return self.client.fget_object(self.bucket_name, object_name, file_name)

    def delete_file(self, object_name: str):
        """
        删除文件
        :param object_name: 存储路径
        :return:
        """
        return self.client.remove_object(self.bucket_name, object_name)

    def get_bucket_list(self):
        """
        获取bucket列表
        :return:
        """
        return self.client.list_buckets()

    def list_bucket_object_list(self, bucket_name: str):
        """
        获取bucket下的文件列表
        :param bucket_name: bucket名称
        :return:
        """
        return self.client.list_objects(bucket_name)

    def pre_signature_put_object_url(self, object_name: str, expires: int = 7 * 24 * 60 * 60):
        """
        获取预签名url；前端通过该url上传文件到minio，无需经过后端
        :param object_name: 存储路径
        :param expires: 过期时间 秒 默认7天
        """
        expires = timedelta(seconds=expires)
        return self.client.presigned_put_object(self.bucket_name, object_name, expires)

    def pre_signature_get_object_url(self, object_name: str, expires: int = 7 * 24 * 60 * 60):
        """
        获取预签名url
        :param object_name: 存储路径
        :param expires: 过期时间秒, 默认7天
        """
        return self.client.presigned_get_object(self.bucket_name, object_name, timedelta(seconds=expires))
