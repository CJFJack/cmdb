# -*- encoding: utf-8 -*-

"""API的自定义exception

主要包含了在创建host的过程中一些字段不能为''
"""


class HostFieldEmpty(Exception):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)


class MoreThanOneIpIsRequired(Exception):
    """至少需要一个ip字段"""

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)


class ParamError(Exception):
    """参数错误
    api没有检测到该有的参数
    """

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)


class GameServerNotExist(Exception):
    """通过查询条件没有找到游戏服
    """

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)


class SrvSelectTypeError(Exception):
    """srv_select_type错误
    """

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)
