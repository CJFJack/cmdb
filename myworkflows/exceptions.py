# -*- encoding: utf-8 -*-

"""myworkflows的自定义exception
"""


class CurrentStateError(Exception):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)


class WorkflowStateUserRelationError(Exception):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)


class WorkflowError(Exception):
    """流程错误，没有设置初始状态"""

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)


class UserNotInGroup(Exception):
    """用户没有分组"""

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)


class GroupExtentionError(Exception):
    """分组扩展错误"""

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)


class GameProjectError(Exception):
    """用户没有分组"""

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)


class HotUpdateBlock(Exception):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)
