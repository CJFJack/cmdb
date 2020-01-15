# -*- encoding: utf-8 -*-

from channels import Group
import json


def modify_srv_open_time_schedule_list_connect(message):
    """
    修改开服时间计划列表connect
    """
    Group('modify_srv_open_time_schedule_list').add(message.reply_channel)
    message.reply_channel.send({"accept": True})


def update_modify_srv_open_time_schedule_list(message):
    """更新修改开服时间计划列表"""
    Group('modify_srv_open_time_schedule_list').send({
        "text": json.dumps(message.content),
    })


def modify_srv_open_time_schedule_list_disconnect(message):
    """
    修改开服时间计划列表disconnect
    """
    Group('modify_srv_open_time_schedule_list').discard(message.reply_channel)


def modify_srv_open_time_schedule_detail_connect(message, id):
    """
    修改开服时间计划详情connect
    """
    group_name = 'modify_srv_open_time_schedule_detail%s' % id
    Group(group_name).add(message.reply_channel)
    message.reply_channel.send({"accept": True})


def update_modify_srv_open_time_schedule_detail(message):
    """更新修改开服时间计划详情"""
    obj_id = message.content['obj_id']
    group_name = 'modify_srv_open_time_schedule_detail%s' % obj_id
    Group(group_name).send({
        "text": json.dumps(message.content),
    })


def modify_srv_open_time_schedule_detail_disconnect(message, id):
    """
    修改开服时间计划详情disconnect
    """
    group_name = 'modify_srv_open_time_schedule_detail%s' % id
    Group(group_name).discard(message.reply_channel)


def modify_srv_open_time_schedule_log_connect(message, id):
    """
    修改开服时间计划日志connect
    """
    group_name = 'modify_srv_open_time_schedule_log%s' % id
    Group(group_name).add(message.reply_channel)
    message.reply_channel.send({"accept": True})


def update_modify_srv_open_time_schedule_log(message):
    """刷新修改开服时间计划日志"""
    modify_schedule_id = message.content['modify_schedule_id']
    group_name = 'modify_srv_open_time_schedule_log%s' % modify_schedule_id
    Group(group_name).send({
        "text": json.dumps(message.content),
    })


def modify_srv_open_time_schedule_log_disconnect(message, id):
    """
    修改开服时间计划日志disconnect
    """
    group_name = 'modify_srv_open_time_schedule_log%s' % (id)
    Group(group_name).discard(message.reply_channel)
