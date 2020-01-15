# -*- encoding: utf-8 -*-
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from assets.models import *
from assets.exceptions import *
from api.serializers import *
from api.exceptions import *

from django.http import JsonResponse
from django.http import HttpResponse
from django.core.exceptions import FieldError, MultipleObjectsReturned
from django.db import IntegrityError
from django.db import transaction
from django.db.models import Q
from django.contrib.auth.models import User

from users.models import Profile, UserProfileHost, OrganizationMptt

from myworkflows.models import GameServer
from myworkflows.models import GameServerType
from myworkflows.models import ClientHotUpdate
from myworkflows.models import ClientHotUpdateRsyncTask
from myworkflows.models import ServerHotUpdate
from myworkflows.models import ServerHotUpdateRsyncTask
from myworkflows.models import HostCompressionApply
from myworkflows.models import HostMigrateSrvDetail
from myworkflows.models import SpecialUserParamConfig
from myworkflows.models import GameServerActionRecord
from myworkflows.models import VersionUpdate
from myworkflows.utils import unlock_hot_update
from myworkflows.utils import get_next_hot_update
from myworkflows.utils import ws_notify
from myworkflows.utils import ws_hot_server_notify
from myworkflows.utils import get_hot_update_all_related_user
from myworkflows.utils import write_host_compression_log
from myworkflows.utils import ws_update_host_compression_detail
from myworkflows.utils import ws_update_host_compression_list
from myworkflows.utils import ws_update_host_compression_log
from myworkflows.utils import ws_update_game_server_action
from myworkflows.utils import ws_update_game_server_action_record
from myworkflows.myredis import *
from assets.utils import get_ip
from assets.utils import ws_update_host_initialize_list
from assets.utils import write_host_initialize_log
from assets.utils import saltstack_test_ping
from ops.models import GameServerOff
from ops.models import ModifyOpenSrvSchedule
from ops.utils import write_game_server_off_log
from ops.utils import ws_update_game_server_off_log
from ops.utils import ws_update_game_server_off_detail
from ops.utils import ws_update_game_server_off_list
from ops.utils import write_modify_srv_open_time_schedule_log
from ops.utils import ws_update_modify_srv_open_time_schedule_detail
from ops.utils import ws_modify_srv_open_time_schedule_list
from ops.utils import ws_update_modify_srv_open_time_schedule_log

from api.utils import make_host_recover_email_content
from api.utils import make_game_server_off_email_content
from api.utils import make_modsrv_opentime_email_content
from api.utils import make_host_compression_result_email_content
from api.utils import send_robot_message

from tasks import do_hot_update
from tasks import do_hot_client
from tasks import do_hot_server
from tasks import send_qq
from tasks import send_mail
from tasks import send_weixin_message
from tasks import saltstack_test_ping_tasks
from test_tasks import do_test_hot_client
from test_tasks import do_test_hot_server

from cmdb.logs import HotUpdateLog
from cmdb.qq_notify import hot_update_qq_notify
from cmdb.mail_notify import hot_update_mail_notify
from cmdb.mail_notify import rsync_failed_mail_notify
from cmdb.wx_notify import hot_update_wx_notify
from cmdb.settings import PRODUCTION_ENV

import traceback
import time
import json
import datetime
import uuid


# hot_update_log = HotUpdateLog()


class HostDetail(APIView):
    """获取服务器主机列表

    根据post过来的参数获取列表
    keywords用来筛选主机，可选,格式:
    {
        'telecom_ip': '192.168.56.101',
        'system': 0,
        ...
    }
    """

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):

        data = request.data

        # 字段过滤条件查询
        keywords = data.get('keywords', None)

        try:
            if keywords:
                h = Host.objects.filter(**keywords)
            else:
                h = Host.objects.all()

            data = [x.show_all(project_name=False) for x in h]

            if data:
                success = 1
            else:
                success = 13
        except FieldError:
            data = 'keywords的参数错误'
            success = 13
        except Exception:
            data = '内部错误'
            success = 13

        return JsonResponse({"reason": data, "resp": success})


class HostCreate(APIView):
    """增加主机

    根据post过来的参数增加主机
    如果增加成功，返回主机的相应信息
    """

    authentication_classes = (TokenAuthentication,)

    def post(self, request, format=None):

        allow_nonfield = ['internal_ip', 'telecom_ip', 'unicom_ip', 'belongs_to_host', 'sshport', 'sshuser']

        all_fields_name = [x.name for x in Host._meta.fields]
        all_fields_name.remove('id')

        valid_fiels = list(set(all_fields_name) - set(allow_nonfield))
        valid_fiels.append('area')

        raw_data = request.data
        source_ip = get_ip(request)

        try:
            for f in valid_fiels:
                v = raw_data.get(f, None)
                if v is None or v == '':
                    raise HostFieldEmpty('%s不能为空' % (f))

            belongs_to_game_project = GameProject.objects.get(
                project_name_en=raw_data.get('belongs_to_game_project'))

            raw_data['belongs_to_game_project'] = belongs_to_game_project

            area = raw_data.pop('area')
            try:
                belongs_to_room = Room.objects.get(room_name=raw_data.get('belongs_to_room'),
                                                   area__chinese_name=area)
                area_obj = Area.objects.get(chinese_name=area)
            except:
                belongs_to_room = Room.objects.get(room_name_en=raw_data.get('belongs_to_room'),
                                                   area__short_name=area)
                area_obj = Area.objects.get(short_name=area)
            raw_data['belongs_to_room'] = belongs_to_room

            try:
                belongs_to_business = Business.objects.get(business_name=raw_data.get('belongs_to_business'))
            except Business.DoesNotExist:
                belongs_to_business = Business.objects.create(business_name=raw_data.get('belongs_to_business'))
            raw_data['belongs_to_business'] = belongs_to_business

            # 至少需要一个IP
            internal_ip_value = raw_data.get('internal_ip', None)
            telecom_ip_value = raw_data.get('telecom_ip', None)
            unicom_ip_vlaue = raw_data.get('unicom_ip', None)

            if not (internal_ip_value or telecom_ip_value or unicom_ip_vlaue):
                raise MoreThanOneIpIsRequired('至少需要一个ip')

            opsmanager = raw_data.pop('opsmanager', None)
            if opsmanager:
                try:
                    opsmanager_project = opsmanager.split('-')[0]
                    opsmanager_room_name = opsmanager.split('-')[1]
                except Exception:
                    raise Exception('参数%s格式不正确' % opsmanager)
                project = GameProject.objects.filter(Q(project_name=opsmanager_project) |
                                                     Q(project_name_en=opsmanager_project))
                room = Room.objects.filter((Q(room_name=opsmanager_room_name) |
                                            Q(room_name_en=opsmanager_room_name)), area=area_obj)
                if project and room:
                    project = project[0]
                    room = room[0]
                    opsmanager_obj = OpsManager.objects.get(project=project, room=room)
                    raw_data['opsmanager'] = opsmanager_obj
                else:
                    raise Exception('参数opsmanager中的项目或者机房不存在')

            """
            根据机房项目/机房/内网IP判断主机是否已经存在，
            如果存在，则更新字段信息，
            否则新建主机，
            """
            h = Host.objects.filter(belongs_to_game_project=belongs_to_game_project,
                                    belongs_to_room=belongs_to_room, internal_ip=internal_ip_value)
            if h:
                # 记录所有字段之前值
                old_host = h[0].show_all()
                # 更新object
                h.update(**raw_data)
                h = h[0]
                # 记录所有字段之后值
                new_host = h.show_all()
                # 找出差异字段，并记录操作日志
                alter_fields_list = []
                for k, v in new_host.items():
                    if v != old_host[k]:
                        alter_fields_list.append(k)
                for x in alter_fields_list:
                    alter_field = Host._meta.get_field(x).help_text
                    HostHistoryRecord.objects.create(host=h,
                                                     operation_user=request.user, type=2,
                                                     alter_field=alter_field, source_ip=source_ip,
                                                     old_content=old_host[x], new_content=new_host[x])

            else:
                h = Host.objects.create(**raw_data)
                """记录新增主机记录"""
                HostHistoryRecord.objects.create(host=h, operation_user=request.user, type=1, source_ip=source_ip)

            data = h.show_all(project_name=False)
            success = 1
        except GameProject.DoesNotExist:
            data = '项目英文名不存在'
            success = 13
        except Room.DoesNotExist:
            data = '机房不存在，请检查参数belongs_to_room和area是否正确，必须同时为中文或英文'
            success = 13
        except OpsManager.DoesNotExist:
            data = '运维管理机不存在'
            success = 13
        except IntegrityError as e:
            data = str(e)
            success = 13
        except HostFieldEmpty as e:
            data = str(e)
            success = 13
        except MoreThanOneIpIsRequired as e:
            data = str(e)
            success = 13
        except Exception as e:
            data = '内部错误' + str(e)
            success = 13

        return JsonResponse({"reason": data, "resp": success})


class HostModify(APIView):
    """修改主机

    接收两个重要的参数:
    1 old_host_info 这个参数用来查找出cmdb的唯一host记录
    2 new_host_info 这个参数用来更新查找出来的唯一host记录

    更新成功以后返回新的host信息
    """

    authentication_classes = (TokenAuthentication,)

    def _telcom_ip_match(self, old_host_info):
        '''根据电信ip来获取唯一记录'''
        telecom_ip = old_host_info.get('telecom_ip', None)

        if telecom_ip:
            host = Host.objects.get(telecom_ip=telecom_ip)
            return host
        else:
            return None

    def _unicom_ip_match(self, old_host_info):
        '''根据联通ip获取唯一记录'''
        unicom_ip = old_host_info.get('unicom_ip', None)

        if unicom_ip:
            host = Host.objects.get(unicom_ip=unicom_ip)
            return host
        else:
            return None

    def _match_project_room_internal_ip(self, old_host_info):
        '''根据游戏项目，机房，内网ip三个联合字段获取唯一记录'''

        belongs_to_game_project = old_host_info.get('belongs_to_game_project', None)
        belongs_to_room = old_host_info.get('belongs_to_room', None)
        if belongs_to_room:
            area = old_host_info.pop('area', None)
            if area is None:
                raise Exception('缺少参数：area')
        internal_ip = old_host_info.get('internal_ip', None)

        if belongs_to_game_project and belongs_to_room and internal_ip:
            belongs_to_game_project = GameProject.objects.get(project_name_en=belongs_to_game_project)
            old_host_info['belongs_to_game_project'] = belongs_to_game_project

            try:
                belongs_to_room = Room.objects.get(room_name=belongs_to_room, area__chinese_name=area)
            except:
                belongs_to_room = Room.objects.get(room_name_en=belongs_to_room, area__short_name=area)
            old_host_info['belongs_to_room'] = belongs_to_room

            old_host_info.pop('belongs_to_business', None)

            host = Host.objects.get(**old_host_info)
            return host
        else:
            return None

    def _host_identifier_match(self, old_host_info):
        '''根据主机标识获取唯一记录'''
        host_identifier = old_host_info.get('host_identifier', None)

        if host_identifier:
            host = Host.objects.get(host_identifier=host_identifier)
            return host
        else:
            return None

    def match_host(self, old_host_info):
        '''根据提交的host_info来匹配出cmdb唯一的host记录'''

        host = self._telcom_ip_match(old_host_info)

        if host:
            return host
        else:
            host = self._unicom_ip_match(old_host_info)
            if host:
                return host
            else:
                host = self._match_project_room_internal_ip(old_host_info)
                if host:
                    return host
                else:
                    host = self._host_identifier_match(old_host_info)
                    if host:
                        return host
                    else:
                        return None

    def post(self, request, format=None):

        raw_data = request.data

        old_host_info = raw_data.get('old_host_info', None)
        new_host_info = raw_data.get('new_host_info', None)
        source_ip = get_ip(request)

        # 检测这两个参数必须存在
        if not old_host_info:
            data = '请post old_host_info参数'
            success = 13
            return JsonResponse({"reason": data, "resp": success})

        if not new_host_info:
            data = '请post new_host_info参数'
            success = 13
            return JsonResponse({"reason": data, "resp": success})

        try:
            host = self.match_host(old_host_info)

            if host:
                # 根据查找出来的host的id来update
                belongs_to_game_project = new_host_info.get('belongs_to_game_project', None)
                if belongs_to_game_project:
                    belongs_to_game_project = GameProject.objects.get(project_name_en=belongs_to_game_project)
                    new_host_info['belongs_to_game_project'] = belongs_to_game_project

                belongs_to_room = new_host_info.get('belongs_to_room', None)
                if belongs_to_room:
                    area = new_host_info.pop('area', None)
                    if area is None:
                        raise Exception('缺少参数：area')
                    try:
                        belongs_to_room = Room.objects.get(room_name=belongs_to_room, area__chinese_name=area)
                    except:
                        belongs_to_room = Room.objects.get(room_name_en=belongs_to_room, area__short_name=area)
                    new_host_info['belongs_to_room'] = belongs_to_room

                belongs_to_business = new_host_info.get('belongs_to_business', None)
                if belongs_to_business:
                    belongs_to_business = Business.objects.get(business_name=belongs_to_business)
                    new_host_info['belongs_to_business'] = belongs_to_business

                opsmanager = new_host_info.get('opsmanager', None)
                if opsmanager:
                    opsmanager_project = opsmanager.split('-')[0]
                    opsmanager_room = opsmanager.split('-')[1]
                    area = new_host_info.pop('area', None)
                    if area is None:
                        raise Exception('缺少参数：area')
                    try:
                        project = GameProject.objects.get(project_name=opsmanager_project)
                    except:
                        project = GameProject.objects.get(project_name_en=opsmanager_project)
                    try:
                        room = Room.objects.get(room_name=opsmanager_room, area__chinese_name=area)
                    except:
                        room = Room.objects.get(room_name_en=opsmanager_room, area__short_name=area)
                    opsmanager_obj = OpsManager.objects.get(project=project, room=room)
                    new_host_info['opsmanager'] = opsmanager_obj

                # 修改为已经归还状态
                new_status = new_host_info.get('status', None)

                old_status = host.status

                # 归属的游戏项目英文名
                project_name_en = host.belongs_to_game_project.project_name_en

                # 后缀项目英文名加上bak jyjhbak
                # suffix = '.' + project_name_en + 'bak'

                """2019.2修改，机器状态修改为已归还后IP不增加后缀"""
                if new_status is not None:
                    if str(old_status) != str(new_status):
                        if str(new_status) == '4':
                            # if new_host_info.get('internal_ip', None):
                            #     new_host_info['internal_ip'] += suffix
                            # else:
                            #     if host.internal_ip:
                            #         new_host_info['internal_ip'] = host.internal_ip + suffix
                            # if new_host_info.get('telecom_ip', None):
                            #     new_host_info['telecom_ip'] += suffix
                            # else:
                            #     if host.telecom_ip:
                            #         new_host_info['telecom_ip'] = host.telecom_ip + suffix
                            # if new_host_info.get('unicom_ip', None):
                            #     new_host_info['unicom_ip'] += suffix
                            # else:
                            #     if host.unicom_ip:
                            #         new_host_info['unicom_ip'] = host.unicom_ip + suffix

                            # 归还的机器修改服务器权限为过期状态
                            UserProfileHost.objects.filter(host=host).update(**{'is_valid': 0})

                """记录所有字段之前值"""
                old_host = Host.objects.filter(id=host.id)[0].show_all()

                """更新object"""
                Host.objects.filter(id=host.id).update(**new_host_info)
                """记录所有字段之后值"""
                new_host = Host.objects.filter(id=host.id)[0].show_all()

                """找出差异字段，并记录操作日志"""
                alter_fields_list = []
                for k, v in new_host.items():
                    if v != old_host[k]:
                        alter_fields_list.append(k)
                for x in alter_fields_list:
                    alter_field = Host._meta.get_field(x).help_text
                    HostHistoryRecord.objects.create(host=Host.objects.filter(id=host.id)[0],
                                                     operation_user=request.user, type=2,
                                                     alter_field=alter_field, source_ip=source_ip,
                                                     old_content=old_host[x], new_content=new_host[x])

                data = Host.objects.get(id=host.id).show_all(project_name=False)
                success = 1
            else:
                data = '记录没有找到'
                success = 13
        except GameProject.DoesNotExist:
            data = '游戏项目不存在'
            success = 13
        except Room.DoesNotExist:
            data = '机房不存在'
            success = 13
        except OpsManager.DoesNotExist:
            data = '运维管理机不存在'
            success = 13
        except Business.DoesNotExist:
            data = '业务类型不存在'
            success = 13
        except IntegrityError as e:
            data = str(e)
            success = 13
        except MultipleObjectsReturned:
            data = '记录不唯一'
            success = 13
        except Host.DoesNotExist:
            data = '记录没有找到'
            success = 13
        except Exception as e:
            data = str(e)
            success = 13
            traceback.print_tb(e.__traceback__)
        return JsonResponse({"reason": data, "resp": success})


class LockOpsManager(APIView):
    """给运维管理机上锁
    """
    authentication_classes = (TokenAuthentication,)

    def get(self, request, format=None):
        reason = "ok"
        raw_data = request.query_params

        try:
            with transaction.atomic():
                project = raw_data.get('project', None)
                area = raw_data.get('area', None)
                status = raw_data.get('status', None)
                end_time = raw_data.get('end_time', None)
                source_ip = get_ip(request)

                if not end_time:
                    end_time = None
                else:
                    st = time.localtime(int(raw_data.get('end_time')))
                    end_time = time.strftime('%Y-%m-%d %H:%M', st)

                if status is None:
                    raise StatusError('状态不能为空')

                project = GameProject.objects.get(project_name_en=project)

                list_ops_manager = OpsManager.objects.filter(project=project, room__area__chinese_name=area)

                if not list_ops_manager:
                    raise OpsManager.DoesNotExist
                else:
                    if list_ops_manager.count() > 1:
                        ops_manager = list_ops_manager.filter(url__icontains=source_ip)
                        if ops_manager:
                            list_ops_manager = ops_manager
                    for x in list_ops_manager:
                        if x.status == '0' and str(status) in OpsManager.OPS_MANAGER_CAN_CHANGE_STATUS:
                            x.status = status
                            x.end_time = end_time
                            x.save()
                        else:
                            raise StatusError('当前运维管理机状态:%s' % (x.get_status_display()))
                    resp = 1

        except GameProject.DoesNotExist:
            resp = 12
            reason = '游戏项目英文名不存在'
        except OpsManager.DoesNotExist:
            resp = 20
            reason = '没有匹配到运维管理机'
        except StatusError as e:
            resp = 21
            reason = str(e)
        except Exception as e:
            reason = str(e)
            resp = 11
        return JsonResponse({"resp": resp, "reason": reason})


class UnLockOpsManager(APIView):
    """设置运维管理机状态
    """
    authentication_classes = (TokenAuthentication,)

    def get(self, request, format=None):
        reason = "ok"
        raw_data = request.query_params

        try:
            with transaction.atomic():
                project = raw_data.get('project', None)
                area = raw_data.get('area', None)
                status = raw_data.get('status', None)
                source_ip = get_ip(request)

                if status is None:
                    raise StatusError('要更新的状态不能为空')

                project = GameProject.objects.get(project_name_en=project)

                list_ops_manager = OpsManager.objects.filter(project=project, room__area__chinese_name=area)

                if not list_ops_manager:
                    raise OpsManager.DoesNotExist
                else:
                    if list_ops_manager.count() > 1:
                        ops_manager = list_ops_manager.filter(url__icontains=source_ip)
                        if ops_manager:
                            list_ops_manager = ops_manager
                    for x in list_ops_manager:
                        if x.status in OpsManager.OPS_MANAGER_CAN_CHANGE_STATUS and x.status == status:
                            # x.status = status
                            x.status = '0'
                            x.end_time = None
                            x.save()
                        else:
                            raise StatusError('当前运维管理机状态:%s' % (x.get_status_display()))
                    resp = 1

        except GameProject.DoesNotExist:
            resp = 12
            reason = '游戏项目英文名不存在'
        except OpsManager.DoesNotExist:
            resp = 20
            reason = '没有匹配到运维管理机'
        except StatusError as e:
            resp = 21
            reason = str(e)
        except Exception as e:
            reason = str(e)
            resp = 11
        else:
            msg, next_hot_update = get_next_hot_update(project, area)
            if next_hot_update:
                if next_hot_update.status == '4':
                    do_hot_update(next_hot_update)
        return JsonResponse({"resp": resp, "reason": reason})


class GameServerList(APIView):
    """获取区服列表API文档
    """

    def get(self, request, format=None):
        reason = "ok"
        count = 0
        resp = 1
        raw_data = request.query_params

        try:
            filter_data = {'srv_status': 0, 'merge_id': None}
            for param, value in raw_data.items():
                if param == 'project':
                    project = GameProject.objects.get(project_name_en=value)
                    filter_data[param] = project
                elif param == 'area_name':
                    filter_data[param] = value
            list_game_server = GameServer.objects.filter(**filter_data)
            # 转化为srv_id
            reason = [x.srv_id for x in list_game_server]
            count = len(reason)
        except GameProject.DoesNotExist:
            reason = '项目不存在'
            resp = 2
        except Exception as e:
            reason = str(e)
            resp = 3
        return JsonResponse({"resp": resp, "reason": reason, "count": count})


class NewSrvCallBack(APIView):
    """新建游戏服
    """

    authentication_classes = (TokenAuthentication,)

    def get(self, request, format=None):
        reason = "ok"
        count = 0
        source_ip = get_ip(request)
        raw_data = request.query_params
        need_params = (
            'project_type', 'game', 'game_type', 'pf_name', 'room',
            'srv_id', 'srv_name', 'ip', 'client_version', 'server_version',
            'cdn_root_url', 'open_time', 'area_name', 'cdn_dir', 'host'
        )
        try:
            # 构造表字段参数，并且判断参数是否满足要求
            add_data = {}
            for param in need_params:
                add_data_param = raw_data.get(param, None)
                if add_data_param is None:
                    raise ParamError("%s: 参数没有" % (param))
                else:
                    # 如果是game字段，做一些转换
                    if param == 'game':
                        add_data_param = GameProject.objects.get(project_name_en=add_data_param)
                        param = 'project'

                    # 如果是room，做一些转化
                    if param == 'room':
                        area_name = raw_data.get('area_name', None)
                        if area_name is None:
                            raise Exception("area_name: 参数没有")
                        try:
                            add_data_param = Room.objects.get(room_name=add_data_param, area__chinese_name=area_name)
                        except:
                            add_data_param = Room.objects.get(room_name_en=add_data_param, area__short_name=area_name)

                    # 如果是host,做一些转化
                    if param == 'host':
                        add_data_param = Host.objects.get(host_identifier=add_data_param)

                    # 如果是game_type,做一些转化
                    if param == 'game_type':
                        add_data_param = GameServerType.objects.get(
                            project=add_data['project'], game_type_code=str(add_data_param))

                    # 如果是area_name,做一些转化
                    if param == 'area_name':
                        if '大陆' in str(add_data_param):
                            add_data_param = '大陆'

                    add_data[param] = add_data_param

            add_data['sid'] = raw_data.get('sid', None)

            # 添加主服id和合服时间的参数，如果有的话
            if raw_data.get('merge_id', None) is not None:
                merge_id = raw_data.get('merge_id')
                if str(merge_id) == '0':
                    pass
                else:
                    merge_time = raw_data.get('merge_time', None)
                    if not merge_time:
                        raise ParamError('需要传递合服时间参数')
                    else:
                        try:
                            GameServer.objects.get(project=add_data['project'], srv_id=merge_id,
                                                   host__belongs_to_room__area__chinese_name=add_data['area_name'])
                        except:
                            GameServer.objects.get(project=add_data['project'], srv_id=merge_id,
                                                   host__belongs_to_room__area__short_name=add_data['area_name'])
                        add_data['merge_id'] = merge_id
                        timeArray = time.localtime(int(raw_data.get('merge_time')))
                        merge_time = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
                        add_data['merge_time'] = merge_time

            # 入库到区服列表中
            game_server = GameServer.objects.create(**add_data)
            # 插入入库记录
            my_uuid = str(uuid.uuid1())
            GameServerActionRecord.objects.create(game_server=game_server, operation_type='add',
                                                  operation_user=request.user, result=1, uuid=my_uuid,
                                                  old_status=game_server.srv_status, source_ip=source_ip)
            ws_update_game_server_action_record('update_table')
            count = 1
            resp = 1

        except ParamError as e:
            resp = 4
            reason = str(e)
        except GameServerType.DoesNotExist:
            resp = 19
            reason = '没有找到游戏区服类型'
        except Host.DoesNotExist:
            resp = 10
            reason = '所属主机没有找到'
        except GameServer.DoesNotExist:
            resp = 14
            reason = '游戏服没有找到'
        except GameServer.MultipleObjectsReturned:
            resp = 16
            reason = '游戏服不唯一'
        except GameProject.DoesNotExist:
            resp = 12
            reason = '游戏项目英文名不存在'
        except IntegrityError:
            resp = 13
            reason = '区服id有重复'
        except Room.DoesNotExist:
            resp = 15
            reason = '机房不存在'
        except Exception as e:
            resp = 11
            reason = str(e)

        return JsonResponse({"resp": resp, "reason": reason, "count": count})


class UpdateClientPara(APIView):
    """更新服务器参数配置（前端更新）接口（页游）
    根据cdn根地址+cdn目录修改前端版本号
    """

    authentication_classes = (TokenAuthentication,)

    def get(self, request, format=None):
        reason = "ok"
        count = 0
        source_ip = get_ip(request)
        raw_data = request.query_params
        need_params = (
            'game', 'cdn_root_url', 'cdn_dir', 'client_ver', 'area_name',
        )
        try:
            with transaction.atomic():
                # 判断参数是否都提交了过来
                for param in need_params:
                    edit_data_param = raw_data.get(param, None)
                    if edit_data_param is None:
                        raise ParamError("%s: 参数没有" % (param))

                game_list = GameServer.objects.filter(
                    project=GameProject.objects.get(project_name_en=raw_data.get('game')),
                    cdn_root_url=raw_data.get('cdn_root_url'), cdn_dir=raw_data.get('cdn_dir'),
                    host__belongs_to_room__area__chinese_name=raw_data.get('area_name'))

                if game_list:
                    # 插入修改记录
                    my_uuid = str(uuid.uuid1())
                    for g in game_list:
                        if g.client_version != raw_data.get('client_ver'):
                            GameServerActionRecord.objects.create(game_server=g, operation_type='update',
                                                                  operation_user=request.user, result=1, uuid=my_uuid,
                                                                  old_status=g.srv_status, source_ip=source_ip,
                                                                  remark='前端版本号：{} ==> {}'.format(g.client_version,
                                                                                                  raw_data.get(
                                                                                                      'client_ver')))

                    game_list.update(client_version=raw_data.get('client_ver'))
                    ws_update_game_server_action_record('update_table')
                    count = game_list.count()
                    resp = 1
                else:
                    raise GameServerNotExist('游戏服找不到')

        except GameServerNotExist as e:
            resp = 8
            reason = str(e)
        except GameProject.DoesNotExist:
            resp = 12
            reason = '游戏项目英文名不存在'
        except ParamError as e:
            resp = 4
            reason = str(e)
        except Exception as e:
            reason = str(e)
            resp = 11
        return JsonResponse({"resp": resp, "reason": reason, "count": count})


class UpdateSrvPara(APIView):
    """更新服务器参数配置（后端更新）接口（页游）
    """

    authentication_classes = (TokenAuthentication,)

    def get(self, request, format=None):
        reason = "ok"
        count = 0
        source_ip = get_ip(request)
        raw_data = request.query_params
        need_params = ('game', 'server_ver', 'area_name')
        try:
            with transaction.atomic():
                # 判断参数是否都提交了过来
                for param in need_params:
                    edit_data_param = raw_data.get(param, None)
                    if edit_data_param is None:
                        raise ParamError("%s: 参数没有" % (param))

                project = GameProject.objects.get(project_name_en=raw_data.get('game'))
                old_version_no = raw_data.get('old_version_no', None)
                server_version = raw_data.get('server_ver')
                area_name = raw_data.get('area_name')

                pf_select_type = raw_data.get('pf_select_type', None)
                pf_list = raw_data.get('pf_list', None)
                srv_select_type = raw_data.get('srv_select_type', None)
                srv_list = raw_data.get('srv_list', None)

                include_query = Q()
                # exclude_query = Q()

                # 过滤游戏
                include_query.add(Q(project=project), Q.AND)

                # 过滤地区
                include_query.add(Q(host__belongs_to_room__area__chinese_name=area_name), Q.AND)

                # 过滤老版本号
                if old_version_no is not None:
                    include_query.add(Q(server_version=old_version_no), Q.AND)

                if pf_select_type is not None:
                    if pf_select_type == 'all':
                        pass
                    elif pf_select_type == 'include':
                        if pf_list is not None:
                            pf_list = pf_list.split(',')
                            include_query.add(Q(pf_name__in=pf_list), Q.AND)
                        else:
                            raise Exception('pf_select_type为include,需要pf_list参数')
                    elif pf_select_type == 'exclude':
                        if pf_list is not None:
                            pf_list = pf_list.split(',')
                            # exclude_query.add(Q(pf_name__in=pf_list), Q.AND)
                            include_query.add(~Q(pf_name__in=pf_list), Q.AND)
                        else:
                            raise Exception('pf_select_type为exclude,需要pf_list参数')
                    else:
                        raise SrvSelectTypeError('pf_select_type只能是all, include, exclude')

                if srv_select_type is not None:
                    if srv_select_type == 'all':
                        pass
                    elif srv_select_type == 'include':
                        if srv_list is not None:
                            srv_list = srv_list.split(',')
                            include_query.add(Q(srv_id__in=srv_list), Q.AND)
                        else:
                            raise Exception('srv_select_type为include,需要srv_list参数')
                    elif srv_select_type == 'exclude':
                        if srv_list is not None:
                            srv_list = srv_list.split(',')
                            # exclude_query.add(Q(srv_id__in=srv_list), Q.AND)
                            include_query.add(~Q(srv_id__in=srv_list), Q.AND)
                        else:
                            raise Exception('srv_select_type为exclude,需要srv_list参数')
                    else:
                        raise SrvSelectTypeError('srv_select_type只能是all, include, exclude')

                # game_list = GameServer.objects.filter(include_query).exclude(exclude_query)
                game_list = GameServer.objects.filter(include_query)

                if not game_list:
                    raise Exception('查找记录为空')
                else:
                    update_data = {'server_version': server_version}
                    count = game_list.count()
                    # 插入修改记录
                    my_uuid = str(uuid.uuid1())
                    for g in game_list:
                        if g.server_version != server_version:
                            GameServerActionRecord.objects.create(game_server=g, operation_type='update',
                                                                  operation_user=request.user, result=1, uuid=my_uuid,
                                                                  old_status=g.srv_status, source_ip=source_ip,
                                                                  remark='后端版本号：{} ==> {}'.format(g.server_version,
                                                                                                  server_version))
                    game_list.update(**update_data)
                    ws_update_game_server_action_record('update_table')
                    resp = 1

        except SrvSelectTypeError as e:
            resp = 17
            reason = str(e)
        except GameProject.DoesNotExist:
            resp = 12
            reason = '游戏项目英文名不存在'
        except ParamError as e:
            resp = 4
            reason = str(e)
        except Exception as e:
            reason = str(e)
            resp = 11
        return JsonResponse({"resp": resp, "reason": reason, "count": count})

    def post(self, request, format=None):
        reason = "ok"
        count = 0
        source_ip = get_ip(request)
        raw_data = request.data
        need_params = ('game', 'server_ver', 'area_name', 'srv_list')

        try:
            with transaction.atomic():
                # 判断参数是否都提交了过来
                for param in need_params:
                    edit_data_param = raw_data.get(param, None)
                    if edit_data_param is None:
                        raise ParamError("%s: 参数没有" % (param))

                project = GameProject.objects.get(project_name_en=raw_data.get('game'))
                server_version = raw_data.get('server_ver')
                area_name = raw_data.get('area_name')
                srv_list = raw_data.get('srv_list')

                srv_list = srv_list.split(',')

                game_list = GameServer.objects.filter(project=project,
                                                      host__belongs_to_room__area__chinese_name=area_name,
                                                      srv_id__in=srv_list)

                if not game_list:
                    raise Exception('查找记录为空')
                else:
                    update_data = {'server_version': server_version}
                    # 插入修改记录
                    my_uuid = str(uuid.uuid1())
                    for g in game_list:
                        GameServerActionRecord.objects.create(game_server=g, operation_type='update',
                                                              operation_user=request.user, result=1, uuid=my_uuid,
                                                              old_status=g.srv_status, source_ip=source_ip,
                                                              remark='修改后端版本号：{} ==> {}'.format(g.server_version,
                                                                                                server_version))
                    game_list.update(**update_data)
                    ws_update_game_server_action_record('update_table')
                    count = game_list.count()
                    resp = 1
        except GameProject.DoesNotExist:
            resp = 12
            reason = '游戏项目英文名不存在'
        except ParamError as e:
            resp = 4
            reason = str(e)
        except Exception as e:
            reason = str(e)
            resp = 11
        return JsonResponse({"resp": resp, "reason": reason, "count": count})


class DelSrvRelateInfo(APIView):
    """删除某个服的数据接口
    """

    authentication_classes = (TokenAuthentication,)

    def get(self, request, format=None):
        reason = "ok"
        count = 0
        source_ip = get_ip(request)
        raw_data = request.query_params
        need_params = ('game', 'srv_id', 'area_name')

        try:
            with transaction.atomic():
                # 必须提供的参数
                for param in need_params:
                    if raw_data.get(param, None) is None:
                        raise ParamError("%s: 参数没有" % (param))

                # 根据游戏和游戏id获取游戏服
                project = GameProject.objects.get(project_name_en=raw_data.get('game'))
                game_server = GameServer.objects.get(
                    project=project, srv_id=raw_data.get('srv_id'),
                    host__belongs_to_room__area__chinese_name=raw_data.get('area_name'))
                if game_server.merge_id:
                    raise Exception('%s有合服,不能删除' % (raw_data.get('srv_id')))
                # 插入删除记录，在备注处保留区服srv_id
                my_uuid = str(uuid.uuid1())
                GameServerActionRecord.objects.create(game_server=game_server, operation_type='delete',
                                                      operation_user=request.user, result=1, uuid=my_uuid,
                                                      old_status=game_server.srv_status, source_ip=source_ip)
                records = GameServerActionRecord.objects.filter(game_server=game_server)
                for record in records:
                    if record.remark:
                        record.remark = '区服ID：{}，项目：{}，{}'.format(game_server.srv_id,
                                                                  game_server.project.project_name, record.remark)
                    else:
                        record.remark = '区服ID：{}，项目：{}'.format(game_server.srv_id, game_server.project.project_name)
                    record.save(update_fields=['remark'])
                # 删除区服
                game_server.delete()
                ws_update_game_server_action_record('update_table')
                resp = 1
                count = 1
        except GameServer.DoesNotExist:
            resp = 14
            reason = '游戏服没有找到'
        except GameServer.MultipleObjectsReturned:
            resp = 16
            reason = '游戏服不唯一'
        except GameProject.DoesNotExist:
            resp = 12
            reason = '游戏项目英文名不存在'
        except ParamError as e:
            resp = 4
            reason = str(e)
        except Exception as e:
            reason = str(e)
            resp = 11
        return JsonResponse({"resp": resp, "reason": reason, "count": count})


class ModifySrvRelateInfo(APIView):
    """修改服务器相关信息接口
    """

    authentication_classes = (TokenAuthentication,)

    def get(self, request, format=None):
        reason = "ok"
        count = 0
        resp = 1
        remark = ''
        my_uuid = str(uuid.uuid1())
        source_ip = get_ip(request)
        operation_user = request.user
        raw_data = request.query_params
        need_params = ('game', 'srv_id', 'area_name')

        try:
            with transaction.atomic():
                for param in need_params:
                    if raw_data.get(param, None) is None:
                        raise ParamError("%s: 参数没有" % (param))

                game = raw_data.get('game')
                srv_id = raw_data.get('srv_id')
                area_name = raw_data.get('area_name')

                project = GameProject.objects.get(project_name_en=game)
                game_server = GameServer.objects.get(
                    project=project, srv_id=srv_id, host__belongs_to_room__area__chinese_name=area_name)

                # 更新机房，如果有的话
                room = raw_data.get('room', None)
                if room is not None:
                    try:
                        room = Room.objects.get(room_name=room, area__chinese_name=area_name)
                    except:
                        room = Room.objects.get(room_name_en=room, area__short_name=area_name)
                    finally:
                        old = game_server.room.room_name
                        new = room.room_name
                        if old != new:
                            remark += '机房： {} ==> {}\n'.format(old, new)
                        game_server.room = room

                # 更新主机，如果有的话
                host = raw_data.get('host', None)
                if host is not None:
                    host = Host.objects.get(host_identifier=host)
                    old = game_server.host.telecom_ip
                    new = host.telecom_ip
                    if old != new:
                        remark += '主机： {} ==> {}\n'.format(old, new)
                    game_server.host = host

                # 更新平台，如果有的话
                pf_name = raw_data.get('pf_name', None)
                if pf_name:
                    old = game_server.pf_name
                    new = pf_name
                    if old != new:
                        remark += '平台： {} ==> {}\n'.format(old, new)
                    game_server.pf_name = pf_name

                # 更新状态
                srv_status = raw_data.get('srv_status', None)
                old_status = game_server.srv_status
                if srv_status is not None:
                    new = game_server.get_srv_status_tuple_remark(srv_status)
                    if game_server.get_srv_status_display() != new:
                        remark += '状态： {} ==> {}\n'.format(game_server.get_srv_status_display(), new)
                    game_server.srv_status = int(srv_status)

                # 更新游戏名称，如果有的话
                srv_name = raw_data.get('srv_name', None)
                if srv_name:
                    old = game_server.srv_name
                    new = srv_name
                    if old != new:
                        remark += '区服名： {} ==> {}\n'.format(old, new)
                    game_server.srv_name = srv_name

                # 更新ip，如果有的话
                ip = raw_data.get('ip', None)
                if ip:
                    old = game_server.ip
                    new = ip
                    if old != new:
                        remark += 'ip： {} ==> {}\n'.format(old, new)
                    game_server.ip = ip

                # 更新game_type， 如果有的话
                game_type = raw_data.get('game_type', None)
                if game_type:
                    game_type = GameServerType.objects.get(project=game_server.project, game_type_code=str(game_type))
                    old = game_server.game_type.game_type_text
                    new = game_type.game_type_text
                    if old != new:
                        remark += '区服类型： {} ==> {}\n'.format(old, new)
                    game_server.game_type = game_type

                # 更新后端版本，如果有的话
                server_version = raw_data.get('server_version', None)
                if server_version:
                    old = game_server.server_version
                    new = server_version
                    if old != new:
                        remark += '后端版本号： {} ==> {}\n'.format(old, new)
                    game_server.server_version = server_version

                # 更新合服id，如果有的话
                merge_id = raw_data.get('merge_id', None)
                if merge_id is not None:
                    if str(merge_id) == '0':
                        game_server.merge_id = None
                    else:
                        try:
                            GameServer.objects.get(project=project, srv_id=srv_id,
                                                   host__belongs_to_room__area__chinese_name=area_name)
                        except:
                            GameServer.objects.get(project=project, srv_id=srv_id,
                                                   host__belongs_to_room__area__short_name=area_name)
                        finally:
                            old = game_server.merge_id
                            new = merge_id
                            if old != new:
                                remark += '合服id： {} ==> {}\n'.format(old, new)
                            game_server.merge_id = merge_id

                # 更新合服时间，如果有的话
                merge_time = raw_data.get('merge_time', None)
                if merge_time is not None:
                    if str(merge_id) == '0':
                        merge_time = None
                    else:
                        timeArray = time.localtime(int(merge_time))
                        merge_time = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
                        old = str(game_server.merge_time)
                        new = merge_time
                        if old != new:
                            remark += '合服时间： {} ==> {}\n'.format(old, new)
                        game_server.merge_time = merge_time
                else:
                    if str(merge_id) == '0':
                        old = str(game_server.merge_time)
                        new = None
                        if old != new:
                            remark += '合服时间： {} ==> {}\n'.format(old, new)
                        game_server.merge_time = None

                # 更新开服时间，如果有的话
                open_time = raw_data.get('open_time', None)
                if open_time:
                    old = game_server.open_time
                    new = open_time
                    if old != new:
                        remark += '开服时间： {} ==> {}\n'.format(old, new)
                    game_server.open_time = open_time

                # 更新cdn和前端版本，如果都存在的话
                cdn_root_url = raw_data.get('cdn_root_url', None)
                cdn_dir = raw_data.get('cdn_dir', None)
                client_version = raw_data.get('client_version', None)

                # 更新sid，如果有的话
                sid = raw_data.get('sid', None)
                if sid:
                    old = game_server.sid
                    new = sid
                    if old != new:
                        remark += 'sid： {} ==> {}\n'.format(old, new)
                    game_server.sid = sid

                if cdn_root_url is not None and cdn_dir is not None and client_version is not None:
                    if game_server.cdn_root_url != cdn_root_url:
                        remark += 'cdn根： {} ==> {}\n'.format(game_server.cdn_root_url, cdn_root_url)
                    if game_server.cdn_dir != cdn_dir:
                        remark += 'cdn目录： {} ==> {}\n'.format(game_server.cdn_dir, cdn_dir)
                    if game_server.client_version != client_version:
                        remark += 'cdn前端版本号： {} ==> {}\n'.format(game_server.client_version, client_version)
                    game_server.cdn_root_url = cdn_root_url
                    game_server.cdn_dir = cdn_dir
                    game_server.client_version = client_version
                elif cdn_root_url is None and cdn_dir is None and client_version is None:
                    pass
                else:
                    raise ParamError('cdn_root_url, cdn_dir, client_version必须同时存在')

                game_server.save()
                GameServerActionRecord.objects.create(game_server=game_server, operation_type='update',
                                                      operation_user=operation_user, result=1, uuid=my_uuid,
                                                      old_status=old_status, source_ip=source_ip,
                                                      remark=remark)
                count = 1
                resp = 1

        except GameServer.DoesNotExist:
            resp = 14
            reason = '游戏服没有找到'
        except GameServerType.DoesNotExist:
            resp = 20
            reason = '区服类型没有找到'
        except Host.DoesNotExist:
            resp = 10
            reason = '所属主机没有找到'
        except Room.DoesNotExist:
            resp = 15
            reason = '机房名找不到'
        except GameServer.MultipleObjectsReturned:
            resp = 16
            reason = '游戏服不唯一'
        except GameProject.DoesNotExist:
            resp = 12
            reason = '游戏项目英文名不存在'
        except ParamError as e:
            resp = 4
            reason = str(e)
        except Exception as e:
            reason = str(e)
            resp = 11
        return JsonResponse({"resp": resp, "reason": reason, "count": count})


class BatchModifyCdn(APIView):
    """根据条件批量修改cdn地址接口
    """
    authentication_classes = (TokenAuthentication,)

    def get(self, request, format=None):
        reason = "ok"
        count = 0
        source_ip = get_ip(request)
        raw_data = request.query_params
        need_params = ('game', 'new_cdn_root_url', 'new_cdn_dir', 'client_version', 'area_name')

        try:
            with transaction.atomic():
                for param in need_params:
                    if raw_data.get(param, None) is None:
                        raise ParamError("%s: 参数没有" % (param))

                old_cdn_root_url = raw_data.get('old_cdn_root_url', None)
                old_cdn_dir = raw_data.get('old_cdn_dir', None)
                srv_list = raw_data.get('srv_list', None)

                area_name = raw_data.get('area_name')

                project = GameProject.objects.get(project_name_en=raw_data.get('game'))
                client_version = raw_data.get('client_version')

                new_cdn_root_url = raw_data.get('new_cdn_root_url')
                new_cdn_dir = raw_data.get('new_cdn_dir')

                if old_cdn_root_url is not None and old_cdn_dir is not None:
                    game_list = GameServer.objects.filter(
                        project=project, cdn_root_url=old_cdn_root_url, cdn_dir=old_cdn_dir,
                        host__belongs_to_room__area__chinese_name=area_name)
                elif srv_list is not None:
                    srv_list = srv_list.split(',')
                    game_list = GameServer.objects.filter(project=project, srv_id__in=srv_list,
                                                          host__belongs_to_room__area__chinese_name=area_name)
                else:
                    raise ParamError('需要old_cdn_root_url和old_cdn_dir或者srv_list')

                if not game_list:
                    raise GameServer.DoesNotExist
                # 插入修改记录
                my_uuid = str(uuid.uuid1())
                for g in game_list:
                    if g.cdn_root_url != new_cdn_root_url or g.cdn_dir != new_cdn_dir or g.client_version != client_version:
                        GameServerActionRecord.objects.create(game_server=g, operation_type='update',
                                                              operation_user=request.user, result=1, uuid=my_uuid,
                                                              old_status=g.srv_status, source_ip=source_ip,
                                                              remark='cdn根url：{} ==> {}\ncdn目录：{} ==> {}\n前端版本号：{} ==> {}'.format(
                                                                  g.cdn_root_url, new_cdn_root_url, g.cdn_dir,
                                                                  new_cdn_dir, g.client_version, client_version))
                update_data = {'cdn_root_url': new_cdn_root_url, 'cdn_dir': new_cdn_dir,
                               'client_version': client_version}
                count = game_list.count()
                game_list.update(**update_data)
                ws_update_game_server_action_record('update_table')
                resp = 1

        except GameProject.DoesNotExist:
            resp = 12
            reason = '游戏项目英文名不存在'
        except GameServer.DoesNotExist:
            resp = 14
            reason = '游戏服没有找到'
        except IndexError:
            resp = 19
            reason = '解析cdn出错'
        except ParamError as e:
            resp = 4
            reason = str(e)
        except Exception as e:
            reason = str(e)
            resp = 11
        return JsonResponse({"resp": resp, "reason": reason, "count": count})


class MergeSrvCallBack(APIView):
    """合服完成回调接口
    """
    authentication_classes = (TokenAuthentication,)

    def get(self, request, format=None):
        reason = "ok"
        count = 0
        source_ip = get_ip(request)
        raw_data = request.query_params
        need_params = ('game', 'merge_id', 'merge_time', 'srv_id', 'area_name')

        try:
            with transaction.atomic():
                for param in need_params:
                    if raw_data.get(param, None) is None:
                        raise ParamError("%s: 参数没有" % (param))

                project = GameProject.objects.get(project_name_en=raw_data.get('game'))
                merge_server = GameServer.objects.get(
                    project=project, srv_id=raw_data.get('merge_id'),
                    host__belongs_to_room__area__chinese_name=raw_data.get('area_name'))  # 主服

                srv_server = GameServer.objects.get(
                    project=project, srv_id=raw_data.get('srv_id'),
                    host__belongs_to_room__area__chinese_name=raw_data.get('area_name'))  # 被合服

                # 插入修改记录
                my_uuid = str(uuid.uuid1())
                GameServerActionRecord.objects.create(game_server=srv_server, operation_type='update',
                                                      operation_user=request.user, result=1, uuid=my_uuid,
                                                      old_status=srv_server.srv_status, source_ip=source_ip,
                                                      remark='合并到主服，主服srv_id: {}'.format(merge_server.srv_id))
                # 修改区服所属主服、合服时间、区服状态
                srv_server.merge_id = merge_server.srv_id
                st = time.localtime(int(raw_data.get('merge_time')))
                merge_time = time.strftime('%Y-%m-%d %H:%M', st)
                srv_server.merge_time = merge_time
                srv_server.srv_status = 1
                srv_server.save()
                resp = 1
                count = 1

        except GameProject.DoesNotExist:
            resp = 12
            reason = '游戏项目英文名不存在'
        except GameServer.DoesNotExist:
            resp = 14
            reason = '游戏服没有找到'
        except GameServer.MultipleObjectsReturned:
            resp = 16
            reason = '游戏服不唯一'
        except ParamError as e:
            resp = 4
            reason = str(e)
        except Exception as e:
            reason = str(e)
            resp = 11
        return JsonResponse({"resp": resp, "reason": reason, "count": count})


class HotClientCallBack(APIView):
    """前热更新完成的回调接口
    返回的方式POST
    参数:
    {
        'update_type': 'hot_client',
        'data': [
            {'cdn_root_url': 'res.ssss.chuangyunet.com', 'cdn_dir': 't1', 'status': True},
            {'cdn_root_url': 'res.ssss.chuangyunet.com', 'cdn_dir': 'test_r1', 'status': True},
            {'cdn_root_url': 'res.ssss.chuangyunet.com', 'cdn_dir': 's1', 'status': True},
            {'cdn_root_url': 'res.ssss.chuangyunet.com', 'cdn_dir': 'r1', 'status': False}
        ],
        'uuid': 'id',
        'version': '003100000'
    }
    """

    def get_index(self, content, cdn_root_url, cdn_dir):
        """content的内容是:
        [
            {'cdn_root_url': 'res.ssss.chuangyunet.com', 'cdn_dir': 't1'},
            {'cdn_root_url': 'res.ssss.chuangyunet.com', 'cdn_dir': 'test_r1'},
            {'cdn_root_url': 'res.ssss.chuangyunet.com', 'cdn_dir': 's1'},
            {'cdn_root_url': 'res.ssss.chuangyunet.com', 'cdn_dir': 'r1'}
        ]
        """

        for index, t in enumerate(content):
            if cdn_root_url == t['cdn_root_url'] and cdn_dir == t['cdn_dir']:
                return index

        return None

    def update_content(self, data, content):
        """根据data里面的值更新content里面的值
        主要就是给content增加一个status的key
        """

        for d in data:
            cdn_root_url = d.get('cdn_root_url')
            cdn_dir = d.get('cdn_dir')
            status = d.get('status')
            data = d.get('data')
            flag = False
            for t in content:
                if t['cdn_root_url'] == cdn_root_url and t['cdn_dir'] == cdn_dir:
                    t['status'] = status
                    t['data'] = data
                    flag = True
            else:
                if not flag:
                    raise Exception('没有找到匹配的cdn组合')

        return content

    def parse_data(self, data):
        """解析data里面的数据
        如果不是要求的格式，有异常
        """

        for x in data:
            if x.get('cdn_root_url', None) is None:
                raise Exception('data参数里面需要cdn_root_url')
            if x.get('cdn_dir', None) is None:
                raise Exception('data参数里面需要cdn_dir')
            if x.get('status', None) is None:
                raise Exception('data参数里面需要status')

    def is_all_done(self, content):
        """判断是否所有的cdn组合都完成
        根据是否有status的值来确定
        """
        for t in content:
            if t.get('status', None) is None:
                return False

        return True

    def is_all_good(self, content):
        """判断是否所有的cdn组合都是status True
        """

        for t in content:
            if not t.get('status'):
                return False

        return True

    def post(self, request, format=None):
        reason = "ok"
        raw_data = json.loads(request.data)
        need_params = ('uuid', 'update_type', 'data', 'version')

        try:
            for param in need_params:
                if raw_data.get(param, None) is None:
                    raise ParamError("%s: 参数没有" % (param))

            uuid = raw_data.get('uuid')
            update_type = raw_data.get('update_type')
            data = raw_data.get('data')
            version = raw_data.get('version')

            self.parse_data(data)

            hot_update_log = HotUpdateLog(uuid)

            if update_type == 'hot_client':
                obj = ClientHotUpdate.objects.get(uuid=uuid)
            else:
                raise ParamError('update_type只能是hot_client或者hot_server')

            if obj.client_version != version:
                raise Exception('version和前端热更新工单的client_version不同')

            """增加事务机制"""
            with transaction.atomic():
                content = json.loads(obj.content)
                content = self.update_content(data, content)
                obj.content = json.dumps(content)
                obj.save()

            if self.is_all_done(content):
                if self.is_all_good(content):
                    obj.status = '3'
                    obj.save()
                    # 通知所有相关人员本次更新成功
                    all_user_objs = get_hot_update_all_related_user(obj)
                    all_users = ','.join([x.first_name for x in all_user_objs])
                    hot_update_qq_notify(all_users, obj, True)
                    to_list = [x.email for x in all_user_objs]
                    hot_update_mail_notify(to_list, obj, True)
                    wx_users = '|'.join([x.first_name for x in all_user_objs])
                    hot_update_wx_notify(wx_users, obj, True)

                    hot_update_log.logger.info('hot_client: %s-更新完成' % (obj.title))

                    # 解锁，如果解锁成功，然后执行下一条热更新
                    """2019.3修改，遍历热更新子任务中的运维管理机，进行解锁"""
                    all_unlock_hot_update_result = True
                    for task in obj.clienthotupdatersynctask_set.all():
                        ops = task.ops
                        unlock_hot_update_result = unlock_hot_update(uuid, ops)
                        if not unlock_hot_update_result:
                            all_unlock_hot_update_result = False
                            hot_update_log.logger.info('hot_client: %s-解锁失败' % task.ops)
                    if all_unlock_hot_update_result:
                        hot_update_log.logger.info('hot_client: %s-解锁完成' % (obj.title))
                        result, next_hot_update = get_next_hot_update(obj.project, obj.area_name, content_object=obj)
                        if next_hot_update:
                            hot_update_log.logger.info('hot_client: 发送下一个前端热更新任务-%s' % (next_hot_update.title))
                            if isinstance(next_hot_update, ClientHotUpdate):
                                # do_hot_client.delay(0, obj_id=next_hot_update.id, update_type='hot_client')
                                if next_hot_update.status == '4':
                                    do_hot_update(next_hot_update)
                            elif isinstance(next_hot_update, ServerHotUpdate):
                                # do_hot_client.delay(0, obj_id=next_hot_update.id, update_type='hot_server')
                                if next_hot_update.status == '4':
                                    do_hot_update(next_hot_update)
                            else:
                                hot_update_log.logger.info('hot_client: 未知类型的热更新-%s' % (next_hot_update.title))
                        else:
                            hot_update_log.logger.info(result)
                    else:
                        hot_update_log.logger.info('hot_client: %s-解锁失败' % (obj.title))

                else:
                    hot_update_log.logger.info('hot_client: %s-更新失败' % (obj.title))
                    obj.status = '2'
                    obj.save()
                    # 通知所有相关人员本次更新失败
                    all_user_objs = get_hot_update_all_related_user(obj)
                    all_users = ','.join([x.first_name for x in all_user_objs])
                    hot_update_qq_notify(all_users, obj, False)
                    to_list = [x.email for x in all_user_objs]
                    hot_update_mail_notify(to_list, obj, False)
                    wx_users = '|'.join([x.first_name for x in all_user_objs])
                    hot_update_wx_notify(wx_users, obj, False)

                # 发送微信机器人接口通知指定项目
                if obj.project.wx_robot:
                    success, msg = send_robot_message(obj)
                    if success:
                        hot_update_log.logger.info('hot_client: {}'.format('发送微信机器人通知成功'))
                    else:
                        hot_update_log.logger.info('hot_client: {}: {}'.format('发送微信机器人通知失败', msg))

                resp = 0
            else:
                hot_update_log.logger.info('没有全部匹配到cdn版本组合,继续等待')
                obj.status = '1'
                obj.save()
                resp = 0

        except ClientHotUpdate.DoesNotExist:
            reason = "没有找到前端热更新工单"
            resp = 1
        except Exception as e:
            traceback.print_exc()
            resp = 1
            reason = str(e)
        finally:
            ws_notify()
        return JsonResponse({"resp": resp, "reason": reason})


class SNSYHotClientCallBack(APIView):
    """超神学院前热更新完成的回调接口
    返回的方式POST
    参数:
    {
        'update_type': 'hot_client',
        'data': [
            {'cdn_root_url': 'root', 'cdn_dir': 't1', 'version': 'v', 'client_type': 'cn_ios', 'status': True, 'data': 'xx'},
            {'cdn_root_url': 'root', 'cdn_dir': 'te', 'version': 'v', 'client_type': 'cn_ios', 'status': True, 'data': 'xx'},
            {'cdn_root_url': 'root', 'cdn_dir': 's1', 'version': 'v', 'client_type': 'cn_ios', 'status': True, 'data': 'xx'},
            {'cdn_root_url': 'root', 'cdn_dir': 'r1', 'version': 'v', 'client_type': 'cn_ios', 'status': False, 'data': 'xx'}
        ],
        'uuid': 'id',
    }
    """

    def get_index(self, content, cdn_root_url, cdn_dir):
        """content的内容是:
        [
            {'cdn_root_url': 'root', 'cdn_dir': 't1', 'version': 'axxx_13342', 'client_type': 'cn_ios'},
            {'cdn_root_url': 'root', 'cdn_dir': 'test_r1', 'version': 'axxx_13342', 'client_type': 'cn_ios'},
            {'cdn_root_url': 'root', 'cdn_dir': 's1', 'version': 'axxx_13342', 'client_type': 'cn_ios'},
            {'cdn_root_url': 'root', 'cdn_dir': 'r1', 'version': 'axxx_13342', 'client_type': 'cn_ios'}
        ]
        """

        for index, t in enumerate(content):
            if cdn_root_url == t['cdn_root_url'] and cdn_dir == t['cdn_dir'] and \
                    t['client_type'] == 'client_type' and t['version'] == 'version':
                return index

        return None

    def update_content(self, data, content):
        """根据data里面的值更新content里面的值
        主要就是给content增加一个status的key
        """

        for d in data:
            cdn_root_url = d.get('cdn_root_url')
            cdn_dir = d.get('cdn_dir')
            version = d.get('version')
            client_type = d.get('client_type')
            status = d.get('status')
            data = d.get('data')
            flag = False
            for t in content:
                if t['cdn_root_url'] == cdn_root_url and t['cdn_dir'] == cdn_dir and \
                        t['version'] == version and t['client_type'] == client_type:
                    # 增加字段
                    t['status'] = status
                    t['data'] = data
                    flag = True
            else:
                if not flag:
                    raise Exception('没有找到匹配的cdn组合')

        return content

    def parse_data(self, data):
        """解析data里面的数据
        如果不是要求的格式，有异常
        """

        for x in data:
            if x.get('cdn_root_url', None) is None:
                raise Exception('data参数里面需要cdn_root_url')
            if x.get('cdn_dir', None) is None:
                raise Exception('data参数里面需要cdn_dir')
            if x.get('version', None) is None:
                raise Exception('data参数里面需要version')
            if x.get('client_type', None) is None:
                raise Exception('data参数里面需要client_type')
            if x.get('status', None) is None:
                raise Exception('data参数里面需要status')
            if x.get('data', None) is None:
                raise Exception('data参数里面需要data')

    def is_all_done(self, content):
        """判断是否所有的cdn组合都完成
        根据是否有status的值来确定
        """
        for t in content:
            if t.get('status', None) is None:
                return False

        return True

    def is_all_good(self, content):
        """判断是否所有的cdn组合都是status True
        """

        for t in content:
            if not t.get('status'):
                return False

        return True

    def post(self, request, format=None):
        reason = "ok"
        raw_data = json.loads(request.data)
        need_params = ('uuid', 'update_type', 'data')

        try:
            for param in need_params:
                if raw_data.get(param, None) is None:
                    raise ParamError("%s: 参数没有" % (param))

            uuid = raw_data.get('uuid')
            update_type = raw_data.get('update_type')
            data = raw_data.get('data')

            self.parse_data(data)

            hot_update_log = HotUpdateLog(uuid)

            if update_type == 'hot_client':
                obj = ClientHotUpdate.objects.get(uuid=uuid)
            else:
                raise ParamError('update_type只能是hot_client或者hot_server')

            """增加事务机制"""
            with transaction.atomic():
                content = json.loads(obj.content)
                content = self.update_content(data, content)
                obj.content = json.dumps(content)
                obj.save()

            if self.is_all_done(content):
                if self.is_all_good(content):
                    obj.status = '3'
                    obj.save()
                    # 通知所有相关人员本次更新成功
                    all_user_objs = get_hot_update_all_related_user(obj)
                    all_users = ','.join([x.first_name for x in all_user_objs])
                    hot_update_qq_notify(all_users, obj, True)
                    to_list = [x.email for x in all_user_objs]
                    hot_update_mail_notify(to_list, obj, True)
                    wx_users = '|'.join([x.first_name for x in all_user_objs])
                    hot_update_wx_notify(wx_users, obj, True)

                    hot_update_log.logger.info('hot_client: %s-更新完成' % (obj.title))

                    # 解锁，如果解锁成功，然后执行下一条热更新
                    """2019.3修改，遍历热更新子任务中的运维管理机，进行解锁"""
                    all_unlock_hot_update_result = True
                    for task in obj.clienthotupdatersynctask_set.all():
                        ops = task.ops
                        unlock_hot_update_result = unlock_hot_update(uuid, ops)
                        if not unlock_hot_update_result:
                            all_unlock_hot_update_result = False
                            hot_update_log.logger.info('hot_client: %s-解锁失败' % task.ops)
                    if all_unlock_hot_update_result:
                        hot_update_log.logger.info('hot_client: %s-解锁完成' % (obj.title))
                        result, next_hot_update = get_next_hot_update(obj.project, obj.area_name, content_object=obj)
                        if next_hot_update:
                            hot_update_log.logger.info('hot_client: 发送下一个前端热更新任务-%s' % (next_hot_update.title))
                            if isinstance(next_hot_update, ClientHotUpdate):
                                # do_hot_client.delay(0, obj_id=next_hot_update.id, update_type='hot_client')
                                if next_hot_update.status == '4':
                                    do_hot_update(next_hot_update)
                            elif isinstance(next_hot_update, ServerHotUpdate):
                                # do_hot_client.delay(0, obj_id=next_hot_update.id, update_type='hot_server')
                                if next_hot_update.status == '4':
                                    do_hot_update(next_hot_update)
                            else:
                                hot_update_log.logger.info('hot_client: 未知类型的热更新-%s' % (next_hot_update.title))
                        else:
                            hot_update_log.logger.info(result)
                    else:
                        hot_update_log.logger.info('hot_client: %s-解锁失败' % (obj.title))

                else:
                    hot_update_log.logger.info('hot_client: %s-更新失败' % (obj.title))
                    obj.status = '2'
                    obj.save()
                    # 通知所有相关人员本次更新失败
                    all_user_objs = get_hot_update_all_related_user(obj)
                    all_users = ','.join([x.first_name for x in all_user_objs])
                    hot_update_qq_notify(all_users, obj, False)
                    to_list = [x.email for x in all_user_objs]
                    hot_update_mail_notify(to_list, obj, False)
                    wx_users = '|'.join([x.first_name for x in all_user_objs])
                    hot_update_wx_notify(wx_users, obj, False)

                resp = 0
            else:
                hot_update_log.logger.info('没有全部匹配到cdn版本组合,继续等待')
                obj.status = '1'
                obj.save()
                resp = 0

        except ClientHotUpdate.DoesNotExist:
            reason = "没有找到前端热更新工单"
            resp = 1
        except Exception as e:
            traceback.print_exc()
            resp = 1
            reason = str(e)
        finally:
            ws_notify()
        return JsonResponse({"resp": resp, "reason": reason})


class CSXYHotClientCallBack(APIView):
    """前热更新完成的回调接口
    返回的方式POST
    参数:
    {
        'update_type': 'hot_client',
        'data': [
            {
                'input_type': 'iosmj2', 'input_compare': '', 'input_version': 'fdadf', 'input_platform': 'morefun', 'status': True, 'data': ''
            },
            {
                'input_type': 'android', 'input_compare': 'dfasg', 'input_version': 'fdasf', 'input_platform': 'xinghuiorg', 'status': True, 'data': ''
            }
        ],
        'uuid': 'id',
    }
    """

    def update_content(self, data, content):
        """根据data里面的值更新content里面的值
        主要就是给content增加一个status的key
        """

        for d in data:
            input_type = d.get('input_type')
            input_compare = d.get('input_compare')
            input_version = d.get('input_version')
            input_platform = d.get('input_platform')
            status = d.get('status')
            data = d.get('data')
            flag = False
            for t in content:
                if t['input_type'] == input_type and t['input_compare'] == input_compare and \
                        t['input_version'] == input_version and t['input_platform'] == input_platform:
                    # 增加字段
                    t['status'] = status
                    t['data'] = data
                    flag = True
            else:
                if not flag:
                    raise Exception('没有找到匹配的cdn组合')

        return content

    def parse_data(self, data):
        """解析data里面的数据
        如果不是要求的格式，有异常
        """

        for x in data:
            if x.get('input_type', None) is None:
                raise Exception('data参数里面需要input_type')
            if x.get('input_compare', None) is None:
                raise Exception('data参数里面需要input_compare')
            if x.get('input_version', None) is None:
                raise Exception('data参数里面需要input_version')
            if x.get('input_platform', None) is None:
                raise Exception('data参数里面需要input_platform')
            if x.get('status', None) is None:
                raise Exception('data参数里面需要status')
            if x.get('data', None) is None:
                raise Exception('data参数里面需要data')

    def is_all_done(self, content):
        """判断是否所有的cdn组合都完成
        根据是否有status的值来确定
        """
        for t in content:
            if t.get('status', None) is None:
                return False

        return True

    def is_all_good(self, content):
        """判断是否所有的cdn组合都是status True
        """

        for t in content:
            if not t.get('status'):
                return False

        return True

    def post(self, request, format=None):
        reason = "ok"
        raw_data = json.loads(request.data)
        need_params = ('uuid', 'update_type', 'data')

        try:
            for param in need_params:
                if raw_data.get(param, None) is None:
                    raise ParamError("%s: 参数没有" % (param))

            uuid = raw_data.get('uuid')
            update_type = raw_data.get('update_type')
            data = raw_data.get('data')

            self.parse_data(data)

            hot_update_log = HotUpdateLog(uuid)

            if update_type == 'hot_client':
                obj = ClientHotUpdate.objects.get(uuid=uuid)
            else:
                raise ParamError('update_type只能是hot_client或者hot_server')

            """增加事务机制"""
            with transaction.atomic():
                content = json.loads(obj.content)
                content = self.update_content(data, content)
                obj.content = json.dumps(content)
                obj.save()

            if self.is_all_done(content):
                if self.is_all_good(content):
                    obj.status = '3'
                    obj.save()
                    # 通知所有相关人员本次更新成功
                    all_user_objs = get_hot_update_all_related_user(obj)
                    all_users = ','.join([x.first_name for x in all_user_objs])
                    hot_update_qq_notify(all_users, obj, True)
                    to_list = [x.email for x in all_user_objs]
                    hot_update_mail_notify(to_list, obj, True)
                    wx_users = '|'.join([x.first_name for x in all_user_objs])
                    hot_update_wx_notify(wx_users, obj, True)

                    hot_update_log.logger.info('hot_client: %s-更新完成' % (obj.title))

                    # 解锁，如果解锁成功，然后执行下一条热更新
                    """2019.3修改，遍历热更新子任务中的运维管理机，进行解锁"""
                    all_unlock_hot_update_result = True
                    for task in obj.clienthotupdatersynctask_set.all():
                        ops = task.ops
                        unlock_hot_update_result = unlock_hot_update(uuid, ops)
                        if not unlock_hot_update_result:
                            all_unlock_hot_update_result = False
                            hot_update_log.logger.info('hot_client: %s-解锁失败' % task.ops)
                    if all_unlock_hot_update_result:
                        hot_update_log.logger.info('hot_client: %s-解锁完成' % (obj.title))
                        result, next_hot_update = get_next_hot_update(obj.project, obj.area_name, content_object=obj)
                        if next_hot_update:
                            hot_update_log.logger.info('hot_client: 发送下一个前端热更新任务-%s' % (next_hot_update.title))
                            if isinstance(next_hot_update, ClientHotUpdate):
                                # do_hot_client.delay(0, obj_id=next_hot_update.id, update_type='hot_client')
                                if next_hot_update.status == '4':
                                    do_hot_update(next_hot_update)
                            elif isinstance(next_hot_update, ServerHotUpdate):
                                # do_hot_client.delay(0, obj_id=next_hot_update.id, update_type='hot_server')
                                if next_hot_update.status == '4':
                                    do_hot_update(next_hot_update)
                            else:
                                hot_update_log.logger.info('hot_client: 未知类型的热更新-%s' % (next_hot_update.title))
                        else:
                            hot_update_log.logger.info(result)
                    else:
                        hot_update_log.logger.info('hot_client: %s-解锁失败' % (obj.title))

                else:
                    hot_update_log.logger.info('hot_client: %s-更新失败' % (obj.title))
                    obj.status = '2'
                    obj.save()
                    # 通知所有相关人员本次更新失败
                    all_user_objs = get_hot_update_all_related_user(obj)
                    all_users = ','.join([x.first_name for x in all_user_objs])
                    hot_update_qq_notify(all_users, obj, False)
                    to_list = [x.email for x in all_user_objs]
                    hot_update_mail_notify(to_list, obj, False)
                    wx_users = '|'.join([x.first_name for x in all_user_objs])
                    hot_update_wx_notify(wx_users, obj, False)

                resp = 0
            else:
                hot_update_log.logger.info('没有全部匹配到cdn版本组合,继续等待')
                obj.status = '1'
                obj.save()
                resp = 0

        except ClientHotUpdate.DoesNotExist:
            reason = "没有找到前端热更新工单"
            resp = 1
        except Exception as e:
            traceback.print_exc()
            resp = 1
            reason = str(e)
        finally:
            ws_notify()
        return JsonResponse({"resp": resp, "reason": reason})


class HotServerCallBack(APIView):
    """后端热更新完成后的API接口
    修改redis里面的数据
    单个ip的返回接口
    返回的方式POST
    参数:
    {
        "ip": {
            "10.1.1.1": {
                "update_data": {
                    "qq_1": {"data": "更新失败,不执行erl命令", "status": False},
                    "qq_2": {"data": "更新失败,不执行erl命令", "status": False},
                },
                "erl_data": {
                    "qq_1": {"data": "更新失败,不执行erl命令", "status": False},
                    "qq_2": {"data": "更新失败,不执行erl命令", "status": False},
                }
            }
        },
        "uuid": 'xxxx',
        "update_type": "hot_server",
        "version": 'xxxxx',
    }
    """

    def update_update_server_list(self, update_server_list, erl_or_update_data, data_type, ip):
        """更新热更新后端的server_list
        添加erl_data或者update_date
        """
        if data_type == "update_data":
            for srv_id, data_status in erl_or_update_data.items():
                # 找到更新工单里面的ip和srv_id的组合，然后增加一个key
                flag = False
                for index, x in enumerate(update_server_list):
                    if x['ip'] == ip and x['srv_id'] == srv_id:
                        update_server_list[index]['update_data'] = data_status
                        flag = True
                else:
                    if not flag:
                        raise Exception('没有找到%s: %s的组合' % (ip, srv_id))

        if data_type == "erl_data":
            for srv_id, data_status in erl_or_update_data.items():
                # 找到更新工单里面的ip和srv_id的组合，然后增加一个key
                flag = False
                for index, x in enumerate(update_server_list):
                    if x['ip'] == ip and x['srv_id'] == srv_id:
                        update_server_list[index]['erl_data'] = data_status
                        flag = True
                else:
                    if not flag:
                        raise Exception('没有找到%s: %s的组合' % (ip, srv_id))

    def post(self, request, format=None):
        """原来的数据格式
        {'srv_id': '37_1', 'gtype': 'game', 'ip': '10.104.104.36', 'pf_name': '37', 'srv_name': 'S1'}
        {'srv_id': '37_2', 'gtype': 'game', 'ip': '10.135.44.1', 'pf_name': '37', 'srv_name': 'S2'}
        {'srv_id': '37_3', 'gtype': 'game', 'ip': '10.186.0.163', 'pf_name': '37', 'srv_name': 'S3'}
        {'srv_id': '37_4', 'gtype': 'game', 'ip': '10.135.61.161', 'pf_name': '37', 'srv_name': 'S4'}
        """

        try:
            reason = "ok"
            resp = 0
            raw_data = json.loads(request.data)
            need_params = ('uuid', 'update_type', 'ip', 'version')
            for param in need_params:
                if raw_data.get(param, None) is None:
                    raise ParamError("%s: 参数没有" % (param))

            update_type = raw_data.get('update_type')

            if update_type == "hot_server":
                uuid = raw_data.get('uuid')
                hot_update_log = HotUpdateLog(uuid)
                version = raw_data.get('version')

                hot_server = ServerHotUpdate.objects.get(uuid=uuid)

                if hot_server.server_version != version:
                    raise Exception('版本号对不上')

                update_ip_srv = raw_data.get('ip')

                ip = next(iter(update_ip_srv))

                update_srv_data = update_ip_srv[ip]

                # 更新redis里面的数据
                update_data = update_srv_data.get("update_data", None)
                erl_data = update_srv_data.get("erl_data", None)
                update_server(hot_server.uuid, ip, hot_server.hot_server_type, update_data=update_data,
                              erl_data=erl_data)

                # 发送websocket通知
                ws_hot_server_notify(hot_server.id)
            else:
                raise Exception('update_type类型不对')
        except ServerHotUpdate.DoesNotExist:
            reason = "没有找到热更新工单"
            hot_update_log.logger.error(reason)
            resp = 1
        except Exception as e:
            reason = str(e)
            hot_update_log.logger.error(reason)
            resp = 1
        return JsonResponse({"resp": resp, "reason": reason})


class HotServerOnFinishedCallBack(APIView):
    """热更新后端完成后总的回调接口
    数据格式如下:
    {
        "final_result": True,
        "final_data": "全部完成",
        "uuid": 'xxxx',
        "update_type": "hot_server",
        "version": 'xxxxx',
    }
    """

    def check_status(self, hot_server):
        """检查本次后端热更新的更新情况，决定是否展示
        更新成功或者更新失败
        """

        hot_server_type = hot_server.hot_server_type
        result_update_file_list = json.loads(hot_server.result_update_file_list)

        if hot_server_type == '0':
            # 只热更新
            for x in result_update_file_list:
                update_data_status = x.get('update_data_status', '失败')
                if update_data_status == '失败' or update_data_status == '':
                    return False
            return True
        elif hot_server_type in ['1', '3']:
            # 热更和erl命令都执行
            for x in result_update_file_list:
                update_data_status = x.get('update_data_status', '失败')
                erl_data_status = x.get('erl_data_status', '失败')
                if update_data_status == '失败' or update_data_status == '':
                    return False
                if erl_data_status == '失败' or erl_data_status == '':
                    return False
            return True
        elif hot_server_type == '2':
            for x in result_update_file_list:
                erl_data_status = x.get('erl_data_status', '失败')
                if erl_data_status == '失败' or erl_data_status == '':
                    return False
            return True

    def check_all_done(self, hot_server):
        """检查是否都已经更新完成，判断条件是是否能取到update_data_status"""
        hot_server_type = hot_server.hot_server_type
        result_update_file_list = json.loads(hot_server.result_update_file_list)

        if hot_server_type == '0':
            # 只热更新
            for x in result_update_file_list:
                update_data_status = x.get('update_data_status', '')
                if update_data_status == '':
                    return False
            return True
        elif hot_server_type in ['1', '3']:
            # 热更和erl命令都执行
            for x in result_update_file_list:
                update_data_status = x.get('update_data_status', '')
                erl_data_status = x.get('erl_data_status', '')
                if update_data_status == '':
                    return False
                if erl_data_status == '':
                    return False
            return True
        elif hot_server_type == '2':
            for x in result_update_file_list:
                erl_data_status = x.get('erl_data_status', '')
                if erl_data_status == '':
                    return False
            return True

    def post(self, request, format=None):
        try:
            reason = "ok"
            resp = 0
            raw_data = json.loads(request.data)
            need_params = ('uuid', 'update_type', 'final_data', 'version', 'final_result')
            for param in need_params:
                if raw_data.get(param, None) is None:
                    raise ParamError("%s: 参数没有" % (param))

            uuid = raw_data.get('uuid')
            hot_update_log = HotUpdateLog(uuid)
            version = raw_data.get('version')

            hot_server = ServerHotUpdate.objects.get(uuid=uuid)

            if hot_server.server_version != version:
                raise Exception('版本号对不上')

            final_data = raw_data.get('final_data')
            final_result = raw_data.get('final_result')

            hot_server.final_data = final_data
            hot_server.final_result = final_result

            # 将redis中的数据保存到工单中
            result_update_file_list = get_uuid_related_value(hot_server.uuid)
            hot_server.result_update_file_list = json.dumps(result_update_file_list)
            hot_server.save()

            if self.check_all_done(hot_server):
                # 删除掉redis中的数据
                delete_uuid_related_value(hot_server.uuid)
                hot_update_log.logger.info('hot_server: %s-收到更新完成请求，删除redis数据' % (hot_server.title))

                if self.check_status(hot_server):
                    hot_server.status = '3'
                    hot_server.save()
                    # 通知所有相关人员本次更新成功
                    all_user_objs = get_hot_update_all_related_user(hot_server)
                    all_users = ','.join([x.first_name for x in all_user_objs])
                    hot_update_qq_notify(all_users, hot_server, True)
                    to_list = [x.email for x in all_user_objs]
                    hot_update_mail_notify(to_list, hot_server, True)
                    wx_users = '|'.join([x.first_name for x in all_user_objs])
                    hot_update_wx_notify(wx_users, hot_server, True)

                    hot_update_log.logger.info('hot_server: %s-更新完成' % (hot_server.title))

                    # 解锁，如果解锁成功，然后执行下一条热更新
                    for task in hot_server.serverhotupdatersynctask_set.all():
                        unlock_hot_update_result = unlock_hot_update(uuid, task.ops)
                    if unlock_hot_update_result:
                        hot_update_log.logger.info('hot_server: %s-解锁完成' % (hot_server.title))
                        result, next_hot_update = get_next_hot_update(
                            hot_server.project, hot_server.area_name, content_object=hot_server)
                        if next_hot_update:
                            hot_update_log.logger.info('hot_server: 发送下一个热更新任务-%s' % (next_hot_update.title))
                            if isinstance(next_hot_update, ClientHotUpdate):
                                # do_hot_client.delay(0, obj_id=next_hot_update.id, update_type='hot_client')
                                if next_hot_update.status == '4':
                                    do_hot_update(next_hot_update)
                            elif isinstance(next_hot_update, ServerHotUpdate):
                                # do_hot_client.delay(0, obj_id=next_hot_update.id, update_type='hot_server')
                                if next_hot_update.status == '4':
                                    do_hot_update(next_hot_update)
                            else:
                                hot_update_log.logger.info('hot_server: 未知类型的热更新-%s' % (next_hot_update.title))
                        else:
                            hot_update_log.logger.info(result)
                    else:
                        hot_update_log.logger.info('hot_client: %s-解锁失败' % (hot_server.title))
                else:
                    hot_server.status = '2'
                    hot_update_log.logger.error('hot_server: %s-更新完成,但是发现更新有失败' % (hot_server.title))
                    hot_server.save()
                    # 通知所有相关人员本次更新失败
                    all_user_objs = get_hot_update_all_related_user(hot_server)
                    all_users = ','.join([x.first_name for x in all_user_objs])
                    hot_update_qq_notify(all_users, hot_server, False)
                    to_list = [x.email for x in all_user_objs]
                    hot_update_mail_notify(to_list, hot_server, False)
                    wx_users = '|'.join([x.first_name for x in all_user_objs])
                    hot_update_wx_notify(wx_users, hot_server, False)

                # 发送微信机器人接口通知指定项目
                if hot_server.project.wx_robot:
                    success, msg = send_robot_message(hot_server)
                    if success:
                        hot_update_log.logger.info('hot_server: {}'.format('发送微信机器人通知成功'))
                    else:
                        hot_update_log.logger.info('hot_server: {}: {}'.format('发送微信机器人通知失败', msg))

        except ServerHotUpdate.DoesNotExist:
            reason = "hot_server: 没有找到热更新工单"
            hot_update_log.logger.error(reason)
            resp = 1
        except Exception as e:
            reason = 'hot_server: ' + str(e)
            hot_update_log.logger.error(reason)
            resp = 1
        finally:
            ws_notify()
            ws_hot_server_notify(hot_server.id)
            hot_update_log.logger.info('通知刷新websocket')
            return JsonResponse({"resp": resp, "reason": reason})


class RsyncOnFinishedCallBack(APIView):
    """版本接收机器完成rsync后回调接口
    cmdb用来发送请求到运维管理机执行热更新命令
    """

    def post(self, request, format=None):

        raw_data = request.data
        uuid = raw_data.get('uuid')
        hot_update_log = HotUpdateLog(uuid)

        resp = 0
        reason = ''

        try:
            update_type = raw_data.get('update_type')
            content_object_id = raw_data.get('content_object_id')
            success = raw_data.get('success')
            msg = raw_data.get('msg')
            ops_ip = raw_data.get('ops_ip')

            if update_type == 'hot_client':
                content_object = ClientHotUpdate.objects.get(id=content_object_id)
                task = content_object.clienthotupdatersynctask_set.filter(ops__rsync_ip__icontains=ops_ip)
                if task:
                    ops = task[0].ops
                else:
                    raise Exception('%s没有找到对应的运维管理机' % ops_ip)
                if success:
                    """更新热更新rsync子任务结果"""
                    task.update(**{'rsync_result': 1})
                    # 解锁
                    unlock_hot_update_result = unlock_hot_update(uuid, ops)
                    if unlock_hot_update_result:
                        hot_update_log.logger.info('rsync推送成功，%s解锁成功' % ops)
                        """判断是否热更新工单所有的推送子任务都完成，是则异步发起前端热更新到运维管理机器"""
                        list_rsync_status = [x.rsync_result for x in content_object.clienthotupdatersynctask_set.all()]
                        if len(list(set(list_rsync_status))) == 1 and 1 in list_rsync_status:
                            if PRODUCTION_ENV:
                                do_hot_client.delay(content_object_id)
                            else:
                                do_test_hot_client.delay(content_object_id)
                    else:
                        hot_update_log.logger.info('rsync推送成功，%s解锁失败' % ops)
                else:
                    hot_update_log.logger.error(msg)
                    content_object.status = '2'
                    content_object.save()
                    ws_notify()
                    rsync_failed_mail_notify(content_object)
            elif update_type == 'hot_server':
                content_object = ServerHotUpdate.objects.get(id=content_object_id)
                task = content_object.serverhotupdatersynctask_set.filter(ops__rsync_ip__icontains=ops_ip)
                if task:
                    ops = task[0].ops
                else:
                    raise Exception('%s没有找到对应的运维管理机' % ops_ip)
                if success:
                    """更新热更新rsync子任务结果"""
                    task.update(**{'rsync_result': 1})
                    # 解锁
                    unlock_hot_update_result = unlock_hot_update(uuid, ops)
                    if unlock_hot_update_result:
                        hot_update_log.logger.info('rsync推送成功，%s解锁成功' % ops)
                        """判断是否热更新工单所有的推送子任务都完成，是则异步发起前端热更新到运维管理机器"""
                        list_rsync_status = [x.rsync_result for x in content_object.serverhotupdatersynctask_set.all()]
                        if len(list(set(list_rsync_status))) == 1 and 1 in list_rsync_status:
                            if PRODUCTION_ENV:
                                do_hot_server.delay(content_object_id)
                            else:
                                do_test_hot_server.delay(content_object_id)
                    else:
                        hot_update_log.logger.info('rsync推送成功，解锁失败')
                else:
                    hot_update_log.logger.error(msg)
                    content_object.status = '2'
                    content_object.save()
                    task = ServerHotUpdateRsyncTask.objects.filter(server_hot_update=content_object, ops=ops)
                    if task:
                        task.update(**{'rsync_result': 0})
                    else:
                        raise Exception('没有找到对应的rsync子任务 %s-%s' % (content_object.title, ops))
                    ws_notify()
                    rsync_failed_mail_notify(content_object)
            else:
                hot_update_log.logger.error('未知类型的热更新-%s' % (uuid))
        except Exception as e:
            msg = str(e)
            hot_update_log.logger.error(msg)
        return JsonResponse({"resp": resp, "reason": reason})


class UserHostAdd(APIView):
    """增加服务器权限
    """

    # authentication_classes = (TokenAuthentication, )

    def get(self, request, format=None):
        msg = ""
        raw_data = request.query_params

        try:
            with transaction.atomic():
                username = raw_data.get('username', None)
                user = User.objects.get(first_name=username)
                try:
                    profile = user.profile
                except:
                    profile = Profile.objects.create(user=user)
                """
                2018.12修改，增加关联新组织架构表字段organization_id
                """
                organization = OrganizationMptt.objects.get(user=user)

                host_identifier = raw_data.get('host', None)
                host = Host.objects.get(host_identifier=host_identifier)

                temporary = raw_data.get('temporary', None)
                start_time = raw_data.get('start_time', None)  # 时间戳
                end_time = raw_data.get('end_time', None)  # 时间戳
                is_root = raw_data.get('is_root', None)

                if temporary is None:
                    raise Exception('temporary没有找到')

                if is_root is None:
                    raise Exception('is_root没有找到')

                if int(temporary) == 0:
                    start_time = None
                    end_time = None
                elif int(temporary) == 1:
                    if start_time is None:
                        raise Exception('临时的权限，需要开始时间')
                    else:
                        start_time = time.strftime('%Y-%m-%d %H:%M', time.localtime(float(start_time)))
                    if end_time is None:
                        raise Exception('临时的权限，需要结束时间')
                    else:
                        end_time = time.strftime('%Y-%m-%d %H:%M', time.localtime(float(end_time)))
                else:
                    raise Exception('temporary只能是0或者1')

                if int(is_root) not in (0, 1):
                    raise Exception('is_root只能是0或者1')

                UserProfileHost.objects.create(
                    user_profile=profile, host=host, start_time=start_time,
                    end_time=end_time, temporary=temporary, is_root=is_root, organization=organization)
                success = True
        except User.DoesNotExist:
            msg = '用户不存在'
            success = False
        except MultipleObjectsReturned:
            msg = '用户有重复'
            success = False
        except Host.DoesNotExist:
            msg = '主机不存在'
            success = False
        except TypeError:
            msg = '时间参数不对, 请参考文档'
            success = False
        except ValueError:
            msg = '参数格式不对，请参考文档'
            success = False
        except Exception as e:
            msg = str(e)
            success = False
        return JsonResponse({"success": success, "msg": msg})


class UserHostDel(APIView):
    """删除用户的永久服务器权限
    """

    def get(self, request, format=None):
        msg = ""
        raw_data = request.query_params

        try:
            with transaction.atomic():
                username = raw_data.get('username', None)
                user = User.objects.get(first_name=username)
                profile = user.profile

                if not user.profile:
                    profile = Profile.objects.create(user=user)

                host_identifier = raw_data.get('host', None)
                host = Host.objects.get(host_identifier=host_identifier)

                # 找到用户服务器权限的永久记录
                user_profile_host = UserProfileHost.objects.filter(user_profile=profile, host=host, temporary=0)
                user_profile_host.update(**{'is_valid': 0})
                success = True
        except User.DoesNotExist:
            msg = '用户不存在'
            success = False
        except Host.DoesNotExist:
            msg = '主机不存在'
            success = False
        except Exception as e:
            msg = str(e)
            success = False
        return JsonResponse({"success": success, "msg": msg})


class BatchModifyGameServerStatus(APIView):
    """根据条件批量修改区服状态接口
    请求参数：
    {
        'area_name': '越南',                                                 # 地区
        'project': 'jyjh',                                                  # 游戏项目英文名
        'status_dict': {'cross_allpf_1': 1, 'cross_alltestpf_1': 5},        # 区服：状态字典
    }
    返回格式：
    {
        “count”: 2, "resp": 1, "reason": "ok"                               # count： 修改区服成功个数
    }
    """
    authentication_classes = (TokenAuthentication,)

    def post(self, request, format=None):
        reason = "ok"
        count = 0
        source_ip = get_ip(request)
        raw_data = request.data
        need_params = ('project', 'area_name')
        no_exist_srv_list = []

        try:
            with transaction.atomic():
                for param in need_params:
                    if raw_data.get(param, None) is None:
                        raise ParamError("%s: 参数没有" % (param))

                status_dict = raw_data.get('status_dict', None)
                area_name = raw_data.get('area_name')
                project = GameProject.objects.get(project_name_en=raw_data.get('project'))

                if status_dict is None:
                    raise ParamError('需要%s' % status_dict)
                else:
                    my_uuid = str(uuid.uuid1())
                    for srv_id, srv_status in status_dict.items():
                        game_server = GameServer.objects.filter(project=project,
                                                                host__belongs_to_room__area__chinese_name=area_name,
                                                                srv_id=srv_id)
                        if game_server:
                            if srv_status not in [x[0] for x in GameServer.STATUS]:
                                raise ParamError("%s:%s: 没有该状态" % (srv_id, srv_status))
                            # 插入修改记录
                            for g in game_server:
                                if g.get_srv_status_display() != g.get_srv_status_tuple_remark(srv_status):
                                    GameServerActionRecord.objects.create(game_server=g, operation_type='update',
                                                                          operation_user=request.user, result=1,
                                                                          uuid=my_uuid, old_status=g.srv_status,
                                                                          source_ip=source_ip,
                                                                          remark='状态：{} ==> {}'.format(
                                                                              g.get_srv_status_display(),
                                                                              g.get_srv_status_tuple_remark(srv_status)))
                            update_data = {'srv_status': srv_status}
                            game_server.update(**update_data)
                            ws_update_game_server_action_record('update_table')
                            count = count + 1
                        else:
                            no_exist_srv_list.append(srv_id)
                if count > 0:
                    if no_exist_srv_list:
                        raise Exception(','.join(str(x) for x in no_exist_srv_list) + '：以上游戏服找不到')
                    else:
                        resp = 1
                else:
                    raise Exception('所有游戏服都找不到')

        except GameProject.DoesNotExist:
            resp = 12
            reason = '游戏项目英文名不存在'
        except GameServer.DoesNotExist as e:
            resp = 14
            reason = str(e)
        except ParamError as e:
            resp = 4
            reason = str(e)
        except Exception as e:
            reason = str(e)
            resp = 11
        return JsonResponse({"resp": resp, "reason": reason, "count": count})


class GameServerOffCallBack(APIView):
    """
    区服下线回调接口
    请求格式：
    {
        "uuid": "xxx-xxx-xxxxx",
        "srv_id": "331910", (web区服id) 或者 "srv_flag": "yy_1234", (cmdb区服id)
        "result": True or False,
        "msg": "xxx",
    }
    返回格式：
    {
        "success": True or False,
        "msg": "xxx",
    }
    """

    def is_all_done(self, obj):
        for x in obj.gameserveroffdetail_set.all():
            if x.status == 2:
                return False
        return True

    def is_all_good(self, obj):
        for x in obj.gameserveroffdetail_set.all():
            if x.status == 0:
                return False
        return True

    def post(self, request):
        msg = 'ok'
        success = True
        content = ''
        raw_data = request.data
        uuid = raw_data.get('uuid', None)
        try:
            """检查参数是否齐全"""
            need_param = ('uuid', 'sid', 'result')
            sid = raw_data.get('srv_id', None)
            result = raw_data.get('result', None)
            msg = raw_data.get('msg', '')
            for param in need_param:
                if param is None:
                    raise Exception('缺少参数：%s' % param)
            """匹配任务结果"""
            game_server_off = GameServerOff.objects.get(uuid=uuid)
            task_obj = game_server_off.gameserveroffdetail_set.filter(game_server__sid=sid)
            if task_obj:
                if result:
                    update_info = {'status': 1, 'remark': '下线成功'}
                    game_server = GameServer.objects.filter(id=task_obj[0].game_server_id)
                    game_server.update(**{'srv_status': 4})
                    write_game_server_off_log('INFO', '区服%s下线成功' % sid, game_server_off)
                else:
                    msg = str(msg)
                    msg = msg.replace('[', '').replace(']', '').replace('\"', '').replace('\'', '')
                    remark = msg
                    update_info = {'status': 0, 'remark': remark}
                    write_game_server_off_log('ERROR', '区服%s下线失败：%s' % (sid, remark), game_server_off)
                task_obj.update(**update_info)
                ws_update_game_server_off_log(game_server_off.id)
                ws_update_game_server_off_detail(game_server_off.id)
                msg = '回调成功'
            else:
                raise Exception('该任务 %s 不存在此区服 %s' % (uuid, sid))
            """检查最终状态"""
            if self.is_all_done(game_server_off):
                if self.is_all_good(game_server_off):
                    game_server_off.status = 3
                    game_server_off.save(update_fields=['status'])

                    """解锁运维管理机"""
                    list_game_server = [x.game_server for x in game_server_off.gameserveroffdetail_set.all()]
                    list_ops = [x.host.opsmanager for x in list_game_server]
                    list_ops = list(set(list_ops))
                    for ops in list_ops:
                        ops.status = 0
                        ops.save(update_fields=['status'])
                        write_game_server_off_log('INFO', '运维管理机%s解锁成功' % ops.url, game_server_off)

                    content = '所有区服下线成功'
                    write_game_server_off_log('INFO', content, game_server_off)
                else:
                    game_server_off.status = 4
                    game_server_off.save(update_fields=['status'])
                    content = '下线完成，但有失败的区服'
                    write_game_server_off_log('ERROR', content, game_server_off)
                ws_update_game_server_off_list()
                """通知任务负责人"""
                user_objs = game_server_off.get_relate_role_user()
                qq_users = ','.join([x.first_name for x in user_objs])
                wx_users = '|'.join([x.first_name for x in user_objs])
                email_users = [x.email for x in user_objs]
                subject = '项目下架结果'
                content = '项目下架任务%s，' % game_server_off.uuid + content
                email_content = make_game_server_off_email_content(content, game_server_off)
                send_qq.delay(qq_users, subject, subject, content, 'https://cmdb.cy666.com/')
                send_weixin_message.delay(touser=wx_users, content=content)
                send_mail.delay(email_users, subject, email_content)
            else:
                write_game_server_off_log('INFO', '还有未完成下线的区服，继续等待', game_server_off)
        except GameServerOff.DoesNotExist:
            success = False
            msg = 'uuid-%s不存在' % uuid
        except Exception as e:
            success = False
            msg = str(e)
        finally:
            return JsonResponse({'success': success, 'msg': msg})


class HostMigrationCallBack(APIView):
    """
    主机迁服回调接口
    请求格式：
    {
        "uuid": "xxx-xxx-xxxxx",
        "sid": "31251",
        "result": True or False,
        "msg": "xxx",
    }
    返回格式：
    {
        "success": True or False,
        "msg": "xxx",
    }
    """

    def is_all_done(self, obj):
        for x in obj.hostcompressiondetail_set.all():
            if x.migration_status == 2:
                return False
        return True

    def is_all_good(self, obj):
        for x in obj.hostcompressiondetail_set.all():
            if x.migration_status == 0:
                return False
        return True

    def post(self, request):
        msg = 'ok'
        success = True
        content = ''
        raw_data = request.data
        uuid = raw_data.get('uuid', None)
        try:
            """检查参数是否齐全"""
            need_param = ('uuid', 'sid', 'result')
            sid = raw_data.get('sid', None)
            result = raw_data.get('result', None)
            msg = raw_data.get('msg', '')
            for param in need_param:
                if param is None:
                    raise Exception('缺少参数：%s' % param)

            """判断是单个区服迁服回调，还是主机迁服回调"""
            if uuid.split('-')[-1] == 'migrate':
                """单个区服迁服"""
                record = GameServerActionRecord.objects.filter(uuid=uuid)
                msg = str(msg)
                msg = msg.replace('[', '').replace(']', '').replace('\"', '').replace('\'', '')
                if result:
                    action_result = 1
                else:
                    action_result = 0

                record.update(**{'result': action_result, 'remark': msg})
                """恢复原来的区服状态"""
                game_server = record[0].game_server
                game_server.srv_status = record[0].old_status
                game_server.save(update_fields=['srv_status'])

                """通知前端页面刷新结果"""
                notice = '区服 {} <span class="text-danger">{}</span>操作完成，请留意页面刷新结果！也可以进入<a href="/myworkflows/game_server_action_record/">区服操作记录</a>查看实时结果'.format(
                    game_server.srv_id, '迁服')
                ws_update_game_server_action(notice)
                ws_update_game_server_action_record('update_table')

                """解锁运维管理机"""
                list_game_server = [x.game_server for x in GameServerActionRecord.objects.filter(uuid=uuid)]
                list_ops = [x.get_ops_manager() for x in list_game_server]
                list_ops = list(set(list_ops))
                for ops in list_ops:
                    ops.status = '0'
                    ops.save(update_fields=['status'])

            else:
                """主机迁服"""
                """匹配任务结果"""
                host_compression = HostCompressionApply.objects.get(uuid=uuid)
                srv_detail = HostMigrateSrvDetail.objects.filter(migrate_host__apply__uuid=uuid, sid=sid)
                if srv_detail:
                    if result:
                        update_info = {'status': 1, 'remark': '迁服成功'}
                        write_host_compression_log('INFO', '区服%s迁服成功' % sid, host_compression)
                    else:
                        msg = str(msg)
                        msg = msg.replace('[', '').replace(']', '').replace('\"', '').replace('\'', '')
                        remark = msg
                        update_info = {'status': 0, 'remark': remark}
                        write_host_compression_log('ERROR', '区服%s迁服失败：%s' % (sid, remark), host_compression)
                    srv_detail.update(**update_info)
                    msg = '回调成功'
                else:
                    raise Exception('该任务 %s 不涉及此区服 %s' % (uuid, sid))
                """检查是否主机上全部区服已经迁服完成"""
                for detail in host_compression.hostcompressiondetail_set.all():
                    if detail.check_srv_statue() == 0:
                        detail.migration_status = 0
                        write_host_compression_log('ERROR', '主机%s有迁服失败的区服' % detail.ip, host_compression)
                        detail.migration_remark = '失败区服sid：' + detail.get_failure_srv()
                    if detail.check_srv_statue() == 1:
                        if detail.migration_status != 1:
                            write_host_compression_log('INFO', '主机%s全部区服已迁移成功' % detail.ip, host_compression)
                        detail.migration_status = 1
                        detail.migration_remark = '迁服成功'
                    if detail.check_srv_statue() == 2:
                        pass
                        # write_host_compression_log('INFO', '还有未完成迁移的区服，继续等待', host_compression)
                    detail.save(update_fields=['migration_status', 'migration_remark'])
                    ws_update_host_compression_log(host_compression.id)
                    ws_update_host_compression_detail(host_compression.id)
                """检查迁服任务最终状态"""
                if self.is_all_done(host_compression):
                    if self.is_all_good(host_compression):
                        host_compression.action_status = 3
                        host_compression.save()

                        """解锁运维管理机"""
                        list_host_ip = [x.ip for x in host_compression.hostcompressiondetail_set.all()]
                        list_host = Host.objects.filter(telecom_ip__in=list_host_ip)
                        list_ops = [x.opsmanager for x in list_host]
                        list_ops = list(set(list_ops))
                        for ops in list_ops:
                            ops.status = 0
                            ops.save(update_fields=['status'])
                            write_host_compression_log('INFO', '运维管理机%s解锁成功' % ops.url, host_compression)

                        content = '所有主机迁服成功'
                        write_host_compression_log('INFO', content, host_compression)
                        """任务成功后通知工单申请人"""
                        apply_user = host_compression.apply_user
                        user_objs = User.objects.get(username=apply_user)
                        qq_users = user_objs.first_name
                        wx_users = user_objs.first_name
                        email_users = [user_objs.email]
                        subject = '主机迁服结果'
                        notice_content = '主机%s申请单<%s>' % (
                            host_compression.get_type_display(), host_compression.title) + content
                        send_qq.delay(qq_users, subject, subject, notice_content, 'https://cmdb.cy666.com/')
                        send_weixin_message.delay(touser=wx_users, content=notice_content)
                        email_notice_content = make_host_compression_result_email_content(host_compression, '迁服')
                        send_mail.delay(email_users, subject, email_notice_content)
                    else:
                        host_compression.action_status = 4
                        host_compression.save()
                        content = '迁服完成，但有失败的主机'
                        write_host_compression_log('ERROR', content, host_compression)
                    ws_update_host_compression_list()
                    """通知任务负责人"""
                    user_objs = host_compression.ops
                    qq_users = user_objs.first_name
                    wx_users = user_objs.first_name
                    email_users = [user_objs.email]
                    subject = '主机迁服结果'
                    notice_content = '主机迁服申请单<%s>' % host_compression.title + content
                    send_qq.delay(qq_users, subject, subject, notice_content, 'https://cmdb.cy666.com/')
                    send_weixin_message.delay(touser=wx_users, content=notice_content)
                    send_mail.delay(email_users, subject, notice_content)

        except HostCompressionApply.DoesNotExist:
            success = False
            msg = 'uuid-%s不存在' % uuid
        except Exception as e:
            success = False
            msg = str(e)
        finally:
            return JsonResponse({'success': success, 'msg': msg})


class HostRecoverCallBack(APIView):
    """
    主机回收回调接口
    请求格式：
    {
        "uuid": "xxx-xxx-xxxxx",
        "ip": "10.10.10.10",
        "result": True or False,
        "msg": "xxx",
    }
    返回格式：
    {
        "success": True or False,
        "msg": "xxx",
    }
    """

    def is_all_done(self, obj):
        for x in obj.hostcompressiondetail_set.all():
            if x.recover_status == 2:
                return False
        return True

    def is_all_good(self, obj):
        for x in obj.hostcompressiondetail_set.all():
            if x.recover_status == 0:
                return False
        return True

    def post(self, request):
        msg = 'ok'
        success = True
        content = ''
        raw_data = request.data
        uuid = raw_data.get('uuid', None)
        try:
            """检查参数是否齐全"""
            need_param = ('uuid', 'ip', 'result')
            ip = raw_data.get('ip', None)
            result = raw_data.get('result', None)
            msg = raw_data.get('msg', '')
            for param in need_param:
                if param is None:
                    raise Exception('缺少参数：%s' % param)
            """匹配任务结果"""
            host_compression = HostCompressionApply.objects.get(uuid=uuid)
            task_obj = host_compression.hostcompressiondetail_set.filter(ip=ip)
            if task_obj:
                if result:
                    update_info = {'recover_status': 1, 'recover_remark': '回收成功'}
                    host = Host.objects.filter(telecom_ip=ip)
                    host.update(**{'status': 4})
                    write_host_compression_log('INFO', '主机%s回收成功' % ip, host_compression)
                else:
                    msg = str(msg)
                    msg = msg.replace('[', '').replace(']', '').replace('\"', '').replace('\'', '')
                    remark = msg
                    update_info = {'recover_status': 0, 'recover_remark': remark}
                    write_host_compression_log('ERROR', '主机%s回收失败：%s' % (ip, remark), host_compression)
                task_obj.update(**update_info)
                ws_update_host_compression_log(host_compression.id)
                ws_update_host_compression_detail(host_compression.id)
                msg = '回调成功'
            else:
                raise Exception('该任务 %s 不存在此主机 %s' % (uuid, ip))
            """检查最终状态"""
            if self.is_all_done(host_compression):
                if self.is_all_good(host_compression):
                    host_compression.recover_status = 3
                    host_compression.save()

                    """解锁运维管理机"""
                    list_host_ip = [x.ip for x in host_compression.hostcompressiondetail_set.all()]
                    list_host = Host.objects.filter(telecom_ip__in=list_host_ip)
                    list_ops = [x.opsmanager for x in list_host]
                    list_ops = list(set(list_ops))
                    for ops in list_ops:
                        ops.status = 0
                        ops.save(update_fields=['status'])
                        write_host_compression_log('INFO', '运维管理机%s解锁成功' % ops.url, host_compression)

                    content = '所有主机回收成功'
                    write_host_compression_log('INFO', content, host_compression)
                    """任务成功后通知工单申请人"""
                    apply_user = host_compression.apply_user
                    user_objs = User.objects.get(username=apply_user)
                    qq_users = user_objs.first_name
                    wx_users = user_objs.first_name
                    email_users = [user_objs.email]
                    subject = '主机回收结果'
                    notice_content = '主机%s申请单<%s>' % (
                        host_compression.get_type_display(), host_compression.title) + content
                    send_qq.delay(qq_users, subject, subject, notice_content, 'https://cmdb.cy666.com/')
                    send_weixin_message.delay(touser=wx_users, content=notice_content)
                    email_notice_content = make_host_compression_result_email_content(host_compression, '回收')
                    send_mail.delay(email_users, subject, email_notice_content)
                    """任务成功后通知云机器负责人回收机器"""
                    cloud_platform_administrator = SpecialUserParamConfig.objects.get(
                        param='CLOUD_PLATFORM_ADMINISTRATOR').get_user_list()
                    user_objs = User.objects.filter(username__in=cloud_platform_administrator)
                    email_users = [x.email for x in user_objs]
                    qq_users = ','.join([x.first_name for x in user_objs])
                    wx_users = '|'.join([x.first_name for x in user_objs])
                    subject = '主机回收申请'
                    notice_content = make_host_recover_email_content(host_compression)
                    send_mail.delay(email_users, subject, notice_content)
                    send_qq.delay(qq_users, subject, subject, '你有一个主机回收申请，详情请查收邮件！', 'https://cmdb.cy666.com/')
                    send_weixin_message.delay(touser=wx_users, content='你有一个主机回收申请，详情请查收邮件！')
                else:
                    host_compression.recover_status = 4
                    host_compression.save()
                    content = '回收完成，但有失败的主机'
                    write_host_compression_log('ERROR', content, host_compression)
                ws_update_host_compression_list()
                """通知任务负责人"""
                user_objs = host_compression.ops
                qq_users = user_objs.first_name
                wx_users = user_objs.first_name
                email_users = [user_objs.email]
                subject = '主机回收结果'
                notice_content = '主机回收申请单<%s>' % host_compression.title + content
                send_qq.delay(qq_users, subject, subject, notice_content, 'https://cmdb.cy666.com/')
                send_weixin_message.delay(touser=wx_users, content=notice_content)
                send_mail.delay(email_users, subject, notice_content)
            else:
                write_host_compression_log('INFO', '还有未完成回收的主机，继续等待', host_compression)
        except HostCompressionApply.DoesNotExist:
            success = False
            msg = 'uuid-%s不存在' % uuid
        except Exception as e:
            success = False
            msg = str(e)
        finally:
            return JsonResponse({'success': success, 'msg': msg})


class ModSrvOpenTimeCallBack(APIView):
    """
    修改开服时间回调接口
    请求格式：
    {
        "uuid": "xxx-xxx-xxxxx",
        "sid": "331910",             # web区服id
        "result": True or False,
        "msg": "xxx",
    }
    返回格式：
    {
        "success": True or False,
        "msg": "cmdb回调成功",
    }
    """

    def is_all_done(self, obj):
        for x in obj.modifyopensrvscheduledetail_set.all():
            if x.status == 2:
                return False
        return True

    def is_all_good(self, obj):
        for x in obj.modifyopensrvscheduledetail_set.all():
            if x.status == 0:
                return False
        return True

    def post(self, request):
        msg = 'cmdb回调成功'
        success = True
        raw_data = request.data
        uuid = raw_data.get('uuid', None)
        try:
            """检查参数是否齐全"""
            need_param = ('uuid', 'sid', 'result')
            sid = raw_data.get('sid', None)
            result = raw_data.get('result', None)
            msg = raw_data.get('msg', '')
            for param in need_param:
                if param is None:
                    raise Exception('缺少参数：%s' % param)
            """匹配任务结果"""
            modify_schedule = ModifyOpenSrvSchedule.objects.get(uuid=uuid)
            task_obj = modify_schedule.modifyopensrvscheduledetail_set.filter(game_server__sid=sid)
            if task_obj:
                if result:
                    update_info = {'status': 1, 'remark': '修改开服时间成功'}
                    write_modify_srv_open_time_schedule_log('INFO', '区服 %s 修改开服时间成功' % sid, modify_schedule)
                else:
                    remark = msg
                    update_info = {'status': 0, 'remark': remark}
                    write_modify_srv_open_time_schedule_log('ERROR', '区服 %s 修改开服时间失败：%s' % (sid, remark),
                                                            modify_schedule)
                task_obj.update(**update_info)
                ws_update_modify_srv_open_time_schedule_log(modify_schedule.id)
                ws_update_modify_srv_open_time_schedule_detail(modify_schedule.id)
            else:
                raise Exception('该任务 %s 不存在此区服 %s' % (uuid, sid))
            """检查最终状态"""
            if self.is_all_done(modify_schedule):
                if self.is_all_good(modify_schedule):
                    modify_schedule.status = 3
                    modify_schedule.save(update_fields=['status'])

                    """解锁运维管理机"""
                    list_game_server = [x.game_server for x in modify_schedule.modifyopensrvscheduledetail_set.all()]
                    list_ops = [x.host.opsmanager for x in list_game_server]
                    list_ops = list(set(list_ops))
                    for ops in list_ops:
                        ops.status = 0
                        ops.save(update_fields=['status'])
                        write_modify_srv_open_time_schedule_log('INFO', '运维管理机%s解锁成功' % ops.url, modify_schedule)

                    content = '所有区服修改开服时间成功'
                    write_modify_srv_open_time_schedule_log('INFO', content, modify_schedule)
                else:
                    modify_schedule.status = 4
                    modify_schedule.save(update_fields=['status'])
                    content = '修改开服时间完成，但有失败的区服'
                    write_modify_srv_open_time_schedule_log('ERROR', content, modify_schedule)
                """ws刷新任务列表"""
                ws_modify_srv_open_time_schedule_list()
                """通知任务负责人"""
                user_objs = modify_schedule.get_relate_role_user()
                qq_users = ','.join([x.first_name for x in user_objs])
                wx_users = '|'.join([x.first_name for x in user_objs])
                email_users = [x.email for x in user_objs]
                subject = '修改开服时间结果'
                content = '修改开服时间任务 %s，%s' % (modify_schedule.uuid, content)
                email_content = make_modsrv_opentime_email_content(content, modify_schedule)
                send_qq.delay(qq_users, subject, subject, content, 'https://cmdb.cy666.com/')
                send_weixin_message.delay(touser=wx_users, content=content)
                send_mail.delay(email_users, subject, email_content)
            else:
                write_modify_srv_open_time_schedule_log('INFO', '还有未完成修改开服时间的区服，继续等待', modify_schedule)
        except ModifyOpenSrvSchedule.DoesNotExist:
            success = False
            msg = 'uuid-%s 不存在' % uuid
        except Exception as e:
            success = False
            msg = str(e)
        finally:
            return JsonResponse({'success': success, 'msg': msg})


class GameServerActionCallback(APIView):
    """
    区服操作回调接口
    请求格式：
    {
        'uuid': 'xxxx-x-x-xxxx-xxx',
        'project': 'jyjh',
        'area': '大陆',
        'srv_id': 'cross_yy_4',
        'action_type': 'stop',
        'result': 1     # 1:成功   0:失败,
        'msg': '成功或者失败的原因'
    }
    返回格式：
    {
        'success': True,
        'msg': '回调成功'
    }
    """

    def is_all_done(self, uuid):
        for x in GameServerActionRecord.objects.filter(uuid=uuid):
            if x.status == 2:
                return False
        return True

    def post(self, request):
        success = True
        msg = '回调成功'
        try:
            raw_data = request.data
            """检查参数是否齐全"""
            project = raw_data.get('project', '')
            srv_id = raw_data.get('srv_id', '')
            action_type = raw_data.get('action_type', '')
            result = raw_data.get('result', '')
            remark = raw_data.get('msg', '')
            uuid = raw_data.get('uuid', '')
            need_param = ('project', 'srv_id', 'action_type', 'result', 'msg', 'uuid')
            for param in need_param:
                if param == '':
                    raise Exception('缺少参数：%s' % param)

            game_server = GameServer.objects.filter(srv_id=srv_id, project__project_name_en=project)

            if str(result) not in ('0', '1'):
                raise Exception('参数 {} 只能是 0 或者 1'.format(result))

            record = GameServerActionRecord.objects.filter(uuid=uuid, game_server=game_server,
                                                           operation_type=action_type)
            if not record:
                raise Exception('没有匹配的区服操作记录：{}'.format(uuid))

            """恢复区服原来的状态"""
            game_server.update(**{'srv_status': record[0].old_status})

            record.update(**{'result': result, 'remark': remark})
            """通知前端页面刷新结果"""
            notice = '区服 {} <span class="text-danger">{}</span>操作完成，请留意页面刷新结果！也可以进入<a href="/myworkflows/game_server_action_record/">区服操作记录</a>查看实时结果'.format(
                srv_id, action_type)
            ws_update_game_server_action(notice)
            ws_update_game_server_action_record('update_table')

            """判断相同uuid的区服是否全部完成，是则解锁运维管理机"""
            if self.is_all_done:
                """解锁运维管理机"""
                list_game_server = [x.game_server for x in GameServerActionRecord.objects.filter(uuid=uuid)]
                list_ops = [x.get_ops_manager() for x in list_game_server]
                list_ops = list(set(list_ops))
                for ops in list_ops:
                    ops.status = '0'
                    ops.save(update_fields=['status'])

        except GameServer.DoesNotExist:
            msg = '区服 {}-{} 不存在'.format(project, srv_id)
        except GameProject.DoesNotExist:
            msg = '项目 {} 不存在'.format(project)
        except Exception as e:
            success = False
            msg = str(e)
        finally:
            return JsonResponse({'success': success, 'msg': msg})


class HostInitializeCallback(APIView):
    """
    主机安装salt-minion和初始化结果回调接口
    input:
    {
        'telecom_ip': '11.22.33.44',
        'type': 1,                   # 1: 安装salt-minion结果回调，   2: 主机初始化结果回调
        'result': True or False,
        'msg': '安装成功或者失败的原因备注',
    }
    return:
    {
        'success': True,
        'msg': 'cmdb回调成功'
    }
    """

    def post(self, request):
        success = True
        msg = 'cmdb回调成功'
        level = 'INFO'
        # 提取参数
        raw_data = json.loads(request.data)
        telecom_ip = raw_data.get('minion_ip', '')
        host_initialize = HostInitialize.objects.get(telecom_ip=telecom_ip)
        try:

            callback_type = raw_data.get('type', '')
            result = raw_data.get('result', '')
            remark = raw_data.get('msg', '')
            need_param = ('telecom_ip', 'type', 'result')

            # 检查参数是否为空
            for param in need_param:
                if param == '' or param is None:
                    raise Exception('缺少参数：%s' % param)

            # 参数做一些转化
            assert type(result) is bool, 'result必须为布尔值'
            if result:
                status = 2
            else:
                status = 3

            # 更新状态
            if str(callback_type) == '1':
                host_initialize.install_status = status
                host_initialize.install_remark = remark
                if result:
                    log = '收到回调，安装salt-minion成功'
                    write_host_initialize_log(level, log, host_initialize)
                    # 开始test.ping异步测试
                    write_host_initialize_log(level, '【步骤2】-【开始】-【进行 test.ping 测试】', host_initialize)
                    saltstack_test_ping_tasks.delay(telecom_ip, host_initialize.id)
                else:
                    success = False
                    level = 'ERROR'
                    log = '收到回调，安装salt-minion失败: {}'.format(msg)
                    write_host_initialize_log(level, log, host_initialize)
                    host_initialize.save(update_fields=['install_status', 'install_remark'])
                    # 发送邮件/QQ/微信消息
                    to_list = [host_initialize.add_user.email]
                    first_name = host_initialize.add_user.first_name
                    subject = '主机初始化结果-{}'.format(host_initialize.telecom_ip)
                    content = '主机初始化【步骤1】-【安装salt-minion】失败，IP: {}，请登录cmdb查看详细日志！'.format(host_initialize.telecom_ip)
                    if to_list:
                        send_mail.delay(to_list, subject, content)
                    send_qq.delay(first_name, subject, subject, content, '')
                    send_weixin_message.delay(touser=first_name, content=content)
            elif str(callback_type) == '2':
                host_initialize.initialize_status = status
                host_initialize.initialize_remark = remark
                if result:
                    log = '收到回调，初始化成功'
                else:
                    success = False
                    level = 'ERROR'
                    log = '收到回调，初始化失败: {}'.format(msg)
                write_host_initialize_log(level, log, host_initialize)
                host_initialize.save(
                    update_fields=['initialize_status', 'initialize_remark'])
            else:
                raise Exception('未知的回调类型，type只能是1或2')

            # 刷新websocket
            ws_update_host_initialize_list()

        except HostInitialize.DoesNotExist:
            success = False
            msg = '主机初始化记录不存在，请确认主机IP是否正确'
        except Exception as e:
            success = False
            msg = str(e)
        finally:
            if not success:
                # 发送邮件/QQ/微信消息
                to_list = [host_initialize.add_user.email]
                first_name = host_initialize.add_user.first_name
                subject = '主机初始化结果-{}'.format(host_initialize.telecom_ip)
                content = '主机初始化【步骤1】-【安装salt-minion】失败，IP: {}，请登录cmdb查看详细日志！'.format(host_initialize.telecom_ip)
                if to_list:
                    send_mail.delay(to_list, subject, content)
                send_qq.delay(first_name, subject, subject, content, '')
                send_weixin_message.delay(touser=first_name, content=content)
            return JsonResponse({'success': success, 'msg': msg})


class VersionUpdatePlan(APIView):
    """
    获取审批完成的版本更新计划，默认获取开始时间为当天
    """

    def post(self, request):
        success = True
        data = []
        try:
            raw_data = request.data
            update_date = raw_data.get('update_date', '')
            if update_date:
                objs = VersionUpdate.objects.filter(start_time__date=update_date)
            else:
                objs = VersionUpdate.objects.filter(start_time__date=datetime.datetime.today())
            for obj in objs:
                if obj.workflows.last().state.name == '完成':
                    data.append({'project': obj.project.project_name, 'area': obj.area.chinese_name,
                                 'start_time': str(obj.start_time), 'end_time': str(obj.end_time),
                                 'applicant': obj.applicant.username, 'title': obj.title})
        except Exception as e:
            success = False
            data = str(e)
        finally:
            return JsonResponse({'success': success, 'data': data})
