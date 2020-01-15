# -*- encoding: utf-8 -*-

from channels import Group
import json


def mysql_list_connect(message):
    """
    数据库实例列表connect
    """
    Group('mysql_list').add(message.reply_channel)
    message.reply_channel.send({"accept": True})


def update_mysql_list(message):
    """更新数据库实例列表"""
    Group('mysql_list').send({
        "text": json.dumps(message.content),
    })


def mysql_list_disconnect(message):
    """
    数据库实例列表disconnect
    """
    Group('mysql_list').discard(message.reply_channel)
