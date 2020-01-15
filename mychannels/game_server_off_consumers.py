# -*- encoding: utf-8 -*-

from channels import Group
import json


def game_server_off_list_connect(message):
    """
    区服下线任务列表connect
    """
    Group('game_server_off_list').add(message.reply_channel)
    message.reply_channel.send({"accept": True})


def update_game_server_off_list(message):
    """更新区服下线任务列表"""
    Group('game_server_off_list').send({
        "text": json.dumps(message.content),
    })


def game_server_off_list_disconnect(message):
    """
    区服下线任务列表disconnect
    """
    Group('game_server_off_list').discard(message.reply_channel)


def game_server_off_detail_connect(message, id):
    """
    区服下线详情connect
    """
    group_name = 'game_server_off_detail%s' % id
    Group(group_name).add(message.reply_channel)
    message.reply_channel.send({"accept": True})


def update_game_server_off_detail(message):
    """更新区服下线详情"""
    obj_id = message.content['obj_id']
    group_name = 'game_server_off_detail%s' % obj_id
    Group(group_name).send({
        "text": json.dumps(message.content),
    })


def game_server_off_detail_disconnect(message, id):
    """
    区服下线详情disconnect
    """
    group_name = 'game_server_off_detail%s' % id
    Group(group_name).discard(message.reply_channel)


def game_server_off_log_connect(message, id):
    """
    区服下线日志connect
    """
    group_name = 'game_server_off_log%s' % (id)
    Group(group_name).add(message.reply_channel)
    message.reply_channel.send({"accept": True})


def update_game_server_off_log(message):
    """刷新区服下线日志"""
    game_server_off_id = message.content['game_server_off_id']
    group_name = 'game_server_off_log%s' % game_server_off_id
    Group(group_name).send({
        "text": json.dumps(message.content),
    })


def game_server_off_log_disconnect(message, id):
    """
    区服下线日志disconnect
    """
    group_name = 'game_server_off_log%s' % (id)
    Group(group_name).discard(message.reply_channel)
