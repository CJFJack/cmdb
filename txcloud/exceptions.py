# -*- encoding: utf-8 -*-

"""txcloud的自定义exception
"""


class TxCloudError(Exception):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)


