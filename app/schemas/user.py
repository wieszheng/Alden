#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Version  : Python 3.12
@Time     : 2024/7/8 23:44
@Author   : wiesZheng
@Software : PyCharm
"""
from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.user import UserModel
from typing import Any, Dict, List, Optional, Tuple, Type
from sqlalchemy import inspect
from sqlalchemy.orm import DeclarativeBase


def get_model_fields(model: Type[DeclarativeBase], include: Tuple[str, ...], exclude: Tuple[str, ...]) -> Dict[
    str, Any]:
    mapper = inspect(model)
    columns = {column.key: column for column in mapper.columns}
    relationships = {rel.key: rel for rel in mapper.relationships}

    fields = {key: {'field_type': value.type.python_type} for key, value in columns.items()}
    fields.update({key: {'field_type': value.mapper.class_} for key, value in relationships.items()})

    if include:
        fields = {k: v for k, v in fields.items() if k in include}
    if exclude:
        fields = {k: v for k, v in fields.items() if k not in exclude}

    return fields


class PydanticModel(BaseModel):
    # 这里可以添加Pydantic模型的基本配置
    pass


def sqlalchemy_model_creator(
        cls: Type[DeclarativeBase],
        *,
        name: Optional[str] = None,
        exclude: Tuple[str, ...] = (),
        include: Tuple[str, ...] = (),
) -> Type[PydanticModel]:
    """
    Function to build Pydantic Model off SQLAlchemy ORM model.

    :param cls: The SQLAlchemy ORM model
    :param name: Specify a custom name explicitly, instead of a generated name.
    :param exclude: Fields to exclude from the provided model.
    :param include: Fields to include from the provided model.
    """
    # 全限定类名
    fqname = cls.__module__ + "." + cls.__qualname__

    # 获取所有字段
    fields = get_model_fields(cls, include, exclude)

    # 创建Pydantic模型类
    model_name = name or fqname
    model_dict = {"__annotations__": {k: v['field_type'] for k, v in fields.items()}}

    # 创建并返回Pydantic模型
    model = type(model_name, (PydanticModel,), model_dict)
    model.__doc__ = cls.__doc__
    return model


UserIn = sqlalchemy_model_creator(UserModel, name="UserIn")

UserOut = sqlalchemy_model_creator(UserModel, name="UserOut", exclude=("password",))


class RegisterUserBody(BaseModel):
    username: str = Field(..., title="用户名", description="必传")
    password: str = Field(..., title="密码", description="必传")
    nickname: str = Field(..., title="姓名", description="必传")
    email: EmailStr = Field(..., title="邮箱号", description="必传")

    @field_validator("username")
    def validate_username(cls, value: str):
        if len(value) < 4:
            raise ValueError("用户名长度不能小于4")
        return value

    @field_validator("email")
    def validate_email(cls, value: str):
        if not value.endswith("@qq.com"):
            raise ValueError("邮箱格式不正确")
        return value


class UserLoginIn(BaseModel):
    username: str = Field(..., description="用户昵称")
    # 我们也得拿到用户密码 用密码去数据库比对，用户输入了正确的密码才能正常登录
    password: str = Field(..., description="用户密码")


class BaseRespModel(BaseModel):
    code: str = Field(..., description="响应吗")
    message: str = Field(..., description="响应消息")
    data: dict = Field(..., description="响应数据")


# 用户详情
class UserDetailItem(BaseModel):
    id: int = Field(description="用户唯一标识id")
    username: str = Field(description="用户昵称")
    email: str = Field(description="用户邮箱")
    phone: str = Field(description="手机号")


class UserDetailOut(BaseRespModel):
    """用户详情出参"""

    data: UserDetailItem = Field(description="用户详情信息")
