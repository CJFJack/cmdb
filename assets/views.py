# -*- encoding: utf-8 -*-
from django.shortcuts import render, render_to_response, reverse
from django.http import JsonResponse, HttpResponseRedirect
from django.db import IntegrityError
from django.db import transaction
from django.db.models import Q
from django.db.models import Count
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.http import FileResponse
from assets.salt_api_tasks import salt_init
from assets.risk_command import risk_command

import re
import json
import hashlib
from datetime import datetime, timedelta
import copy
import time
import xlwt
import uuid
import shlex

from assets.models import *
from assets.utils import *
from assets.excel_utils import gen_host_excel
from users.models import UserProfileHost
from users.models import Profile, OrganizationMptt, Role
from .forms import UploadFileForm

from myworkflows.config import FAILURE_DECLARE_WITH_ADMIN
from myworkflows.config import NETWORK_ADMINISTRATOR
from myworkflows.config import CC_NETWORK_ADMINISTRATOR
from myworkflows.models import GameServer

from cmdb.url_to_title import *
from cmdb.utils import *
from tasks import execute_salt_task
from tasks import refresh_txcloud_cdn
from tasks import refresh_bscloud_cdn
from tasks import install_salt_minion
from tasks import saltstack_host_reboot
from tasks import saltstack_host_import
from django.views import generic
from assets.TXcloudCdnRefresh import QcloudRefreshResultQuery
from assets.BScloudCdnRefresh import BScloudRefreshResultQuery
from cmdb.logs import *
from django.core.files import File
from cmdb.settings import SALT_MASTER_HOST


def error_version(request):
    '''浏览器是ie跳转'''
    return render(request, 'error_version.html')


def hostAPI(request):
    """主机的api文档"""

    if request.method == 'GET':
        if request.user.is_superuser:
            return render(request, 'hostAPI.html')
        else:
            return render(request, '403.html')


def server_permission_api(request):
    '''服务器权限接口文档'''
    if request.method == 'GET':
        if request.user.is_superuser:
            return render(request, 'server_permission_api_doc.html')
        else:
            return render(request, '403.html')


def calendar(request):
    'full calendar页面的展示'

    if request.method == "GET":
        head = {"value": "FullCalendar"}
        return render(request, 'monitor.html', {'head': head})


def add_data_fullcalendar(request):
    '给fullcalendar添加一个事件'
    if request.method == "POST":
        msg = 'ok'

        # 所有post过来的数据
        add_data = json.loads(request.body.decode('utf-8'))

        # 去掉id
        add_data.pop('id')

        try:
            belongs_to_game_project = GameProject.objects.get(id=add_data.pop('belongs_to_game_project'))
            related_user = User.objects.get(id=add_data.pop('related_user'))
            add_data['title'] = belongs_to_game_project.project_name + '#' + related_user.username
            FullCalendar.objects.create(**add_data)
            success = True
        except GameProject.DoesNotExist:
            msg = '游戏项目不存在'
            success = False
        except User.DoesNotExist:
            msg = '用户不存在'
            success = False
        except Exception as e:
            msg = str(e)
            success = False
        return JsonResponse({'data': success, 'msg': msg})


def edit_data_fullcalendar(request):
    '修改fullcalendar事件'

    if request.method == "POST":
        msg = 'ok'

        # 所有post过来的数据
        edit_data = json.loads(request.body.decode('utf-8'))

        try:
            fc_obj = FullCalendar.objects.filter(id=edit_data.pop('id'))
            belongs_to_game_project = GameProject.objects.get(id=edit_data.pop('belongs_to_game_project'))
            related_user = User.objects.get(id=edit_data.pop('related_user'))
            edit_data['title'] = belongs_to_game_project.project_name + '#' + related_user.username
            fc_obj.update(**edit_data)
            success = True
        except GameProject.DoesNotExist:
            msg = '游戏项目不存在'
            success = False
        except User.DoesNotExist:
            msg = '用户不存在'
            success = False
        except Exception as e:
            msg = str(e)
            success = False
        return JsonResponse({'data': success, 'msg': msg})


def add_or_edit_game_project(request):
    '增加或者修改游戏项目'

    if request.method == "POST":
        raw_data = json.loads(request.body.decode('utf-8'))
        msg = 'ok'
        success = True
        editFlag = raw_data.pop('editFlag')
        id = raw_data.pop('id')

        leader = raw_data.pop('leader')
        try:
            leader = User.objects.get(id=leader)
        except User.DoesNotExist:
            leader = None
        raw_data['leader'] = leader

        related_user = raw_data.pop('related_user')
        related_user = list(User.objects.filter(id__in=related_user))

        relate_role = raw_data.pop('relate_role')
        relate_role = list(Role.objects.filter(id__in=relate_role))

        related_organization = raw_data.pop('related_organization', '')
        if related_organization != '':
            org_obj = OrganizationMptt.objects.filter(id__in=related_organization)
        else:
            org_obj = False

        if raw_data.get('is_game_project') == "1":
            raw_data['is_game_project'] = True
        else:
            raw_data['is_game_project'] = False

        cloud_account = raw_data.pop('cloud_account', '')
        if cloud_account:
            raw_data['content_type_id'] = cloud_account.split('-')[0]
            raw_data['object_id'] = cloud_account.split('-')[-1]

        raw_data['softlist'] = json.dumps(raw_data.get('softlist', ''))
        area = raw_data.pop('area')
        if area is not None:
            raw_data['area'] = Area.objects.get(pk=area)

        try:
            # 对于空的svn_repo 设置为None
            if not raw_data.get('svn_repo'):
                raw_data['svn_repo'] = None

            if editFlag:
                g = GameProject.objects.filter(id=id)
                g.update(**raw_data)
                g[0].related_user.clear()
                g[0].related_user.add(*related_user)
                g[0].role_set.clear()
                g[0].role_set.add(*relate_role)
                gp = g[0]
                for x in gp.organizationmptt_set.all():
                    org = OrganizationMptt.objects.get(pk=x.id)
                    org.project.remove(gp)
                if org_obj:
                    for org in org_obj:
                        org.project.add(gp)
            else:
                if User.objects.get(id=request.user.id).has_perm('users.add_game_project_obj'):
                    gp = GameProject.objects.create(**raw_data)
                    gp.related_user.add(*related_user)
                    gp.role_set.add(*relate_role)
                    if org_obj:
                        for org in org_obj:
                            org.project.add(gp)
                else:
                    raise PermissionDenied

            # 如果初始化参数都不为空，则调用API接口，生成主机初始化所需要的sls文件
            call = True
            need_params = ('web_ip', 'manager_wan_ip', 'manager_lan_ip', 'zabbix_proxy_ip', 'area', 'softlist')
            for param in need_params:
                field_val = gp.__getattribute__(param)
                if field_val is None or field_val == '':
                    call = False
            if call:
                success, msg = call_host_start_pro(game_project=gp)
                # msg = '脚本打包和salt初始化配置完成，脚本下载地址为:http://119.29.79.89:8081/manager/manager_test.tar.gz'
                if not success:
                    raise Exception('调用startpro接口失败: {}'.format(msg))

        except GameProject.DoesNotExist:
            msg = '项目不存在'
            success = False
        except PermissionDenied:
            msg = '你没有增加游戏项目的权限'
            success = False
        except Exception as e:
            msg = str(e)
            success = False

        return JsonResponse({'data': success, 'msg': msg})


def add_or_edit_project_group(request):
    '增加或者修改游戏项目分组'

    if request.method == "POST":
        raw_data = json.loads(request.body.decode('utf-8'))
        msg = 'ok'
        id = raw_data.pop('id')
        editFlag = raw_data.pop('editFlag')
        project = raw_data.pop('project')
        project_group_leader = raw_data.pop('project_group_leader')
        group_section = raw_data.pop('group_section', '0')
        try:
            project = GameProject.objects.get(id=project)
            raw_data['project'] = project

            if group_section == '0':
                group_section = None
            else:
                group_section = GroupSection.objects.get(id=group_section)
            raw_data['group_section'] = group_section

            project_group_leader = User.objects.get(id=project_group_leader)
            raw_data['project_group_leader'] = project_group_leader

            if editFlag:
                pg = ProjectGroup.objects.filter(id=id)
                pg.update(**raw_data)
                success = True
            else:
                ProjectGroup.objects.create(**raw_data)
                success = True
        except User.DoesNotExist:
            msg = '组长不存在'
            success = False
        except GameProject.DoesNotExist:
            msg = '游戏项目不存在'
            success = False
        except Group.DoesNotExist:
            msg = '部门分组不存在'
            success = False
        except Exception as e:
            msg = str(e)
            success = False
        return JsonResponse({'data': success, 'msg': msg})


def add_or_edit_host(request):
    """增加或者修改主机"""

    if request.method == "POST":
        raw_data = json.loads(request.body.decode('utf-8'))
        msg = 'ok'
        editFlag = raw_data.pop('editFlag')
        id = raw_data.pop('id')
        source_ip = get_ip(request)

        try:
            if editFlag:
                h = Host.objects.filter(id=id)
                belongs_to_game_project = GameProject.objects.get(id=raw_data.pop('belongs_to_game_project'))
                raw_data['belongs_to_game_project'] = belongs_to_game_project

                belongs_to_room = Room.objects.get(id=raw_data.pop('belongs_to_room'))
                raw_data['belongs_to_room'] = belongs_to_room

                belongs_to_business = Business.objects.get(id=raw_data.pop('belongs_to_business'))
                raw_data['belongs_to_business'] = belongs_to_business

                if raw_data.get('opsmanager') != "0":
                    opsmanager = OpsManager.objects.get(id=raw_data.pop('opsmanager'))
                    raw_data['opsmanager'] = opsmanager
                else:
                    raw_data.pop('opsmanager')

                if raw_data.get('belongs_to_host') == '':
                    raw_data['belongs_to_host'] = None

                # 原来主机的状态
                old_status = h[0].status

                # 原来主机的项目英文名
                raw_project_name_en = h[0].belongs_to_game_project.project_name_en

                # 后缀
                suffix = '.' + raw_project_name_en + 'bak'

                """2019.2修改，机器状态修改为已归还后IP不增加后缀"""
                if str(old_status) != str(raw_data['status']):
                    if str(raw_data['status']) == '4':
                        # if raw_data['internal_ip']:
                        #     raw_data['internal_ip'] += suffix
                        # if raw_data['telecom_ip']:
                        #     raw_data['telecom_ip'] += suffix
                        # if raw_data['unicom_ip']:
                        #     raw_data['unicom_ip'] += suffix

                        # 归还的机器修改服务器权限为过期状态
                        UserProfileHost.objects.filter(host=h[0]).update(**{'is_valid': 0})

                """记录所有字段之前值"""
                old_host = h[0].show_all()
                old_host.pop('area')
                """更新object"""
                h.update(**raw_data)
                """记录所有字段之后值"""
                new_host = h[0].show_all()
                new_host.pop('area')

                """找出差异字段，并记录操作日志"""
                alert_fields_list = []
                for k, v in new_host.items():
                    if v != old_host[k]:
                        alert_fields_list.append(k)
                for x in alert_fields_list:
                    alter_field = Host._meta.get_field(x).help_text
                    HostHistoryRecord.objects.create(host=h[0], operation_user=request.user, type=2,
                                                     alter_field=alter_field,
                                                     old_content=old_host[x], new_content=new_host[x],
                                                     source_ip=source_ip)

                success = True
            else:
                if User.objects.get(id=request.user.id).has_perm('users.add_host_obj'):
                    belongs_to_game_project = GameProject.objects.get(id=raw_data.pop('belongs_to_game_project'))
                    raw_data['belongs_to_game_project'] = belongs_to_game_project

                    belongs_to_room = Room.objects.get(id=raw_data.pop('belongs_to_room'))
                    raw_data['belongs_to_room'] = belongs_to_room

                    belongs_to_business = Business.objects.get(id=raw_data.pop('belongs_to_business'))
                    raw_data['belongs_to_business'] = belongs_to_business

                    if raw_data.get('opsmanager') != "0":
                        opsmanager = OpsManager.objects.get(id=raw_data.pop('opsmanager'))
                        raw_data['opsmanager'] = opsmanager
                    else:
                        raw_data.pop('opsmanager')

                    """2019.2修改，机器状态修改为已归还后IP不增加后缀"""
                    # if str(raw_data['status']) == '4':
                    #     if raw_data['internal_ip']:
                    #         raw_data['internal_ip'] += '.bak'
                    #     if raw_data['telecom_ip']:
                    #         raw_data['telecom_ip'] += '.bak'
                    #     if raw_data['unicom_ip']:
                    #         raw_data['unicom_ip'] += '.bak'

                    host = Host.objects.create(**raw_data)

                    """记录新增主机记录"""
                    HostHistoryRecord.objects.create(host=host, operation_user=request.user, type=1,
                                                     source_ip=source_ip)

                    success = True
                else:
                    raise PermissionDenied
        except PermissionDenied:
            msg = '你没有增加主机的权限'
            success = False
        except GameProject.DoesNotExist:
            msg = '游戏项目不存在'
            success = False
        except Room.DoesNotExist:
            msg = '机房名不存在'
            success = False
        except Business.DoesNotExist:
            msg = '业务类型不存在'
            success = False
        except Exception as e:
            msg = str(e)
            success = False
        return JsonResponse({'data': success, 'msg': msg})


def add_or_edit_business(request):
    '增加或者修改业务类型'

    if request.method == "POST":
        raw_data = json.loads(request.body.decode('utf-8'))
        msg = 'ok'
        editFlag = raw_data.pop('editFlag')
        id = raw_data.pop('id')

        try:
            if editFlag:
                b = Business.objects.filter(id=id)
                b.update(**raw_data)
                success = True
            else:
                if User.objects.get(id=request.user.id).has_perm('users.add_business_obj'):
                    Business.objects.create(**raw_data)
                    success = True
                else:
                    raise PermissionDenied
        except PermissionDenied:
            msg = '你没有增加业务类型的权限'
            success = False
        except Exception as e:
            msg = str(e)
            success = False

        return JsonResponse({'data': success, 'msg': msg})


def add_or_edit_room(request):
    """增加或者修改机房信息"""

    if request.method == "POST":
        raw_data = json.loads(request.body.decode('utf-8'))
        msg = 'ok'
        editFlag = raw_data.pop('editFlag')
        id = raw_data.pop('id')
        area_id = raw_data.pop('area', '')
        area_obj = Area.objects.get(pk=area_id)
        raw_data['area'] = area_obj

        try:
            if editFlag:
                r = Room.objects.filter(id=id)
                r.update(**raw_data)
                success = True
            else:
                if User.objects.get(id=request.user.id).has_perm('users.add_room_obj'):
                    Room.objects.create(**raw_data)
                    success = True
                else:
                    raise PermissionDenied
        except PermissionDenied:
            msg = '你没有增加机房的权限'
            success = False
        except Exception as e:
            msg = str(e)
            success = False

        return JsonResponse({'data': success, 'msg': msg})


def add_or_edit_ops_manager(request):
    '增加或者修改运维管理机'

    if request.method == "POST":
        raw_data = json.loads(request.body.decode('utf-8'))
        msg = 'ok'
        editFlag = raw_data.pop('editFlag')
        id = raw_data.pop('id')

        project = GameProject.objects.get(id=raw_data.get('project'))
        raw_data['project'] = project

        room = Room.objects.get(id=raw_data.get('room'))
        raw_data['room'] = room

        try:
            if editFlag:
                om = OpsManager.objects.filter(id=id)
                om.update(**raw_data)
                success = True
            else:
                if User.objects.get(id=request.user.id).has_perm('users.add_host_obj'):
                    OpsManager.objects.create(**raw_data)
                    success = True
                else:
                    raise PermissionDenied
        except PermissionDenied:
            msg = '你没有增加的权限'
            success = False
        except GameProject.DoesNotExist:
            msg = '项目不存在'
            success = False
        except Room.DoesNotExist:
            msg = '机房不存在'
            success = False
        except Exception as e:
            msg = str(e)
            success = False
        return JsonResponse({'data': success, 'msg': msg})


def cmdb_page(request, raw_url):
    """页面的展示"""

    if request.method == "GET":
        value = url2title.get(raw_url)
        permission = 'users' + '.' + url2view_perm.get(raw_url)
        if raw_url == 'duty_schedule':
            head = {'value': value, 'username': request.user.username}
            all_project_id = list(set([x['belongs_to_game_project'] for x in DutySchedule.objects.values(
                'belongs_to_game_project')]))
            all_project = [
                {'id': x.id, 'text': x.project_name} for x in GameProject.objects.filter(id__in=all_project_id)
            ]
            all_ops_user = Group.objects.get(name='运维部').user_set.all()
            exclude_users = copy.deepcopy(NETWORK_ADMINISTRATOR)
            exclude_users.extend(['张文辉', '黎小龙', '严文驰', '运维公共账户'])
            all_ops_user = [
                {'id': x.id, 'text': x.username} for x in all_ops_user if x.is_active and
                                                                          x.username not in exclude_users
            ]
            data = {'all_ops_user': all_ops_user, 'all_project': all_project}
            head['data'] = data
            html_file = raw_url + '.html'
            return render(request, html_file, {'head': head, 'user': request.user})
        if raw_url == 'ops_manager_list':
            if request.user.is_superuser:
                head = {'value': value, 'username': request.user.username}
                all_status = dict(Host.STATUS)
                all_class = dict(Host.CLASSES)
                all_project_id = [
                    x['belongs_to_game_project'] for x in Host.objects.values(
                        'belongs_to_game_project').annotate(count=Count('belongs_to_game_project'))
                ]
                all_project = [{'id': x.id, 'text': x.project_name} for x in GameProject.objects.filter(
                    id__in=all_project_id)]
                all_room = [{'id': x.id, 'text': x.area.chinese_name + '-' + x.room_name} for x in Room.objects.all()]
                all_type = dict(Host.TYPE)
                all_business = [{'id': x.id, 'text': x.business_name} for x in Business.objects.all()]
                all_system = dict(Host.SYSTEM)
                all_internet = dict(Host.INTERNET)
                data = {
                    'all_status': all_status, 'all_class': all_class, 'all_project': all_project, 'all_room': all_room,
                    'all_type': all_type, 'all_business': all_business, 'all_system': all_system,
                    'all_internet': all_internet,
                }
                head['data'] = data
                html_file = raw_url + '.html'
                return render(request, html_file, {'head': head, 'user': request.user})
            else:
                return render(request, '403.html')
        if raw_url == 'host':
            head = {'value': value, 'username': request.user.username}
            all_status = dict(Host.STATUS)
            all_class = dict(Host.CLASSES)
            all_project_id = [
                x['belongs_to_game_project'] for x in Host.objects.values(
                    'belongs_to_game_project').annotate(count=Count('belongs_to_game_project'))
            ]
            all_project = [{'id': x.id, 'text': x.project_name} for x in GameProject.objects.filter(
                id__in=all_project_id)]
            all_room = [{'id': x.id, 'text': x.area.chinese_name + '-' + x.room_name} for x in Room.objects.all()]
            all_type = dict(Host.TYPE)
            all_business = [{'id': x.id, 'text': x.business_name} for x in Business.objects.all()]
            all_system = dict(Host.SYSTEM)
            all_internet = dict(Host.INTERNET)
            all_opsmanager = [{'id': x.id, 'text': x.room.room_name + '-' + x.project.project_name + '-' + x.url}
                              for x in OpsManager.objects.all()]
            data = {
                'all_status': all_status, 'all_class': all_class, 'all_project': all_project, 'all_room': all_room,
                'all_type': all_type, 'all_business': all_business, 'all_system': all_system,
                'all_internet': all_internet, 'all_opsmanager': all_opsmanager,
            }
            head['data'] = data
            html_file = raw_url + '.html'
            return render(request, html_file, {'head': head, 'user': request.user})
        if User.objects.get(id=request.user.id).has_perm(permission):
            if raw_url == 'game_project_list':
                all_cloud_account = [{'id': str(ContentType.objects.get_for_model(account).id) + '-' + str(account.id),
                                      'text': account.cloud.name + '-' + account.remark} for account in
                                     TecentCloudAccount.objects.all()]
                all_role = Role.objects.all()
                all_status = GameProject.STATUS
                all_area = Area.objects.all()
                success, all_soft = get_host_install_soft()
                # success, all_soft = True, []
                if not success:
                    all_soft = dict()
                head = {'value': value, 'username': request.user.username, 'all_cloud_account': all_cloud_account,
                        'all_role': all_role, 'all_status': all_status, 'all_area': all_area, 'all_soft': all_soft}
                data = GameProject.PTYPE
                head['data'] = data
            else:
                head = {'value': value, 'username': request.user.username}
            html_file = raw_url + '.html'
            return render(request, html_file, {'head': head, 'user': request.user})
        else:
            return render(request, '403.html', {'head': {'username': request.user.username}})


def cmdb_data_obj(request, raw_url):
    """cmdb的数据请求部分"""

    # 从url到model的映射
    obj = url2obj.get(raw_url)

    if request.method == "GET":

        raw_get = request.GET.dict()

        '''
            下面的这些参数都是datatables的关于
            server-side的参数，用于请求后端的数据
            参数说明:
            search[value]: 全局所搜的值
            start: 分页的页面
            length: 每页展示的个数
            draw:计数器
            详细的文档可以参考: https://datatables.net/manual/server-side
        '''
        search_value = raw_get.get('search[value]', '')
        start = int(raw_get.get('start', 0))
        draw = raw_get.get('draw', 0)
        length = int(raw_get.get('length', 10))

        raw_data = ''

        if raw_url == "cmdb_duty_schedule":
            data_tables_game_project = raw_get.get('data_tables_game_project')
            if data_tables_game_project == '0':
                query = obj.objects.select_related(
                    'tuesday_person').select_related(
                    'thursday_person').select_related(
                    'weekdays_person').select_related(
                    'weekend_person').filter(
                    Q(start_date__contains=search_value) |
                    Q(end_date__contains=search_value) |
                    Q(tuesday_person__username__icontains=search_value) |
                    Q(thursday_person__username__icontains=search_value) |
                    Q(weekdays_person__username__icontains=search_value) |
                    Q(weekend_person__username__icontains=search_value))
                raw_data = query[start: start + length]
                recordsTotal = query.count()
                # recordsFiltered = len(raw_data)
            else:
                belongs_to_game_project = GameProject.objects.get(id=data_tables_game_project)
                query = obj.objects.select_related('tuesday_person').select_related(
                    'thursday_person').select_related(
                    'weekdays_person').select_related('weekend_person').filter(
                    Q(belongs_to_game_project=belongs_to_game_project) & (
                            Q(start_date__contains=search_value) |
                            Q(end_date__contains=search_value) |
                            Q(tuesday_person__username__icontains=search_value) |
                            Q(thursday_person__username__icontains=search_value) |
                            Q(weekdays_person__username__icontains=search_value) |
                            Q(weekend_person__username__icontains=search_value)))
                raw_data = query[start: start + length]
                recordsTotal = query.count()
                # recordsFiltered = len(raw_data)
        elif raw_url == 'project_group_list':
            id = raw_get.get('id')
            recordsTotal = obj.objects.filter(project=id).count()
            raw_data = obj.objects.filter(project=id)
            # recordsFiltered = recordsTotal
        elif raw_url == 'ops_manager_list':
            """
            2018.12修改：
                1. superuser拥有整个操作整个页面的权限
                2. 拥有查看主机页面权限的staff拥有查看所有主机的权限
                3. 拥有查看主机页面权限的普通用户只能查看所在部门负责项目的主机
            """
            sub_query = Q()
            search_value = search_value.split('-')[-1]
            if not (request.user.is_superuser or request.user.is_staff):
                org_user_obj = OrganizationMptt.objects.get(user=request.user)
                projects_obj_list = org_user_obj.get_user_charge_project()
                for project in projects_obj_list:
                    sub_query.add(Q(project=project), Q.OR)
            query = obj.objects.select_related('project').select_related('room').filter(
                (Q(project__project_name__icontains=search_value) |
                 Q(room__room_name__icontains=search_value) |
                 Q(url__icontains=search_value)) & sub_query)
            recordsTotal = query.count()
            raw_data = query.all()
        elif raw_url == 'game_project_list':
            sub_query = Q()

            filter_role = raw_get.get('filter_role', '全部')
            filter_status = raw_get.get('filter_status', '全部')
            filter_is_game_project = raw_get.get('filter_is_game_project', '100')
            filter_project_type = raw_get.get('filter_project_type', '100')

            if str(filter_status) != '100':
                sub_query.add(Q(status=filter_status), Q.AND)
            if str(filter_role) != '100':
                role = Role.objects.get(pk=filter_role)
                sub_query.add(Q(role=role), Q.AND)
            if str(filter_is_game_project) != '100':
                sub_query.add(Q(is_game_project=filter_is_game_project), Q.AND)
            if str(filter_project_type) != '100':
                sub_query.add(Q(project_type=filter_project_type), Q.AND)

            """
            1. superuser拥有整个操作整个页面的权限
            2. 拥有查看主机页面权限的普通用户只能查看所在部门负责项目的主机
            """
            if request.user.is_superuser:
                query = obj.objects.prefetch_related('role_set').filter(sub_query)
            else:
                org_user_obj = OrganizationMptt.objects.get(user=request.user)
                projects_obj_list = org_user_obj.get_user_charge_project()
                sub_query.add(Q(id__in=[p.id for p in projects_obj_list]), Q.AND)
                query = obj.objects.prefetch_related('role_set').filter(sub_query)

            recordsTotal = query.count()
            raw_data = query.all()
        else:
            recordsTotal = obj.objects.count()
            raw_data = obj.objects.all()
            # recordsFiltered = recordsTotal
        data = {"data": [i.show_all() for i in raw_data], 'draw': draw, 'recordsTotal': recordsTotal,
                'recordsFiltered': recordsTotal}
        return JsonResponse(data)

    if request.method == "POST":

        raw_get = request.POST.dict()

        search_value = raw_get.get('search[value]', '')
        start = int(raw_get.get('start', 0))
        draw = raw_get.get('draw', 0)
        length = int(raw_get.get('length', 10))

        raw_data = ''

        if raw_url == 'cmdb_fullcalendar':
            raw_data = obj.objects.all()
            data = [i.show_all() for i in raw_data]
            return JsonResponse(data, safe=False)
        elif raw_url == "cmdb_duty_schedule":
            # 自定义查询标签
            filter_belongs_to_game_project = raw_get.get('filter_belongs_to_game_project', '全部')
            filter_weekdays_person = raw_get.get('filter_weekdays_person', '全部')
            filter_weekend_person = raw_get.get('filter_weekend_person', '全部')
            filter_start_date = raw_get.get('filter_start_date', '')
            filter_end_date = raw_get.get('filter_end_date', '')
            # 添加sub_query
            sub_query = Q()

            if filter_belongs_to_game_project != '全部':
                project = GameProject.objects.get(id=filter_belongs_to_game_project)
                sub_query.add(Q(belongs_to_game_project=project), Q.AND)

            if filter_weekdays_person != '全部':
                user = User.objects.get(id=filter_weekdays_person)
                sub_query.add(Q(weekdays_person=user), Q.AND)

            if filter_weekend_person != '全部':
                user = User.objects.get(id=filter_weekend_person)
                sub_query.add(Q(weekend_person=user), Q.AND)

            if filter_start_date:
                sub_query.add(Q(start_date__lte=filter_start_date, end_date__gte=filter_start_date), Q.AND)

            if filter_end_date:
                sub_query.add(Q(end_date__gte=filter_end_date, start_date__lte=filter_end_date), Q.AND)

            if search_value:
                query = DutySchedule.objects.select_related(
                    'belongs_to_game_project').prefetch_related(
                    'weekdays_person').prefetch_related(
                    'weekend_person').filter(
                    Q(belongs_to_game_project__project_name__icontains=search_value) |
                    Q(weekend_person__username__icontains=search_value) |
                    Q(weekend_person__username__icontains=search_value) |
                    Q(start_date__contains=search_value) |
                    Q(end_date__contains=search_value) & sub_query)
            else:
                query = DutySchedule.objects.select_related(
                    'belongs_to_game_project').prefetch_related(
                    'weekdays_person').prefetch_related(
                    'weekend_person').filter(sub_query)
            raw_data = query[start: start + length]
            recordsTotal = query.count()
            # recordsFiltered = len(raw_data)
            data = {"data": [i.show_all() for i in raw_data], 'draw': draw, 'recordsTotal': recordsTotal,
                    'recordsFiltered': recordsTotal}
            return JsonResponse(data)
        elif raw_url == "host":

            # 根据字段过滤出host的参数
            filter_status = request.POST.getlist('filter_status[]', '全部')
            filter_host_class = raw_get.get('filter_host_class', '全部')
            filter_belongs_to_game_project = raw_get.get('filter_belongs_to_game_project', '全部')
            filter_belongs_to_room = raw_get.get('filter_belongs_to_room', '全部')
            filter_machine_type = raw_get.get('filter_machine_type', '全部')
            filter_belongs_to_business = raw_get.get('filter_belongs_to_business', '全部')
            filter_platform = raw_get.get('filter_platform', '')
            filter_internal_ip = raw_get.get('filter_internal_ip', '')
            filter_telecom_ip = raw_get.get('filter_telecom_ip', '')
            filter_unicom_ip = raw_get.get('filter_unicom_ip', '')
            filter_system = raw_get.get('filter_system', '全部')
            filter_is_internet = raw_get.get('filter_is_internet', '全部')
            filter_sshuser = raw_get.get('filter_sshuser', '')
            filter_sshport = raw_get.get('filter_sshport', '')
            filter_machine_model = raw_get.get('filter_machine_model', '')
            filter_cpu_num = raw_get.get('filter_cpu_num', '')
            filter_cpu = raw_get.get('filter_cpu', '')
            filter_ram = raw_get.get('filter_ram', '')
            filter_disk = raw_get.get('filter_disk', '')
            filter_host_comment = raw_get.get('filter_host_comment', '')
            # filter_belongs_to_host = raw_get.get('filter_belongs_to_host', '')
            filter_host_identifier = raw_get.get('filter_host_identifier', '')
            filter_opsmanager = raw_get.get('filter_opsmanager', '全部')
            filter_project = raw_get.get('filter_project', '全部')
            filter_room = raw_get.get('filter_room', '全部')
            filter_status2 = request.POST.getlist('filter_status2[]', '全部')

            # 添加sub_query
            sub_query = Q()

            """
            2018.12修改：
                1. superuser拥有整个操作整个页面的权限
                2. 拥有查看主机页面权限的staff拥有查看所有主机的权限
                3. 拥有查看主机页面权限的普通用户只能查看所在部门负责项目的主机
            """
            if not (request.user.is_superuser or request.user.has_perm('users.view_all_host_obj')):
                org_user_obj = OrganizationMptt.objects.get(user=request.user)
                projects_obj_list = org_user_obj.get_user_charge_project()
                for project in projects_obj_list:
                    sub_query.add(Q(belongs_to_game_project=project), Q.OR)

            """
            if filter_status:
                sub_query.add(
                    Q(status__in=[
                        v for k, v in STATUS_DIC.items()
                        if (k.startswith(filter_status) or k.endswith(filter_status))]), Q.AND)
            """

            if filter_status != '全部':
                sub_query.add(Q(status__in=filter_status), Q.AND)

            if filter_host_class != '全部':
                sub_query.add(Q(host_class=filter_host_class), Q.AND)

            if filter_belongs_to_game_project != '全部':
                sub_query.add(Q(belongs_to_game_project=GameProject.objects.get(
                    id=filter_belongs_to_game_project)), Q.AND)

            if filter_belongs_to_room != '全部':
                sub_query.add(Q(belongs_to_room=Room.objects.get(id=filter_belongs_to_room)), Q.AND)

            if filter_machine_type != '全部':
                sub_query.add(Q(machine_type=filter_machine_type), Q.AND)

            if filter_belongs_to_business != '全部':
                sub_query.add(Q(belongs_to_business=Business.objects.get(id=filter_belongs_to_business)), Q.AND)

            if filter_platform:
                sub_query.add(Q(platform__icontains=filter_platform), Q.AND)

            if filter_internal_ip:
                sub_query.add(Q(internal_ip__icontains=filter_internal_ip), Q.AND)

            if filter_telecom_ip:
                sub_query.add(Q(telecom_ip__icontains=filter_telecom_ip), Q.AND)

            if filter_unicom_ip:
                sub_query.add(Q(unicom_ip__icontains=filter_unicom_ip), Q.AND)

            if filter_system != '全部':
                sub_query.add(Q(system=filter_system), Q.AND)

            if filter_is_internet != '全部':
                sub_query.add(Q(is_internet=filter_is_internet), Q.AND)

            if filter_sshuser:
                sub_query.add(Q(sshuser__icontains=filter_sshuser), Q.AND)

            if filter_sshport:
                sub_query.add(Q(sshport__icontains=filter_sshport), Q.AND)

            if filter_machine_model:
                sub_query.add(Q(machine_model__icontains=filter_machine_model), Q.AND)

            if filter_cpu_num:
                sub_query.add(Q(cpu_num__icontains=filter_cpu_num), Q.AND)

            if filter_cpu:
                sub_query.add(Q(cpu__icontains=filter_cpu), Q.AND)

            if filter_ram:
                sub_query.add(Q(ram__icontains=filter_ram), Q.AND)

            if filter_disk:
                sub_query.add(Q(disk__icontains=filter_disk), Q.AND)

            if filter_host_comment:
                sub_query.add(Q(host_comment__icontains=filter_host_comment), Q.AND)

            # if filter_belongs_to_host:
            # sub_query.add(Q(belongs_to_host__icontains=filter_belongs_to_host), Q.AND)

            if filter_host_identifier:
                sub_query.add(Q(host_identifier__icontains=filter_host_identifier), Q.AND)

            if filter_opsmanager != '全部':
                sub_query.add(Q(opsmanager=OpsManager.objects.get(id=filter_opsmanager)), Q.AND)

            if filter_project != '全部':
                sub_query.add(Q(belongs_to_game_project=GameProject.objects.get(
                    id=filter_project)), Q.AND)

            if filter_room != '全部':
                sub_query.add(Q(belongs_to_room=Room.objects.get(id=filter_room)), Q.AND)

            if filter_status2 != '全部':
                sub_query.add(Q(status__in=filter_status2), Q.AND)

            if search_value:
                search_value = search_value.split('-')[-1]
                # 将choices转化为dic
                STATUS_DIC = dict((v, k) for k, v in Host.STATUS)
                CLASS_DICT = dict((v, k) for k, v in Host.CLASSES)
                TYPE_DIC = dict((v, k) for k, v in Host.TYPE)
                SYSTEM_DIC = dict((v, k) for k, v in Host.SYSTEM)
                INTERNET_DIC = dict((v, k) for k, v in Host.INTERNET)

                status_list = [
                    v for k, v in STATUS_DIC.items() if (k.startswith(search_value) or k.endswith(search_value))
                ]

                class_list = [
                    v for k, v in CLASS_DICT.items() if (k.startswith(search_value) or k.endswith(search_value))
                ]

                type_list = [
                    v for k, v in TYPE_DIC.items() if (k.startswith(search_value) or k.endswith(search_value))
                ]

                system_list = [
                    v for k, v in SYSTEM_DIC.items() if (k.startswith(search_value) or k.endswith(search_value))
                ]

                internet_list = [
                    v for k, v in INTERNET_DIC.items() if (k.startswith(search_value) or k.endswith(search_value))
                ]

                query = obj.objects.select_related(
                    'belongs_to_game_project').select_related(
                    'belongs_to_room').select_related(
                    'belongs_to_business').select_related(
                    'opsmanager').filter((
                                                 Q(status__in=status_list) |
                                                 Q(host_class__in=class_list) |
                                                 Q(belongs_to_game_project__project_name__icontains=search_value) |
                                                 Q(belongs_to_room__room_name__icontains=search_value) |
                                                 Q(belongs_to_room__area__chinese_name__icontains=search_value) |
                                                 Q(machine_type__in=type_list) |
                                                 Q(belongs_to_business__business_name__icontains=search_value) |
                                                 Q(platform__icontains=search_value) |
                                                 Q(internal_ip__icontains=search_value) |
                                                 Q(telecom_ip__icontains=search_value) |
                                                 Q(unicom_ip__icontains=search_value) |
                                                 Q(system__in=system_list) |
                                                 Q(is_internet__in=internet_list) |
                                                 Q(sshuser__icontains=search_value) |
                                                 Q(sshport__icontains=search_value) |
                                                 Q(machine_model__icontains=search_value) |
                                                 Q(cpu_num__icontains=search_value) |
                                                 Q(cpu__icontains=search_value) |
                                                 Q(ram__icontains=search_value) |
                                                 Q(disk__icontains=search_value) |
                                                 Q(belongs_to_host=search_value) |
                                                 Q(host_identifier=search_value) |
                                                 Q(host_comment__icontains=search_value)) & sub_query).order_by('-id')
            else:
                query = obj.objects.select_related(
                    'belongs_to_game_project').select_related(
                    'belongs_to_room').select_related(
                    'belongs_to_business').select_related(
                    'opsmanager').filter(sub_query).order_by('-id')
            raw_data = query[start: start + length]
            recordsTotal = query.count()
            # recordsFiltered = len(raw_data)
            data = {"data": [i.show_all() for i in raw_data], 'draw': draw, 'recordsTotal': recordsTotal,
                    'recordsFiltered': recordsTotal}
            return JsonResponse(data)


def host_download(request):
    """主机导出excel
    """
    if request.method == "POST":
        perm = 'users.view_host_obj'
        if User.objects.get(id=request.user.id).has_perm(perm):
            try:
                raw_get = json.loads(request.body.decode('utf-8'))

                # 自定义的过滤标签
                # 根据字段过滤出host的参数
                filter_status = raw_get.get('filter_status', '全部')
                if filter_status is None:
                    filter_status = '全部'
                filter_status2 = raw_get.get('filter_status2', '全部')
                if filter_status2 is None:
                    filter_status2 = '全部'
                filter_host_class = raw_get.get('filter_host_class', '全部')
                filter_belongs_to_game_project = raw_get.get('filter_belongs_to_game_project', '全部')
                filter_belongs_to_room = raw_get.get('filter_belongs_to_room', '全部')
                filter_machine_type = raw_get.get('filter_machine_type', '全部')
                filter_belongs_to_business = raw_get.get('filter_belongs_to_business', '全部')
                filter_platform = raw_get.get('filter_platform', '')
                filter_internal_ip = raw_get.get('filter_internal_ip', '')
                filter_telecom_ip = raw_get.get('filter_telecom_ip', '')
                filter_unicom_ip = raw_get.get('filter_unicom_ip', '')
                filter_system = raw_get.get('filter_system', '全部')
                filter_is_internet = raw_get.get('filter_is_internet', '全部')
                filter_sshuser = raw_get.get('filter_sshuser', '')
                filter_sshport = raw_get.get('filter_sshport', '')
                filter_machine_model = raw_get.get('filter_machine_model', '')
                filter_cpu_num = raw_get.get('filter_cpu_num', '')
                filter_cpu = raw_get.get('filter_cpu', '')
                filter_ram = raw_get.get('filter_ram', '')
                filter_disk = raw_get.get('filter_disk', '')
                filter_host_comment = raw_get.get('filter_host_comment', '')
                # filter_belongs_to_host = raw_get.get('filter_belongs_to_host', '')
                filter_host_identifier = raw_get.get('filter_host_identifier', '')
                filter_opsmanager = raw_get.get('filter_opsmanager', '')

                # 添加sub_query
                sub_query = Q()

                if filter_status != '全部':
                    sub_query.add(Q(status__in=filter_status), Q.AND)

                if filter_status2 != '全部':
                    sub_query.add(Q(status__in=filter_status2), Q.AND)

                if filter_host_class != '全部':
                    sub_query.add(Q(host_class=filter_host_class), Q.AND)

                if filter_belongs_to_game_project != '全部':
                    sub_query.add(Q(belongs_to_game_project=GameProject.objects.get(
                        id=filter_belongs_to_game_project)), Q.AND)

                if filter_belongs_to_room != '全部':
                    sub_query.add(Q(belongs_to_room=Room.objects.get(id=filter_belongs_to_room)), Q.AND)

                if filter_machine_type != '全部':
                    sub_query.add(Q(machine_type=filter_machine_type), Q.AND)

                if filter_belongs_to_business != '全部':
                    sub_query.add(Q(belongs_to_business=Business.objects.get(id=filter_belongs_to_business)), Q.AND)

                if filter_platform:
                    sub_query.add(Q(platform__icontains=filter_platform), Q.AND)

                if filter_internal_ip:
                    sub_query.add(Q(internal_ip__icontains=filter_internal_ip), Q.AND)

                if filter_telecom_ip:
                    sub_query.add(Q(telecom_ip__icontains=filter_telecom_ip), Q.AND)

                if filter_unicom_ip:
                    sub_query.add(Q(unicom_ip__icontains=filter_unicom_ip), Q.AND)

                if filter_system != '全部':
                    sub_query.add(Q(system=filter_system), Q.AND)

                if filter_is_internet != '全部':
                    sub_query.add(Q(is_internet=filter_is_internet), Q.AND)

                if filter_sshuser:
                    sub_query.add(Q(sshuser__icontains=filter_sshuser), Q.AND)

                if filter_sshport:
                    sub_query.add(Q(sshport__icontains=filter_sshport), Q.AND)

                if filter_machine_model:
                    sub_query.add(Q(machine_model__icontains=filter_machine_model), Q.AND)

                if filter_cpu_num:
                    sub_query.add(Q(cpu_num__icontains=filter_cpu_num), Q.AND)

                if filter_cpu:
                    sub_query.add(Q(cpu__icontains=filter_cpu), Q.AND)

                if filter_ram:
                    sub_query.add(Q(ram__icontains=filter_ram), Q.AND)

                if filter_disk:
                    sub_query.add(Q(disk__icontains=filter_disk), Q.AND)

                if filter_host_comment:
                    sub_query.add(Q(host_comment__icontains=filter_host_comment), Q.AND)

                # if filter_belongs_to_host:
                # sub_query.add(Q(belongs_to_host__icontains=filter_belongs_to_host), Q.AND)

                if filter_host_identifier:
                    sub_query.add(Q(host_identifier__icontains=filter_host_identifier), Q.AND)

                if filter_opsmanager != '全部':
                    sub_query.add(Q(opsmanager=OpsManager.objects.get(id=filter_opsmanager)), Q.AND)

                query = Host.objects.select_related(
                    'belongs_to_game_project').select_related(
                    'belongs_to_room').select_related(
                    'belongs_to_business').select_related(
                    'opsmanager').filter(sub_query).order_by('belongs_to_game_project')
                data, success = gen_host_excel(query)
            except Exception as e:
                data = str(e)
                success = False
            return JsonResponse({'data': data, 'success': success})
        else:
            data = '权限拒绝'
            success = False
            return JsonResponse({'data': data, 'success': success})


def get_cmdb_obj(request, raw_url):
    '获取cmdb某个模型下的数据'

    if request.method == "POST":
        id = json.loads(request.body.decode('utf-8')).get('id')

        permission = 'users' + '.' + url2edit_perm.get(raw_url, '')

        if raw_url == "duty_schedule":
            if User.objects.get(id=request.user.id).has_perm(permission):
                obj = DutySchedule.objects.get(id=id)
            else:
                raise PermissionDenied
        # elif raw_url == "fullcalendar":
        #    if User.objects.get(id=request.user.id).has_perm(permission):
        #        obj = FullCalendar.objects.get(id=id)
        elif raw_url == "game_project_list":
            if User.objects.get(id=request.user.id).has_perm(permission):
                obj = GameProject.objects.get(id=id)
            else:
                raise PermissionDenied
        elif raw_url == "room":
            if User.objects.get(id=request.user.id).has_perm(permission):
                obj = Room.objects.get(id=id)
            else:
                raise PermissionDenied
        elif raw_url == "business":
            if User.objects.get(id=request.user.id).has_perm(permission):
                obj = Business.objects.get(id=id)
            else:
                raise PermissionDenied
        elif raw_url == "host":
            if User.objects.get(id=request.user.id).has_perm(permission):
                obj = Host.objects.get(id=id)
            else:
                raise PermissionDenied
        elif raw_url == 'project_group_list':
            if User.objects.get(id=request.user.id).has_perm(permission):
                obj = ProjectGroup.objects.get(id=id)
            else:
                raise PermissionDenied

        elif raw_url == 'ops_manager_list':
            if User.objects.get(id=request.user.id).has_perm(permission):
                obj = OpsManager.objects.get(id=id)
            else:
                raise PermissionDenied

        elif raw_url == 'tecent_cloud_account':
            if request.user.is_superuser:
                obj = TecentCloudAccount.objects.get(id=id)
            else:
                raise PermissionDenied

        edit_data = obj.edit_data()

        return JsonResponse(edit_data)


def get_objs(request, raw_url, del_data):
    '从url获取对象'

    permission = 'users' + '.' + url2del_perm.get(raw_url, '')

    if raw_url == "duty_schedule":
        if User.objects.get(id=request.user.id).has_perm(permission):
            objs = DutySchedule.objects.filter(id__in=del_data)
        else:
            raise PermissionDenied
    elif raw_url == "fullcalendar":
        objs = FullCalendar.objects.filter(id__in=del_data)
    elif raw_url == "game_project_list":
        if User.objects.get(id=request.user.id).has_perm(permission):
            objs = GameProject.objects.filter(id__in=del_data)
        else:
            raise PermissionDenied
    elif raw_url == "room":
        if User.objects.get(id=request.user.id).has_perm(permission):
            objs = Room.objects.filter(id__in=del_data)
        else:
            raise PermissionDenied
    elif raw_url == "business":
        if User.objects.get(id=request.user.id).has_perm(permission):
            objs = Business.objects.filter(id__in=del_data)
        else:
            raise PermissionDenied
    elif raw_url == "host":
        if User.objects.get(id=request.user.id).has_perm(permission):
            objs = Host.objects.filter(id__in=del_data)
        else:
            raise PermissionDenied
    elif raw_url == "project_group_list":
        if User.objects.get(id=request.user.id).has_perm(permission):
            objs = ProjectGroup.objects.filter(id__in=del_data)
        else:
            raise PermissionDenied
    elif raw_url == "ops_manager_list":
        if User.objects.get(id=request.user.id).has_perm(permission):
            objs = OpsManager.objects.filter(id__in=del_data)
        else:
            raise PermissionDenied
    elif raw_url == "cloud":
        if request.user.is_superuser:
            objs = Cloud.objects.filter(id__in=del_data)
        else:
            raise PermissionDenied
    elif raw_url == "tecent_cloud_account":
        if request.user.is_superuser:
            objs = TecentCloudAccount.objects.filter(id__in=del_data)
        else:
            raise PermissionDenied

    return objs


def del_cmdb_obj(request, raw_url):
    """删除cmdb某个模型下的数据"""

    if request.method == "POST":
        del_data = json.loads(request.body.decode('utf-8'))
        try:
            objs = get_objs(request, raw_url, del_data)
            """记录主机删除日志"""
            if raw_url == 'host':
                source_ip = get_ip(request)
                for x in objs:
                    record = HostHistoryRecord.objects.filter(host=x)
                    record.update(**{'remark': x.get_host_ip()})
                    HostHistoryRecord.objects.create(host=x, operation_user=request.user, type=3,
                                                     remark=x.get_host_ip(), source_ip=source_ip)
            objs.delete()

            success = True
            msg = 'ok'

        except PermissionDenied:
            msg = '权限拒绝'
            success = False
        except Exception as e:
            msg = str(e)
            success = False

        return JsonResponse({'data': success, 'msg': msg})


def list_game_project(request):
    '下拉展示游戏项目'

    if request.method == "POST":
        data = []

        q = request.POST.get('q', None)

        if q:
            all_game_projects = GameProject.objects.filter(
                Q(project_name__icontains=q) |
                Q(project_name_en__icontains=q), status=1)
        else:
            all_game_projects = GameProject.objects.filter(status=1)

        for x in all_game_projects:
            data.append({'id': x.id, 'text': x.project_name})

        return JsonResponse(data, safe=False)


def list_room(request):
    '下拉展示机房名称'

    if request.method == "POST":
        data = []

        q = request.POST.get('q', None)

        if q:
            all_room = Room.objects.filter(
                Q(room_name__icontains=q) |
                Q(room_name_en__icontains=q) |
                Q(area__short_name__icontains=q) |
                Q(area__chinese_name__icontains=q)
            )
        else:
            all_room = Room.objects.all()

        for x in all_room:
            data.append({'id': x.id, 'text': x.area.chinese_name + '-' + x.room_name})

        return JsonResponse(data, safe=False)


def list_ip(request):
    '下拉展示某个机房下的所有ip'

    if request.method == "POST":
        data = []

        q = request.POST.get('q', None)

        room = request.POST.get('room')

        if room != '0':
            room = Room.objects.get(id=room)
            all_host = room.host_set.all()

            for x in all_host:
                if x.internal_ip:
                    data.append({'id': x.internal_ip, 'text': x.internal_ip})
                if x.telecom_ip:
                    data.append({'id': x.telecom_ip, 'text': x.telecom_ip})
                if x.unicom_ip:
                    data.append({'id': x.unicom_ip, 'text': x.unicom_ip})

            # 去除掉重复的ip
            data = [dict(t) for t in set([tuple(d.items()) for d in data])]

            if q:
                data = [x for x in data if re.search(q, x.get('text'))]

        return JsonResponse(data, safe=False)


def list_ip_room(request):
    '下拉展示ip-机房'

    if request.method == "POST":
        data = []

        q = request.POST.get('q', None)

        project = request.POST.get('project')

        if q is None:
            q = ''

        if project != '0':
            project = GameProject.objects.get(id=project)

            all_host = Host.objects.filter(
                Q(status=1) &
                Q(belongs_to_game_project=project) &
                (Q(internal_ip__icontains=q) | Q(telecom_ip__icontains=q))
            ).exclude(
                Q(internal_ip__icontains='bak') | Q(telecom_ip__icontains='bak')
            )

            for x in all_host:
                # if x.internal_ip:
                #     data.append(
                #         {'id': str(x.id) + '_' + 'internal_ip',
                #             'text': x.internal_ip + ':' + str(x.sshport) + '-' + x.belongs_to_room.room_name})
                if x.telecom_ip:
                    data.append(
                        {'id': str(x.id) + '_' + 'telecom_ip',
                         'text': x.telecom_ip + ':' + str(x.sshport) + '-' + x.belongs_to_room.room_name})
                else:
                    data.append(
                        {'id': str(x.id) + '_' + 'internal_ip',
                         'text': x.internal_ip + ':' + str(x.sshport) + '-' + x.belongs_to_room.room_name})

        return JsonResponse(data, safe=False)


def list_ip_room_game_server(request):
    '下拉展示ip-机房-区服id'
    results = []

    q = request.POST.get('q', None)

    project = request.POST.get('project')
    page = int(request.POST.get('page'))

    default_max = 100
    count_filtered = 0

    if q is None:
        q = ''

    if project != '0':
        project = GameProject.objects.get(id=project)

        count_filtered = GameServer.objects.select_related('project').filter(
            project=project, merge_id=None, srv_id__icontains=q, srv_status=0).count()

        all_game_server = GameServer.objects.select_related('project').filter(
            project=project, merge_id=None, srv_id__icontains=q, srv_status=0)[(page - 1) * default_max: page * default_max]

        for game in all_game_server:
            room = game.room
            ip = game.ip
            try:
                host = Host.objects.select_related('belongs_to_game_project').select_related('belongs_to_room').get(
                    Q(status=1) &
                    Q(belongs_to_game_project=project) &
                    Q(belongs_to_room=room) &
                    (Q(internal_ip=ip) | Q(telecom_ip=ip) | Q(unicom_ip=ip)))
                results.append(
                    {'id': host.id, 'text': ip + ':' + str(host.sshport) + '-' + room.room_name + '-' + game.srv_id})
            except Exception as e:
                continue
    return JsonResponse({"results": results, "count_filtered": count_filtered}, safe=False)


def list_business(request):
    '下拉展示业务类型'

    if request.method == "POST":
        data = []

        q = request.POST.get('q', None)

        if q:
            all_business = Business.objects.filter(business_name__icontains=q)
        else:
            all_business = Business.objects.all()

        for x in all_business:
            data.append({'id': x.id, 'text': x.business_name})

        return JsonResponse(data, safe=False)


def list_opsmanager(request):
    """下拉展示运维管理机器"""

    if request.method == "POST":
        data = []

        q = request.POST.get('q', None)

        if q:
            all_opsmanager = OpsManager.objects.filter(Q(url__icontains=q) |
                                                       Q(project__project_name__icontains=q) |
                                                       Q(room__room_name__icontains=q))
        else:
            all_opsmanager = OpsManager.objects.all()

        for x in all_opsmanager:
            data.append({'id': x.id, 'text': x.room.room_name + '-' + x.project.project_name + '-' + x.url})

        return JsonResponse(data, safe=False)


def list_ops_user(request):
    '下拉展示运维值班表的用户'

    if request.method == "POST":
        data = []

        q = request.POST.get('q', None)

        # group = Group.objects.get(name='运维部')
        org = OrganizationMptt.objects.get(name='运维部')

        all_users = org.get_all_children_user_obj_list()

        if q:
            all_users = [x for x in all_users if x.username == q or x.first_name == q]

        for x in all_users:
            if x.is_active:
                data.append({'id': x.id, 'text': x.username})

        return JsonResponse(data, safe=False)


def list_administrator(request):
    '下拉展示网络管理员'

    if request.method == "POST":
        data = []

        # 判断用户所在的公司，创畅的公司是固定的人员处理
        user_ancestors = request.user.organizationmptt_set.first().get_ancestors_name()
        if '创畅' in user_ancestors:
            ADMIN = User.objects.filter(username__in=CC_NETWORK_ADMINISTRATOR)
            for x in ADMIN:
                data.append({'id': x.id, 'text': x.username})
            return JsonResponse(data, safe=False)

        q = request.POST.get('q', None)

        classification = request.POST.get('classification', None)

        if classification:
            username_list = FAILURE_DECLARE_WITH_ADMIN.get(int(classification))
            all_users = [User.objects.get(username=x) for x in username_list]
        else:
            # group = Group.objects.get(name='运维网络管理员组')
            all_users = User.objects.filter(username__in=NETWORK_ADMINISTRATOR, is_active=1)

        if q:
            all_users = [x for x in all_users if re.search(q, x.username)]

        for x in all_users:
            if x.is_active:
                data.append({'id': x.id, 'text': x.username})

        return JsonResponse(data, safe=False)


def list_test_user(request):
    """
    根据工单发起人的所在部门
    找到这个部门的所有测试组
    """

    if request.method == "POST":
        data = []
        all_users = []

        q = request.POST.get('q', None)
        refer_url = request.META['HTTP_REFERER']
        project_id = request.POST.get('project_id', refer_url.split('project')[-1].replace('=', ''))
        project = GameProject.objects.get(pk=project_id)

        """
        2019.12修改，根据项目找到所有负责该项目的部门，找出这些部门下的测试组和策划组人员
        """
        departments = project.organizationmptt_set.all()
        for department in departments:
            test_department_group = department.get_children().filter(type=1, name__icontains='测试')
            plan_department_group = department.get_children().filter(type=1, name__icontains='策划')
            test_users = []
            plan_users = []
            if test_department_group:
                for test in test_department_group:
                    test_users = [x.user for x in test.get_children().filter(type=2)]
                    test_users.append(test.get_leader_org_obj().user)
                    test_users = list(set(test_users))
            if plan_department_group:
                for plan in plan_department_group:
                    plan_users = [x.user for x in plan.get_children().filter(type=2)]
                    plan_users.append(plan.get_leader_org_obj().user)
                    plan_users = list(set(plan_users))
            all_users.extend(test_users)
            all_users.extend(plan_users)

        if q:
            all_users = [x for x in all_users if (re.search(q, x.username) or re.search(q, x.first_name))]

        for x in all_users:
            if x.is_active:
                data.append({'id': x.id, 'text': x.username})

        return JsonResponse(data, safe=False)


def list_cc_test_user(request):
    """创畅测试部门的用户"""
    if request.method == "POST":
        data = []
        q = request.POST.get('q', '')
        project = request.POST.get('project')
        project = GameProject.objects.get(id=project)
        """
        2018.12修改，根据项目所属部门，找到这个部门的测试组，关联新组织架构表
        """
        try:
            department = project.organizationmptt_set.all()[0]
            test_department_group = OrganizationMptt.objects.get(parent=department, name='测试组')
            all_users = [x for x in test_department_group.get_children()]
            all_users.append(test_department_group.get_leader_org_obj())
            all_users = list(set(all_users))

            if q:
                all_users = [x for x in all_users if (re.search(q, x.name))]

            for x in all_users:
                print(x)
                if x.is_active:
                    data.append({'id': x.user_id, 'text': x.name})

            return JsonResponse(data, safe=False)
        except Exception:
            pass


def list_cc_operation_user(request):
    """创畅工作室运营组的人，比较特殊，单独使用
    """
    if request.method == "POST":
        data = []
        q = request.POST.get('q', '')
        # group = Group.objects.get(name='创畅工作室')
        # group_section = GroupSection.objects.get(group=group, name='运营组')
        # all_users = [x.user for x in Profile.objects.filter(group_section=group_section) if x.user.is_active]
        # all_users.append(group_section.leader)
        # all_users = list(set(all_users))
        # for x in all_users:
        #     if q in x.username or q in x.first_name:
        #         data.append({'id': x.id, 'text': x.username})

        """
        2018.12修改，创畅工作室运营组的人，比较特殊，单独使用，使用新组织架构表获取
        """
        department = OrganizationMptt.objects.get(name='创畅工作室')
        department_group = department.get_children().filter(type=1, is_department_group=1, name='运营组')
        if department_group:
            department_group = department_group[0]
            all_users = [x.user for x in department_group.get_children().filter(type=2, is_active=1)]
            all_users.append(department_group.get_leader_org_obj().user)
            all_users = list(set(all_users))
            for x in all_users:
                if q in x.username or q in x.first_name:
                    data.append({'id': x.id, 'text': x.username})

        return JsonResponse(data, safe=False)


def list_operation_user(request):
    """下拉展示项目负责部门下的运营组用户"""

    if request.method == "POST":
        data = []
        all_users = []
        try:
            refer_url = request.META['HTTP_REFERER']
            q = request.POST.get('q', None)
            project_id = request.POST.get('project_id', refer_url.split('project')[-1].replace('=', ''))
            project = GameProject.objects.get(pk=project_id)
            if project.project_name_en in ('mjfz', 'h5cc'):
                return list_cc_operation_user(request)

            # 找出商务运营中心下的运营部的人员
            department = OrganizationMptt.objects.filter(name='商务运营中心')
            if department:
                department_group = OrganizationMptt.objects.filter(parent=department, name='运营部')
                if department_group:
                    department_group = department_group[0]
                    all_org_users = OrganizationMptt.objects.filter(parent=department_group)
                    all_users = [org_user.user for org_user in all_org_users]

            # 找出负责该项目的部门下运营组下面的人员
            project_group_name = '运营组'
            departments = project.organizationmptt_set.all()
            for department in departments:
                department_group = department.get_children().filter(type=1, is_department_group=1,
                                                                    name=project_group_name)
                if department_group:
                    department_group = department_group[0]
                    all_users.extend([org.user for org in department_group.get_children()])

            all_users = list(set(all_users))
            # 添加管理员为审批候选人
            if request.user.is_superuser:
                all_users.append(request.user)
            if q:
                all_users = [x for x in all_users if (re.search(q, x.username) or re.search(q, x.first_name))]
            for x in all_users:
                if x.is_active:
                    data.append({'id': x.id, 'text': x.username})

        except GameProject.DoesNotExist:
            pass
        except Exception as e:
            print(str(e))
        return JsonResponse(data, safe=False)


def list_backup_dev(request):
    """下拉展示项目分组备用主程
    排除掉自己
    """
    if request.method == "POST":
        data = []
        all_users = []

        q = request.POST.get('q', '')
        project = request.POST.get('project')
        project_group = request.POST.get('project_group')
        if project_group == '前端组':
            department_group_name = '客户端技术组'
        if project_group == '后端组':
            department_group_name = '服务端技术组'

        if project == '0':
            all_users = []
        else:
            project = GameProject.objects.get(id=project)
            # 这里不仅仅是单独的前端或者后端，而是前后端都需要
            # project_group = ['前端组', '后端组']
            # project_group = ProjectGroup.objects.filter(project=project, name__in=project_group)

            # project_group = ProjectGroup.objects.get(project=project, name=project_group)
            # # 这个项目分组指向的部门管理分组
            # group_section = project_group.group_section
            # if group_section is not None:
            #     all_users = User.objects.filter(is_active=1, profile__group_section=group_section, username__icontains=q)
            # else:
            #     all_users = []
            """
            2019.12修改，找到负责该项目的所有部门下的分组成员
            """
            departments = project.organizationmptt_set.all()
            if not departments:
                raise Exception('该项目没有设置所属负责部门')
            for department in departments:
                department_group = OrganizationMptt.objects.filter(parent=department, name=department_group_name)
                if department_group:
                    all_users.extend([x.user for x in department_group[0].get_children().filter(type=2, is_active=1)])

        for x in all_users:
            data.append({'id': x.id, 'text': x.username})

        # 最后，添加工单发起人
        data.append({'id': request.user.id, 'text': request.user.username})

        # 去重
        def dedupe(items, key=None):
            seen = set()
            for item in items:
                val = item if key is None else key(item)
                if val not in seen:
                    yield item
                seen.add(val)

        return JsonResponse(list(dedupe(data, key=lambda d: d['id'])), safe=False)


def list_user(request):
    '下拉展示用户列表'

    if request.method == "POST":
        data = []

        # 查询参数
        q = request.POST.get('q', None)

        # 所属的游戏项目
        game_project_id = request.POST.get('game_project_id', None)

        if game_project_id:
            belongs_to_game_project = GameProject.objects.get(id=game_project_id)
            if q:
                all_users = [x for x in belongs_to_game_project.related_user.all() if re.search(q, x.username)]
            else:
                all_users = belongs_to_game_project.related_user.all()
        else:
            if not q:
                q = ''
            all_users = User.objects.filter(Q(username__icontains=q) | Q(first_name__icontains=q) & Q(is_active=1))

        # 是否需要展示用户的项目分组
        # 项目调整工单需要使用
        user_project_group = request.POST.get('user_project_group', None)
        if user_project_group is not None:
            all_users = User.objects.filter(
                (Q(username__icontains=q) | Q(first_name__icontains=q)) & Q(is_active=1))
            for x in all_users:
                data.append({'id': x.id, 'text': x.username})
            return JsonResponse(data, safe=False)

        for x in all_users:
            if x.is_active:
                data.append({'id': x.id, 'text': x.username})

        return JsonResponse(data, safe=False)


def list_project_group(request):
    """下拉展示项目分组列表"""

    if request.method == "POST":
        data = []

        # 查询参数
        q = request.POST.get('q', '')

        # 所属的游戏项目
        project = request.POST.get('project', None)

        if project == '0':
            return JsonResponse(data, safe=False)
        elif project is None:
            all_project_groups = ProjectGroup.objects.filter(
                Q(project__project_name__icontains=q) |
                Q(project__project_name_en__icontains=q) |
                Q(name__icontains=q)
            )
            for x in all_project_groups:
                text = x.project.project_name + '-' + x.name
                data.append({'id': x.id, 'text': text})
            return JsonResponse(data, safe=False)
        else:
            project = GameProject.objects.get(id=project)
            # all_project_groups = ProjectGroup.objects.filter(project=project, name__icontains=q)
            #
            # for x in all_project_groups:
            #     data.append({'id': x.id, 'text': x.name})
            """
            2018.12修改，关联新组织架构表获取项目所属部门下的分组
            """
            belongs_to_department = project.organizationmptt_set.all()[0]
            department_group = belongs_to_department.get_children().filter(type=1, is_department_group=1)
            for x in department_group:
                data.append({'id': x.id, 'text': x.name})

            return JsonResponse(data, safe=False)


def list_group(request):
    """下拉展示分组"""

    if request.method == "POST":
        data = []

        # 查询参数
        q = request.POST.get('q', None)

        if not q:
            q = ''

        all_groups = Group.objects.filter(name__icontains=q)

        for x in all_groups:
            data.append({'id': x.id, 'text': x.name, 'is_public': x.groupprofile.is_public})

        return JsonResponse(data, safe=False)


def list_register_group(request):
    """下拉展示分组"""

    if request.method == "POST":
        data = []

        # 查询参数
        q = request.POST.get('q', None)

        if not q:
            q = ''

        all_groups = Group.objects.filter(
            name__icontains=q).exclude(
            name='手游中心').exclude(
            name='页游中心').exclude(
            name='产品开发部').exclude(
            name='管理层').exclude(name='心源工作室')

        for x in all_groups:
            data.append({'id': x.id, 'text': x.name, 'is_public': x.groupprofile.is_public})

        return JsonResponse(data, safe=False)


def add_data_cmdb_duty_schedule(request):
    """增加值班安排表数据"""

    if request.method == "POST":
        msg = 'ok'

        # 所有post过来的数据
        add_data = json.loads(request.body.decode('utf-8'))

        # 去掉id
        add_data.pop('id')

        try:
            with transaction.atomic():
                if User.objects.get(id=request.user.id).has_perm('users.add_duty_schedule_obj'):
                    list_project = GameProject.objects.filter(id__in=add_data.get('belongs_to_game_project'))
                    start_date = add_data.get('start_date')
                    end_date = add_data.get('end_date')
                    weekdays_person = add_data.get('weekdays_person')
                    weekend_person = add_data.get('weekend_person')

                    for project in list_project:
                        weekdays_person = User.objects.filter(id__in=weekdays_person)
                        weekend_person = User.objects.filter(id__in=weekend_person)

                        obj = DutySchedule.objects.create(
                            belongs_to_game_project=project, start_date=start_date, end_date=end_date)
                        obj.weekdays_person.add(*weekdays_person)
                        obj.weekend_person.add(*weekend_person)
                    success = True
                else:
                    raise PermissionDenied
        except PermissionDenied:
            msg = '你没有增加值班记录表的权限'
            success = False
        except IntegrityError:
            msg = '记录有重复!'
            success = False
        except GameProject.DoesNotExist:
            msg = '项目不存在!'
            success = False
        except User.DoesNotExist:
            msg = '用户不存在!'
        except Exception as e:
            msg = str(e)
            success = False

        return JsonResponse({'data': success, 'msg': msg})


def edit_data_cmdb_duty_schedule(request):
    '修改值班表信息'

    if request.method == "POST":
        msg = 'ok'
        edit_data = json.loads(request.body.decode('utf-8'))
        try:
            # 获取duty_obj对象
            with transaction.atomic():
                duty_schedule = DutySchedule.objects.get(id=edit_data.pop('id'))

                # edit_data['belongs_to_game_project'] = GameProject.objects.get(id=edit_data['belongs_to_game_project'])
                # edit_data['weekdays_person'] = User.objects.get(id=edit_data['weekdays_person'])
                # edit_data['weekend_person'] = User.objects.get(id=edit_data['weekend_person'])
                start_date = edit_data.get('start_date')
                end_date = edit_data.get('end_date')

                weekdays_person = User.objects.filter(id__in=edit_data.get('weekdays_person'))
                weekend_person = User.objects.filter(id__in=edit_data.get('weekend_person'))

                duty_schedule.start_date = start_date
                duty_schedule.end_date = end_date

                duty_schedule.weekdays_person.clear()
                duty_schedule.weekend_person.clear()

                duty_schedule.weekdays_person.add(*weekdays_person)
                duty_schedule.weekend_person.add(*weekend_person)

            success = True

        except User.DoesNotExist:
            msg = '用户不存在'
            success = False
        except Exception as e:
            msg = str(e)
            success = False

        return JsonResponse({'data': success, 'msg': msg})


def upload(request):
    '''上传导入文件'''

    if request.method == "GET":
        form = UploadFileForm()
        head = {'value': '上传文件', 'username': request.user.username}
        return render(request, 'upload.html', {'head': head, 'form': form})

    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES['file'])

            fname = request.FILES['file'].name
            fpath = os.path.join(os.getcwd(), 'assets/upload/', fname)
            fmd5 = hashlib.md5(open(fpath, 'rb').read()).hexdigest()
            head = {'value': '导入数据'}
            ftime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            return render(request, 'upload.html', {'head': head, 'fpath': fpath, 'fmd5': fmd5, 'ftime': ftime})


def import_data(request):
    '''导入excel文件里面的数据'''
    if request.method == "POST":
        pdata = json.loads(request.body.decode('utf-8'))

        fpath = pdata.get('fpath')
        action = pdata.get('action')
        ts = pdata.get('ts')

        ie = ImportExcel(fpath, action, ts)
        msg = ie.doImport()

        if not msg:
            success = True
        else:
            success = False

        return JsonResponse({'data': success, 'msg': msg})

    if request.method == "GET":
        '''根据ts来查询进度'''
        ts = request.GET.get("ts")
        tpath = os.path.join('/tmp', str(ts))

        if os.path.isfile(tpath):
            with open(tpath) as f:
                info = f.readlines()

            finished = int(info[0].split('\n')[0])
            records_total = int(info[1])

            return JsonResponse({'finished': finished, 'records_total': records_total})
        else:
            return JsonResponse({'finished': 0, 'records_total': 1})


def game_project_ops_staff(request):
    '项目对接运维人员页面'
    if request.method == 'GET':
        if request.user.is_superuser:
            head = {'value': '项目对接运维人员', 'username': request.user.username}
            return render(request, 'game_project_ops_staff.html', {'head': head})
        else:
            return render(request, '403.html')


def data_game_project_ops_staff(request):
    if request.method == "GET":
        raw_get = request.GET.dict()

        # search_value = raw_get.get('search[value]', '')
        # start = int(raw_get.get('start', 0))
        draw = raw_get.get('draw', 0)
        # length = int(raw_get.get('length', 10))

        raw_data = ''

        raw_data = GameProject.objects.all()
        recordsTotal = raw_data.count()
        data = {"data": [i.show_related_user() for i in raw_data], 'draw': draw, 'recordsTotal': recordsTotal,
                'recordsFiltered': recordsTotal}
        return JsonResponse(data)


def get_game_project_related_user(request):
    '获取游戏项目的运维对接人员'
    if request.method == "POST":
        id = json.loads(request.body.decode('utf-8')).get('id')
        project = GameProject.objects.get(id=id)
        related_user = project.get_related_user()
        return JsonResponse(related_user)


def add_or_edit_game_project_related_user(request):
    if request.method == "POST":
        raw_data = json.loads(request.body.decode('utf-8'))
        msg = 'ok'
        # editFlag = raw_data.pop('editFlag')
        id = raw_data.pop('id')

        try:
            with transaction.atomic():
                project = GameProject.objects.get(id=id)
                project.related_user.clear()
                related_user_list = User.objects.filter(id__in=raw_data.get('related_user'))
                project.related_user.add(*related_user_list)
                success = True
        except GameProject.DoesNotExist:
            msg = '机房不存在'
            success = False
        except Exception as e:
            msg = str(e)
            success = False

        return JsonResponse({'data': success, 'msg': msg})


def user_host_list(request):
    """用户服务器页面
    """
    if request.method == "GET":
        if User.objects.get(id=request.user.id).has_perm('users.view_host_obj'):
            head = {'value': '用户权限统计', 'username': request.user.username}
            all_user = [{'id': x.id, 'username': x.username} for x in User.objects.all()]
            all_host = [{'id': x.id, 'host_identifier': x.host_identifier} for x in Host.objects.all()]
            all_game_project = [{'id': x.id, 'project_name': x.project_name} for x in
                                GameProject.objects.filter(status=1)]
            all_room = [{'id': x.id, 'room_name': x.area.chinese_name + '-' + x.room_name} for x in Room.objects.all()]
            all_group = [{'id': x.id, 'name': x.name} for x in
                         OrganizationMptt.objects.filter(type=1, is_department_group=0)]
            all_t_status = dict(UserProfileHost.T_STATUS)
            all_r_status = dict(UserProfileHost.R_STATUS)
            all_v_status = dict(UserProfileHost.V_STATUS)
            return render(request,
                          'user_host_list.html',
                          {
                              'head': head, 'all_user': all_user,
                              'all_host': all_host, 'all_t_status': all_t_status,
                              'all_r_status': all_r_status, 'all_v_status': all_v_status,
                              'all_game_project': all_game_project, 'all_room': all_room,
                              'all_group': all_group
                          }
                          )
        else:
            return render(request, '403.html')


def key_permission_type(request):
    """服务器权限类型图表
    """
    if request.method == "GET":
        if User.objects.get(id=request.user.id).has_perm('users.view_host_obj'):
            head = {'value': '服务器权限类型图表', 'username': request.user.username}
            all_data_structure = get_permission_detail()
            return render(request, 'key_permission.html', {'head': head, 'all_data_structure': all_data_structure})
        else:
            return render(request, '403.html')


def permission_data_detail(request):
    """服务器权限详细分布数据
    """
    if request.method == "POST":
        if User.objects.get(id=request.user.id).has_perm('users.view_host_obj'):
            pdata = json.loads(request.body.decode('utf-8'))
            id = pdata.get('id')

            data = get_data_permission_detail(id)
            return JsonResponse(data, safe=False)


def permission_data_detail_pie(request):
    """服务器权限详细分布pie图
    """

    if request.method == "POST":
        if User.objects.get(id=request.user.id).has_perm('users.view_host_obj'):
            pdata = json.loads(request.body.decode('utf-8'))
            id = pdata.get('id')
            data = get_data_permission_detail_pie(id)
            return JsonResponse(data, safe=False)


def data_key_permission_type(request):
    """服务器权限类型数据
    """

    if request.method == "POST":
        if User.objects.get(id=request.user.id).has_perm('users.view_host_obj'):
            data_user = []
            data_time = []

            root_user_count = UserProfileHost.objects.filter(is_root=1, is_valid=1).count()
            normal_user_count = UserProfileHost.objects.filter(is_root=0, is_valid=1).count()

            data_user.append({'label': 'root用户', 'data': root_user_count})
            data_user.append({'label': '普通用户', 'data': normal_user_count})

            temporary_count = UserProfileHost.objects.filter(temporary=1, is_valid=1).count()
            nontemporary_count = UserProfileHost.objects.filter(temporary=0, is_valid=1).count()

            data_time.append({'label': '永久', 'data': nontemporary_count})
            data_time.append({'label': '临时', 'data': temporary_count})

            return JsonResponse({'data_user': data_user, 'data_time': data_time})
        else:
            raise PermissionDenied


def data_user_host_list(request):
    """用户服务器数据"""

    if request.method == "POST":
        if User.objects.get(id=request.user.id).has_perm('users.view_host_obj'):
            raw_get = request.POST.dict()

            search_value = raw_get.get('search[value]', '')
            start = int(raw_get.get('start', 0))
            draw = raw_get.get('draw', 0)
            length = int(raw_get.get('length', 10))

            filter_username = raw_get.get('filter_username', '')
            filter_host = raw_get.get('filter_host', '')
            filter_internal_ip = raw_get.get('filter_internal_ip', '')
            filter_telecom_ip = raw_get.get('filter_telecom_ip', '')
            filter_unicom_ip = raw_get.get('filter_unicom_ip', '')
            filter_start_time = raw_get.get('filter_start_time', '')
            filter_end_time = raw_get.get('filter_end_time', '')
            filter_t_status = raw_get.get('filter_t_status', '')
            filter_r_status = raw_get.get('filter_r_status', '')
            filter_v_status = raw_get.get('filter_v_status', '')
            filter_game_project = raw_get.get('filter_game_project', '')
            filter_room = raw_get.get('filter_room', '')
            filter_group = raw_get.get('filter_group', '')

            # 添加sub_query
            sub_query = Q()

            """
            2018.12修改：
                1. superuser拥有整个操作整个页面的权限
                2. 拥有查看主机页面权限的staff拥有查看所有主机的权限
                3. 拥有查看主机页面权限的普通用户只能查看所在部门负责项目的主机
            """
            if not (request.user.is_superuser or request.user.is_staff):
                org_user_obj = OrganizationMptt.objects.get(user=request.user)
                projects_obj_list = org_user_obj.get_user_charge_project()
                for project in projects_obj_list:
                    sub_query.add(Q(host__in=project.host_set.all()), Q.OR)

            if filter_username != '0':
                sub_query.add(Q(user_profile__user=User.objects.get(id=filter_username)), Q.AND)

            if filter_host != '0':
                sub_query.add(Q(host=Host.objects.get(id=filter_host)), Q.AND)

            if filter_internal_ip:
                sub_query.add(Q(host__internal_ip__icontains=filter_internal_ip), Q.AND)

            if filter_telecom_ip:
                sub_query.add(Q(host__telecom_ip__icontains=filter_telecom_ip), Q.AND)

            if filter_unicom_ip:
                sub_query.add(Q(host__unicom_ip__icontains=filter_unicom_ip), Q.AND)

            if filter_start_time:
                sub_query.add(Q(start_time__contains=filter_start_time), Q.AND)

            if filter_end_time:
                sub_query.add(Q(end_time__contains=filter_end_time), Q.AND)

            if filter_t_status != '100':
                sub_query.add(Q(temporary=filter_t_status), Q.AND)

            if filter_r_status != '100':
                sub_query.add(Q(is_root=filter_r_status), Q.AND)

            if filter_v_status != '100':
                sub_query.add(Q(is_valid=filter_v_status), Q.AND)

            if filter_game_project != '0':
                sub_query.add(Q(host__belongs_to_game_project=GameProject.objects.get(id=filter_game_project)), Q.AND)

            if filter_room != '0':
                sub_query.add(Q(host__belongs_to_room=Room.objects.get(id=filter_room)), Q.AND)

            if filter_group != '0':
                org = OrganizationMptt.objects.get(pk=filter_group)
                leaf_user = org.get_all_children_user_obj_list()
                sub_query.add(Q(organization__user__in=leaf_user), Q.AND)

            raw_data = ''

            if search_value:
                T_STATUS_DIC = dict((v, k) for k, v in UserProfileHost.T_STATUS)
                t_status_list = [
                    v for k, v in T_STATUS_DIC.items() if (k.startswith(search_value) or k.endswith(search_value))
                ]

                R_STATUS_DIC = dict((v, k) for k, v in UserProfileHost.R_STATUS)
                r_status_list = [
                    v for k, v in R_STATUS_DIC.items() if (k.startswith(search_value) or k.endswith(search_value))
                ]

                V_STATUS_DIC = dict((v, k) for k, v in UserProfileHost.V_STATUS)
                v_status_list = [
                    v for k, v in V_STATUS_DIC.items() if (k.startswith(search_value) or k.endswith(search_value))
                ]

                query = UserProfileHost.objects.select_related(
                    'user_profile__user').select_related(
                    'host').select_related(
                    'host__belongs_to_game_project').select_related(
                    'host__belongs_to_room').select_related('host__belongs_to_game_project__group').filter((
                                                                                                                   Q(
                                                                                                                       host__host_identifier__icontains=search_value) |
                                                                                                                   Q(
                                                                                                                       user_profile__user__username__icontains=search_value) |
                                                                                                                   Q(
                                                                                                                       host__internal_ip__icontains=search_value) |
                                                                                                                   Q(
                                                                                                                       host__telecom_ip__icontains=search_value) |
                                                                                                                   Q(
                                                                                                                       host__unicom_ip__icontains=search_value) |
                                                                                                                   Q(
                                                                                                                       start_time__contains=search_value) |
                                                                                                                   Q(
                                                                                                                       end_time__contains=search_value) |
                                                                                                                   Q(
                                                                                                                       temporary__in=t_status_list) |
                                                                                                                   Q(
                                                                                                                       is_root__in=r_status_list) |
                                                                                                                   Q(
                                                                                                                       is_valid__in=v_status_list)) & sub_query)
            else:
                query = UserProfileHost.objects.select_related(
                    'user_profile__user').select_related(
                    'host').select_related(
                    'host__belongs_to_game_project').select_related(
                    'host__belongs_to_room').select_related('host__belongs_to_game_project__group').filter(sub_query)

            raw_data = query[start: start + length]
            recordsTotal = query.count()
            # recordsFiltered = len(raw_data)
            data = {"data": [i.show_all() for i in raw_data], 'draw': draw, 'recordsTotal': recordsTotal,
                    'recordsFiltered': recordsTotal}
            return JsonResponse(data)


def project_svn_api(request):
    """项目svn api文档
    """
    if request.method == 'GET':
        if request.user.is_superuser:
            return render(request, 'project_svn_api_doc.html')
        else:
            return render(request, '403.html')


def get_host_history_record(request):
    """获取主机修改历史记录数据"""
    if request.method == "POST":
        if request.user.is_superuser:
            host_id = json.loads(request.body.decode('utf-8')).get('host_id')
            host_history_record = HostHistoryRecord.objects.filter(host_id=host_id).order_by('create_time')
            record_list = format_host_record(host_history_record)
            data = {'data': record_list}
            return JsonResponse(data)
        else:
            raise PermissionDenied


def system_cron_list(request):
    """系统作业管理页面"""
    if request.method == 'GET':
        if request.user.is_superuser:
            current_page = request.GET.get('current_page', None)
            if not current_page:
                current_page = 0
            salt_tasks = SaltConfig.objects.select_related('salt_task')
            return render(request, 'system_cron_list.html', {'salt_tasks': salt_tasks, 'current_page': current_page})
        else:
            return render(request, '403.html')


def system_cron_execute(request, task_id):
    """系统作业执行页面"""
    if request.user.is_superuser:
        try:
            salt_task = SaltTask.objects.get(pk=task_id)
            return render(request, 'system_cron_execute.html', {'salt_task': salt_task})
        except Exception as e:
            return render(request, 'system_cron_execute.html', {'msg': str(e)})
    else:
        return render(request, '403.html')


def salt_config(request, config_id):
    """获取某个任务的配置文件数据"""
    if request.user.is_superuser:
        config_obj = SaltConfig.objects.get(pk=config_id)
        data = {'config_id': config_obj.id, 'filename': config_obj.filename, 'task_name': config_obj.salt_task.name,
                'content': config_obj.content, 'status': config_obj.salt_task.status, 'push_path': config_obj.push_path}
        return JsonResponse({'data': data})
    else:
        raise PermissionDenied


def save_salt_config(request):
    """保存配置文件/任务信息数据"""
    if request.user.is_superuser:
        """获取请求参数"""
        content = request.POST['content']
        config_id = request.POST['config_id']
        status = request.POST['status']
        remark = request.POST['remark']
        task_name = request.POST['task_name']
        filename = request.POST['filename']
        push_path = request.POST['push_path']
        current_page = request.POST['current_page']
        """保存配置文件修改"""
        salt_config = SaltConfig.objects.get(pk=config_id)
        salt_config.filename = filename
        salt_config.push_path = push_path
        salt_config.save(update_fields=['filename', 'push_path'])
        """保存任务信息修改"""
        task_obj = salt_config.salt_task
        task_obj.name = task_name
        task_obj.status = status
        task_obj.save(update_fields=['status', 'name'])
        """若配置内容发生改变，则保存新配置内容，并记录修改记录"""
        old_config = salt_config.content
        if old_config != content:
            salt_config.content = content
            salt_config.modified_user = request.user
            salt_config.save()
            SaltConfigHistory.objects.create(salt_config=salt_config, type=2, content=content,
                                             modified_user=request.user, remark=remark)
        """更新配置文件对应的下发记录表下发状态待下发，若记录不存在，则新增"""
        if not salt_config.release_set.filter():
            Release.objects.create(salt_config=salt_config)
        else:
            for x in salt_config.release_set.all():
                x.status = 2
                x.save()

        return HttpResponseRedirect('/assets/system_cron_list/?current_page=' + current_page)
    else:
        return render(request, '403.html')


def salt_config_history(request, config_id):
    """salt配置修改历史记录页面"""
    if request.user.is_superuser:
        history = SaltConfigHistory.objects.filter(salt_config_id=config_id).order_by('-id')
        salt_config = SaltConfig.objects.get(pk=config_id)
        task_config = salt_config.salt_task.name + '-' + salt_config.filename
        return render(request, 'salt_config_history.html', {'history': history, 'task_config': task_config})
    else:
        return render(request, '403.html')


def history_detail(request, history_id):
    """salt配置修改历史记录详情"""
    if request.user.is_superuser:
        history_obj = SaltConfigHistory.objects.get(pk=history_id)
        data = {'history_id': history_obj.id, 'filename': history_obj.salt_config.filename,
                'remark': history_obj.remark,
                'task_name': history_obj.salt_config.salt_task.name, 'content': history_obj.content}
        return JsonResponse({'data': data})
    else:
        raise PermissionDenied


def history_recover(request):
    """salt配置回滚"""
    if request.user.is_superuser:
        history_id = request.POST['history_id']
        recover_remark = request.POST['recover_remark']
        history_obj = SaltConfigHistory.objects.get(pk=history_id)
        config_obj = history_obj.salt_config
        config_obj.content = history_obj.content
        config_obj.save()
        release = config_obj.release_set.all()
        release.update(**{'status': 2})
        """记录回滚日志"""
        SaltConfigHistory.objects.create(salt_config=config_obj, type=4, content=history_obj.content,
                                         modified_user=request.user, remark=recover_remark)
        return HttpResponseRedirect(reverse('system_cron_list'))
    else:
        return render(request, '403.html')


def salt_config_push(request):
    """salt配置文件推送"""
    if request.user.is_superuser:
        result = True
        msg = '推送成功'
        raw_data = json.loads(request.body.decode('utf-8'))
        config_id = raw_data.get('config_id', 0)
        config_obj = SaltConfig.objects.get(pk=int(config_id))
        """校验推送所需信息是否完善"""
        if config_obj.filename is None or config_obj.filename == '':
            result = False
            return JsonResponse({'success': result, 'msg': '请先填写配置文件名！'})
        if config_obj.push_path is None or config_obj.push_path == '':
            result = False
            return JsonResponse({'success': result, 'msg': '请先填写远程推送路径！'})
        if config_obj.content is None or config_obj.content == '':
            result = False
            return JsonResponse({'success': result, 'msg': '请先填写配置文件内容！'})
        """生成配置文件"""
        file_path = os.path.join(os.getcwd(), 'assets', 'saltstack_config', config_obj.filename)
        with open(file_path, 'w') as f:
            config_file = File(f)
            config_file.write(str(config_obj.content))
        """推送配置文件task"""
        push_dir = config_obj.push_path.split('/')
        push_dir = list(filter(None, push_dir))[1:]
        push_dir = '/'.join(push_dir)
        cmd = """rsync --port=%d -az  --password-file=%s %s %s@%s::%s/%s""" % (
            10022, '/etc/salt_rsync.pass', file_path, 'salt_master', '119.29.79.89', 'salt_rsync', push_dir)
        log = RsyncLog()
        log.logger.info('rsync命令:%s' % (cmd,))
        res = os.system(cmd)
        if res == 0:
            result = True
            log.logger.info('rsync传送文件成功')
        else:
            result = False
            log.logger.info('rsync传送文件失败')
            msg = 'rsync传送文件失败'
        # time.sleep(2)
        # result = False
        # msg = '推送超时'

        """若推送成功，则更新推送状态，更新推送人，推送时间"""
        if result:
            for x in config_obj.release_set.all():
                x.status = 1
                x.release_user = request.user
                x.release_time = datetime.now()
                x.save()

        return JsonResponse({'success': result, 'msg': msg})

    else:
        raise PermissionDenied


def start_execute_salt_task(request):
    """开始执行salt任务"""
    if request.user.is_superuser:
        try:
            raw_data = json.loads(request.body.decode('utf-8'))
            task_id = raw_data.get('execute_task_id', 0)
            selected_host = raw_data.get('selected_host', None)
            telecom_ip_list = [x.telecom_ip for x in Host.objects.filter(id__in=selected_host) if
                               x.telecom_ip is not None and x.telecom_ip != '']
            if telecom_ip_list:
                execute_salt_task.delay(task_id, request.user.id, telecom_ip_list)
            else:
                raise Exception('所选主机不存在')
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'msg': str(e)})
    else:
        raise PermissionDenied


def salt_task_execute_history(request, task_id):
    """执行saltstack任务历史记录列表页"""
    if request.user.is_superuser:
        history = SaltTaskExecuteHistory.objects.filter(salt_task_id=task_id).order_by('-id')
        salt_task = SaltTask.objects.get(pk=task_id)
        return render(request, 'salt_task_execute_history.html', {'history': history, 'salt_task': salt_task})
    else:
        return render(request, '403.html')


def execute_history_detail(request, history_id):
    """salt任务执行历史记录详情"""
    if request.user.is_superuser:
        history_obj = SaltTaskExecuteHistory.objects.get(pk=history_id)
        data = {'task_name': history_obj.salt_task.name, 'execute_result': history_obj.execute_result}
        return JsonResponse({'data': data})
    else:
        raise PermissionDenied


def execute_history_host_detail(request, id):
    """salt任务执行历史记录主机单独详情"""
    if request.user.is_superuser:
        obj = SaltExecuteHistoryDetail.objects.get(pk=id)
        data = {'task_name': obj.execute_history.salt_task.name, 'execute_result': obj.result}
        return JsonResponse({'data': data})
    else:
        raise PermissionDenied


def add_salt_task(request):
    """新建saltstack任务"""
    if request.user.is_superuser:
        add_task_name = request.POST['add_task_name']
        add_status = request.POST['add_status']
        add_filename = request.POST['add_filename']
        add_content = request.POST['add_content']
        add_push_path = request.POST['add_push_path']
        current_page = request.POST['current_page']
        salt_task = SaltTask(name=add_task_name, status=add_status)
        salt_task.save()
        salt_config = SaltConfig(salt_task=salt_task, filename=add_filename, content=add_content,
                                 push_path=add_push_path)
        salt_config.save()
        Release.objects.create(salt_config=salt_config)
        return HttpResponseRedirect(reverse('system_cron_list', kwargs={'current_page': current_page}))
    else:
        return render(request, '403.html')


def delete_salt_task(request):
    """删除所选saltstack任务"""
    msg = 'ok'
    success = True
    try:
        if request.user.is_superuser and request.method == 'POST':
            del_data = json.loads(request.body.decode('utf-8'))
            salt_task = SaltTask.objects.filter(id__in=del_data)
            salt_task.delete()
        else:
            raise PermissionDenied
    except PermissionDenied:
        msg = '权限拒绝'
        success = False
    except Exception as e:
        msg = str(e)
        success = False
    return JsonResponse({'data': success, 'msg': msg})


def salt_command_history(request):
    """执行salt命令历史记录"""
    if request.user.is_superuser:
        history = SaltCommandHistory.objects.order_by('-execute_time')
        return render(request, 'salt_command_history.html', {'history': history})
    else:
        return render(request, '403.html')


def cdn_api_info(request):
    """cdn api接口信息"""
    if request.user.is_superuser:
        cdn_api_obj = CDNAPI.objects.all()
        return render(request, 'cdn_api_info.html', {'cdn_api_obj': cdn_api_obj})
    else:
        return render(request, '403.html')


def list_cdn_supplier(request):
    """列出cdn供应商数据"""
    if request.user.is_superuser:
        if request.method == "POST":
            data = []

            q = request.POST.get('q', None)

            if q:
                all_cdn = CDN.objects.filter(
                    Q(name__icontains=q))
            else:
                all_cdn = CDN.objects.all()

            for x in all_cdn:
                data.append({'id': x.id, 'text': x.name})

            return JsonResponse(data, safe=False)
    else:
        raise PermissionDenied


def add_cdn_api(request):
    """新增cdn api接口信息"""
    try:
        if not request.user.is_superuser:
            raise PermissionDenied('权限受限')
        data = json.loads(request.body.decode('utf-8'))
        cdn_id = data.get('cdn_supplier', 0)
        cdn_obj = CDN.objects.get(pk=cdn_id)
        auth = data.get('auth', 0)
        remark = data.get('remark', '')
        area = data.get('area', '')
        game_project = data.pop('game_project', '')
        if auth == '1':
            token = data.get('token', '')
            cdn_api_obj = CDNAPI(cdn=cdn_obj, token=token, remark=remark, auth=auth, area=area)
            cdn_api_obj.save()
        else:
            secret_id = data.get('secret_id', '')
            secret_key = data.get('secret_key', '')
            cdn_api_obj = CDNAPI(cdn=cdn_obj, secret_id=secret_id, secret_key=secret_key, remark=remark, auth=auth,
                                 area=area)
            cdn_api_obj.save()
        if game_project:
            game_project = list(GameProject.objects.filter(id__in=game_project))
            cdn_api_obj.game_project.add(*game_project)
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'msg': str(e)})


def get_cdn_api_detail(request):
    """获取cdn api接口详细信息"""
    if request.user.is_superuser and request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        cdn_api_id = data.get('id', 0)
        cdn_api = CDNAPI.objects.get(pk=cdn_api_id)
        res = cdn_api.edit_data()
        return JsonResponse(res)
    else:
        raise PermissionDenied


def edit_cdn_api(request):
    """修改cdn api接口信息"""
    if request.method == 'POST':
        try:
            if not request.user.is_superuser:
                raise PermissionDenied('权限受限')
            data = json.loads(request.body.decode('utf-8'))
            auth = data.get('auth')
            game_project = data.pop('game_project')
            cdn_api_id = data.pop('cdn_api_id')
            cdn_api_obj = CDNAPI.objects.filter(id=cdn_api_id)
            if auth == '1':
                data['secret_id'] = ''
                data['secret_key'] = ''
                cdn_api_obj.update(**data)
            else:
                data['token'] = ''
                cdn_api_obj.update(**data)
            cdn_api_obj = cdn_api_obj[0]
            cdn_api_obj.game_project.clear()
            if game_project:
                game_project = list(GameProject.objects.filter(id__in=game_project))
                cdn_api_obj.game_project.add(*game_project)
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'msg': str(e)})


def delete_cdn_api(request):
    """删除所选cdn接口信息"""
    msg = 'ok'
    success = True
    try:
        if request.user.is_superuser and request.method == 'POST':
            del_data = json.loads(request.body.decode('utf-8'))
            cdn_api = CDNAPI.objects.filter(id__in=del_data)
            cdn_api.delete()
        else:
            raise PermissionDenied
    except PermissionDenied:
        msg = '权限拒绝'
        success = False
    except Exception as e:
        msg = str(e)
        success = False
    return JsonResponse({'data': success, 'msg': msg})


def cdn_refresh_page(request):
    """进入刷新cdn的页面"""
    if request.method == 'GET':
        now = datetime.now()
        delta = timedelta(days=30)
        past = now - delta
        if request.user.is_superuser:
            cdn_refresh_record = CDNRefreshRecord.objects.filter(commit_time__gte=past).order_by('-id')
            return render(request, 'cdn_refresh.html', {'cdn_refresh_record': cdn_refresh_record})
        elif request.user.has_perm('users.execute_cdn_refresh'):
            cdn_refresh_record = CDNRefreshRecord.objects.filter(commit_user=request.user,
                                                                 commit_time__gte=past).order_by('-id')
            return render(request, 'cdn_refresh.html', {'cdn_refresh_record': cdn_refresh_record})
        else:
            return render(request, '403.html')


def cdn_refresh(request):
    """提交cdn刷新"""
    if request.method == 'POST':
        if request.user.is_superuser or request.user.has_perm('users.execute_cdn_refresh'):
            raw_data = json.loads(request.body.decode('utf-8'))
            refresh_obj = raw_data.get('refresh_obj', '')
            raw_refresh_obj = raw_data.get('raw_refresh_obj', '')
            """去重/去空字符串"""
            refresh_obj = list(set(refresh_obj))
            refresh_obj = [x for x in refresh_obj if x != '']
            refresh_type = raw_data.get('refresh_type', '')
            """获取对应cdn接口"""
            cdn_api_id = raw_data.get('game_project', 0)
            cdn_api = CDNAPI.objects.filter(id=cdn_api_id)
            if cdn_api:
                cdn_api = cdn_api[0]
                """创建刷新记录"""
                record = CDNRefreshRecord(commit_user=request.user, cdn_api=cdn_api, refresh_obj=raw_refresh_obj,
                                          result=2)
                record.save()
                if cdn_api.cdn.name == '腾讯云':
                    refresh_txcloud_cdn.delay(refresh_type=refresh_type, refresh_obj=refresh_obj, record_id=record.id)
                if cdn_api.cdn.name == '白山云':
                    refresh_bscloud_cdn.delay(refresh_type=refresh_type, refresh_obj=refresh_obj, record_id=record.id)

            else:
                msg = '该项目没有设置对应的CDN信息，请联系运维部！'
                return JsonResponse({'success': False, 'msg': msg})

            return JsonResponse({'success': True})
        else:
            raise PermissionDenied


def manual_query_cdn(request):
    """手动查询cdn刷新结果"""
    if request.user.is_superuser or request.user.has_perm('users.execute_cdn_refresh'):
        raw_data = json.loads(request.body.decode('utf-8'))
        record_id = raw_data.get('record_id', 0)
        record = CDNRefreshRecord.objects.get(id=record_id)
        token = record.cdn_api.token
        secret_id = record.cdn_api.secret_id
        secret_key = record.cdn_api.secret_key
        if record.cdn_api.auth == 1:
            res = BScloudRefreshResultQuery(record.task_id, token)
        else:
            res = QcloudRefreshResultQuery(record.task_id, secret_id, secret_key)
        if res['success']:
            record.result = 1
            record.finish_time = datetime.now()
            record.save()
        else:
            if res['msg'] == '刷新中':
                pass
            else:
                record.result = -1
                record.remark = res['msg']
                record.save()
        return JsonResponse({'success': True})
    else:
        raise PermissionDenied


def view_refresh_detail(request):
    """查看cdn提交刷新的内容"""
    if request.user.is_superuser or request.user.has_perm('users.execute_cdn_refresh'):
        raw_data = json.loads(request.body.decode('utf-8'))
        record_id = raw_data.get('record_id', 0)
        if record_id == 0:
            raise CDNRefreshRecord.DoesNotExist
        record_obj = CDNRefreshRecord.objects.get(pk=record_id)
        refresh_obj = record_obj.refresh_obj
        return JsonResponse({'success': True, 'data': refresh_obj})
    else:
        raise PermissionDenied


def cdn_refresh_record_page(request):
    """cdn刷新记录查询页面"""
    if request.user.is_superuser:
        return render(request, 'cdn_refresh_record.html', {})
    else:
        return render(request, '403.html')


def query_cdn_refresh_record(request):
    """查询cdn刷新记录"""
    if request.method == 'POST':
        if request.user.is_superuser:
            raw_data = request.POST.dict()
            cdn_api_id = raw_data.get('project_id', 0)
            startDate = raw_data.get('startDate', 0)
            endDate = raw_data.get('endDate', 0)
            draw = raw_data.get('draw', 0)
            cdn_api = CDNAPI.objects.filter(id=cdn_api_id)
            if cdn_api:
                cdn_api = cdn_api[0]
                token = cdn_api.token
                secret_id = cdn_api.secret_id
                secret_key = cdn_api.secret_key
                if cdn_api.cdn.name == '腾讯云':
                    result = query_tx_cdn_refresh_record(startDate, endDate, secret_id, secret_key)
                    if result['success']:
                        data = result['data']
                        total = result['total']
                        return JsonResponse({'success': True, 'data': data, 'draw': draw, 'recordsTotal': total,
                                             'recordsFiltered': total})
                    else:
                        msg = result['msg']
                        return JsonResponse({'success': False, 'msg': msg, 'data': [], 'draw': draw, 'recordsTotal': 0,
                                             'recordsFiltered': 0})
                if cdn_api.cdn.name == '白山云':
                    result = query_bs_cdn_refresh_record(token, startDate, endDate)
                    if result['success']:
                        data = result['data']
                        total = result['total']
                        return JsonResponse({'success': True, 'data': data, 'draw': draw, 'recordsTotal': total,
                                             'recordsFiltered': total})
                    else:
                        msg = result['msg']
                        return JsonResponse({'success': False, 'msg': msg, 'data': [], 'draw': draw, 'recordsTotal': 0,
                                             'recordsFiltered': 0})
            else:
                msg = '该游戏项目还没有配置CDN接口信息，请联系运维部！'
                return JsonResponse({'success': False, 'msg': msg, 'data': [], 'draw': draw, 'recordsTotal': 0,
                                     'recordsFiltered': 0})
        else:
            raise PermissionDenied


def list_cdn_game_project_by_group(request):
    """根据登录人展示cdn接口信息
    """
    if request.method == "POST":
        data = []
        q = request.POST.get('q', '')
        # 添加sub_query
        sub_query = Q()
        if q:
            sub_query.add(Q(game_project__project_name__icontains=q), Q.OR)
            sub_query.add(Q(game_project__project_name_en__icontains=q), Q.OR)
            sub_query.add(Q(area__icontains=q), Q.OR)
            sub_query.add(Q(cdn__name__icontains=q), Q.OR)

        if request.user.is_superuser:
            all_cdn_api = CDNAPI.objects.select_related('cdn').prefetch_related('game_project__project_name').filter(
                sub_query).values(
                'id', 'game_project__project_name', 'area', 'cdn__name')
            data = [{'id': i['id'], 'text': i['cdn__name'] + '-' + i['area'] + '-' + i['game_project__project_name']}
                    for i in all_cdn_api]
        else:
            org = OrganizationMptt.objects.get(user=request.user)
            org_charge_project_list = org.get_user_charge_project()
            all_cdn_api = CDNAPI.objects.select_related('cdn').prefetch_related('game_project__project_name').filter(
                Q(game_project__in=org_charge_project_list) & sub_query).values(
                'id', 'game_project__project_name', 'area', 'cdn__name')
            data = [{'id': i['id'], 'text': i['cdn__name'] + '-' + i['area'] + '-' + i['game_project__project_name']}
                    for i in all_cdn_api]

        return JsonResponse(data, safe=False)


def list_area_from_ops(request):
    """根据运维管理机的地区字段去重后列出"""
    if request.method == 'POST':
        data = []
        all_area = OpsManager.objects.values('area').distinct()
        for x in all_area:
            data.append({'id': x['area'], 'text': x['area']})
        return JsonResponse(data, safe=False)


def host_usage(request):
    """主机使用率页面"""
    if request.user.has_perm('users.view_host_usage'):
        return render(request, 'host_usage.html', {})
    else:
        return render(request, '403.html')


def data_host_usage(request):
    """状态为可用的主机使用率数据"""
    if request.method == "POST":
        if request.user.has_perm('users.view_host_usage'):
            raw_get = request.POST.dict()

            search_value = raw_get.get('search[value]', '')
            draw = raw_get.get('draw', 0)

            filter_project = raw_get.get('id_project', 0)
            filter_room = raw_get.get('id_room', "0")

            # 添加sub_query
            sub_query = Q()

            if int(filter_project) != 0:
                project = GameProject.objects.get(pk=filter_project)
                sub_query.add(Q(belongs_to_game_project=project), Q.AND)

            if filter_room != "0":
                filter_room = filter_room.split('-')[-1]
                sub_query.add(Q(belongs_to_room__room_name=filter_room), Q.AND)

            if search_value:
                search_value = search_value.split('-')[-1]
                query = Host.objects.select_related('belongs_to_game_project').select_related(
                    'belongs_to_room').exclude(status=4).filter(
                    (
                            Q(belongs_to_game_project__project_name__icontains=search_value) |
                            Q(belongs_to_game_project__project_name_en__icontains=search_value) |
                            Q(belongs_to_room__room_name__icontains=search_value) |
                            Q(belongs_to_business__business_name__icontains=search_value) |
                            Q(telecom_ip__icontains=search_value)) & sub_query
                ).distinct()

            else:
                query = Host.objects.select_related('belongs_to_game_project').select_related(
                    'belongs_to_room').exclude(status=4).filter(sub_query)

            raw_data = query
            recordsTotal = query.count()
            data = {"data": [i.show_usage() for i in raw_data], 'draw': draw, 'recordsTotal': recordsTotal,
                    'recordsFiltered': recordsTotal}
            return JsonResponse(data)
        else:
            raise PermissionDenied


def host_recover_migration_apply(request):
    """主机迁服/回收申请页面"""
    if request.user.has_perm('users.host_compression_apply'):
        return render(request, 'host_recover_migration_apply.html', {})
    else:
        return render(request, '403.html')


def area(request):
    """地区信息"""
    if request.user.is_superuser:
        all_area = Area.objects.all()
        return render(request, 'area.html', {'all_area': all_area})
    else:
        return render(request, '403.html')


def list_all_area_name(request):
    """列出所有地区"""
    if request.method == 'POST':
        data = [{'id': x.chinese_name, 'text': x.chinese_name} for x in Area.objects.all()]
        return JsonResponse(data, safe=False)


def add_area(request):
    """新增地区信息"""
    success = True
    msg = 'ok'
    try:
        if not request.user.is_superuser:
            raise PermissionDenied('权限受限')
        data = json.loads(request.body.decode('utf-8'))
        chinese_name = data.get('chinese_name', '')
        short_name = data.get('short_name', '')
        Area.objects.create(chinese_name=chinese_name, short_name=short_name)
    except Exception as e:
        success = False
        msg = str(e)
    finally:
        return JsonResponse({'success': success, 'msg': msg})


def get_area_detail(request):
    """获取地区详细信息"""
    if request.user.is_superuser and request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        area_id = data.get('id', 0)
        area = Area.objects.get(pk=area_id)
        data = area.edit_data()
        return JsonResponse(data)
    else:
        raise PermissionDenied


def edit_area(request):
    """修改地区信息"""
    if request.method == 'POST':
        success = True
        msg = 'ok'
        try:
            if not request.user.is_superuser:
                raise PermissionDenied('权限受限')
            data = json.loads(request.body.decode('utf-8'))
            area_id = data.pop('area_id', '')
            area_obj = Area.objects.filter(pk=area_id)
            area_obj.update(**data)
        except Exception as e:
            msg = str(e)
            success = False
        finally:
            return JsonResponse({'success': success, 'msg': msg})


def delete_area(request):
    """删除地区"""
    if request.method == 'POST':
        msg = 'ok'
        success = True
        try:
            if request.user.is_superuser:
                del_data = json.loads(request.body.decode('utf-8'))
                area = Area.objects.filter(id__in=del_data)
                area.delete()
            else:
                raise PermissionDenied
        except PermissionDenied:
            msg = '权限拒绝'
            success = False
        except Exception as e:
            msg = str(e)
            success = False
        finally:
            return JsonResponse({'data': success, 'msg': msg})


def host_usage_downloads(request):
    """生成主机使用率下载数据"""
    if request.method == 'POST':
        raw_data = json.loads(request.body.decode('utf-8'))
        filter_project = raw_data.get('id_project', 0)
        filter_room = raw_data.get('id_room', "0")
        file_suffix = int(time.time())
        file_name = 'host_usage_' + str(file_suffix) + '.xls'
        download_path = os.path.join(os.path.dirname(__file__), 'host_usage_download', file_name)

        def gen_excel(download_path):
            if request.user.has_perm('users.view_host_usage'):
                wb = xlwt.Workbook()
                sheet_name = wb.add_sheet("user")

                # 第一行记录字段
                row1 = sheet_name.row(0)

                col_fields = [
                    '项目', '机房', '业务类型', '外网IP', 'CPU核数', 'RAM', '硬盘', '区服', '已装服数', '使用率'
                ]

                try:
                    for index, field in enumerate(col_fields):
                        row1.write(index, field)

                    # 添加sub_query
                    sub_query = Q(status=1)

                    if int(filter_project) != 0:
                        project = GameProject.objects.get(pk=filter_project)
                        sub_query.add(Q(belongs_to_game_project=project), Q.AND)

                    if filter_room != "0":
                        filter_room_name = filter_room.split('-')[-1]
                        sub_query.add(Q(belongs_to_room__room_name=filter_room_name), Q.AND)

                    query = Host.objects.select_related('belongs_to_game_project').select_related(
                        'belongs_to_room').filter(
                        sub_query).distinct()

                    search_host_usage = [i.show_usage() for i in query]

                    nrow = 1

                    for u in search_host_usage:
                        row = sheet_name.row(nrow)
                        for index, field in enumerate(col_fields):
                            if index == 0:
                                value = u['project']
                            elif index == 1:
                                value = u['room']
                            elif index == 2:
                                value = u['business']
                            elif index == 3:
                                value = u['extranet_ip']
                            elif index == 4:
                                value = u['cpu_num']
                            elif index == 5:
                                value = u['ram']
                            elif index == 6:
                                value = u['disk']
                            elif index == 7:
                                value = u['game_server']
                            elif index == 8:
                                value = u['game_server_count']
                            elif index == 9:
                                value = str(u['usage']) + '%'
                            row.write(index, value)
                        nrow += 1

                    wb.save(download_path)
                    data = file_name
                    success = True

                except Exception as e:
                    data = str(e)
                    success = False

                return {'data': data, 'success': success}
            else:
                success = False
                return {'msg': '没有权限', 'success': success}

        return JsonResponse(gen_excel(download_path))


def hostusagedownloads(request, filename):
    """主机使用率下载"""
    file = open('/data/www/cmdb/assets/host_usage_download/' + filename + '.xls', 'rb')
    response = FileResponse(file)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="' + filename + '.xls"'
    return response


def list_area(request):
    """列出地区数据"""
    if request.method == 'POST':
        data = []

        q = request.POST.get('q', None)

        if q:
            all_area = Area.objects.filter(
                Q(chinese_name=q) |
                Q(short_name=q))
        else:
            all_area = Area.objects.all()

        for x in all_area:
            data.append({'id': x.id, 'text': x.chinese_name})

        return JsonResponse(data, safe=False)


def host_migration_callback_api_doc(request):
    """主机迁服回调接口文档"""
    if request.method == 'GET':
        if request.user.is_superuser:
            return render(request, 'cmdb_host_migration_callbackapi_doc.html')
        else:
            return render(request, '403.html')


def host_recover_callback_api_doc(request):
    """主机回收回调接口文档"""
    if request.method == 'GET':
        if request.user.is_superuser:
            return render(request, 'cmdb_host_recover_callbackapi_doc.html')
        else:
            return render(request, '403.html')


def ops_manager_lock(request):
    """项目地区锁页面
    """

    if request.method == "GET":
        if request.user.is_superuser:
            head = {"value": "项目地区锁", "username": request.user.username}
            data = dict(OpsManager.STATUS)
            return render(request, 'project_area_lock.html', {"head": head, "data": data})
        else:
            return render(request, '403.html')


def saltstack_data_host(request):
    """saltstack选择执行主机的列表数据"""

    if request.method == 'POST':
        raw_get = request.POST.dict()
        draw = raw_get.get('draw', 0)

        # 根据字段过滤出host的参数
        filter_area = raw_get.get('filter_area', '0')
        filter_project = raw_get.get('filter_project', '全部')
        filter_room = raw_get.get('filter_room', '全部')

        # 添加sub_query
        sub_query = Q()

        if filter_area != '0':
            sub_query.add(Q(belongs_to_room__area__id=filter_area), Q.AND)

        if filter_project != '全部':
            sub_query.add(Q(belongs_to_game_project__project_name=filter_project), Q.AND)

        if filter_room != '全部':
            filter_room = filter_room.split('-')[-1]
            sub_query.add(Q(belongs_to_room__room_name=filter_room), Q.AND)

        query = Host.objects.select_related(
            'belongs_to_game_project').select_related(
            'belongs_to_room').filter(status=1).filter(sub_query)
        raw_data = query
        recordsTotal = query.count()
        data = {"data": [i.saltstack_show_all() for i in raw_data], 'draw': draw, 'recordsTotal': recordsTotal,
                'recordsFiltered': recordsTotal}
        return JsonResponse(data)


def saltstack_history_host_detail(request):
    """saltstack任务执行历史记录的主机详情"""

    if request.method == 'POST':
        raw_get = request.POST.dict()
        draw = raw_get.get('draw', 0)
        start = int(raw_get.get('start', 0))
        length = int(raw_get.get('length', 10))
        search_value = raw_get.get('search[value]', '')

        # 根据字段过滤出host的参数
        history_id = raw_get.get('history_id', None)
        if history_id:
            history = SaltTaskExecuteHistory.objects.get(pk=history_id)

            if search_value:
                search_value = search_value.split('-')[-1]
                query = history.saltexecutehistorydetail_set.select_related(
                    'host').select_related(
                    'host__belongs_to_game_project').select_related(
                    'host__belongs_to_room').filter(host__status=1).filter(
                    Q(host__belongs_to_game_project__project_name__icontains=search_value) |
                    Q(host__belongs_to_room__room_name__icontains=search_value) |
                    Q(host__belongs_to_business__business_name__icontains=search_value) |
                    Q(host__platform__icontains=search_value) |
                    Q(host__internal_ip__icontains=search_value) |
                    Q(host__telecom_ip__icontains=search_value) |
                    Q(host__unicom_ip__icontains=search_value) |
                    Q(host__host_identifier=search_value) |
                    Q(host__host_comment__icontains=search_value)
                ).order_by('status')
            else:
                query = history.saltexecutehistorydetail_set.select_related(
                    'host').select_related(
                    'host__belongs_to_game_project').select_related(
                    'host__belongs_to_room').filter(host__status=1).order_by('status')
            raw_data = query[start: start + length]
            recordsTotal = query.count()
            data = {"data": [i.show_all() for i in raw_data], 'draw': draw, 'recordsTotal': recordsTotal,
                    'recordsFiltered': recordsTotal}
            return JsonResponse(data)


def execute_salt_command_page(request):
    """执行salt命令页面"""
    if request.method == 'GET':
        if request.user.is_superuser:
            my_uuid = str(uuid.uuid1())
            return render(request, 'execute_salt_command.html', {'uuid': my_uuid})
        else:
            return render(request, '403.html')


def execute_salt_command(request):
    """执行salt命令"""
    if request.method == 'POST':
        success = True
        msg = 'ok'
        raw_data = json.loads(request.body.decode('utf-8'))
        raw_command = raw_data.get('salt_command', '')
        try:
            if not request.user.is_superuser:
                raise Exception('权限受限')
            if not raw_command:
                raise Exception('请输入salt命令！')
            uuid = raw_data.get('uuid', '')
            try:
                command = list(shlex.split(raw_command))
                info = format_salt_command(command)
            except:
                raise Exception('执行失败，请检查命令是否正确！')
            client = info['minion']
            fun = info['method']
            arg = info['arg']
            if fun == 'cmd.run':
                for a in arg:
                    if a in risk_command:
                        raise Exception('危险命令，禁止执行！')
            tgt_type = info['tgt_type']
            """执行salt命令"""
            salt = salt_init()
            result = salt.salt_command(client, fun, arg=arg, tgt_type=tgt_type)
            if not result:
                raise Exception('执行失败，请检查命令是否正确！')
            for k, v in result.items():
                if isinstance(v, bool):
                    v = json.dumps(v)
                if isinstance(v, str):
                    v = v.replace('\n', '<br/>').replace(' ', '&nbsp;')
                ws_update_salt_command_execute_result(
                    '<span style="color: #1e96d2;">' + json.dumps(k) + ':</span><br/>' +
                    '<span style="color: #50f04b;">' + json.dumps(v, indent=4, ensure_ascii=False) +
                    '</span>' + '<br/>', uuid)

            """记录日志"""
            SaltCommandHistory.objects.create(execute_user=request.user, command=raw_command, result=json.dumps(result))

        except Exception as e:
            success = False
            msg = str(e)
            """记录日志"""
            SaltCommandHistory.objects.create(execute_user=request.user, command=raw_command, result=json.dumps(msg))
        finally:
            return JsonResponse({'success': success, 'msg': msg})


def salt_command_history_result(request, history_id):
    """执行salt命令历史记录结果"""
    if request.method == 'POST':
        try:
            if not request.user.is_superuser:
                raise Exception('权限受限')
            history_obj = SaltCommandHistory.objects.get(pk=history_id)
            result = json.loads(history_obj.result)
            text = ''
            if isinstance(result, dict):
                for k, v in result.items():
                    if isinstance(v, bool):
                        v = json.dumps(v)
                    v = v.replace('\n', '<br/>').replace(' ', '&nbsp;')
                    text += '<span style="color: #1e96d2;">' + k + ':</span><br/>' + '<span style="color: #50f04b;">' + v + '</span>' + '<br/>'
            else:
                text = '<span style="color: #1e96d2;">' + result + '</span><br/>'
            data = {'text': text}
            return JsonResponse({'data': data})
        except Exception as e:
            data = {'text': str(e)}
            return JsonResponse({'data': data})


def host_statistics(request):
    """主机统计图表页面"""
    if request.method == 'GET':
        if request.user.is_superuser:
            return render(request, 'host_statistics.html')
        else:
            return render(request, '403.html')


def host_statistics_by_project_chart(request):
    """主机统计图表数据-按项目"""
    if request.method == 'POST':
        success = True
        data = ''
        try:
            if not request.user.is_superuser:
                raise Exception('权限受限')
            title = '按项目统计主机数量'
            legend_data = [x[1] for x in Host.STATUS]
            yAxis_data = list(set([x.belongs_to_game_project.project_name for x in
                                   Host.objects.select_related('belongs_to_game_project').all()]))
            yAxis_data.sort()
            series = get_host_statistics_by_project_chart_series(yAxis_data)
            data = {'title': title, 'legend_data': legend_data, 'yAxis_data': yAxis_data, 'series': series}

        except Exception as e:
            success = False
            data = str(e)
        finally:
            return JsonResponse({'success': success, 'data': data})


def host_statistics_by_room_chart(request):
    """主机统计图表数据-按机房"""
    if request.method == 'POST':
        success = True
        data = ''
        try:
            if not request.user.is_superuser:
                raise Exception('权限受限')
            title = '按机房统计主机数量'
            legend_data = [x[1] for x in Host.STATUS]
            yAxis_data = list(set([x.belongs_to_room.area.chinese_name + '-' + x.belongs_to_room.room_name for x in
                                   Host.objects.select_related('belongs_to_room').select_related(
                                       'belongs_to_room__area').all()]))
            yAxis_data.sort()
            series = get_host_statistics_by_room_chart_series(yAxis_data)
            data = {'title': title, 'legend_data': legend_data, 'yAxis_data': yAxis_data, 'series': series}

        except Exception as e:
            success = False
            data = str(e)
        finally:
            return JsonResponse({'success': success, 'data': data})


def host_initialize(request):
    """主机初始化功能页面"""
    if request.method == 'GET':
        if request.user.is_superuser:
            install_status = HostInitialize.INSTALL_STATUS
            initialize_status = HostInitialize.INITIALIZE_STATUS
            reboot_status = HostInitialize.REBOOT_STATUS
            instance_state = HostInitialize.INSTANCE_STATE
            import_status = HostInitialize.IMPORT_STATUS
            return render(request, 'host_initialize.html',
                          {'install_status': install_status, 'initialize_status': initialize_status,
                           'reboot_status': reboot_status, 'instance_state': instance_state,
                           'import_status': import_status})
        else:
            return render(request, '403.html')


def data_host_initialize(request):
    """主机初始化数据"""
    if request.method == 'POST':
        success = True
        msg = ''
        draw = 0
        recordsTotal = 0
        try:
            raw_get = request.POST.dict()

            search_value = raw_get.get('search[value]', '')
            start = int(raw_get.get('start', 0))
            draw = raw_get.get('draw', 0)
            length = int(raw_get.get('length', 10))

            # 添加sub_query
            sub_query = Q()
            if search_value:
                query = HostInitialize.objects.select_related('add_user').select_related('project').select_related(
                    'room').filter((Q(telecom_ip__icontains=search_value) |
                                    Q(sshport__icontains=search_value) |
                                    Q(sshuser__icontains=search_value) |
                                    Q(password__icontains=search_value) |
                                    Q(add_user__username__icontains=search_value) |
                                    Q(project__project_name__icontains=search_value) |
                                    Q(project__project_name_en__icontains=search_value) |
                                    Q(room__room_name__icontains=search_value) |
                                    Q(room__room_name_en__icontains=search_value) |
                                    Q(room__area__chinese_name__icontains=search_value) |
                                    Q(room__area__short_name__icontains=search_value))
                                   & sub_query).order_by('-add_time')
            else:
                query = HostInitialize.objects.select_related('add_user').select_related('project').select_related(
                    'room').filter(sub_query).order_by('-add_time')
            raw_data = query[start: start + length]
            recordsTotal = query.count()
            data = {"data": [i.show_all() for i in raw_data], 'draw': draw, 'recordsTotal': recordsTotal,
                    'recordsFiltered': recordsTotal, 'success': success}
            return JsonResponse(data)
        except Exception as e:
            success = False
            msg = str(e)
            return JsonResponse({'success': success, 'msg': msg, "data": [], 'draw': draw, 'recordsTotal': recordsTotal,
                                 'recordsFiltered': recordsTotal, })


def add_or_edit_host_initialize_manual(request):
    """
    添加初始化主机
    - 根据主机实例查询主机初始化记录是否存在
        - 存在，更新除电信IP以外的字段信息
        - 不存在，新增主机初始化记录
    """

    if request.method == "POST":
        raw_data = json.loads(request.body.decode('utf-8'))
        msg = 'ok'
        success = True

        try:
            if request.user.is_superuser:
                telecom_ip = raw_data.get('telecom_ip', '')
                project = raw_data.pop('project')
                project = GameProject.objects.get(pk=project)
                raw_data['project'] = project
                room = raw_data.pop('room')
                room = Room.objects.get(pk=room)
                raw_data['room'] = room
                business = raw_data.pop('business')
                business = Business.objects.get(pk=business)
                raw_data['business'] = business
                raw_data['add_user'] = request.user
                at_once = raw_data.pop('at_once', '')
                editFlag = raw_data.pop('editFlag', '')

                """创建主机初始化记录"""
                host_initialize = HostInitialize.objects.filter(telecom_ip=telecom_ip)
                if host_initialize:
                    raw_data.pop('telecom_ip')
                    if not editFlag:
                        raw_data['install_status'] = 0
                        raw_data['initialize_status'] = 0
                        host_initialize[0].save(update_fields=['add_time'])
                    host_initialize.update(**raw_data)
                else:
                    raw_data.pop('install_status', '')
                    raw_data.pop('initialize_status', '')
                    host_initialize = HostInitialize.objects.create(**raw_data)
                    """创建主机初始化日志记录"""
                    HostInitializeLog.objects.create(host_initialize=host_initialize)

                """如果立即执行为True，则调用主机初始化异步任务"""
                if at_once:
                    host_initialize.update(**{'install_status': 1})
                    ws_update_host_initialize_list()
                    log = '{} - 开始执行主机初始化任务'.format(request.user.username)
                    for i in host_initialize:
                        write_host_initialize_log('INFO', log, i)
                        write_host_initialize_log('INFO', '【步骤1】-【开始】-【安装salt-minion】', i)
                    """发送安装salt-minion异步任务"""
                    install_salt_minion.delay([h.telecom_ip for h in host_initialize])
            else:
                raise PermissionDenied
        except PermissionDenied:
            msg = '你没有初始化主机的权限'
            success = False
        except GameProject.DoesNotExist:
            msg = '游戏项目不存在'
            success = False
        except Room.DoesNotExist:
            msg = '机房名不存在'
            success = False
        except Business.DoesNotExist:
            msg = '业务类型不存在'
            success = False
        except Exception as e:
            msg = str(e)
            success = False
        return JsonResponse({'data': success, 'msg': msg})


def get_initialize_host_info(request):
    """获取初始化主机信息"""
    if request.method == "POST":
        edit_data = dict()
        try:
            id = json.loads(request.body.decode('utf-8')).get('id')
            host_initialize = HostInitialize.objects.get(pk=id)
            edit_data = host_initialize.edit_data()
            edit_data['success'] = True
        except HostInitialize.DoesNotExist:
            edit_data['success'] = False
            edit_data['msg'] = '主机初始化记录不存在'
        except Exception as e:
            edit_data['success'] = False
            edit_data['msg'] = str(e)
        finally:
            return JsonResponse(edit_data)


def host_initialize_log(request, initialize_id):
    """主机初始化日志"""
    if request.method == "GET":
        if request.user.is_superuser:
            host_initialize = HostInitialize.objects.get(pk=initialize_id)
            telecom_ip = host_initialize.telecom_ip
            content = host_initialize.hostinitializelog.content
            return render(request, 'host_initialize_log.html',
                          {'initialize_id': initialize_id, 'telecom_ip': telecom_ip, 'content': content})
        else:
            return render(request, '403.html')


def start_host_initialize(request):
    """开始初始化主机"""
    if request.method == 'POST':
        raw_data = json.loads(request.body.decode('utf-8'))
        msg = 'ok'
        success = True

        try:
            if request.user.is_superuser:
                telecom_ip_list = raw_data.get('telecom_ip', '')
                host_initialize = HostInitialize.objects.filter(telecom_ip__in=telecom_ip_list)
                host_initialize.update(**{'install_status': 1})
                ws_update_host_initialize_list()
                log = '{} - 开始执行主机初始化任务'.format(request.user.username)
                for i in host_initialize:
                    write_host_initialize_log('INFO', log, i)
                    write_host_initialize_log('INFO', '【步骤1】-【开始】-【安装salt-minion】', i)
                """发送安装salt-minion异步任务"""
                install_salt_minion.delay(telecom_ip_list)
            else:
                raise PermissionDenied
        except PermissionDenied:
            msg = '你没有初始化主机的权限'
            success = False
        except Exception as e:
            msg = str(e)
            success = False
        return JsonResponse({'data': success, 'msg': msg})


def reboot_initialize_host(request):
    """开始重启主机"""
    if request.method == 'POST':
        raw_data = json.loads(request.body.decode('utf-8'))
        msg = 'ok'
        success = True

        try:
            if request.user.is_superuser:
                telecom_ip_list = raw_data.get('telecom_ip', '')
                host_initialize = HostInitialize.objects.filter(telecom_ip__in=telecom_ip_list)
                host_initialize.update(**{'reboot_status': 1})
                ws_update_host_initialize_list()
                for i in host_initialize:
                    write_host_initialize_log('INFO', '【步骤5】-【开始】-【重启主机】', i)
                    """发送重启主机异步任务"""
                    saltstack_host_reboot.delay(i.telecom_ip)
            else:
                raise PermissionDenied
        except PermissionDenied:
            msg = '你没有重启主机的权限'
            success = False
        except Exception as e:
            msg = str(e)
            success = False
        return JsonResponse({'data': success, 'msg': msg})


def import_initialize_host(request):
    """开始入库主机"""
    if request.method == 'POST':
        raw_data = json.loads(request.body.decode('utf-8'))
        msg = 'ok'
        success = True

        try:
            if request.user.is_superuser:
                telecom_ip_list = raw_data.get('telecom_ip', '')
                host_initialize = HostInitialize.objects.filter(telecom_ip__in=telecom_ip_list)
                host_initialize.update(**{'import_status': 1})
                ws_update_host_initialize_list()
                for i in host_initialize:
                    write_host_initialize_log('INFO', '【步骤6】-【开始】-【入库主机】', i)
                    """发送入库主机异步任务"""
                    saltstack_host_import.delay(i.telecom_ip)
            else:
                raise PermissionDenied
        except PermissionDenied:
            msg = '你没有入库主机的权限'
            success = False
        except Exception as e:
            msg = str(e)
            success = False
        return JsonResponse({'data': success, 'msg': msg})


def host_initialize_templates_download(request, filename):
    """主机初始化excel模板下载"""
    file = open('/data/www/cmdb/assets/excel_templates/' + filename + '.xlsx', 'rb')
    response = FileResponse(file)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="' + filename + '.xlsx"'
    return response


def host_initialize_batch_excel_import(request):
    """初始化主机批量excel导入"""
    if request.method == 'POST':
        msg = 'ok'
        success = True
        try:
            with transaction.atomic():
                form = UploadFileForm(request.POST, request.FILES)
                if form.is_valid():
                    fname = request.FILES['file'].name
                    save_uploaded_file(request.FILES['file'], 'assets/upload/', fname)
                    table = read_excel_table_data('assets/upload/' + fname)
                    if table['tbody']:
                        for data in table['tbody']:
                            minion_ip = data[0].strip()
                            host_initialize = HostInitialize.objects.filter(telecom_ip=minion_ip)
                            try:
                                business = Business.objects.get(business_name=data[5].strip())
                            except Exception:
                                raise Exception('业务类型不存在: {}'.format(data[5].strip()))
                            try:
                                project = GameProject.objects.get(project_name_en=data[6].strip())
                            except Exception:
                                raise Exception('游戏项目不存在: {}'.format(data[6].strip()))
                            try:
                                area_name = data[7].strip().split('-')[0]
                                room_name = data[7].strip().split('-')[-1]
                                room = Room.objects.get(area__chinese_name=area_name, room_name=room_name)
                            except Exception:
                                raise Exception('机房不存在: {}，请确认机房格式是否正确'.format(data[7]))

                            if host_initialize:
                                host_initialize = host_initialize[0]
                                host_initialize.syndic_ip = data[1].strip()
                                host_initialize.sshport = data[2].strip()
                                host_initialize.sshuser = data[3].strip()
                                host_initialize.password = data[4].strip()
                                host_initialize.business = business
                                host_initialize.project = project
                                host_initialize.room = room
                                host_initialize.add_user = request.user
                                host_initialize.install_status = 0
                                host_initialize.initialize_status = 0
                                host_initialize.reboot_status = 0
                                host_initialize.save()
                            else:
                                HostInitialize.objects.create(telecom_ip=minion_ip, syndic_ip=data[1].strip(),
                                                              sshport=data[2].strip(), sshuser=data[3].strip(),
                                                              password=data[4].strip(), business=business,
                                                              project=project, room=room, add_user=request.user)
                else:
                    msg = form.errors
        except Exception as e:
            success = False
            msg = str(e)
            print(msg)
        finally:
            return JsonResponse({'success': success, 'msg': msg})


def sync_pillar(request):
    """同步pillar"""
    if request.method == 'POST':
        msg = 'ok'
        success = True
        try:
            if request.user.is_superuser:
                """执行同步pillar任务"""
                result = sync_pillar_config()
                msg = result
            else:
                raise PermissionDenied
        except PermissionDenied:
            msg = '你没有同步pillar的权限'
            success = False
        except Exception as e:
            msg = str(e)
            success = False
        return JsonResponse({'data': success, 'msg': msg})


def cloud(request):
    """云供应商"""
    if request.method == 'GET':
        if request.user.is_superuser:
            return render(request, 'cloud.html')
        else:
            return render(request, '403.html')

    if request.method == 'POST':
        raw_get = request.POST.dict()

        draw = raw_get.get('draw', 0)

        recordsTotal = Cloud.objects.count()
        raw_data = Cloud.objects.all()
        data = {"data": [i.show_all() for i in raw_data], 'draw': draw, 'recordsTotal': recordsTotal,
                'recordsFiltered': recordsTotal}
        return JsonResponse(data)


def add_or_edit_cloud(request):
    """增加或者修改云供应商信息"""

    if request.method == "POST":
        raw_data = json.loads(request.body.decode('utf-8'))
        msg = 'ok'
        editFlag = raw_data.pop('editFlag')
        id = raw_data.pop('id')

        try:
            if not request.user.is_superuser:
                raise PermissionError
            if editFlag:
                c = Cloud.objects.filter(id=id)
                c.update(**raw_data)
                success = True
            else:
                Cloud.objects.create(**raw_data)
                success = True
        except PermissionDenied:
            msg = '权限受限'
            success = False
        except Exception as e:
            msg = str(e)
            success = False

        return JsonResponse({'data': success, 'msg': msg})


def tecent_cloud_account(request):
    """腾讯云帐号信息"""
    if request.method == 'GET':
        if request.user.is_superuser:
            return render(request, 'tecent_cloud_account.html')
        else:
            return render(request, '403.html')

    if request.method == 'POST':
        raw_get = request.POST.dict()

        draw = raw_get.get('draw', 0)

        recordsTotal = TecentCloudAccount.objects.count()
        raw_data = TecentCloudAccount.objects.all()
        data = {"data": [i.show_all() for i in raw_data], 'draw': draw, 'recordsTotal': recordsTotal,
                'recordsFiltered': recordsTotal}
        return JsonResponse(data)


def add_or_edit_tecent_cloud_account(request):
    """增加或者修改腾讯云帐号信息"""

    if request.method == "POST":
        raw_data = json.loads(request.body.decode('utf-8'))
        msg = 'ok'
        editFlag = raw_data.pop('editFlag')
        id = raw_data.pop('id')
        raw_data['cloud'] = Cloud.objects.get(name='腾讯云')

        try:
            if not request.user.is_superuser:
                raise PermissionError
            if editFlag:
                t = TecentCloudAccount.objects.filter(id=id)
                t.update(**raw_data)
                success = True
            else:
                TecentCloudAccount.objects.create(**raw_data)
                success = True

        except IntegrityError:
            msg = '备注必须唯一'
            success = False
        except PermissionDenied:
            msg = '权限受限'
            success = False
        except Exception as e:
            msg = str(e)
            success = False

        return JsonResponse({'data': success, 'msg': msg})


def host_trace(request):
    """主机变更记录页面"""
    if request.method == 'GET':
        if request.user.is_superuser:
            all_type = HostHistoryRecord.TYPE
            all_users = User.objects.all()
            return render(request, 'host_trace.html', {'type': all_type, 'all_users': all_users})
        else:
            return render(request, '403.html')


def data_host_trace(request):
    """主机变更追踪数据"""
    if request.method == "POST":
        if request.user.is_superuser:
            raw_get = request.POST.dict()

            search_value = raw_get.get('search[value]', '')
            start = int(raw_get.get('start', 0))
            draw = raw_get.get('draw', 0)
            length = int(raw_get.get('length', 10))

            filter_type = raw_get.get('filter_type', '0')
            filter_operation_user = raw_get.get('filter_operation_user', '0')
            filter_host_ip = raw_get.get('filter_host_ip', '')
            filter_source_ip = raw_get.get('filter_source_ip', '')

            # 添加sub_query
            sub_query = Q()

            if filter_type != '0':
                sub_query.add(Q(type=filter_type), Q.AND)
            if filter_operation_user != '0':
                sub_query.add(Q(operation_user__id=filter_operation_user), Q.AND)
            if filter_host_ip != '':
                sub_query.add((Q(host__telecom_ip__icontains=filter_host_ip) | Q(
                    host__internal_ip__icontains=filter_host_ip) | Q(host__unicom_ip__icontains=filter_host_ip) | Q(
                    remark__icontains=filter_host_ip)), Q.AND)
            if filter_source_ip != '':
                sub_query.add(Q(source_ip__icontains=filter_source_ip), Q.AND)

            query = HostHistoryRecord.objects.select_related('host').select_related(
                'host__belongs_to_game_project').select_related('host__belongs_to_room').select_related(
                'host__belongs_to_business').filter(sub_query).order_by(
                '-create_time')

            raw_data = query[start: start + length]
            recordsTotal = query.count()
            data = {"data": [i.show_all() for i in raw_data], 'draw': draw, 'recordsTotal': recordsTotal,
                    'recordsFiltered': recordsTotal}
            return JsonResponse(data)
