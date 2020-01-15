# -*- encoding: utf-8 -*-

from channels import Group

import json

import time
import random

from myworkflows.models import ServerHotUpdate
from myworkflows.utils import get_hot_server_processing


def ws_connect(message, update_type):
    # Work out room name from path (ignore slashes)
    """
    if update_type == "hot_client":
        group_name = "hot_client"
    elif update_type == "hot_server":
        group_name = "hot_server"
    else:
        message.reply_channel.send({"accept": False})
    """
    # 这里不再区分前后端
    Group('hot_update').add(message.reply_channel)
    # Accept the connection request
    message.reply_channel.send({"accept": True})


def ws_hot_server_connect(message, hot_server_id):
    """热更新详情
    """

    group_name = 'hot_server%s' % (hot_server_id)

    Group(group_name).add(message.reply_channel)
    message.reply_channel.send({"accept": True})


def ws_hot_server_disconnect(message, hot_server_id):
    """热更新详情
    """

    group_name = 'hot_server%s' % (hot_server_id)

    Group(group_name).discard(message.reply_channel)


def ws_message(message, update_type):
    # ASGI WebSocket packet-received and send-packet message types
    # both have a "text" key for their textual data.
    """
    if update_type == "hot_client":
        group_name = "hot_client"
    elif update_type == "hot_server":
        group_name = "hot_server"
    """
    Group('hot_update').send({
        "text": "ok",
    })


def ws_disconnect(message, update_type):
    Group('hot_update').discard(message.reply_channel)


def update_msg(message):
    """
    update_type = message.content["update_type"]
    if update_type == "hot_client":
        group_name = "hot_client"
    elif update_type == "hot_server":
        group_name = "hot_server"
    """
    Group('hot_update').send({
        "text": message.content['message'],
    })


def hot_detail_update(message):
    hot_server_id = message.content["hot_server_id"]
    group_name = 'hot_server%s' % (hot_server_id)
    # 休眠三秒
    time.sleep(random.random())
    Group(group_name).send({
        "text": json.dumps(message.content),
    })


def ws_hot_server_on_message(message, hot_server_id):
    try:
        hot_server = ServerHotUpdate.objects.get(id=hot_server_id)
    except ServerHotUpdate.DoesNotExist:
        pass
    else:
        result = get_hot_server_processing(hot_server)
        group_name = 'hot_server%s' % (hot_server_id)
        Group(group_name).send({
            "text": json.dumps(result),
        })


def ws_clean_user_connect(message, user_id):
    """热更新详情
    """

    group_name = 'user_id%s' % (user_id)
    Group(group_name).add(message.reply_channel)
    message.reply_channel.send({"accept": True})


def ws_clean_user_disconnect(message, user_id):
    """热更新详情
    """

    group_name = 'user_id%s' % (user_id)

    Group(group_name).discard(message.reply_channel)


def update_clean_user(message):
    user_id = message.content["user_id"]
    group_name = 'user_id%s' % (user_id)
    Group(group_name).send({
        "text": json.dumps(message.content),
    })


def execute_salt_task_connect(message):
    """
    执行salt任务结果connect
    """
    Group('salt_task').add(message.reply_channel)
    message.reply_channel.send({"accept": True})


def update_execute_salt_task(message):
    """更新执行saltstack任务结果"""
    group_name = message.content['group_name']
    Group(group_name).send({
        "text": json.dumps(message.content),
    })


def execute_salt_task_disconnect(message):
    """
    执行salt任务结果disconnect
    """
    Group('salt_task').discard(message.reply_channel)


def game_server_action_connect(message):
    """
    区服操作connect
    """
    Group('game_server_action').add(message.reply_channel)
    message.reply_channel.send({"accept": True})


def update_game_server_action(message):
    """更新区服操作结果"""
    group_name = message.content['group_name']
    Group(group_name).send({
        "text": json.dumps(message.content),
    })


def game_server_action_disconnect(message):
    """
    区服操作disconnect
    """
    Group('game_server_action').discard(message.reply_channel)


def game_server_action_record_connect(message):
    """
    区服操作记录connect
    """
    Group('game_server_action_record').add(message.reply_channel)
    message.reply_channel.send({"accept": True})


def update_game_server_action_record(message):
    """刷新区服操作记录表"""
    group_name = message.content['group_name']
    Group(group_name).send({
        "text": json.dumps(message.content),
    })


def game_server_action_record_disconnect(message):
    """
    区服操作记录disconnect
    """
    Group('game_server_action_record').discard(message.reply_channel)


def execute_salt_command_connect(message, uuid):
    """
    执行salt命令connect
    """
    Group('execute_salt_command{}'.format(uuid)).add(message.reply_channel)
    message.reply_channel.send({"accept": True})


def update_execute_salt_command(message):
    """刷新执行salt命令结果"""
    group_name = message.content['group_name'] + message.content['uuid']
    Group(group_name).send({
        "text": json.dumps(message.content),
    })


def execute_salt_command_disconnect(message, uuid):
    """
    执行salt命令disconnect
    """
    Group('execute_salt_command{}'.format(uuid)).discard(message.reply_channel)
