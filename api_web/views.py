# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# from rest_framework.authentication import TokenAuthentication
# from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from django.http import JsonResponse

from django.db import transaction
from django.db import IntegrityError
from django.db.models import Q

import json

from assets.models import GameProject
from assets.models import Area
from myworkflows.models import GameServer
from myworkflows.models import VersionUpdate
from ops.models import GameServerOff, GameServerOffDetail, GameServerOffLog
from ops.models import InstallGameServer, InstallGameServerRecord
from ops.models import ModifyOpenSrvSchedule, ModifyOpenSrvScheduleDetail, ModifyOpenSrvScheduleLog
from ops.models import GameServerMergeSchedule
from ops.utils import game_install_notify
from ops.utils import ws_modify_srv_open_time_schedule_list

from cmdb.api_permissions import api_permission
from cmdb.logs import WebApiLog
from cmdb.logs import GameInstallLog
from cmdb.logs import GameSeverMergeAPILog
from cmdb.logs import RecvWebMaintenanceLog
from tasks import do_modify_srv_open_time
from tasks import do_game_server_merge
from tasks import do_game_install
from tasks import send_weixin_message
from tasks import version_update_task

from cmdb.settings import NEW_VERSION_UPDATE
from cmdb.settings import PRODUCTION_ENV
import datetime
import time
import uuid

log = WebApiLog()


@api_permission(api_perms=['api_add_installgameserver_obj'])
class InstallGameServerCreate(APIView):
    """新增开服计划
    返回json
    {"status": 1, "data": "json", "message": "ok"}
    """

    # parser_classes = (JSONParser, )

    def post(self, request, format=None):
        status = 0
        message = ''
        data = ''
        list_game_install_id = []
        pdata_list = request.data
        need_params = ('project area pf_id pf_name srv_num srv_name server_version open_time status unique_srv_id').split()

        try:
            with transaction.atomic():
                for pdata in pdata_list:
                    for param in need_params:
                        if pdata.get(param, None) is None:
                            raise Exception("%s: 参数没有" % (param))

                for pdata in pdata_list:
                    project_name_en = pdata.pop('project')
                    svr_id = pdata.get('srv_num')
                    project = GameProject.objects.get(project_name_en=project_name_en)
                    pdata['project'] = project
                    pdata['status'] = 0
                    installgameserver = InstallGameServer(**pdata)
                    installgameserver.save()
                    list_game_install_id.append(installgameserver.id)
                    # 记录操作日志
                    remark = '成功添加开服计划-' + installgameserver.project.project_name + '-' + installgameserver.srv_name + \
                             '-' + str(installgameserver.srv_num)
                    InstallGameServerRecord.objects.create(OperationUser=request.user, OperationType=1,
                                                           OperationResult=1,
                                                           InstallGameServer=installgameserver, remark=remark)
                else:
                    status = 1
                    # 发起装服异步任务
                    do_game_install.delay(list_game_install_id, request.user.id)

        except GameProject.DoesNotExist:
            message = '{}游戏在CMDB中没有找到'.format(project_name_en)
            # 记录操作日志
            InstallGameServerRecord.objects.create(OperationUser=request.user, OperationType=1,
                                                   OperationResult=0, remark=message)
        except IntegrityError as e:
            code, *_ = e.args
            if code == 1062:
                message = '区服id: {} 在cmdb中有重复'.format(svr_id)
            else:
                message = str(e)
            # 记录操作日志
            InstallGameServerRecord.objects.create(OperationUser=request.user, OperationType=1,
                                                   OperationResult=0, remark=message)
        except Exception as e:
            message = str(e)
            # 记录操作日志
            InstallGameServerRecord.objects.create(OperationUser=request.user, OperationType=1,
                                                   OperationResult=0, remark=message)

        return JsonResponse({"status": status, "message": message, "data": data})


@api_permission(api_perms=['api_delete_installgameserver_obj'])
class InstallGameServerDelete(APIView):
    """卸载服
    """

    def post(self, request, format=None):
        status = 0
        message = ''
        data = ''
        list_game_uninstall_id = []
        pdata_list = json.loads(request.data)

        need_params = ('project', 'area', 'srv_num')

        try:
            with transaction.atomic():
                for pdata in pdata_list:
                    for param in need_params:
                        if pdata.get(param, None) is None:
                            raise Exception("%s: 参数没有" % (param))
                for pdata in pdata_list:
                    server_not_found_string = json.dumps(pdata)
                    project_name_en = pdata.pop('project')
                    project = GameProject.objects.get(project_name_en=project_name_en)
                    pdata['project'] = project

                    obj = InstallGameServer.objects.get(**pdata)
                    remark = obj.project.project_name + '-' + obj.srv_name + '-' + str(obj.srv_num)
                    obj.status = 4
                    obj.save(update_fields=['status'])
                    list_game_uninstall_id.append(obj.id)
                    """记录操作日志"""
                    InstallGameServerRecord.objects.create(OperationUser=request.user, OperationType=3,
                                                           OperationResult=1, remark='成功添加卸载计划：' + remark)
                else:
                    status = 1
                    # 发起卸服异步任务
                    do_game_install.delay(list_game_uninstall_id, request.user.id)

        except InstallGameServer.DoesNotExist:
            message = '区服记录{}没有在CMDB中找到'.format(server_not_found_string)
            """记录操作日志"""
            InstallGameServerRecord.objects.create(OperationUser=request.user, OperationType=3,
                                                   OperationResult=0, remark=message)
        except GameProject.DoesNotExist:
            message = '{}游戏在CMDB中没有找到'.format(project_name_en)
            InstallGameServerRecord.objects.create(OperationUser=request.user, OperationType=3,
                                                   OperationResult=0, remark=message)
        except Exception as e:
            message = str(e)
            InstallGameServerRecord.objects.create(OperationUser=request.user, OperationType=3,
                                                   OperationResult=0, remark=message)
        return JsonResponse({"status": status, "message": message, "data": data})


@api_permission(api_perms=['api_edit_installgameserver_obj'])
class InstallGameServerModify(APIView):
    """修改开服计划
    """

    def post(self, request, format=None):
        status = 0
        message = ''
        data = ''
        pdata_list = request.data

        try:
            with transaction.atomic():
                # 能修改到的参数
                update_fields = ('open_time', 'qq_srv_id', 'srv_type', 'srv_farm_id', 'srv_farm_name', 'unique_srv_id')
                for pdata in pdata_list:
                    filter_server = pdata.get('filter_server', None)
                    new_data = pdata.get('new_data', None)
                    if filter_server is None:
                        raise Exception('filter_server参数没有')
                    if new_data is None:
                        raise Exception('new_data参数没有')

                    # 修改游戏英文名
                    project_name_en = filter_server.get('project', None)

                    if project_name_en is not None:
                        project = GameProject.objects.get(project_name_en=project_name_en)
                        filter_server['project'] = project

                    # 查找出要更新的单个区服
                    obj = InstallGameServer.objects.get(**filter_server)

                    # 设置要更新的属性
                    update_data = {}
                    for f in update_fields:
                        field_data = new_data.get(f, None)
                        if field_data is not None:
                            update_data[f] = field_data

                    # 开始更新属性
                    for attr, value in update_data.items():
                        pre_value = getattr(obj, attr)
                        setattr(obj, attr, value)
                        remark = '修改字段 ' + attr + '：' + str(pre_value) + '==>' + value
                        """记录操作日志"""
                        InstallGameServerRecord.objects.create(OperationUser=request.user, OperationType=2,
                                                               OperationResult=1, InstallGameServer=obj, remark=remark)
                    obj.save()
                else:
                    status = 1
                    message = len(pdata_list)
        except GameProject.DoesNotExist:
            message = '游戏{}在cmdb中没有找到'.format(project_name_en)
            """记录操作日志"""
            InstallGameServerRecord.objects.create(OperationUser=request.user, OperationType=2,
                                                   OperationResult=0, InstallGameServer=obj, remark=message)
        except InstallGameServer.DoesNotExist:
            filter_server.pop('project', None)
            message = '{}找不到区服'.format(json.dumps(filter_server))
            InstallGameServerRecord.objects.create(OperationUser=request.user, OperationType=2,
                                                   OperationResult=0, InstallGameServer=obj, remark=message)
        except Exception as e:
            message = str(e)
            InstallGameServerRecord.objects.create(OperationUser=request.user, OperationType=2,
                                                   OperationResult=0, InstallGameServer=obj, remark=message)
            raise (e)
        return JsonResponse({"status": status, "message": message, "data": data})


class InOrUninstallGameSrvCallback(APIView):
    """单个装服或者卸服回调接口
    回调数据
    {
        'id': 1,
        'type': 'install'   # or uninstall
        'success': True,
        'data': '成功'
    }
    返回给管理机的数据
    return JsonResponse({"resp": resp, "reason": reason})
    resp 1代表成功
    resp 0代表失败
    """

    def post(self, request, format=None):
        log = GameInstallLog()
        data = request.data

        resp = 0
        reason = 'ok'
        try:
            obj = InstallGameServer.objects.get(id=data.get('id'))
            success = data.get('success', False)
            type = data.get('type', False)
            if type == 'install':
                if success:
                    obj.status = 2
                else:
                    obj.status = 3
            if type == 'uninstall':
                if success:
                    obj.status = 5
                else:
                    obj.status = 6

            obj.save()
            resp = 1

            log.logger.info('回调成功,当前状态是:%s' % (obj.status, ))
        except InstallGameServer.DoesNotExist:
            reason = '装/卸服记录不存在'
            log.logger.error(reason)
        finally:
            game_install_notify()
            return JsonResponse({"resp": resp, "reason": reason})


@api_permission(api_perms=['api_add_gameserveroff_schedule'])
class GameServerOffCreate(APIView):
    """
    游戏区服下线新增计划API接口
    请求格式：
    {
        "project": "jyjh",
        "area": "越南",
        "srv_id": '["31210", "39102"]',    # web区服id
        "off_time": "1381419600",
        "web_callback_url": "https://xxxxxx/",
    }
    或
    {
        "project": "jyjh",
        "area": "越南",
        "srv_flag": '["cross_vng_6", "vng_1"]',    # cmdb区服id
        "off_time": "1381419600",
        "web_callback_url": "https://xxxxxx/",
    }
    返回格式：
    {
        "success": True, "msg": "xxxxxx"
    }
    """

    def post(self, request):
        success = True
        msg = 'ok'
        game_server_list = []
        need_param = (
            'project', 'area', 'off_time', 'web_callback_url'
        )
        myuuid = str(uuid.uuid1())
        try:
            raw_data = request.data.dict()
            project = raw_data.get('project', '')
            area = raw_data.get('area', '')
            srv_id = raw_data.get('srv_flag', '')
            if srv_id:
                srv_id = json.loads(srv_id)
            sid = raw_data.get('srv_id', '')
            if sid:
                sid = json.loads(sid)
            off_time = raw_data.get('off_time', '')
            web_callback_url = raw_data.get('web_callback_url', '')
            """检查必要参数"""
            for param in need_param:
                if param == '':
                    raise Exception('缺少参数：%s' % param)
            if sid == '' and srv_id == '':
                raise Exception('srv_id 和 srv_flag 至少一个不能为空')
            """检验参数是否合格"""
            project_obj = GameProject.objects.filter(Q(project_name=project) | Q(project_name_en=project))
            if project_obj:
                project_obj = project_obj[0]
            else:
                raise Exception('游戏项目%s不存在' % project)
            if srv_id:
                srv_id = list(set(srv_id))
                for x in srv_id:
                    game_server = GameServer.objects.filter(project=project_obj,
                                                            host__belongs_to_room__area__short_name=area, srv_id=x)
                    if not game_server:
                        raise Exception('区服%s-%s-%s不存在' % (project, area, x))
                    game_server_list.append(game_server[0])
            else:
                sid = list(set(sid))
                for s in sid:
                    game_server = GameServer.objects.filter(project=project_obj,
                                                            host__belongs_to_room__area__short_name=area,
                                                            sid=s)
                    if not game_server:
                        raise Exception('区服%s-%s-%s不存在' % (project, area, s))
                    game_server_list.append(game_server[0])
            """转换时间戳为时间字符串"""
            timeArray = time.localtime(int(off_time))
            off_time = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
            """
            创建下线计划，及下线区服明细，创建下线计划日志记录
            先判断状态为未执行的计划中，是否存在下架时间相同的计划，如有，则添加子任务到该计划中，若无，则创建新计划
            """
            game_server_off_list = GameServerOff.objects.filter(off_time=off_time, status=1)
            if game_server_off_list:
                game_server_off = game_server_off_list[0]
            else:
                game_server_off = GameServerOff.objects.create(off_time=off_time, web_callback_url=web_callback_url,
                                                               uuid=myuuid)
                GameServerOffLog.objects.create(game_server_off=game_server_off)

            for x in game_server_list:
                """如果相同任务存在相同区服，相同下线时间的明细，则不重复保存"""
                if GameServerOffDetail.objects.filter(game_server_off=game_server_off, game_server=x,
                                                      game_server_off__off_time=off_time):
                    pass
                else:
                    GameServerOffDetail.objects.create(game_server_off=game_server_off, game_server=x)

        except Exception as e:
            success = False
            msg = str(e)
        finally:
            return JsonResponse({'success': success, 'msg': msg})


@api_permission(api_perms=['api_delete_gameserveroff_schedule'])
class GameServerOffDelete(APIView):
    """
    游戏区服下线删除计划API接口
    请求格式：
    {
        "project": "jyjh",
        "area": "越南",
        "srv_id": '["31210", "39102"]',    # web区服id
        "off_time": "1381419600",
        "web_callback_url": "https://xxxxxx/",
    }
    或
    {
        "project": "jyjh",
        "area": "越南",
        "srv_flag": '["cross_vng_6", "vng_1"]',    # cmdb区服id
        "off_time": "1381419600",
        "web_callback_url": "https://xxxxxx/",
    }
    返回格式：
    {
        "success": True, "msg": "xxxxxx"
    }
    """

    def post(self, request):
        success = True
        msg = 'ok'
        need_param = (
            'project', 'area', 'off_time', 'web_callback_url'
        )
        try:
            raw_data = request.data.dict()
            project = raw_data.get('project', '')
            area = raw_data.get('area', '')
            srv_id = raw_data.get('srv_flag', '')
            if srv_id:
                srv_id = json.loads(srv_id)
            sid = raw_data.get('srv_id', '')
            if sid:
                sid = json.loads(sid)
            off_time = raw_data.get('off_time', '')
            web_callback_url = raw_data.get('web_callback_url', '')
            """检查必要参数"""
            for param in need_param:
                if param == '':
                    raise Exception('缺少参数：%s' % param)

            """检验参数是否合格"""
            project_obj = GameProject.objects.filter(Q(project_name=project) | Q(project_name_en=project))
            if project_obj:
                project_obj = project_obj[0]
            else:
                raise Exception('游戏项目%s不存在' % project)
            if srv_id:
                """格式化srv_id"""
                srv_id = list(set(srv_id))
                srv_id = [str(x) for x in srv_id]
                srv_id.sort()
            else:
                """格式化sid"""
                sid = list(set(sid))
                sid = [str(x) for x in sid]
                sid.sort()
            """转换时间戳为时间字符串"""
            timeArray = time.localtime(int(off_time))
            off_time = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
            """根据参数匹配下线计划，若匹配成功，则删除"""
            game_server_off = GameServerOff.objects.filter(off_time=off_time)
            if game_server_off:
                for g in game_server_off:
                    if sid:
                        detail = g.gameserveroffdetail_set.filter(game_server__sid__in=sid,
                                                                  game_server__project=project_obj)
                    else:
                        detail = g.gameserveroffdetail_set.filter(game_server__srv_id__in=srv_id,
                                                                  game_server__project=project_obj)
                    if detail:
                        detail.delete()
                    """如果所有关联的区服子任务都已删除，则删除下架计划"""
                    if not g.gameserveroffdetail_set.all():
                        g.delete()

        except Exception as e:
            success = False
            msg = str(e)
        finally:
            return JsonResponse({'success': success, 'msg': msg})


@api_permission(api_perms=['api_create_modify_srv_opentime_schedule'])
class ModifySrvOpenTimeScheduleCreate(APIView):
    """
    生成修改开服时间计划的API，cmdb接收到请求后，保存本地记录，并转发至运维管理机
    请求格式：
    {
        'project': 'jyjh',
        "area": "越南",
        "srv_id": "31210",    # web区服id
        "open_time": "1581419600",
    }
    返回格式：
    {
        'success': True,
        'msg': 'ok'
    }
    """

    def post(self, request):
        success = True
        msg = 'cmdb接收成功'
        need_param = (
            'project', 'area', 'open_time', 'srv_id'
        )
        myuuid = str(uuid.uuid1())
        try:
            raw_data = request.data.dict()
            project = raw_data.get('project', '')
            area = raw_data.get('area', '')
            sid = raw_data.get('srv_id', '')
            open_time = raw_data.get('open_time', '')
            """检查必要参数"""
            for param in need_param:
                if param == '':
                    raise Exception('缺少参数：%s' % param)
            """检验参数是否合格"""
            project_obj = GameProject.objects.filter(project_name_en=project)
            if not project_obj:
                raise Exception('游戏项目 %s 不存在' % project)
            area_obj = Area.objects.filter(short_name=area)
            if not area_obj:
                raise Exception('地区 %s 不存在' % area)
            sid_list = []
            sid_list.append(sid)
            game_server_list = []
            for sid in sid_list:
                game_server = GameServer.objects.select_related('host').filter(project=project_obj,
                                                                               host__belongs_to_room__area=area_obj,
                                                                               sid=sid)
                if not game_server:
                    raise Exception('区服 %s-%s-%s，不存在' % project, area, sid)
                else:
                    game_server_list.append(game_server[0])
            """转换时间戳为时间字符串"""
            timeArray = time.localtime(int(open_time))
            open_time = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
            """创建修改开服时间计划及其明细，以及日志"""
            schedule = ModifyOpenSrvSchedule.objects.create(open_time=open_time, uuid=myuuid)
            for game_server in game_server_list:
                ModifyOpenSrvScheduleDetail.objects.create(modify_schedule=schedule, game_server=game_server)
            ModifyOpenSrvScheduleLog.objects.create(modify_schedule=schedule)
            ws_modify_srv_open_time_schedule_list()
            """发送请求到相关运维管理机"""
            do_modify_srv_open_time.delay(schedule.uuid)

        except Exception as e:
            success = False
            msg = str(e)
        finally:
            return JsonResponse({'success': success, 'msg': msg})


@api_permission(api_perms=['api_create_game_srv_merge_schedule'])
class GameServerMergeCreate(APIView):
    """
    合服计划api
    输入json：
    {
        'data': '[
            {"main_srv": "1", "slave_srv": "3,4,5", "group_id": 1, "merge_time": "1234567890", "project": "ssss"},
            {"main_srv": "2", "slave_srv": "6,7,8", "group_id": 2, "merge_time": "1234567123", "project": "ssss"},
            ...
        ]',
    }
    输出：
    {
        'success': True,
        'msg': 'cmdb接收成功'
    }
    """

    def post(self, request):
        log = GameSeverMergeAPILog()
        success = True
        msg = 'cmdb接收成功'
        need_param = ('data',)
        try:
            log.logger.info(json.dumps(request.data.dict()))
            myuuid = str(uuid.uuid1())
            raw_data = request.data.dict()
            if isinstance(raw_data, str):
                raw_data = json.loads(raw_data)
                if isinstance(raw_data, str):
                    raw_data = json.loads(raw_data)
            data = raw_data.get('data', '')
            # 检查必要参数
            for param in need_param:
                if param == '':
                    raise Exception('缺少参数：%s' % param)
            # 检查参数是否符合要求
            for merge_schedule in json.loads(data):
                need_param = ('main_srv', 'slave_srv', 'group_id', 'merge_time')
                main_srv = merge_schedule.get('main_srv', '')
                slave_srv = merge_schedule.get('slave_srv', '')
                group_id = merge_schedule.get('group_id', '')
                project_name_en = merge_schedule.get('project', '')
                merge_time = merge_schedule.get('merge_time', '')
                # 转换时间戳为时间字符串
                time_array = time.localtime(int(merge_time))
                merge_time = time.strftime("%Y-%m-%d %H:%M:%S", time_array)

                for param in need_param:
                    if param == '':
                        raise Exception('{} 缺少参数：{}'.format(merge_schedule, param))

                game_server = GameServer.objects.filter(sid=main_srv)
                if project_name_en:
                    game_server = GameServer.objects.filter(sid=main_srv, project__project_name_en=project_name_en)
                project = None
                room = None
                if game_server:
                    project = game_server[0].project
                    if game_server[0].host:
                        room = game_server[0].host.belongs_to_room
                # 保存合服计划
                GameServerMergeSchedule.objects.create(uuid=myuuid, project=project, main_srv=main_srv, room=room,
                                                       slave_srv=slave_srv, group_id=group_id, merge_time=merge_time)
            # 发送到运维管理机
            do_game_server_merge.delay(data, myuuid)

        except Exception as e:
            success = False
            msg = str(e)
            log.logger.error(msg)
        finally:
            log.logger.info(json.dumps({'success': success, 'msg': msg}))
            return JsonResponse({'success': success, 'msg': msg})


@api_permission(api_perms=['api_web_maintenance_info'])
class RecvWebMaintenanceInfo(APIView):
    """
    web挂维护后同步给cmdb的API接口
    post参数
    {
        'project': 'jysybt',
        'area': 'cn',
        'maintenance_type': 3,          #  1：合服  2：迁服  3：版本更新  -1：其他
        'srv_id_list': '15000001,15000002,16000001,16000001,500001'
    }
    return
    {
        'success': True,
        'msg': 'cmdb接收成功'
    }
    """
    def post(self, request):
        success = True
        msg = 'cmdb接收成功'
        need_param = ('project', 'area', 'maintenance_type')
        log = RecvWebMaintenanceLog()
        try:
            with transaction.atomic():
                raw_data = request.data.dict()
                log.logger.info('收到挂维护信息:  {}'.format(json.dumps(raw_data)))
                project_name_en = raw_data.get('project', '')
                area_en = raw_data.get('area', '')
                maintenance_type = raw_data.get('maintenance_type', '')
                # 检查必要参数
                for param in need_param:
                    if param == '' or param is None:
                        raise Exception('缺少参数：%s' % param)

                project_obj = GameProject.objects.get(project_name_en=project_name_en)
                area_obj = Area.objects.get(short_name=area_en)

                # 发送企业微信已收到挂维护通知
                touser = '|'.join([u.first_name for u in project_obj.get_relate_role_user()])
                if str(maintenance_type) == '1':
                    maintenance_type_text = '合服'
                elif str(maintenance_type) == '2':
                    maintenance_type_text = '迁服'
                elif str(maintenance_type) == '3':
                    maintenance_type_text = '版本更新'
                else:
                    maintenance_type_text = '其他'
                content = '项目：{}，地区：{}，web已挂维护，维护类型：{}'.format(project_obj.project_name, area_obj.chinese_name,
                                                               maintenance_type_text)
                send_weixin_message.delay(touser=touser, content=content)

                # 维护类型是版本更新
                if str(maintenance_type) == '3':
                    # 更新维护状态
                    version_update_obj = VersionUpdate.objects.filter(project=project_obj, area=area_obj, status=2,
                                                                      new_edition=1)
                    version_update_obj.update(**{'is_maintenance': True})

                    # 查找是否有版本更新单需要自动执行
                    if NEW_VERSION_UPDATE:
                        for version_update in version_update_obj:
                            if version_update.workflows.last().state_value == '拒绝':
                                # 排除已经审批拒绝或被取消的版本更新单
                                log.logger.info('版本更新单，#{}，对应工单已被拒绝或取消'.format(version_update.title))
                                continue
                            if not version_update.workflows.last().state.name == '完成':
                                log.logger.info('版本更新单，#{}，对应工单还没有审批完成'.format(version_update.title))
                                continue
                            if not version_update.start_time <= datetime.datetime.now() <= version_update.end_time:
                                log.logger.info('版本更新单，#{}，不再执行时间范围内'.format(version_update.title))
                                continue
                            if not version_update.project.auto_version_update:
                                log.logger.info('项目：{}，没有设置自动更新'.format(project_obj.project_name))
                                continue
                            if not version_update.is_maintenance:
                                log.logger.info(
                                    '项目：{}，地区：{}，还没有挂版本更新维护'.format(project_obj.project_name, area_obj.chinese_name))
                                continue
                            if not version_update.new_edition:
                                log.logger.info('版本更新单，#{}，不是使用新版流程'.format(version_update.title))
                                continue
                            task_result = version_update_task(version_update.id, 'all')
                            log.logger.info('版本更新任务执行结果: {}'.format(json.dumps(task_result)))

                log.logger.info('项目：{}，地区：{}，接收挂维护信息结果：{}'.format(project_obj.project_name, area_obj.chinese_name, msg))

        except GameProject.DoesNotExist:
            success = False
            msg = '项目不存在'
            log.logger.error('接收挂维护信息结果：{}'.format(msg))
        except Area.DoesNotExist:
            success = False
            msg = '地区不存在'
            log.logger.error('接收挂维护信息结果：{}'.format(msg))
        except Exception as e:
            success = False
            msg = str(e)
            log.logger.error('接收挂维护信息结果：{}'.format(msg))
        finally:
            return JsonResponse({'success': success, 'msg': msg})
