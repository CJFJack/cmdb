# -*- encoding: utf-8 -*-

"""assets的自定义exception
"""


class StatusError(Exception):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)
