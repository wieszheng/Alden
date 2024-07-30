#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Version  : Python 3.12
@Time     : 2024/7/16 23:36
@Author   : wiesZheng
@Software : PyCharm
"""
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, INT, TEXT, SMALLINT, UniqueConstraint
from typing import List
from app.models import BaseOrmTableWithTS


class TestCase(BaseOrmTableWithTS):
    __tablename__ = "alden_testcase"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(32), index=True, comment="用例名称")
    request_type: Mapped[int] = mapped_column(INT, default=1, comment="请求类型 1: http 2: grpc 3: dubbo")
    url: Mapped[str] = mapped_column(TEXT, nullable=False, comment="请求url")
    request_method: Mapped[str | None] = mapped_column(String(12), nullable=True, comment="请求方式, 如果非http可为空")
    request_headers: Mapped[str | None] = mapped_column(TEXT, comment="请求头，可为空")
    base_path: Mapped[str | None] = mapped_column(String(24), comment="请求base_path")
    body: Mapped[str | None] = mapped_column(TEXT, comment="请求body")
    body_type: Mapped[int | None] = mapped_column(INT,
                                                  comment="请求类型, 0: none 1: json 2: form 3: x-form 4: binary 5: GraphQL")
    directory_id: Mapped[int | None] = mapped_column(INT, comment="所属目录")
    tag: Mapped[str | None] = mapped_column(String(64), comment="用例标签")
    status: Mapped[int | None] = mapped_column(INT, comment="用例状态: 1: 调试中 2: 暂时关闭 3: 正常运作")
    priority: Mapped[str | None] = mapped_column(String(3), comment="用例优先级: P0-P4")
    case_type: Mapped[int | None] = mapped_column(SMALLINT, comment="0: 普通用例 1: 前置用例 2: 数据工厂")
    # out_parameters: Mapped[List["PityTestCaseOutParameters"]] = mapped_column(comment="输出参数列表")
