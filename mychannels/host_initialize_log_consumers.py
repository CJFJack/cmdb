# -*- encoding: utf-8 -*-

from channels import Group
import json


def host_initialize_list_connect(message):
    """
    主机初始化列表connect
    """
    Group('host_initialize_list').add(message.reply_channel)
    message.reply_channel.send({"accept": True})


def update_host_initialize_list(message):
    """更新主机初始化列表"""
    Group('host_initialize_list').send({
        "text": json.dumps(message.content),
    })


def host_initialize_list_disconnect(message):
    """
    主机初始化列表disconnect
    """
    Group('host_initialize_list').discard(message.reply_channel)


def host_initialize_log_connect(message, id):
    """
    主机初始化日志connect
    """
    group_name = 'host_initialize_log%s' % (id)
    Group(group_name).add(message.reply_channel)
    message.reply_channel.send({"accept": True})


def update_host_initialize_log(message):
    """刷新主机初始化日志"""
    game_server_off_id = message.content['host_initialize_id']
    group_name = 'host_initialize_log%s' % game_server_off_id
    Group(group_name).send({
        "text": json.dumps(message.content),
    })


def host_initialize_log_disconnect(message, id):
    """
    主机初始化日志disconnect
    """
    group_name = 'host_initialize_log%s' % (id,)
    Group(group_name).discard(message.reply_channel)
