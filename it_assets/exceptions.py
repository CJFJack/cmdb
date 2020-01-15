# -*- encoding: utf-8 -*-

"""it_assets的自定义exception
"""


class StatusError(Exception):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)


class StockNotEnough(Exception):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)


class AssetsPartModelNotEnouth(Exception):
    """由固定资产的配件数量不够引发的异常
    """

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)


class PartModelStatusNotEnouth(Exception):
    """由配件状态表中配件数量不够引发的异常
    """

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)
