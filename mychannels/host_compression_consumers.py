# -*- encoding: utf-8 -*-

from channels import Group
import json


def host_compression_list_connect(message):
    """
    机器回收任务列表connect
    """
    Group('host_compression_list').add(message.reply_channel)
    message.reply_channel.send({"accept": True})


def update_host_compression_list(message):
    """更新机器回收任务列表"""
    Group('host_compression_list').send({
        "text": json.dumps(message.content),
    })


def host_compression_list_disconnect(message):
    """
    机器回收任务列表disconnect
    """
    Group('host_compression_list').discard(message.reply_channel)


def host_compression_detail_connect(message, id):
    """
    机器回收详情connect
    """
    group_name = 'host_compression_detail%s' % id
    Group(group_name).add(message.reply_channel)
    message.reply_channel.send({"accept": True})


def update_host_compression_detail(message):
    """更新机器回收详情"""
    obj_id = message.content['obj_id']
    group_name = 'host_compression_detail%s' % obj_id
    Group(group_name).send({
        "text": json.dumps(message.content),
    })


def host_compression_detail_disconnect(message, id):
    """
    机器回收详情disconnect
    """
    group_name = 'host_compression_detail%s' % id
    Group(group_name).discard(message.reply_channel)


def host_compression_log_connect(message, id):
    """
    机器回收日志connect
    """
    group_name = 'host_compression_log%s' % (id)
    Group(group_name).add(message.reply_channel)
    message.reply_channel.send({"accept": True})


def update_host_compression_log(message):
    """刷新机器回收日志"""
    host_compression_id = message.content['host_compression_id']
    group_name = 'host_compression_log%s' % host_compression_id
    Group(group_name).send({
        "text": json.dumps(message.content),
    })


def host_compression_log_disconnect(message, id):
    """
    机器回收日志disconnect
    """
    group_name = 'host_compression_log%s' % (id)
    Group(group_name).discard(message.reply_channel)
