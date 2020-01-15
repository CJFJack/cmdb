# -*- encoding: utf-8 -*-


from channels import Channel
from ops.models import GameServerOff
from ops.models import ModifyOpenSrvSchedule
from django.db import transaction
import hashlib
import datetime


def game_install_notify():
    """以websocket的方式通知浏览器刷新
    """

    msg = {"message": "update_table"}
    Channel("game_install_receive").send(msg)


def md5_convert(string):
    """
    计算字符串的md5值
    """
    m = hashlib.md5()
    m.update(string.encode())
    return m.hexdigest()


def write_game_server_off_log(level, content, obj):
    """更新区服下线任务日志字段内容"""
    try:
        with transaction.atomic():
            log_obj = obj.gameserverofflog
            now = str(datetime.datetime.now())[:23]
            complete_log = now + ' - ' + obj.uuid + ' - ' + level + ' - ' + content + '\n'
            log_obj.log += complete_log
            log_obj.save()
            """刷新区服下线日志"""
            ws_update_game_server_off_log(obj.id)
    except:
        pass


def ws_update_game_server_off_log(id):
    """刷新区服下线日志"""
    game_server_off = GameServerOff.objects.get(pk=id)
    log = game_server_off.gameserverofflog.log
    msg = {"message": 'update_log', 'game_server_off_id': id, 'log': log}
    Channel('update_game_server_off_log').send(msg)


def ws_update_game_server_off_list():
    """刷新区服下线列表"""
    msg = {"message": 'update_table'}
    Channel('update_game_server_off_list').send(msg)


def ws_update_game_server_off_detail(id):
    """更新区服下线详情"""
    msg = {'message': 'update_detail', 'obj_id': id}
    Channel('update_game_server_off_detail').send(msg)


def write_modify_srv_open_time_schedule_log(level, content, obj):
    """更新修改开服时间计划日志内容"""
    try:
        with transaction.atomic():
            log_obj = obj.modifyopensrvschedulelog
            now = str(datetime.datetime.now())[:23]
            complete_log = now + ' - ' + obj.uuid + ' - ' + level + ' - ' + content + '\n'
            log_obj.log += complete_log
            log_obj.save()
            """刷新区服下线日志"""
            ws_update_modify_srv_open_time_schedule_log(obj.id)
    except:
        pass


def ws_update_modify_srv_open_time_schedule_log(id):
    """刷新修改开服时间计划日志"""
    modify_schedule = ModifyOpenSrvSchedule.objects.get(pk=id)
    log = modify_schedule.modifyopensrvschedulelog.log
    msg = {"message": 'update_log', 'modify_schedule_id': id, 'log': log}
    Channel('update_modify_srv_open_time_schedule_log').send(msg)


def ws_modify_srv_open_time_schedule_list():
    """刷新修改开服时间计划列表"""
    msg = {"message": 'update_table'}
    Channel('update_modify_srv_open_time_schedule_list').send(msg)


def ws_update_modify_srv_open_time_schedule_detail(id):
    """更新修改开服时间计划详情"""
    msg = {'message': 'update_detail', 'obj_id': id}
    Channel('update_modify_srv_open_time_schedule_detail').send(msg)
