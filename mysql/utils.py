# -*- encoding: utf-8- -*-
from channels import Channel
import re


def ws_update_mysql_list():
    """刷新数据库实例列表"""
    msg = {"message": 'update_table', 'group_name': 'mysql_list'}
    Channel('update_mysql_list').send(msg)


def is_ip(char):
    p = re.compile('^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$')
    if p.match(char):
        return True
    else:
        return False
