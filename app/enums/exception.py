#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Version  : Python 3.12
@Time     : 2024/7/13 23:05
@Author   : wiesZheng
@Software : PyCharm
"""
from dataclasses import dataclass
from enum import Enum, unique
from functools import lru_cache


class BaseEnum(Enum):
    """枚举基类"""

    @classmethod
    def get_member_values(cls):
        return [item.value for item in cls._member_map_.values()]

    @classmethod
    def get_member_names(cls):
        return [name for name in cls._member_names_]


class ErrorCodeEnum(BaseEnum):
    """ 错误码枚举类 """

    OK = (0, 'SUCCESS')
    ERROR = (-1, 'FAILED')

    IMAGE_CODE_ERR = (4001, '图形验证码错误')
    THROTTLING_ERR = (4002, '访问过于频繁')
    NECESSARY_PARAM_ERR = (4003, '缺少必传参数')
    ACCOUNT_ERR = (4004, '账号或密码错误')
    AUTHORIZATION_ERR = (4005, '权限认证错误')
    CPWD_ERR = (4006, '密码不一致')
    MOBILE_ERR = (4007, '手机号错误')
    SMS_CODE_ERR = (4008, '短信验证码有误')
    ALLOW_ERR = (4009, '未勾选协议')
    SESSION_ERR = (4010, '用户未登录')
    REGISTER_FAILED_ERR = (4011, '注册失败')
    FACILITY_EXIST_ERR = (4012, '房屋设施已存在')
    PUBLISH_HOUSE_ERR = (4013, '发布房源失败')
    DATE_ERR = (4014, '日期错误')
    ORDER_EXIST_ERR = (4015, '订单已存在')
    ORDER_INFO_ERR = (4016, '订单信息错误')
    FORBIDDEN_ERR = (4017, '非法请求')
    REALNAME_AUTH_ERR = (4018, '实名认证错误')

    DB_ERR = (5000, '数据库错误')
    EMAIL_ERR = (5001, '邮箱错误')
    TEL_ERR = (5002, '固定电话错误')
    NODATA_ERR = (5003, '无数据')
    NEW_PWD_ERR = (5004, '新密码错误')
    OPENID_ERR = (5005, '无效的openid')
    PARAM_ERR = (5006, '参数错误')
    STOCK_ERR = (5007, '库存不足')
    SOCKET_ERR = (5008, '网络错误')
    SYSTEM_ERR = (5009, '系统错误')

    @property
    def code(self):
        """ 获取错误码 """
        return self.value[0]

    @property
    def msg(self):
        """ 获取错误码码信息 """
        return self.value[1]


@dataclass
class HttpResponseInfo:
    code: int
    msg: str


@unique
class HttpResponseEnum(Enum):
    """HTTP响应枚举"""

    # 2xx(成功状态码)
    SUCCESS = HttpResponseInfo(200, "请求成功")
    CREATE = HttpResponseInfo(201, "请求成功, 服务端创建了一个新资源")
    NOT_CONTENT = HttpResponseInfo(204, "请求成功, 但响应不包含任何数据")

    # 3xx(重定向错误码)
    MOVED_PERMANENTLY = HttpResponseInfo(301, "资源永久移动到新位置")
    FOUND = HttpResponseInfo(302, "资源暂时移动到新位置")
    GET_LOCATION_URL = HttpResponseInfo(303, "向重定向的url发起get请求")
    NOT_MODIFY = HttpResponseInfo(304, "客户端缓存仍然有效")
    HOLD_METHOD_REQUEST_LOCATION_URL = HttpResponseInfo(
        307, "保持原来的请求方法并向重定向的url发起请求"
    )

    # 4xx(客户端错误码)
    BAD_REQUEST = HttpResponseInfo(400, "请求无效或无法被服务端理解")
    NOT_AUTH = HttpResponseInfo(401, "用户未登录, 或登录已超时")
    NOT_PERMISSION = HttpResponseInfo(403, "当前身份无相关操作权限")
    NOT_FOUND = HttpResponseInfo(404, "访问的资源不存在")
    REQUEST_METHOD_ERROR = HttpResponseInfo(405, "不允许使用此方法提交访问")
    LOCKED_REQUEST_ERROR = HttpResponseInfo(
        423, "请求失败, 请稍后重试"
    )  # 不允许并发请求
    TOO_MANY_REQUEST_ERROR = HttpResponseInfo(429, "请求过于频繁, 请稍后重试")

    # 5xx(服务端错误码)
    SERVER_ERROR = HttpResponseInfo(500, "服务错误, 无法完成请求, 请联系管理员!")
    SERVER_UNAVAILABLE = HttpResponseInfo(503, "服务过载或正在维护")
    SERVER_TIMEOUT = HttpResponseInfo(504, "因服务侧原因导致的请求超时")

    # 以下都为自定义错误码
    FAILED = HttpResponseInfo(600, "请求失败")
    REFRESH_TOKEN_EXPIRED = HttpResponseInfo(601, "刷新令牌无效或已过期")
    # 统一使用错误码606, 表示参数验证错误
    PARAMS_VALID_ERROR = HttpResponseInfo(606, "请求参数校验错误")
    # 防抖
    REQUEST_REPEATED = HttpResponseInfo(900, "重复请求, 请稍后重试")
    # 演示模式
    DEMO_DENY = HttpResponseInfo(901, "演示模式, 禁止写操作")

    @classmethod
    @lru_cache
    def get_code_msg_dict_cache(cls) -> dict[int, str]:
        """以缓存的方式返回响应状态码与响应信息的映射
        Returns:
            dict[int, str]: 响应状态码与响应信息的映射
        """
        return {item.value.code: item.value.msg for item in cls}

    @classmethod
    def use_code_get_enum_msg(cls, code: int) -> str:
        """通过响应状态码获取对应的响应信息
        Args:
            code: 响应状态码

        Returns:
            str: 响应信息
        """
        mapping = cls.get_code_msg_dict_cache()
        return mapping[code]
