from django.shortcuts import render_to_response, render
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.db import transaction
from django.db import IntegrityError
from django.db.models import Q
from django.db.models import Count
from django.db.models import Max
from django.db.models import Sum
from django.core.exceptions import PermissionDenied
from django.core.exceptions import MultipleObjectsReturned
# from cmdb.url_to_title import *

from myworkflows.models import *
from myworkflows.utils import *
from myworkflows.utils import _pair_code_order_updatetype_available
from myworkflows.utils import _add_workflow_state
from myworkflows.utils import _delete_workflow_state
from myworkflows.exceptions import *
from myworkflows.cursors import Cursor
from myworkflows.rsync_conf import RSYNC_MAP
from myworkflows.rsync_conf import PROJECT_CELERY_QUEUE_MAP
from myworkflows.rsync_conf import CSXY_TYPES
from myworkflows.config import MACHINE_CONFIG
from myworkflows.cdn_url_config import WEB_URL
from myworkflows.cdn_url_config import CLIENT_TYPE
from myworkflows.cdn_url_config import CDN_ROOT_URL
from myworkflows.excel_utils import gen_hotupdate_excel

from webapi.utils import get_cdn_list_from_web
from webapi.utils import GetCDNDirFromWeb

from myworkflows.workflow_approve_user_dispatch import workflow_approve_user
from myworkflows.workflow_approve_user_by_chain import get_approve_user_chain

from assets.models import Room
from assets.models import Area
from assets.models import GameProject
from assets.models import ProjectGroup
from assets.models import GroupSection
from assets.utils import group_in_charge_projects
from assets.utils import get_ip

from users.models import Group, OrganizationMptt
from webapi.models import WebGetCdnListAPI

from cmdb.logs import SVNLog, PullFileLog, WorkflowApproveLog
from cmdb.settings import PRODUCTION_ENV
from cmdb.settings import NEW_WORKFLOW
from cmdb.settings import NEW_VERSION_UPDATE

import json
import time
from datetime import datetime
from datetime import timedelta
from operator import itemgetter

from tasks import workflow_add_server_permission
from tasks import add_svn_workflow
from tasks import send_mail
from tasks import do_hot_update
from tasks import send_qq
from tasks import file_pull_8
from tasks import file_pull_15
from tasks import file_pull_cc
from tasks import file_pull_23
from tasks import file_pull_slqy3d_cn
from tasks import file_pull_cyh5s7
from test_tasks import file_pull_test_8
from test_tasks import file_pull_test_15
from test_tasks import file_pull_test_cc
from test_tasks import file_pull_test_slqy3d_cn
from tasks import clean_svn_workflow
from tasks import clean_project_serper
from tasks import add_mysql_permission
from tasks import add_mac
from tasks import send_weixin_message
from tasks import game_server_action_task
from tasks import do_hot_client
from tasks import do_host_migrate
from tasks import do_host_recover
from tasks import send_task_card_to_wx_user
from tasks import do_game_server_migrate
from tasks import version_update_task
from myworkflows.myredis import *
from itertools import islice
from django.forms.models import model_to_dict
from requests.packages.urllib3.util import Retry
from requests.adapters import HTTPAdapter
from requests import Session

import requests
import os
import re
import heapq
import traceback


def get_yl_network_administrator():
    """获取原力网络管理员"""
    yl_network_administrator = SpecialUserParamConfig.objects.filter(param='YL_NETWORK_ADMINISTRATOR')
    if yl_network_administrator:
        yl_network_administrator = yl_network_administrator[0].get_user_list()
    else:
        yl_network_administrator = []
    return yl_network_administrator


def get_machine_administrator():
    """获取原力服务器申请管理员"""
    machine_administrator = SpecialUserParamConfig.objects.filter(param='MACHINE_ADMINISTRATOR')
    if machine_administrator:
        machine_administrator = machine_administrator[0].get_user_list()
    else:
        machine_administrator = []
    return machine_administrator


def get_cc_network_administrator():
    """获取创畅网络管理员"""
    cc_network_administrator = SpecialUserParamConfig.objects.filter(param='CC_NETWORK_ADMINISTRATOR')
    if cc_network_administrator:
        cc_network_administrator = cc_network_administrator[0].get_user_list()
    else:
        cc_network_administrator = []
    return cc_network_administrator


def svn_perm_scheme(request):
    """SVN权限方案列表"""
    if request.method == 'GET':
        if User.objects.get(id=request.user.id).has_perm('users.view_svn_scheme'):
            head = {'value': 'SVN权限方案列表', 'username': request.user.username}
            return render(request, 'svn_perm_scheme.html', {'head': head})
        else:
            return render(request, '403.html')


def data_svn_scheme(request):
    if request.method == "GET":
        if User.objects.get(id=request.user.id).has_perm('users.view_svn_scheme'):
            raw_get = request.GET.dict()
            draw = raw_get.get('draw', 0)

            # 用户只能通过和自己关联的项目来查看到相应的svn套餐
            # 管理员用户可以查看所有的套餐
            if request.user.is_superuser:
                raw_data = SVNScheme.objects.all()
            else:
                # 如果用户是哪些项目的负责人
                project_list = GameProject.objects.filter(leader=request.user)
                raw_data = SVNScheme.objects.filter(project__in=project_list)
            recordsTotal = len(raw_data)
            data = {"data": [i.show_all() for i in raw_data], 'draw': draw, 'recordsTotal': recordsTotal,
                    'recordsFiltered': recordsTotal}
            return JsonResponse(data)


def add_or_edit_svn_scheme(request):
    '增加或者修改svn方案'

    if request.method == "POST":
        raw_data = json.loads(request.body.decode('utf-8'))
        msg = 'ok'
        editFlag = raw_data.pop('editFlag')
        id = raw_data.pop('id')
        project = raw_data.pop('project')

        try:
            project = GameProject.objects.get(id=project)
            raw_data['project'] = project
            if editFlag:
                if User.objects.get(id=request.user.id).has_perm('users.edit_svn_scheme'):
                    s = SVNScheme.objects.filter(id=id)
                    s.update(**raw_data)
                    success = True
                else:
                    raise PermissionDenied
            else:
                if User.objects.get(id=request.user.id).has_perm('users.add_svn_scheme'):
                    SVNScheme.objects.create(**raw_data)
                    success = True
                else:
                    raise PermissionDenied
        # except PermissionDenied:
        #    msg = '你没有增加机房的权限'
        #    success = False
        except PermissionDenied:
            msg = '权限拒绝'
            success = False
        except IntegrityError:
            msg = '方案名重复'
            success = False
        except GameProject.DoesNotExist:
            msg = '项目不存在'
            success = False
        except Exception as e:
            msg = str(e)
            success = False

        return JsonResponse({'data': success, 'msg': msg})


def get_svn_scheme(request):
    '获取svn方案'
    if request.method == "POST":
        if User.objects.get(id=request.user.id).has_perm('users.edit_svn_scheme'):
            id = json.loads(request.body.decode('utf-8')).get('id')
            obj = SVNScheme.objects.get(id=id)

            edit_data = obj.edit_data()

            return JsonResponse(edit_data)
        else:
            raise PermissionDenied


def del_svn_scheme(request):
    '删除方案'
    if request.method == "POST":
        if User.objects.get(id=request.user.id).has_perm('users.del_svn_scheme'):
            del_data = json.loads(request.body.decode('utf-8'))
            objs = SVNScheme.objects.filter(id__in=del_data)
            try:
                with transaction.atomic():
                    objs.delete()
                msg = ''
                success = True
            except Exception as e:
                msg = str(e)
                success = False
            return JsonResponse({'data': success, 'msg': msg})
        else:
            raise PermissionDenied


def svn_scheme_detail(request):
    'SVN权限方案明细, 当前用户的项目分组和svn套餐的项目要一致'
    if request.method == 'GET':
        if User.objects.get(id=request.user.id).has_perm('users.view_svn_scheme'):
            id = request.GET.get('id')

            if request.user.is_superuser:
                svn_scheme = SVNScheme.objects.get(id=id)
                head = {'value': svn_scheme.name, 'username': request.user.username}
                return render(request, 'svn_scheme_detail.html', {'head': head})
            else:
                # 用户的项目分组
                """
                user_game_project_group = request.user.profile.project_group
                if user_game_project_group:
                    try:
                        svn_scheme = SVNScheme.objects.get(id=id, project=user_game_project_group.project)
                        head = {'value': svn_scheme.name, 'username': request.user.username}
                        return render(request, 'svn_scheme_detail.html', {'head': head})
                    except SVNScheme.DoesNotExist:
                        return render(request, '403.html')
                else:
                    return render(request, '403.html')
                """
                # 用户是哪些项目的负责人
                list_game_project = GameProject.objects.filter(leader=request.user)

                # 当前的svn_scheme所属的项目
                svn_scheme = SVNScheme.objects.get(id=id)
                svn_scheme_project = svn_scheme.project
                if svn_scheme_project in list_game_project:
                    head = {'value': svn_scheme.name, 'username': request.user.username}
                    return render(request, 'svn_scheme_detail.html', {'head': head})
                else:
                    return render(request, '403.html')
        else:
            return render(request, '403.html')


def add_or_edit_svn_scheme_detail(request):
    '增加或者修改svn方案明细'

    if request.method == "POST":
        raw_data = json.loads(request.body.decode('utf-8'))
        msg = 'ok'
        editFlag = raw_data.pop('editFlag')
        id = raw_data.pop('id')
        svn_repo = raw_data.pop('svn_repo')
        svn_scheme_id = raw_data.pop('svn_scheme_id')

        try:
            svn_repo = SVNRepo.objects.get(id=svn_repo)
            svn_scheme = SVNScheme.objects.get(id=svn_scheme_id)
            raw_data['svn_repo'] = svn_repo
            raw_data['svn_scheme'] = svn_scheme
            if editFlag:
                if User.objects.get(id=request.user.id).has_perm('users.edit_svn_scheme'):
                    s = SVNSchemeDetail.objects.filter(id=id)
                    s.update(**raw_data)
                    success = True
                else:
                    raise PermissionDenied
            else:
                if User.objects.get(id=request.user.id).has_perm('users.add_svn_scheme'):
                    SVNSchemeDetail.objects.create(**raw_data)
                    success = True
                else:
                    raise PermissionDenied
        except PermissionDenied:
            msg = '权限拒绝'
            success = False
        except IntegrityError:
            msg = '记录有重复'
            success = False
        except SVNRepo.DoesNotExist:
            msg = '仓库不存在'
            success = False
        except SVNScheme.DoesNotExist:
            msg = '方案不存在'
            success = False
        except Exception as e:
            msg = str(e)
            success = False

        return JsonResponse({'data': success, 'msg': msg})


def data_svn_scheme_detail(request):
    if request.method == "POST":
        if User.objects.get(id=request.user.id).has_perm('users.view_svn_scheme'):
            raw_get = request.POST.dict()
            draw = raw_get.get('draw', 0)
            id = raw_get.get('id')
            svn_scheme_obj = SVNScheme.objects.get(id=id)
            if request.user.is_superuser:
                recordsTotal = SVNSchemeDetail.objects.filter(svn_scheme=svn_scheme_obj).count()
                raw_data = SVNSchemeDetail.objects.filter(svn_scheme=svn_scheme_obj)
            else:
                # 用户的项目分组
                """
                user_game_project_group = request.user.profile.project_group
                if user_game_project_group:
                    raw_data = SVNSchemeDetail.objects.filter(
                        svn_scheme=id, svn_scheme__project=user_game_project_group.project)
                    recordsTotal = len(raw_data)
                else:
                    raw_data = SVNSchemeDetail.objects.filter(svn_scheme=id, svn_scheme__project=None)
                    recordsTotal = len(raw_data)
                """

                # 查找出这个人是哪些项目的负责人
                list_game_project = GameProject.objects.filter(leader=request.user)

                # 当前svn_scheme的项目
                svn_scheme_project = svn_scheme_obj.project

                if svn_scheme_project in list_game_project:

                    raw_data = SVNSchemeDetail.objects.filter(svn_scheme=id, svn_scheme__project__in=list_game_project)
                else:
                    raw_data = []
                recordsTotal = len(raw_data)

            data = {"data": [i.show_all() for i in raw_data], 'draw': draw, 'recordsTotal': recordsTotal,
                    'recordsFiltered': recordsTotal}
            return JsonResponse(data)


def get_svn_scheme_data(request):
    'svn方案的全部明细'
    if request.method == "POST":
        svn_scheme_id = json.loads(request.body.decode('utf-8')).get('svn_scheme_id')
        svn_scheme_details = SVNSchemeDetail.objects.filter(svn_scheme=svn_scheme_id)

        return JsonResponse([x.show_all_data() for x in svn_scheme_details], safe=False)


def get_svn_scheme_detail(request):
    '获取svn方案明细'
    if request.method == "POST":
        if User.objects.get(id=request.user.id).has_perm('users.edit_svn_scheme'):
            id = json.loads(request.body.decode('utf-8')).get('id')
            obj = SVNSchemeDetail.objects.get(id=id)

            edit_data = obj.edit_data()

            return JsonResponse(edit_data)
        else:
            raise PermissionDenied


def del_svn_scheme_detail(request):
    '删除方案明细'
    if request.method == "POST":
        if User.objects.get(id=request.user.id).has_perm('users.del_svn_scheme'):
            del_data = json.loads(request.body.decode('utf-8'))
            objs = SVNSchemeDetail.objects.filter(id__in=del_data)
            try:
                with transaction.atomic():
                    objs.delete()
                msg = ''
                success = True
            except Exception as e:
                msg = str(e)
                success = False
            return JsonResponse({'data': success, 'msg': msg})
        else:
            raise PermissionDenied


def list_svn_repo(request):
    '下拉展示SVN仓库'
    if request.method == "POST":
        data = []

        q = request.POST.get('q', None)

        if q:
            all_repo = SVNRepo.objects.filter(name__icontains=q)
        else:
            all_repo = SVNRepo.objects.all()

        for x in all_repo:
            data.append({'id': x.id, 'text': x.name})

        return JsonResponse(data, safe=False)


def list_workflow(request):
    '下拉展示SVN仓库'
    if request.method == "POST":
        data = []

        q = request.POST.get('q', None)

        if q:
            all_repo = Workflow.objects.filter(name__icontains=q)
        else:
            all_repo = Workflow.objects.all()

        for x in all_repo:
            data.append({'id': x.id, 'text': x.name})

        return JsonResponse(data, safe=False)


def list_game_project(request):
    '下拉展示项目'
    if request.method == "POST":

        data = []
        q = request.POST.get('q', None)
        all_game_project_id = [x['project'] for x in
                               GameServer.objects.values('project').annotate(count=Count('project'))]
        if q is None:
            all_game_project = GameProject.objects.filter(id__in=all_game_project_id)
        else:
            all_game_project = GameProject.objects.filter(id__in=all_game_project_id).filter(
                Q(project_name__icontains=q) | Q(project_name_en__icontains=q))

        for x in all_game_project:
            data.append({'id': x.id, 'text': x.project_name})

        return JsonResponse(data, safe=False)


def list_game_project_by_group(request):
    """选择热更新工单后
    根据申请人所在的部门和部门负责的项目
    来下拉选择对应的项目
    """
    if request.method == "POST":
        data = []
        q = request.POST.get('q', None)

        all_game_project_id = [x['project'] for x in
                               GameServer.objects.values('project').annotate(count=Count('project'))]
        if q:
            all_game_project = [x for x in GameProject.objects.filter(id__in=all_game_project_id) if
                                (re.search(q, x.project_name) or re.search(q, x.project_name_en))]
        else:
            all_game_project = list(GameProject.objects.filter(id__in=all_game_project_id))

        if request.user.is_superuser:
            for x in all_game_project:
                data.append({'id': x.id, 'text': x.project_name})
        else:
            """
            2018.12修改，只列出申请人所在部门负责的游戏项目，关联新组织架构表
            """
            org = OrganizationMptt.objects.get(user=request.user)
            for project in all_game_project:
                if not project.organizationmptt_set.all():
                    continue
                if not org.get_department_obj():
                    continue
                project_group = project.organizationmptt_set.all()
                if org.get_department_obj() in project_group:
                    data.append({'id': project.id, 'text': project.project_name})

        return JsonResponse(data, safe=False)


def list_project_group_user(request):
    """下拉展示项目所属部门下对应分组的所有人员"""

    if request.method == "POST":
        data = []
        all_users = []

        # 查询参数
        q = request.POST.get('q', '')

        # 所属的游戏项目
        game_project_id = request.POST.get('project', None)

        if game_project_id == '0':
            return JsonResponse(data, safe=False)

        project = GameProject.objects.get(id=game_project_id)

        # 游戏项目分组 剑雨江湖 后端组（服务端技术组）
        project_group_name = request.POST.get('project_group', None)

        # 少年群侠项目的测试没有了，就是工单发起人自身
        if project.project_name_en == 'snqxz' and project_group_name == '测试组':
            data.append({'id': request.user.id, 'text': request.user.username})
            return JsonResponse(data, safe=False)

        """
        2019.12修改，关联新组织架构表
        找到负责该项目的所有部门，然后找到这些部门下面的部门分组人员
        """
        try:
            departments = project.organizationmptt_set.all()
            for department in departments:
                department_group = department.get_children().filter(type=1, is_department_group=1,
                                                                    name=project_group_name)
                if not department_group:
                    continue
                department_group_users = OrganizationMptt.objects.filter(parent=department_group, type=2, is_active=1)
                all_users.extend([x.user for x in department_group_users])
                if department_group[0].leader == 0:
                    continue
                all_users.append(User.objects.get(pk=department_group[0].leader))

            # 去重
            all_users = list(set(all_users))

            # 然后找出搜索匹配
            all_users = [x for x in all_users if (re.search(q, x.username) or re.search(q, x.first_name))]

            for x in all_users:
                data.append({'id': x.id, 'text': x.username})

        except Exception as e:
            print(str(e))
            return JsonResponse(data, safe=False)

        return JsonResponse(data, safe=False)


def list_project_related_ops(request):
    """选择项目相关的运维人员
    """

    if request.method == "POST":
        data = []

        # 查询参数
        q = request.POST.get('q', '')

        # 所属的游戏项目
        game_project_id = request.POST.get('project', None)

        if game_project_id == '0':
            return JsonResponse(data, safe=False)

        project = GameProject.objects.get(id=game_project_id)

        project_related_ops = project.related_user.all()

        # 然后找出搜索匹配
        all_users = [x for x in project_related_ops if (re.search(q, x.username) or re.search(q, x.first_name))]

        for x in all_users:
            if x.is_active:
                data.append({'id': x.id, 'text': x.username})

        return JsonResponse(data, safe=False)


def list_game_project_area(request):
    '下拉根据项目展示地区'
    if request.method == "POST":

        data = []

        project_id = request.POST.get('project', None)

        if project_id == '0':
            return JsonResponse(data, safe=False)

        project = GameProject.objects.get(id=project_id)

        all_area_name = [
            x['area_name'] for x in GameServer.objects.values('area_name').filter(
                project=project).annotate(dcount=Count('area_name'))
        ]

        for x in all_area_name:
            data.append({'id': x, 'text': x})

        return JsonResponse(data, safe=False)


def list_game_project_area_detail(request):
    """根据cmdb运维管理机过滤项目，
    得到有哪些地区，如果有地区没有在rsnyc_conf.py的配置文件中
    cmdb地区对应到的版本接收机地区， 例如 大陆-> cn
    返回None,此时前端不能选择地区
    """
    if request.method == 'POST':
        try:
            data = []

            project_id = request.POST.get('project', None)
            update_type = request.POST.get('update_type', None)

            if project_id == '0':
                return JsonResponse(data, safe=False)

            project = GameProject.objects.get(id=project_id)

            all_area_name = [
                x['area_name'] for x in GameServer.objects.values('area_name').filter(
                    project=project).annotate(dcount=Count('area_name'))
            ]

            for area_name in all_area_name:
                try:
                    list_area_name_detail = RSYNC_MAP[project.project_name_en][update_type][area_name]
                except KeyError:
                    continue
                else:
                    for x in list_area_name_detail:
                        data.append({'id': area_name, 'text': area_name + '-' + x})
        except Exception as e:
            data = []
        return JsonResponse(data, safe=False)


def list_pair_code(request):
    """下拉选择已经创建好的绑定的热更新代号
    工单状态为0或者4
    """

    if request.method == "POST":
        data = [{'id': '0', 'text': '选择加入', 'order': '无'}]

        update_type = request.POST.get('update_type', None)
        if update_type == 'hot_client':
            obj = ServerHotUpdate
        else:
            obj = ClientHotUpdate

        list_hot_obj = obj.objects.filter(status__in=['0', '4']).exclude(pair_code=None)

        for x in list_hot_obj:
            text = x.pair_code + '-' + x.creator.username + '-' + x.title + '-' + x.create_time.strftime(
                '%Y-%m-%d %H:%M')
            data.append({'id': x.pair_code, 'text': text, 'order': x.order})

        return JsonResponse(data, safe=False)


def pull_file_list(request):
    """热更新获取版本接收机文件列表
    """

    if request.method == "POST":
        raw_data = json.loads(request.body.decode('utf-8'))
        update_type = raw_data.get('update_type')
        project = raw_data.get('project')
        area_name = raw_data.get('area_name')
        area_name_en = Area.objects.get(chinese_name=area_name).short_name
        version = raw_data.get('version')
        uuid = raw_data.get('uuid')
        content = raw_data.get('content')
        client_type = raw_data.get('client_type', None)

        data = ''
        success = True
        result_file_list = []
        celery_queue = None
        log = PullFileLog()

        try:
            project = GameProject.objects.get(id=project)

            if PRODUCTION_ENV:
                map = ProjectCeleryQueueMap.objects.filter(project__project_name_en=project.project_name_en, use=1)
                if map:
                    fun = map[0].celery_queue
                else:
                    raise Exception('没有找到该游戏项目对应celery队列')
            else:
                fun = 'file_pull_test_8'

            """开始获取文件列表"""
            file_path = gen_pull_file_path(update_type, project, area_name_en)
            # 获取文件需要的参数
            pull_data = dict()
            pull_data['file_path'] = file_path
            pull_data['uuid'] = uuid
            pull_data['update_type'] = update_type
            pull_data['version'] = version
            pull_data['area_name_en'] = area_name_en
            if client_type:
                pull_data['client_type'] = client_type

            r = eval(fun).delay(project.project_name_en, **pull_data)
            log.logger.info('%s-%s' % (uuid, pull_data))

            # 循环10s中等待返回的结果
            start_time = int(time.time())
            while not r.ready():
                time.sleep(1)
                now = int(time.time())
                if now - start_time > 10:
                    raise Exception('获取文件列表超时')
            success, data, list_file = r.get()
            log.logger.info('%s-%s-%s-%s' % (uuid, success, data, list_file))
            if success:
                for file in list_file:
                    file['area_dir'] = area_name_en
                    if client_type:
                        client_type_dict = dict()
                        for x in client_type:
                            client_type_dict.update(x)
                        file['client_type'] = client_type_dict[file['version']]
                    result_file_list.append(file)
                data = result_file_list
                success = True
            else:
                raise Exception('%s' % (data))

        except GameProject.DoesNotExist:
            data = '没有找到游戏项目'
            success = False
        except Exception as e:
            data = str(e)
            success = False
        return JsonResponse({"success": success, "data": data})


def list_svn_scheme(request):
    '下拉展示SVN方案'
    if request.method == "POST":
        data = []

        q = request.POST.get('q', None)
        project = request.POST.get('project')

        if not q:
            q = ''

        if project == '0':
            all_repo = SVNScheme.objects.filter(name__icontains=q)
        else:
            all_repo = SVNScheme.objects.filter(project=GameProject.objects.get(id=project), name__icontains=q)

        for x in all_repo:
            data.append({'id': x.id, 'text': x.name})

        return JsonResponse(data, safe=False)


def list_game_client_version(request):
    """根据项目和地区展示前端所有的版本号
    """

    if request.method == "POST":
        data = []

        q = request.POST.get('q', None)

        if q is None:
            q = ''

        project = request.POST.get('project', None)
        project = GameProject.objects.get(id=project)

        area_name = request.POST.get('area', None)

        all_client_version = GameServer.objects.select_related('host').values('client_version').filter(
            project=project, srv_status=0, host__belongs_to_room__area__chinese_name=area_name, merge_id=None,
            game_type__game_type_code=1, client_version__icontains=q).annotate(dcount=Count('client_version'))

        all_client_version = [x['client_version'] for x in all_client_version]

        for x in all_client_version:
            data.append({'id': x, 'text': x})

        return JsonResponse(data, safe=False)


def list_game_server_version(request):
    """根据项目和地区展示后端的所有版本号
    """

    if request.method == "POST":
        data = []

        q = request.POST.get('q', None)

        if q is None:
            q = ''

        project = request.POST.get('project', None)
        project = GameProject.objects.get(id=project)

        area_name = request.POST.get('area', None)

        all_server_version = GameServer.objects.select_related('host').values('server_version').filter(
            project=project, srv_status=0, host__belongs_to_room__area__chinese_name=area_name, merge_id=None,
            server_version__icontains=q).annotate(dcount=Count('server_version'))

        all_server_version = [x['server_version'] for x in all_server_version]

        for x in all_server_version:
            data.append({'id': x, 'text': x})

        return JsonResponse(data, safe=False)


def get_cnd_version_list(request):
    """根据项目和地区和前端版本列出
    cdn和版本的组合
    """
    if request.method == "POST":
        raw_data = json.loads(request.body.decode('utf-8'))
        project = raw_data.get('project')
        area_name = raw_data.get('area_name')
        client_version = raw_data.get('client_version')

        project = GameProject.objects.get(id=project)

        cdn_version = list(
            GameServer.objects.select_related('host').values(
                'project', 'cdn_root_url', 'cdn_dir', 'client_version', 'area_name').filter(
                project=project, srv_status=0, host__belongs_to_room__area__chinese_name=area_name, merge_id=None,
                game_type__game_type_text='game',
                client_version=client_version).annotate(id=Max('id'))
        )

        return JsonResponse(cdn_version, safe=False)


def get_cdn_list(request):
    """
    根据项目和地区和列出cdn
    """
    if request.method == "POST":
        raw_data = json.loads(request.body.decode('utf-8'))
        project = raw_data.get('project')
        area_name = raw_data.get('area_name')

        project = GameProject.objects.get(id=project)

        cdn_version = list(
            GameServer.objects.values(
                'project', 'cdn_root_url', 'cdn_dir', 'client_version', 'area_name').filter(
                project=project, srv_status=0, host__belongs_to_room__area__chinese_name=area_name,
                merge_id=None).annotate(id=Max('id'))
        )[0:1]

        return JsonResponse(cdn_version, safe=False)


def get_game_server_list(request):
    """
    根据cdn域名和目录获取区服数据
    """
    if request.method == "POST":
        raw_data = json.loads(request.body.decode('utf-8'))
        cdn_root_url = raw_data.get('cdn_root_url')
        cdn_area_dir = raw_data.get('cdn_area_dir')
        cdn_area_dir = cdn_area_dir.split('/')[0]
        project = raw_data.get('project')

        project = GameProject.objects.get(id=project)

        game_server_list = list(
            GameServer.objects.values(
                'project', 'cdn_root_url', 'cdn_dir', 'client_version', 'area_name').filter(
                project=project, srv_status=0, cdn_root_url=cdn_root_url, cdn_dir=cdn_area_dir, merge_id=None).annotate(
                id=Max('id'))
        )[0:1]
        return JsonResponse(game_server_list, safe=False)


def list_cdnurl(request):
    """根据项目和更新类型下来选择cdn url
    """
    if request.method == "POST":
        q = request.POST.get('q', None)

        if q is None:
            q = ''

        project_id = request.POST.get('project_id', None)

        if project_id == '0':
            return JsonResponse([], safe=False)
        else:
            # 获取需要查询的表
            project_id = int(project_id)
            table_name = 't_srv_para_cfg_' + str(project_id)

            # 需要查询的字段
            update_type = request.POST.get('update_type', None)
            if update_type == '前端':
                query_field = 'client_version'
            else:
                query_field = 'server_version'

            sql = "select id, cdn_url as text, %s as version from %s where %s like '%s' group by cdn_url" % (
                query_field, table_name, 'cdn_url', '%' + q + '%')

            with Cursor() as cursor:
                cursor.execute(sql)
                all_cdn_url = cursor.fetchall()

            data = list(all_cdn_url)

            return JsonResponse(data, safe=False)


def get_server_tree(request):
    """根据项目id和版本号获取区服列表
    版本号分为前端和后端

    [
        {
            "server_list": {
                "37平台": [
                    {'srv_name': '双线7服', ip': 'ip', 'srv_id': '37_1'},
                    {'srv_name': '双线1服', ip': 'ip', 'srv_id': '37_2'},
                ],
                "qq平台": [
                    {'srv_name': '少年295区', 'ip': 'ip', 'srv_id': 'qq_1'},
                    {'srv_name': '少年295区', 'ip': 'ip', 'srv_id': 'qq_2'},
                ],
            },
            "game_type": "游戏服",
        },
        {
            "server_list": {
                "sougou平台": [
                    {'srv_name': '跨服1服', 'ip': 'ip', 'srv_id': 'sougou_cross_1'},
                    {'srv_name': '跨服12服', 'ip': 'ip', 'srv_id': 'sougou_cross_2'},
                ],
            },
            "game_type": "跨服"
        },
        {
            "server_list": {
                "yy平台": [
                    {'srv_name': '跨服中央1服', 'ip': 'ip', 'srv_id': 'yy_cross_center_1'},
                    {'srv_name': '跨服中央12服', 'ip': 'ip' 'srv_id': 'yy_cross_center_2'},
                ],
                "4399平台": [
                    {'srv_name': '跨服中央9服', 'ip': 'ip' 'srv_id': '4399_cross_center_1'},
                    {'srv_name': '跨服中央13服', 'ip': 'ip' 'srv_id': '4399_cross_center_2'},
                ],
            },
            "game_type": "跨服中央服"
        }
    ]
    """

    if request.method == "POST":
        all_server_list = []  # 全部的类型的游戏服

        # 需要选择的游戏服的类型
        # server_type_list = ['game', 'cross', 'cross_center']

        pdata = json.loads(request.body.decode('utf-8'))
        project = pdata.get('project')
        update_type = pdata.get('update_type', '后端')
        server_version = pdata.get('server_version', '')
        area_name = pdata.get('area_name', '')

        success = False
        msg = ''

        if update_type == '后端':
            try:
                project = GameProject.objects.get(id=project)
                sub_query = Q()
                if server_version:
                    sub_query.add(Q(server_version=server_version), Q.AND)
                if area_name:
                    sub_query.add(Q(host__belongs_to_room__area__chinese_name=area_name), Q.AND)

                # 所有的游戏类型
                all_game_type = GameServer.objects.values('game_type').filter(
                    project=project).annotate(Sum('game_type'))

                server_type_list = GameServerType.objects.filter(id__in=[x['game_type'] for x in all_game_type])

                # 先找出某个游戏服类型的所有平台
                for t in server_type_list:
                    list_type = {}
                    list_type['server_list'] = {}

                    # 根据游戏类型找出平台
                    all_pf_name = [
                        x['pf_name'] for x in GameServer.objects.select_related('host').values('pf_name').filter(
                            project=project, srv_status=0, game_type=t,
                            merge_id=None).filter(sub_query).annotate(dcount=Count('pf_name'))
                    ]
                    # 根据平台找出所有的游戏服
                    for pf in all_pf_name:
                        list_type['game_type'] = t.game_type_text  # 指定游戏类型1, 2, 3
                        game_type_pf_server_list = GameServer.objects.select_related('host').filter(
                            project=project, srv_status=0, game_type=t, pf_name=pf,
                            merge_id=None).filter(sub_query).order_by('open_time')
                        list_type['server_list'][pf] = []
                        for x in game_type_pf_server_list:
                            list_type['server_list'][pf].append(x.show_server_list_info())

                    all_server_list.append(list_type)

                # 全部的游戏类型服加载完成
                success = True

            except GameProject.DoesNotExist:
                msg = '没有找到游戏项目'
            except Exception as e:
                msg = str(e)
                traceback.print_exc()
            return JsonResponse({"success": success, "msg": msg, "all_server_list": all_server_list})


def get_server_list_by_cdn(request):
    """根据cdn获取区服列表
    前端请求的数据格式
    {
        'area_name': '大陆', 'cdn_dir': 't1',
        'cdn_root_url': 'res.qxz.37wan.com',
        'project': 24, 'id': 514975, 'client_version': '008900000'
    }
    """
    if request.method == "POST":
        filter_data = json.loads(request.body.decode('utf-8'))
        filter_data.pop('id')
        filter_data['project'] = GameProject.objects.filter(id=filter_data.get('project'))

        # 添加一些额外的查询参数，只展示主服和正常的区服
        filter_data['srv_status'] = 0
        filter_data['merge_id'] = None

        game_server_list = GameServer.objects.filter(**filter_data)
        server_list_str = ''

        for s in game_server_list:
            server_msg = s.game_type.game_type_text + '    ' + s.pf_name + '    ' + s.srv_name + '    ' + s.srv_id + '\n'
            server_list_str += server_msg

        return JsonResponse({"data": server_list_str})


def get_project_server_tree(request):
    """根据项目id和版本号获取区服列表
    版本号分为前端和后端

    [
        {
            "server_list": {
                "37平台": [
                    {'srv_name': '双线7服', ip': 'ip', 'srv_id': '37_1'},
                    {'srv_name': '双线1服', ip': 'ip', 'srv_id': '37_2'},
                ],
                "qq平台": [
                    {'srv_name': '少年295区', 'ip': 'ip', 'srv_id': 'qq_1'},
                    {'srv_name': '少年295区', 'ip': 'ip', 'srv_id': 'qq_2'},
                ],
            },
            "game_type": "游戏服",
        },
        {
            "server_list": {
                "sougou平台": [
                    {'srv_name': '跨服1服', 'ip': 'ip', 'srv_id': 'sougou_cross_1'},
                    {'srv_name': '跨服12服', 'ip': 'ip', 'srv_id': 'sougou_cross_2'},
                ],
            },
            "game_type": "跨服"
        },
        {
            "server_list": {
                "yy平台": [
                    {'srv_name': '跨服中央1服', 'ip': 'ip', 'srv_id': 'yy_cross_center_1'},
                    {'srv_name': '跨服中央12服', 'ip': 'ip' 'srv_id': 'yy_cross_center_2'},
                ],
                "4399平台": [
                    {'srv_name': '跨服中央9服', 'ip': 'ip' 'srv_id': '4399_cross_center_1'},
                    {'srv_name': '跨服中央13服', 'ip': 'ip' 'srv_id': '4399_cross_center_2'},
                ],
            },
            "game_type": "跨服中央服"
        }
    ]
    """

    if request.method == "POST":
        all_server_list = []  # 全部的类型的游戏服

        # 需要选择的游戏服的类型
        server_type_list = ['game', 'cross', 'cross_center']

        pdata = json.loads(request.body.decode('utf-8'))
        project = pdata.get('project')
        # update_type = pdata.get('update_type')
        # server_version = pdata.get('server_version')
        # area_name = pdata.get('area_name')

        success = False
        msg = ''

        try:
            project = GameProject.objects.get(id=project)

            # 先找出某个游戏服类型的所有平台
            for t in server_type_list:
                list_type = {}
                if t == 'game':
                    game_type = 1
                elif t == 'cross':
                    game_type = 3
                elif t == 'cross_center':
                    game_type = 2

                list_type['game_type'] = t  # 指定游戏类型
                list_type['server_list'] = {}
                # 根据游戏类型找出平台
                all_pf_name = [
                    x['pf_name'] for x in GameServer.objects.values('pf_name').filter(
                        project=project, srv_status=0, game_type=game_type, merge_id=None).annotate(
                        dcount=Count('pf_name'))
                ]
                # 根据平台找出所有的游戏服
                for pf in all_pf_name:
                    game_type_pf_server_list = GameServer.objects.filter(
                        project=project, srv_status=0, game_type=game_type, pf_name=pf, merge_id=None).order_by(
                        'open_time')
                    list_type['server_list'][pf] = [x.show_server_list_info() for x in game_type_pf_server_list]

                all_server_list.append(list_type)

            # 全部的游戏类型服加载完成
            success = True

        except GameProject.DoesNotExist:
            msg = '没有找到游戏项目'
        except Exception as e:
            msg = str(e)
        return JsonResponse({"success": success, "msg": msg, "all_server_list": all_server_list})


def svn_doc(request):
    'SVN申请文档'

    if request.method == "GET":
        return render(request, 'SVNDOC.html')


def hotupdate_email_approve_help_doc(request):
    """热更新邮件设置
    """
    if request.method == "GET":
        return render(request, 'hotupdate_email_approve_help_doc.html')


def get_objs(request, raw_url, del_data):
    '从url获取对象'
    if raw_url == "svn":
        objs = WorkflowStateEvent.objects.filter(id__in=del_data, creator=request.user)
        objs = [x.content_object for x in objs]
    return objs


def del_myworkflow_obj(request, raw_url):
    '删除我的申请'

    if request.method == "POST":
        del_data = json.loads(request.body.decode('utf-8'))
        objs = get_objs(request, raw_url, del_data)

        try:
            with transaction.atomic():
                if can_delete_workflow(objs):
                    for x in objs:
                        x.delete()
            msg = ''
            success = True
        except WorkflowError as e:
            msg = str(e)
            success = False
        except Exception as e:
            msg = str(e)
            success = False
        return JsonResponse({'data': success, 'msg': msg})


def workflow(request):
    '展示workflow页面'

    if request.method == "GET":
        head = {'value': '工单列表', 'username': request.user.username}
        return render(request, 'workflow_list.html', {'head': head})


def data_workflow_list(request):
    '工单列表数据'

    if request.method == "GET":
        raw_data = ''
        draw = 0
        recordsTotal = Workflow.objects.count()
        raw_data = Workflow.objects.all()
        # recordsFiltered = recordsTotal
        data = {"data": [i.show_all() for i in raw_data], 'draw': draw, 'recordsTotal': recordsTotal,
                'recordsFiltered': recordsTotal}
        return JsonResponse(data)


def help_doc(request):
    """工单使用帮助文档"""
    if request.method == "GET":
        workflow = request.GET.get('workflow')
        workflow = Workflow.objects.get(id=workflow)

        if workflow.name == "SVN申请":
            return render(request, 'svn_workflow_help_doc.html')
        elif workflow.name == "服务器权限申请":
            return render(request, 'server_permission_workflow_help_doc.html')
        elif workflow.name == "电脑故障申报":
            return render(request, "failure_declare_workflow_help_doc.html")
        elif workflow.name == "wifi申请和网络问题申报":
            return render(request, "wifi_workflow_help_doc.html")
        elif workflow.name == "办公电脑和配件申请":
            return render(request, "computer_parts_workflow_help_doc.html")
        elif workflow.name == "版本更新单申请":
            if NEW_VERSION_UPDATE:
                return render(request, "version_update_workflow_help_doc_v2.html")
            else:
                return render(request, "version_update_workflow_help_doc.html")
        elif workflow.name == "服务器申请工单":
            return render(request, "machine_workflow_help_doc.html")
        elif workflow.name == "项目人员调整工单":
            return render(request, "project_adjust_workflow_help_doc.html")
        elif workflow.name == "前端热更新":
            return render(request, "hot_client_workflow_help_doc.html")
        elif workflow.name == "后端热更新":
            return render(request, "hot_server_workflow_help_doc.html")
        else:
            return HttpResponse('暂时没有文档，请等待...')


def workflow_template(request):
    """工单模板"""

    if request.method == "GET":
        workflow = request.GET.get('workflow', 1)

        workflow_obj = Workflow.objects.get(id=workflow)

        name = workflow_obj.name
        head = {'value': name, 'workflow': workflow, 'username': request.user.username}
        state_step = {'value': '==>'.join([x.name for x in get_workflow_state_order(workflow_obj)])}

        if name == "SVN申请":
            init_user = {'id': request.user.id, 'username': request.user.username}
            return render(request,
                          'svn_workflow.html', {'head': head, 'state_step': state_step, 'init_user': init_user})

        if name == '服务器权限申请':
            return render(request,
                          'server_permission_workflow.html',
                          {'head': head, 'state_step': state_step, 'first_name': request.user.first_name})
        if name == '电脑故障申报':
            CLASSIFICATION_DICT = dict((v, k) for k, v in FailureDeclareWorkflow.CLASSIFICATION)
            return render(request,
                          'failure_declare_workflow.html',
                          {'head': head, 'state_step': state_step, 'first_name': request.user.first_name,
                           'data': CLASSIFICATION_DICT})
        if name == '前端热更新':
            # 必须是客户端技术组的人员才可以申请
            group_section = OrganizationMptt.objects.get(user=request.user).parent
            if (group_section.is_department_group == 1 and '客户端技术组' in group_section.name) or request.user.is_superuser:
                return render(request, 'hotupdate_template.html', {'head': head})
            else:
                return render(request, '403.html')
        if name == '后端热更新':
            # 判断申请人所在的部门是否有服务端技术组
            group_section = OrganizationMptt.objects.get(user=request.user).parent
            if (group_section.is_department_group == 1 and '服务端技术组' in group_section.name) or request.user.is_superuser:
                return render(request, 'hotupdate_template.html', {'head': head})
            else:
                return render(request, '403.html')
        if name == '版本更新单申请':
            applicant = request.user.username
            if NEW_VERSION_UPDATE:
                new_edition = 1
                version_update_template = 'version_update_workflow_v2.html'
            else:
                new_edition = 0
                version_update_template = 'version_update_workflow.html'
            return render(request, version_update_template,
                          {'head': head, 'state_step': state_step, 'first_name': request.user.first_name,
                           'applicant': applicant, 'new_edition': new_edition})
        if name == 'wifi申请和网络问题申报':
            init_user = {'id': request.user.id, 'username': request.user.username}
            return render(request,
                          'wifi_workflow.html',
                          {'head': head, 'state_step': state_step, 'init_user': init_user})
        if name == '办公电脑和配件申请':
            init_user = {'id': request.user.id, 'username': request.user.username}
            return render(request,
                          'computer_parts_workflow.html',
                          {'head': head, 'state_step': state_step, 'init_user': init_user})
        if name == '服务器申请工单':
            init_user = {'id': request.user.id, 'username': request.user.username}
            list_config = MACHINE_CONFIG
            return render(request,
                          'machine_workflow.html',
                          {'head': head, 'state_step': state_step, 'init_user': init_user, 'list_config': list_config})
        if name == "项目人员调整工单":
            return render(request, 'project_adjust_workflow.html', {'head': head, 'state_step': state_step})

        if name == "数据库权限申请":
            init_user = {'id': request.user.id, 'username': request.user.username}
            return render(request,
                          'mysql_workflow.html', {'head': head, 'state_step': state_step, 'init_user': init_user})

        else:
            return render(request, '403.html')


def start_hotupdate(request):
    """热更新页面
    根据前后端热更新和不同的项目
    """

    if request.method == "GET":
        workflow_id = request.GET.get('workflow')
        project_id = request.GET.get('project')

        workflow = Workflow.objects.get(id=workflow_id)
        project = GameProject.objects.get(id=project_id)

        head = {'value': project.project_name + '-' + workflow.name, 'workflow': workflow,
                'username': request.user.username}

        # group_projects = group_in_charge_projects(request.user.profile.one_group)
        org = OrganizationMptt.objects.get(user=request.user)
        if request.user.is_superuser or project in org.get_department_obj().project.all():
            if workflow.name == '前端热更新':
                project_name_en = project.project_name_en
                html_template = project_name_en + '_client_hot_update_workflow.html'
                data = {}
                client_hotupdate_template = project.get_client_hotupdate_template(tag=True)
                if client_hotupdate_template:
                    return render(request, client_hotupdate_template + '_client_hot_update_workflow.html',
                                  {'head': head, 'data': data})
                try:
                    return render(request, html_template, {'head': head, 'data': data})
                except:
                    return render(request, 'common_client_hot_update_workflow.html', {'head': head, 'data': data})
            if workflow.name == '后端热更新':
                HOT_SERVER_TYPE = dict(ServerHotUpdate.HOT_SERVER_TYPE)
                project_name_en = project.project_name_en
                html_template = project_name_en + '_server_hot_update_workflow.html'
                if project_name_en == 'jyjh':
                    # 去掉一些更新方式
                    HOT_SERVER_TYPE.pop('1', None)
                    HOT_SERVER_TYPE.pop('3', None)
                try:
                    return render(request, html_template, {'head': head, 'data': HOT_SERVER_TYPE})
                except:
                    return render(request, 'common_server_hot_update_workflow.html',
                                  {'head': head, 'data': HOT_SERVER_TYPE})
        else:
            return render(request, '403.html')


def get_remote_cdn(request):
    """从web后台获取cdn
    根据项目和客户端类型
    """

    if request.method == "POST":
        pass


def get_hotupdate_client_type(request):
    """前端热更新获取客户端类型
    根据游戏项目和区域
    """

    if request.method == "POST":
        project_id = request.POST.get('project')
        project = GameProject.objects.get(id=project_id)
        area_name = request.POST.get('area_name')
        area = Area.objects.get(chinese_name=area_name)
        web_api = WebGetCdnListAPI.objects.get(project=project, area=area)
        list_client_type = web_api.get_dev_flag_list()
        client_type = [{'id': x, 'text': x} for x in list_client_type]
        return JsonResponse(client_type, safe=False)


def get_cdn_root_url(request):
    """获取前端热更新cdn根路径
    根据client_type
    """

    if request.method == "POST":
        project_id = request.POST.get('project')
        project = GameProject.objects.get(id=project_id)
        area_name = request.POST.get('area_name')
        area = Area.objects.get(chinese_name=area_name)
        web_api = WebGetCdnListAPI.objects.filter(project=project, area=area)
        if web_api:
            cdn_root_url = web_api[0].get_root()
        else:
            cdn_root_url = [root['cdn_root_url'] for root in
                            GameServer.objects.select_related('host').filter(srv_status=0, project=project,
                                                                             host__belongs_to_room__area=area).values(
                                'cdn_root_url').distinct() if
                            root['cdn_root_url'] is not None and root['cdn_root_url'] != '']
        return JsonResponse([{'id': x, 'text': x} for x in cdn_root_url], safe=False)


def get_cdn_dir(request):
    """获取前端热更新cdn目录
    """

    if request.method == "POST":
        list_cdn_dir = []
        project_id = request.POST.get('project')
        area_name = request.POST.get('area_name')
        client_type = request.POST.get('client_type')
        cdn_root_url = request.POST.get('cdn_root_url')

        project = GameProject.objects.get(id=project_id)
        area = Area.objects.get(chinese_name=area_name)
        api = WebGetCdnListAPI.objects.filter(project=project, area=area)
        if api:
            api = api[0]
            if api.version == 1:
                list_cdn_dir = get_cdn_list_from_web(project, area, cdn_root_url, client_type)
            if api.version == 2:
                obj = GetCDNDirFromWeb(project_id=project_id, root_url=cdn_root_url, area=area)
                list_cdn_dir = obj.post_api()
                list_cdn_dir = list(set(['/'.join(x.split('/')[:2]) for x in list_cdn_dir]))
        else:
            list_cdn_dir = [dir['cdn_dir'] for dir in
                            GameServer.objects.select_related('host').filter(srv_status=0, project=project,
                                                                             host__belongs_to_room__area=area,
                                                                             cdn_root_url=cdn_root_url).values(
                                'cdn_dir').distinct() if dir['cdn_dir'] is not None and dir['cdn_dir'] != '']

        return JsonResponse([{'id': x, 'text': x} for x in list_cdn_dir], safe=False)


def get_workflow_state(request):
    '获取workflow的状态步骤'

    if request.method == "GET":
        workflow = request.GET.get('workflow')
        workflow = Workflow.objects.get(id=workflow)

        # workflow的state
        list_state = [x.name for x in workflow.state_set.all()]

        # state step
        state_step = '==>'.join(list_state)

        return JsonResponse({'state_step': state_step})


def start_workflow(request):
    """开始流程/重新提交流程"""

    if request.method == "POST":
        pdata = json.loads(request.body.decode('utf-8'))

        workflow = pdata.get('workflow', None)
        wse = pdata.get('wse', None)

        if wse:
            wse = WorkflowStateEvent.objects.get(id=wse)

        if workflow:
            workflow_obj = Workflow.objects.get(id=workflow)

        name = workflow_obj.name if workflow else wse.state.workflow.name

        try:
            with transaction.atomic():

                if name == 'SVN申请':
                    # SVN申请
                    if wse:
                        # 更新workflow
                        content_object = wse.content_object
                        content_object.title = pdata.get('title')
                        content_object.reason = pdata.get('reason')
                        content_object.content = json.dumps(pdata.get('content'))

                        svn_scheme = pdata.get('svn_scheme')
                        if svn_scheme != '0':
                            svn_scheme = SVNScheme.objects.get(id=svn_scheme)
                        else:
                            svn_scheme = None
                        content_object.svn_scheme = svn_scheme

                        content_object.save()

                        # 重新设置状态
                        wse = reset_init_state(wse)

                        # 申请人发送的第一个审批节点的审批用户如果是他自己
                        # 则第一个节点自动审批通过
                        init_state_user = get_state_user(wse.state, obj=wse.content_object, list_format=True)

                        if wse.content_object.applicant in init_state_user:
                            transition = wse.state.transition.get(condition='同意')
                            msg, success, wse = do_transition(wse, transition, wse.content_object.applicant)
                        else:
                            msg = 'ok'
                            success = True

                        # 发送邮件通知到第一个节点的审批人
                        to_list = [
                            x.email for x in get_state_user(wse.state, obj=wse.content_object) if
                            x.email and x.is_active
                        ]

                        if to_list:
                            subject, content = make_email_notify(True)
                            send_mail.delay(to_list, subject, content)

                        # 发送qq弹框提醒
                        users = ','.join(
                            [x.first_name for x in get_state_user(wse.state, obj=wse.content_object) if x.is_active])
                        if users:
                            data = get_qq_notify()
                            send_qq.delay(
                                users, data['window_title'], data['tips_title'], data['tips_content'], data['tips_url'])
                        # 发送wx弹框提醒
                        wx_users = '|'.join(
                            [x.first_name for x in get_state_user(wse.state, obj=wse.content_object) if x.is_active])
                        if wx_users:
                            data = get_wx_notify()
                            send_weixin_message.delay(touser=wx_users, content=data)

                        return JsonResponse({"data": msg, "success": success})
                    else:
                        # 创建obj
                        project = GameProject.objects.get(id=pdata.get('project'))
                        applicant = User.objects.get(id=pdata.get('applicant'))

                        # 判断选择的项目是否有svn仓库
                        if not project.svn_repo:
                            msg = '该项目不能申请,没有svn仓库'
                            success = False
                            return JsonResponse({"data": msg, "success": success})

                        svn_scheme = pdata.get('svn_scheme')
                        if svn_scheme != '0':
                            svn_scheme = SVNScheme.objects.get(id=svn_scheme)
                        else:
                            svn_scheme = None

                        obj = SVNWorkflow.objects.create(
                            creator=request.user, title=pdata.get('title'), svn_scheme=svn_scheme,
                            reason=pdata.get('reason'), project=project, create_time=datetime.now(),
                            applicant=applicant, status=1, content=json.dumps(pdata.get('content')))

                        if NEW_WORKFLOW == 1:
                            new_set_state_obj_user(obj, workflow_obj, applicant, project)
                        else:
                            set_state_obj_user(obj, workflow_obj, applicant, project)

                        # 设置obj到流程的初始化状态
                        wse = WorkflowStateEvent.objects.create(
                            content_object=obj, create_time=obj.create_time, creator=request.user, title=obj.title,
                            state=workflow_obj.init_state, is_current=True)

                        # 指定初始状态的审批用户
                        sor = get_sor(wse.state, obj)
                        if sor:
                            users = tuple(sor.users.all())
                            wse.users.add(*users)

                        # 申请人发送的第一个审批节点的审批用户如果是他自己
                        # 则第一个节点自动审批通过
                        init_state_user = get_state_user(wse.state, obj=wse.content_object, list_format=True)

                        if applicant in init_state_user:
                            transition = wse.state.transition.get(condition='同意')
                            msg, success, wse = do_transition(wse, transition, applicant)
                            # 指定下一个状态的审批用户
                            sor = get_sor(wse.state, obj)
                            if sor:
                                users = tuple(sor.users.all())
                                wse.users.add(*users)
                        else:
                            msg = 'ok'
                            success = True

                        # 发送邮件通知到第一个节点的审批人
                        to_list = [
                            x.email for x in get_state_user(wse.state, obj=wse.content_object) if
                            x.email and x.is_active
                        ]
                        if to_list:
                            subject, content = make_email_notify(True)
                            send_mail.delay(to_list, subject, content)

                        # 发送qq弹框提醒
                        users = ','.join(
                            [x.first_name for x in get_state_user(wse.state, obj=wse.content_object) if x.is_active])
                        if users:
                            data = get_qq_notify()
                            send_qq.delay(
                                users, data['window_title'], data['tips_title'], data['tips_content'], data['tips_url'])

                        # # 发送wx弹框提醒
                        # wx_users = '|'.join(
                        #     [x.first_name for x in get_state_user(wse.state, obj=wse.content_object) if
                        #      x.is_active and x.organizationmptt_set.first().wechat_approve == 0])
                        # if wx_users:
                        #     data = get_wx_notify()
                        #     send_weixin_message.delay(touser=wx_users, content=data)

                        # 发送企业微信审批
                        touser = '|'.join([x.first_name for x in get_state_user(wse.state, obj=wse.content_object) if
                                           x.is_active and x.organizationmptt_set.first().wechat_approve == 1])
                        if touser:
                            result = get_wx_task_card_data(touser, wse)
                            if result['success']:
                                send_task_card_to_wx_user.delay(touser, result['data'])

                        return JsonResponse({"data": msg, "success": success})

                if name == '服务器权限申请':
                    project = GameProject.objects.get(id=pdata.get('project'))
                    room = pdata.get('room')
                    if room == '0':
                        room = None
                        all_ip = False
                    else:
                        room = Room.objects.get(id=room)
                        all_ip = True
                    ips = json.dumps(pdata.get('ips'))
                    title = pdata.get('title')
                    reason = pdata.get('reason')
                    is_root = pdata.get('is_root')
                    key = pdata.get('key')
                    start_time = pdata.get('start_time') if pdata.get('start_time') else None
                    end_time = pdata.get('end_time') if pdata.get('end_time') else None

                    temporary = pdata.get('temporary')

                    if not temporary:
                        start_time = None
                        end_time = None

                    group = pdata.get('group')
                    if wse:
                        content_object = wse.content_object
                        content_object.title = pdata.get('title')
                        content_object.reason = reason
                        content_object.is_root = is_root
                        content_object.project = project
                        content_object.room = room
                        content_object.ips = ips
                        content_object.all_ip = all_ip
                        content_object.key = key
                        content_object.start_time = start_time
                        content_object.end_time = end_time
                        content_object.temporary = temporary
                        content_object.group = group

                        content_object.save()

                        # 重新设置状态
                        wse = reset_init_state(wse)

                        # 申请人发送的第一个审批节点的审批用户如果是他自己
                        # 则第一个节点自动审批通过
                        init_state_user = get_state_user(wse.state, obj=wse.content_object, list_format=True)

                        if wse.content_object.applicant in init_state_user:
                            transition = wse.state.transition.get(condition='同意')
                            msg, success, wse = do_transition(wse, transition, wse.content_object.applicant)
                        else:
                            msg = 'ok'
                            success = True

                        # 发送邮件通知到第一个节点的审批人
                        to_list = [
                            x.email for x in get_state_user(wse.state, obj=wse.content_object) if
                            x.email and x.is_active
                        ]

                        if to_list:
                            subject, content = make_email_notify(True)
                            send_mail.delay(to_list, subject, content)

                        # 发送qq弹框提醒
                        users = ','.join(
                            [x.first_name for x in get_state_user(wse.state, obj=wse.content_object) if x.is_active])
                        if users:
                            data = get_qq_notify()
                            send_qq.delay(
                                users, data['window_title'], data['tips_title'], data['tips_content'], data['tips_url'])
                        # 发送wx弹框提醒
                        wx_users = '|'.join(
                            [x.first_name for x in get_state_user(wse.state, obj=wse.content_object) if x.is_active])
                        if wx_users:
                            data = get_wx_notify()
                            send_weixin_message.delay(touser=wx_users, content=data)

                        return JsonResponse({"data": msg, "success": success})

                    else:
                        # 创建obj
                        applicant = request.user

                        obj = ServerPermissionWorkflow.objects.create(
                            creator=request.user, create_time=datetime.now(),
                            applicant=applicant, title=title, reason=reason, is_root=is_root,
                            project=project, room=room, ips=ips, all_ip=all_ip, key=key,
                            start_time=start_time, end_time=end_time, temporary=temporary, group=group)

                        if NEW_WORKFLOW == 1:
                            new_set_state_obj_user(obj, workflow_obj, applicant, project)
                        else:
                            set_state_obj_user(obj, workflow_obj, applicant, project)

                        # 设置obj到流程的初始化状态
                        wse = WorkflowStateEvent.objects.create(
                            content_object=obj, create_time=obj.create_time, creator=request.user, title=obj.title,
                            state=workflow_obj.init_state, is_current=True)

                        # 指定初始状态的审批用户
                        sor = get_sor(wse.state, obj)
                        if sor:
                            users = tuple(sor.users.all())
                            wse.users.add(*users)

                        # 申请人发送的第一个审批节点的审批用户如果是他自己
                        # 则第一个节点自动审批通过
                        init_state_user = get_state_user(wse.state, obj=wse.content_object, list_format=True)

                        if applicant in init_state_user:
                            transition = wse.state.transition.get(condition='同意')
                            msg, success, wse = do_transition(wse, transition, applicant)
                            # 指定下一个状态的审批用户
                            sor = get_sor(wse.state, obj)
                            if sor:
                                users = tuple(sor.users.all())
                                wse.users.add(*users)
                        else:
                            msg = 'ok'
                            success = True

                        msg = 'ok'
                        success = True

                        # 发送邮件通知到第一个节点的审批人
                        to_list = [
                            x.email for x in get_state_user(wse.state, obj=wse.content_object) if
                            x.email and x.is_active
                        ]
                        if to_list:
                            subject, content = make_email_notify(True)
                            send_mail.delay(to_list, subject, content)

                        # 发送qq弹框提醒
                        users = ','.join(
                            [x.first_name for x in get_state_user(wse.state, obj=wse.content_object) if x.is_active])
                        if users:
                            data = get_qq_notify()
                            send_qq.delay(
                                users, data['window_title'], data['tips_title'], data['tips_content'], data['tips_url'])

                        # 发送wx弹框提醒
                        # wx_users = '|'.join(
                        #     [x.first_name for x in get_state_user(wse.state, obj=wse.content_object) if
                        #      x.is_active and x.organizationmptt_set.first().wechat_approve == 0])
                        # if wx_users:
                        #     data = get_wx_notify()
                        #     send_weixin_message.delay(touser=wx_users, content=data)

                        # 发送企业微信审批
                        touser = '|'.join([x.first_name for x in get_state_user(wse.state, obj=wse.content_object) if
                                           x.is_active and x.organizationmptt_set.first().wechat_approve == 1])
                        if touser:
                            result = get_wx_task_card_data(touser, wse)
                            if result['success']:
                                send_task_card_to_wx_user.delay(touser, result['data'])

                        return JsonResponse({"data": msg, "success": success})

                if name == '电脑故障申报':
                    applicant = User.objects.get(id=pdata.get('applicant'))
                    title = pdata.get('title')
                    classification = str(pdata.get('classification'))
                    content = pdata.get('content')
                    project = None

                    assigned_to = pdata.get('assigned_to')

                    if assigned_to == '0':
                        assigned_to = None
                    else:
                        assigned_to = User.objects.get(id=assigned_to)

                    if wse:
                        content_object = wse.content_object
                        content_object.title = title
                        content_object.content = content
                        content_object.save()

                        # 重新设置状态
                        wse = reset_init_state(wse)

                        # 申请人发送的第一个审批节点的审批用户如果是他自己
                        # 则第一个节点自动审批通过
                        init_state_user = get_state_user(wse.state, obj=wse.content_object, list_format=True)

                        if wse.content_object.applicant in init_state_user:
                            transition = wse.state.transition.get(condition='同意')
                            msg, success, wse = do_transition(wse, transition, wse.content_object.applicant)
                        else:
                            msg = 'ok'
                            success = True

                        # 发送邮件通知到第一个节点的审批人
                        to_list = [
                            x.email for x in get_state_user(wse.state, obj=wse.content_object) if
                            x.email and x.is_active
                        ]

                        if to_list:
                            subject, content = make_email_notify(True)
                            send_mail.delay(to_list, subject, content)

                        # 发送qq弹框提醒
                        users = ','.join(
                            [x.first_name for x in get_state_user(wse.state, obj=wse.content_object) if x.is_active])
                        if users:
                            data = get_qq_notify()
                            send_qq.delay(
                                users, data['window_title'], data['tips_title'], data['tips_content'], data['tips_url'])
                        # 发送wx弹框提醒
                        wx_users = '|'.join(
                            [x.first_name for x in get_state_user(wse.state, obj=wse.content_object) if x.is_active])
                        if wx_users:
                            data = get_wx_notify()
                            send_weixin_message.delay(touser=wx_users, content=data)

                        return JsonResponse({"data": msg, "success": success})
                    else:
                        # 创建流程对象
                        obj = FailureDeclareWorkflow.objects.create(
                            create_time=datetime.now(), creator=request.user,
                            applicant=applicant, title=title, classification=classification, content=content)

                        # 指定网络管理员审批
                        if NEW_WORKFLOW == 1:
                            new_set_state_obj_user(obj, workflow_obj, applicant, project, assigned_to)
                        else:
                            # 指定网络管理员审批
                            administrator_state = workflow_obj.init_state
                            sor = StateObjectUserRelation.objects.create(content_object=obj, state=administrator_state)
                            # 获取相应的网管人员,创畅的只有一个人
                            # if applicant.profile.one_group.groupprofile.to_root().company.code == 'GZCC':
                            if '创畅' in applicant.organizationmptt_set.all()[0].get_ancestors_name():
                                administrator = User.objects.get(first_name='yaoweinan')
                            else:
                                administrator = get_administrator(assigned_to, administrator_state, classification)
                            sor.users.add(administrator)

                        # 设置到初始化状态
                        wse = WorkflowStateEvent.objects.create(
                            content_object=obj, create_time=obj.create_time, creator=obj.creator,
                            title=obj.title, state=workflow_obj.init_state, is_current=True)

                        # 指定初始状态的审批用户
                        sor = get_sor(wse.state, obj)
                        if sor:
                            users = tuple(sor.users.all())
                            wse.users.add(*users)

                        # 申请人发送的第一个审批节点的审批用户如果是他自己
                        # 则第一个节点自动审批通过
                        init_state_user = get_state_user(wse.state, obj=wse.content_object, list_format=True)

                        if applicant in init_state_user:
                            transition = wse.state.transition.get(condition='同意')
                            msg, success, wse = do_transition(wse, transition, applicant)
                            # 指定下一个状态的审批用户
                            sor = get_sor(wse.state, obj)
                            if sor:
                                users = tuple(sor.users.all())
                                wse.users.add(*users)
                        else:
                            msg = 'ok'
                            success = True

                        # 发送邮件通知到第一个节点的审批人
                        to_list = [
                            x.email for x in get_state_user(wse.state, obj=wse.content_object) if
                            x.email and x.is_active
                        ]
                        if to_list:
                            subject, content = make_email_notify(True)
                            send_mail.delay(to_list, subject, content)

                        # 发送qq弹框提醒
                        users = ','.join(
                            [x.first_name for x in get_state_user(wse.state, obj=wse.content_object) if x.is_active])
                        if users:
                            data = get_qq_notify()
                            send_qq.delay(
                                users, data['window_title'], data['tips_title'], data['tips_content'], data['tips_url'])
                        # 发送wx弹框提醒
                        # wx_users = '|'.join(
                        #     [x.first_name for x in get_state_user(wse.state, obj=wse.content_object) if
                        #      x.is_active and x.organizationmptt_set.first().wechat_approve == 0])
                        # if wx_users:
                        #     data = get_wx_notify()
                        #     send_weixin_message.delay(touser=wx_users, content=data)

                        # 发送企业微信审批
                        touser = '|'.join(
                            [x.first_name for x in get_state_user(wse.state, obj=wse.content_object) if
                             x.is_active and x.organizationmptt_set.first().wechat_approve == 1])
                        if touser:
                            result = get_wx_task_card_data(touser, wse)
                            if result['success']:
                                send_task_card_to_wx_user.delay(touser, result['data'])

                        return JsonResponse({"data": msg, "success": success})

                if name == '前端热更新':
                    create_time = datetime.now()
                    creator = request.user
                    applicant = creator
                    title = pdata.get('title')
                    reason = pdata.get('reason')
                    attention = pdata.get('attention')
                    project = pdata.get('project')
                    area_name_and_en = pdata.get('area_name_and_en')
                    area_name_en = Area.objects.get(chinese_name=area_name_and_en).short_name
                    area_name = area_name_en
                    rsync_area_name = area_name_en
                    client_version = pdata.get('client_version')
                    client_type = pdata.get('client_type', None)
                    pair_code = pdata.get('pair_code')
                    order = pdata.get('order')
                    list_update_file = pdata.get('list_update_file')
                    uuid = pdata.get('uuid')
                    backup_dev = pdata.get('backup_dev')
                    # 可以有不选测试的情况，如果不选，就是None
                    test_head = pdata.get('test_head', None)
                    operation_head = pdata.get('operation_head', None)
                    extra = pdata.get('extra')
                    extra_project_group = pdata.get('extra_project_group', [])
                    if extra_project_group is None:
                        extra_project_group = []
                    # 如果没有选择额外的通知用户
                    if extra is None:
                        extra = []

                    content = json.dumps(pdata.get('content'))

                    project = GameProject.objects.get(id=project)

                    # 检测如果是要绑定前后端热更新执行，需要检测绑定的可用性
                    if not (pair_code == '无' or order == '无'):
                        msg, success = _pair_code_order_updatetype_available(
                            project, area_name, pair_code, order, 'hot_client')
                        if not success:
                            raise Exception('%s' % msg)
                    else:
                        pair_code = None
                        order = None

                    # 如果不选测试负责人，则工单发起人代替测试审批角色
                    if test_head is None:
                        test_head = [creator]
                    else:
                        test_head = User.objects.filter(id__in=test_head)
                    # 厦门的项目可以不选运营负责人，则工单发起人代替运营test_tasks审批角色
                    if operation_head is None:
                        operation_head = [creator]
                    else:
                        operation_head = User.objects.filter(id__in=operation_head)
                    extra = list(User.objects.filter(id__in=extra))

                    # extra_project_group = ProjectGroup.objects.filter(id__in=extra_project_group)
                    # extra_project_group_users = [x for x in User.objects.filter(
                    #     is_active=1, profile__project_group__in=extra_project_group)]
                    """
                    2018.12修改，根据新组织架构表找出需要额外通知的用户
                    """
                    extra_department_group_users = [x.user for x in
                                                    OrganizationMptt.objects.filter(parent_id__in=extra_project_group,
                                                                                    is_active=1, type=2)]

                    extra.extend(extra_department_group_users)
                    extra = list(set(extra))

                    if wse:
                        pass
                    else:
                        # 创建热更新流程对象
                        obj = ClientHotUpdate.objects.create(
                            create_time=create_time, creator=creator, area_name=area_name,
                            rsync_area_name=rsync_area_name, applicant=applicant, title=title,
                            reason=reason, attention=attention, project=project,
                            client_version=client_version, content=content,
                            client_type=client_type, pair_code=pair_code, order=order,
                            update_file_list=json.dumps(list_update_file), uuid=uuid)

                        content = json.loads(obj.content)
                        """
                        2019.3修改，增加热更新子任务表,用来存放
                        1. 热更新流程需要用到的运维管理机对象
                        2. 及其对应的更新文件和数据
                        3. 及其对应的rsync推送结果
                        需要根据项目的不同做特殊处理
                        """
                        if project.project_name_en in ('snsy', 'csxy', 'syjy', 'jysybt', 'sgby', 'rxqyz') or str(
                                project.get_client_hotupdate_template(tag=True)) in ('sy1', 'sy2', 'sy3', 'sy4'):

                            game_server = GameServer.objects.select_related('host').filter(project_id=project.id,
                                                                                           srv_status=0,
                                                                                           host__belongs_to_room__area__short_name=area_name)
                            list_ops_manager_id = []
                            for gs in game_server:
                                if gs.host:
                                    if gs.host.opsmanager:
                                        list_ops_manager_id.append(gs.host.opsmanager.id)
                            list_ops_manager = OpsManager.objects.filter(id__in=list_ops_manager_id)
                            if not list_ops_manager:
                                raise Exception('没有找到运维管理机')
                            for ops in list_ops_manager:
                                ClientHotUpdateRsyncTask.objects.create(client_hot_update=obj, ops=ops,
                                                                        update_file_list=obj.update_file_list,
                                                                        content=json.dumps(content))
                        else:
                            for c in content:
                                game_server = GameServer.objects.filter(project_id=project.id,
                                                                        cdn_root_url=c['cdn_root_url'],
                                                                        cdn_dir=c['cdn_dir'],
                                                                        client_version=c['client_version'],
                                                                        srv_status=0)
                                list_ops_manager_id = []
                                for gs in game_server:
                                    list_ops_manager_id.append(gs.host.opsmanager.id)
                                list_ops_manager = OpsManager.objects.filter(id__in=list_ops_manager_id)
                                if not list_ops_manager:
                                    raise Exception('没有找到运维管理机')
                                for ops in list_ops_manager:
                                    """
                                    1. 判断管理机对应的子任务是否已存在，存在则更新字段
                                    2. 检查是否有相同url的运维管理机对应的子任务存在，有则找出对应子任务进行更新
                                    3. 若以上两个条件都不符合，则创建子任务
                                    """
                                    task = ClientHotUpdateRsyncTask.objects.filter(client_hot_update=obj, ops=ops)
                                    if task:
                                        task_content = json.loads(task[0].content)
                                        if c not in task_content:
                                            task_content.append(c)
                                        task_content = json.dumps(task_content)
                                        task.update(**{'content': task_content})
                                    elif get_the_same_url_of_ops_task(obj, ops, 'hot_client'):
                                        task = get_the_same_url_of_ops_task(obj, ops, 'hot_client')
                                        task_content = json.loads(task.content)
                                        if c not in task_content:
                                            task_content.append(c)
                                        task_content = json.dumps(task_content)
                                        task.content = task_content
                                        task.save(update_fields=['content'])
                                    else:
                                        task_content = []
                                        task_content.append(c)
                                        task_content = json.dumps(task_content)
                                        update_file_list = json.dumps(list_update_file)
                                        ClientHotUpdateRsyncTask.objects.create(client_hot_update=obj, ops=ops,
                                                                                update_file_list=update_file_list,
                                                                                content=task_content)

                        # 指定项目分组负责人, 根据选择的项目和更新类型，前端或者后端
                        init_state = workflow_obj.init_state

                        # project_group_name = '前端组'
                        # project_group = ProjectGroup.objects.get(project=project, name=project_group_name)
                        # init_user = project_group.project_group_leader

                        """2018.12修改，前端组（客户端技术组）负责人，关联新组织架构表 begin"""
                        project_group_name = '客户端技术组'
                        if not project.organizationmptt_set.all()[0].get_children().filter(name=project_group_name):
                            raise GroupExtentionError("申请人所在的部门没有客户端技术组")
                        if not project.organizationmptt_set.all()[0].get_children().filter(name=project_group_name)[
                            0].leader:
                            raise GroupExtentionError("申请人所在小组没有设置负责人")
                        init_user = User.objects.get(
                            pk=project.organizationmptt_set.all()[0].get_children().filter(name=project_group_name)[
                                0].leader)
                        """2018.12修改，前端组（客户端技术组）负责人，关联新组织架构表 end"""

                        sor = StateObjectUserRelation.objects.create(content_object=obj, state=init_state)
                        sor.users.add(init_user)

                        # 项目分组主程备选人，防止主程不能审批的特殊情况
                        backup_dev = User.objects.get(id=backup_dev)
                        sor.users.add(backup_dev)

                        # 指定测试审批负责人和运营审批负责人
                        test_state = workflow_obj.init_state.transition.get(condition='同意').destination
                        sor = StateObjectUserRelation.objects.create(content_object=obj, state=test_state)
                        sor.users.add(*test_head)

                        operation_state = test_state.transition.get(condition='同意').destination
                        sor = StateObjectUserRelation.objects.create(content_object=obj, state=operation_state)
                        sor.users.add(*operation_head)

                        # 添加更新完成后额外通知的人员
                        obj.extra.add(*extra)

                        # 设置到初始状态
                        wse = WorkflowStateEvent.objects.create(
                            content_object=obj, create_time=obj.create_time, creator=obj.creator,
                            title=obj.title, state=workflow_obj.init_state, is_current=True)

                        # 指定初始状态的审批用户
                        sor = get_sor(wse.state, obj)
                        if sor:
                            users = tuple(sor.users.all())
                            wse.users.add(*users)

                        # 申请人发送的第一个审批节点的审批用户如果是他自己
                        # 则第一个节点自动审批通过
                        init_state_user = get_state_user(wse.state, obj=wse.content_object, list_format=True)

                        if applicant in init_state_user:
                            transition = wse.state.transition.get(condition='同意')
                            msg, success, wse = do_transition(wse, transition, applicant)
                            # 指定下一个状态的审批用户
                            sor = get_sor(wse.state, obj)
                            if sor:
                                users = tuple(sor.users.all())
                                wse.users.add(*users)
                        else:
                            msg = 'ok'
                            success = True

                        # 发送邮件通知到第一个节点的审批人
                        wse_users = wse.users.all()
                        # 邮件通知
                        to_list = [x.email for x in wse_users if not x.profile.hot_update_email_approve]
                        if to_list:
                            subject, content = make_email_notify(True)
                            send_mail.delay(to_list, subject, content)

                        # 邮件审批
                        approve_list = [x.email for x in wse_users if x.profile.hot_update_email_approve]
                        if approve_list:
                            subject, content = make_email(wse)
                            send_mail.delay(approve_list, subject, content)

                        # 送qq弹框提醒
                        users = ','.join([x.first_name for x in wse_users])
                        if users:
                            data = get_qq_notify()
                            send_qq.delay(
                                users, data['window_title'], data['tips_title'], data['tips_content'], data['tips_url'])

                        # 发送wx弹框提醒
                        # wx_users = '|'.join([x.first_name for x in wse_users if
                        #                      x.is_active and x.organizationmptt_set.first().wechat_approve == 0])
                        # if wx_users:
                        #     data = get_wx_notify()
                        #     send_weixin_message.delay(touser=wx_users, content=data)

                        # 发送企业微信审批
                        touser = '|'.join(
                            [x.first_name for x in get_state_user(wse.state, obj=wse.content_object) if
                             x.is_active and x.organizationmptt_set.first().wechat_approve == 1])
                        if touser:
                            result = get_wx_task_card_data(touser, wse)
                            if result['success']:
                                send_task_card_to_wx_user.delay(touser, result['data'])

                        return JsonResponse({"data": msg, "success": success})

                if name == '后端热更新':
                    create_time = datetime.now()
                    creator = request.user
                    applicant = creator
                    title = pdata.get('title')
                    reason = pdata.get('reason')
                    attention = pdata.get('attention')
                    project = pdata.get('project')
                    area_name_and_en = pdata.get('area_name_and_en')
                    area_name_en = Area.objects.get(chinese_name=area_name_and_en).short_name
                    area_name = area_name_en
                    rsync_area_name = area_name_en
                    server_version = pdata.get('server_version')
                    uuid = pdata.get('uuid')
                    pair_code = pdata.get('pair_code')
                    order = pdata.get('order')
                    backup_dev = pdata.get('backup_dev')
                    # 可以有不选测试的情况，如果不选，就是None
                    test_head = pdata.get('test_head', None)
                    operation_head = pdata.get('operation_head', None)
                    extra = pdata.get('extra')
                    extra_project_group = pdata.get('extra_project_group', [])
                    if extra_project_group is None:
                        extra_project_group = []
                    # 如果没有选择额外的通知用户
                    if extra is None:
                        extra = []

                    # 更新方式 erl或者热更新
                    hot_server_type = pdata.get('hot_server_type')

                    # 热更新文件列表包含文件名和MD5
                    list_update_file = json.dumps(pdata.get('list_update_file'))

                    # erlang命令
                    erlang_cmd_list = pdata.get('erlang_cmd_list')

                    # 热更新的区服列表
                    update_server_list = pdata.get('update_server_list')

                    # 本次更新全部的区服列表
                    replication_server_list = pdata.get('replication_server_list')

                    # 是否同步新服
                    on_new_server = pdata.get('on_new_server')

                    project = GameProject.objects.get(id=project)

                    # 如果不选测试负责人，则工单发起人代替测试审批角色
                    if test_head is None:
                        test_head = [creator]
                    else:
                        test_head = User.objects.filter(id__in=test_head)
                    # 厦门项目可以不选运营负责人，则工单发起人代替运营审批角色
                    if operation_head is None:
                        operation_head = [creator]
                    else:
                        operation_head = User.objects.filter(id__in=operation_head)
                    extra = list(User.objects.filter(id__in=extra))

                    extra_project_group = ProjectGroup.objects.filter(id__in=extra_project_group)
                    extra_group_section = []
                    for x in extra_project_group:
                        if x.group_section is not None:
                            extra_group_section.append(x.group_section)
                    extra_project_group_users = [x for x in User.objects.filter(
                        is_active=1, profile__group_section__in=extra_group_section)]
                    extra.extend(extra_project_group_users)
                    extra = list(set(extra))

                    # 处理后端热更新类型的热更文件和erlang命令
                    if hot_server_type == '0':
                        # 只热更
                        erlang_cmd_list = None
                    elif hot_server_type == '1':
                        # 先热更,再执行erl命令
                        pass
                    elif hot_server_type == '2':
                        # 只执行erl命令
                        list_update_file = None
                    elif hot_server_type == '3':
                        # 先执行erl命令,再热更
                        pass
                    else:
                        raise Exception('未知的后端热更新类型')

                    # 检测如果是要绑定前后端热更新执行，需要检测绑定的可用性
                    if not (pair_code == '无' or order == '无'):
                        msg, success = _pair_code_order_updatetype_available(
                            project, area_name, pair_code, order, 'hot_server')
                        if not success:
                            raise Exception('%s' % msg)
                    else:
                        pair_code = None
                        order = None

                    if wse:
                        pass
                    else:
                        # 创建后端热更新对象
                        obj = ServerHotUpdate.objects.create(
                            create_time=create_time, creator=creator, applicant=applicant, title=title,
                            reason=reason, attention=attention, project=project, area_name=area_name,
                            server_version=server_version, hot_server_type=hot_server_type,
                            rsync_area_name=rsync_area_name, erlang_cmd_list=erlang_cmd_list,
                            update_file_list=list_update_file, update_server_list=json.dumps(update_server_list),
                            uuid=uuid, pair_code=pair_code, order=order)

                        # 创建 obj的onetoone
                        ServerHotUpdateReplication.objects.create(
                            replication=obj, replication_server_list=json.dumps(replication_server_list),
                            on_new_server=on_new_server, raw_server_list=json.dumps(update_server_list))

                        """
                        2019.3修改
                        根据update_server_list中的gameserverid字段确定需要更新的区服
                        在根据区服确定需要用到的运维管理机
                        根据运维管理机拆分热更新子任务
                        """
                        if list_update_file:
                            update_file_list = json.loads(list_update_file)
                        else:
                            update_file_list = []
                        for update_server in update_server_list:
                            game_server_id = update_server['gameserverid']
                            game_server = GameServer.objects.get(pk=int(game_server_id))
                            if game_server.host:
                                ops = game_server.host.opsmanager
                                if ops:
                                    """
                                    1. 判断管理机对应的子任务是否已存在，存在则更新字段
                                    2. 检查是否有相同url的运维管理机对应的子任务存在，有则找出对应子任务进行更新
                                    3. 若以上两个条件都不符合，则创建子任务
                                    """
                                    task = ServerHotUpdateRsyncTask.objects.filter(server_hot_update=obj, ops=ops)
                                    if task:
                                        task_update_server_list = json.loads(task[0].update_server_list)
                                        if update_server not in task_update_server_list:
                                            task_update_server_list.append(update_server)
                                        task_update_server_list = json.dumps(task_update_server_list)
                                        task.update(**{"update_server_list": task_update_server_list})
                                    elif get_the_same_url_of_ops_task(obj, ops, 'hot_server'):
                                        task = get_the_same_url_of_ops_task(obj, ops, 'hot_server')
                                        task_update_server_list = json.loads(task.update_server_list)
                                        if update_server not in task_update_server_list:
                                            task_update_server_list.append(update_server)
                                        task_update_server_list = json.dumps(task_update_server_list)
                                        task.update_server_list = task_update_server_list
                                        task.save(update_fields=['update_server_list'])
                                    else:
                                        task_update_file_list = json.dumps(update_file_list)
                                        update_server_list = json.dumps([update_server])
                                        ServerHotUpdateRsyncTask.objects.create(server_hot_update=obj, ops=ops,
                                                                                update_server_list=update_server_list,
                                                                                update_file_list=task_update_file_list)

                        # 指定项目分组负责人, 根据选择的项目和更新类型，前端或者后端
                        init_state = workflow_obj.init_state

                        """2018.12修改，后端组（服务端技术组）负责人，关联新组织架构表 begin"""
                        project_group_name = '服务端技术组'
                        if not project.organizationmptt_set.all()[0].get_children().filter(name=project_group_name):
                            raise GroupExtentionError("申请人所在的部门没有服务端技术组")
                        if not project.organizationmptt_set.all()[0].get_children().filter(name=project_group_name)[
                            0].leader:
                            raise GroupExtentionError("申请人所在小组没有设置负责人")
                        init_user = User.objects.get(
                            pk=project.organizationmptt_set.all()[0].get_children().filter(name=project_group_name)[
                                0].leader)
                        """2018.12修改，前端组（客户端技术组）负责人，关联新组织架构表 end"""

                        sor = StateObjectUserRelation.objects.create(content_object=obj, state=init_state)
                        sor.users.add(init_user)

                        # 项目分组主程备选人，防止主程不能审批的特殊情况
                        backup_dev = User.objects.get(id=backup_dev)
                        sor.users.add(backup_dev)

                        # 指定测试审批负责人和运营审批负责人
                        test_state = workflow_obj.init_state.transition.get(condition='同意').destination
                        sor = StateObjectUserRelation.objects.create(content_object=obj, state=test_state)
                        sor.users.add(*test_head)

                        operation_state = test_state.transition.get(condition='同意').destination
                        sor = StateObjectUserRelation.objects.create(content_object=obj, state=operation_state)
                        sor.users.add(*operation_head)

                        # 指定运维负责人，根据每个项目关联的运维对接人员
                        # ops_state = operation_state.transition.get(condition='同意').destination
                        # sor = StateObjectUserRelation.objects.create(content_object=obj, state=ops_state)
                        # ops_state_user = project.related_user.all()
                        # sor.users.add(*ops_state_user)

                        # 添加更新完成后额外通知的人员
                        obj.extra.add(*extra)

                        # 设置到初始状态
                        wse = WorkflowStateEvent.objects.create(
                            content_object=obj, create_time=obj.create_time, creator=obj.creator,
                            title=obj.title, state=workflow_obj.init_state, is_current=True)

                        # 指定初始状态的审批用户
                        sor = get_sor(wse.state, obj)
                        if sor:
                            users = tuple(sor.users.all())
                            wse.users.add(*users)

                        # 申请人发送的第一个审批节点的审批用户如果是他自己
                        # 则第一个节点自动审批通过
                        init_state_user = get_state_user(wse.state, obj=wse.content_object, list_format=True)

                        if applicant in init_state_user:
                            transition = wse.state.transition.get(condition='同意')
                            msg, success, wse = do_transition(wse, transition, applicant)
                            # 指定下一个状态的审批用户
                            sor = get_sor(wse.state, obj)
                            if sor:
                                users = tuple(sor.users.all())
                                wse.users.add(*users)
                        else:
                            msg = 'ok'
                            success = True

                        # 发送邮件通知到第一个节点的审批人
                        wse_users = wse.users.all()
                        # 邮件通知
                        to_list = [x.email for x in wse_users if not x.profile.hot_update_email_approve]
                        if to_list:
                            subject, content = make_email_notify(True)
                            send_mail.delay(to_list, subject, content)

                        # 邮件审批
                        approve_list = [x.email for x in wse_users if x.profile.hot_update_email_approve]
                        if approve_list:
                            subject, content = make_email(wse)
                            send_mail.delay(approve_list, subject, content)

                        # 送qq弹框提醒
                        users = ','.join([x.first_name for x in wse_users])
                        if users:
                            data = get_qq_notify()
                            send_qq.delay(
                                users, data['window_title'], data['tips_title'], data['tips_content'], data['tips_url'])

                        # 发送wx弹框提醒
                        # wx_users = '|'.join([x.first_name for x in wse_users if
                        #                      x.is_active and x.organizationmptt_set.first().wechat_approve == 0])
                        # if wx_users:
                        #     data = get_wx_notify()
                        #     send_weixin_message.delay(touser=wx_users, content=data)

                        # 发送企业微信审批
                        touser = '|'.join(
                            [x.first_name for x in get_state_user(wse.state, obj=wse.content_object) if
                             x.is_active and x.organizationmptt_set.first().wechat_approve == 1])
                        if touser:
                            result = get_wx_task_card_data(touser, wse)
                            if result['success']:
                                send_task_card_to_wx_user.delay(touser, result['data'])

                        return JsonResponse({"data": msg, "success": success})

                if name == 'wifi申请和网络问题申报':
                    create_time = datetime.now()
                    creator = request.user
                    applicant = User.objects.get(id=pdata.get('applicant'))
                    title = pdata.get('title')
                    mac = pdata.get('mac', pdata.get('ip'))
                    reason = pdata.get('reason')
                    name = pdata.get('name')
                    project = None
                    if wse:
                        pass
                    else:
                        obj = Wifi.objects.create(
                            create_time=create_time, creator=creator, applicant=applicant,
                            title=title, reason=reason, name=name, mac=mac)

                        if NEW_WORKFLOW == 1:
                            new_set_state_obj_user(obj, workflow_obj, applicant)
                        else:
                            set_state_obj_user(obj, workflow_obj, applicant, project)

                        # 设置obj到流程的初始化状态
                        wse = WorkflowStateEvent.objects.create(
                            content_object=obj, create_time=obj.create_time, creator=request.user,
                            title=obj.title + '(' + obj.mac + ')',
                            state=workflow_obj.init_state, is_current=True)

                        # 指定初始状态的审批用户
                        sor = get_sor(wse.state, obj)
                        if sor:
                            users = tuple(sor.users.all())
                            wse.users.add(*users)

                        # 申请人发送的第一个审批节点的审批用户如果是他自己
                        # 则第一个节点自动审批通过
                        init_state_user = get_state_user(wse.state, obj=wse.content_object, list_format=True)

                        if applicant in init_state_user:
                            transition = wse.state.transition.get(condition='同意')
                            msg, success, wse = do_transition(wse, transition, applicant)
                            # 指定下一个状态的审批用户
                            sor = get_sor(wse.state, obj)
                            if sor:
                                users = tuple(sor.users.all())
                                wse.users.add(*users)
                        else:
                            msg = 'ok'
                            success = True

                        # 发送邮件通知到第一个节点的审批人
                        to_list = [
                            x.email for x in get_state_user(wse.state, obj=wse.content_object) if
                            x.email and x.is_active
                        ]
                        if to_list:
                            subject, content = make_email_notify(True)
                            send_mail.delay(to_list, subject, content)

                        # 发送qq弹框提醒
                        users = ','.join(
                            [x.first_name for x in get_state_user(wse.state, obj=wse.content_object) if x.is_active])
                        if users:
                            data = get_qq_notify()
                            send_qq.delay(
                                users, data['window_title'], data['tips_title'], data['tips_content'], data['tips_url'])

                        # 发送wx弹框提醒
                        # wx_users = '|'.join(
                        #     [x.first_name for x in get_state_user(wse.state, obj=wse.content_object) if
                        #      x.is_active and x.organizationmptt_set.first().wechat_approve == 0])
                        # if wx_users:
                        #     data = get_wx_notify()
                        #     send_weixin_message.delay(touser=wx_users, content=data)

                        # 发送企业微信审批
                        touser = '|'.join(
                            [x.first_name for x in get_state_user(wse.state, obj=wse.content_object) if
                             x.is_active and x.organizationmptt_set.first().wechat_approve == 1])
                        if touser:
                            result = get_wx_task_card_data(touser, wse)
                            if result['success']:
                                send_task_card_to_wx_user.delay(touser, result['data'])

                        return JsonResponse({"data": msg, "success": success})

                if name == '办公电脑和配件申请':
                    create_time = datetime.now()
                    creator = request.user
                    applicant = User.objects.get(id=pdata.get('applicant'))
                    title = pdata.get('title')
                    reason = pdata.get('reason')
                    project = None
                    if wse:
                        pass
                    else:
                        obj = ComputerParts.objects.create(
                            create_time=create_time, creator=creator, applicant=applicant,
                            title=title, reason=reason)

                        if NEW_WORKFLOW == 1:
                            new_set_state_obj_user(obj, workflow_obj, applicant, project)
                        else:
                            set_state_obj_user(obj, workflow_obj, applicant, project)

                        # 设置obj到流程的初始化状态
                        wse = WorkflowStateEvent.objects.create(
                            content_object=obj, create_time=obj.create_time, creator=request.user, title=obj.title,
                            state=workflow_obj.init_state, is_current=True)

                        # 指定初始状态的审批用户
                        sor = get_sor(wse.state, obj)
                        if sor:
                            users = tuple(sor.users.all())
                            wse.users.add(*users)

                        # 申请人发送的第一个审批节点的审批用户如果是他自己
                        # 则第一个节点自动审批通过
                        init_state_user = get_state_user(wse.state, obj=wse.content_object, list_format=True)

                        if applicant in init_state_user:
                            transition = wse.state.transition.get(condition='同意')
                            msg, success, wse = do_transition(wse, transition, applicant)
                            # 指定下一个状态的审批用户
                            sor = get_sor(wse.state, obj)
                            if sor:
                                users = tuple(sor.users.all())
                                wse.users.add(*users)
                        else:
                            msg = 'ok'
                            success = True

                        # 发送邮件通知到第一个节点的审批人
                        to_list = [
                            x.email for x in get_state_user(wse.state, obj=wse.content_object) if
                            x.email and x.is_active
                        ]
                        if to_list:
                            subject, content = make_email_notify(True)
                            send_mail.delay(to_list, subject, content)

                        # 发送qq弹框提醒
                        users = ','.join(
                            [x.first_name for x in get_state_user(wse.state, obj=wse.content_object) if x.is_active])
                        if users:
                            data = get_qq_notify()
                            send_qq.delay(
                                users, data['window_title'], data['tips_title'], data['tips_content'], data['tips_url'])

                        # 发送wx弹框提醒
                        # wx_users = '|'.join(
                        #     [x.first_name for x in get_state_user(wse.state, obj=wse.content_object) if
                        #      x.is_active and x.organizationmptt_set.first().wechat_approve == 0])
                        # if wx_users:
                        #     data = get_wx_notify()
                        #     send_weixin_message.delay(touser=wx_users, content=data)

                        # 发送企业微信审批
                        touser = '|'.join(
                            [x.first_name for x in get_state_user(wse.state, obj=wse.content_object) if
                             x.is_active and x.organizationmptt_set.first().wechat_approve == 1])
                        if touser:
                            result = get_wx_task_card_data(touser, wse)
                            if result['success']:
                                send_task_card_to_wx_user.delay(touser, result['data'])

                        return JsonResponse({"data": msg, "success": success})

                if name == '版本更新单申请':
                    create_time = datetime.now()
                    creator = request.user
                    applicant = creator
                    title = pdata.get('title')
                    content = pdata.get('content')
                    project = pdata.get('project')
                    project = GameProject.objects.get(id=project)
                    server_list = pdata.get('server_list')
                    start_time = pdata.get('start_time')
                    end_time = pdata.get('end_time')
                    server_charge = pdata.get('server_charge')
                    client_charge = pdata.get('client_charge')
                    plan_charge = pdata.get('plan_charge')
                    test_charge = pdata.get('test_charge')
                    new_edition = pdata.get('new_edition', 0)
                    area = Area.objects.filter(chinese_name=pdata.get('area', '0'))
                    area = area[0] if area else None
                    if wse:
                        pass
                    else:
                        # if new_edition == "1":
                        #     server_list = json.dumps(server_list)

                        obj = VersionUpdate.objects.create(
                            create_time=create_time, creator=creator, applicant=applicant,
                            title=title, content=content, project=project, start_time=start_time,
                            end_time=end_time, server_list=server_list, new_edition=new_edition, area=area)

                        if NEW_WORKFLOW == 1:
                            new_set_state_obj_user(obj, workflow_obj, applicant, project,
                                                   server_charge=User.objects.get(id=server_charge).username,
                                                   client_charge=User.objects.get(id=client_charge).username,
                                                   plan_charge=User.objects.get(id=plan_charge).username,
                                                   test_charge=User.objects.get(id=test_charge).username)
                        else:
                            # 后端负责人审批
                            init_state = workflow_obj.init_state
                            sor = StateObjectUserRelation.objects.create(content_object=obj, state=init_state)
                            sor.users.add(User.objects.get(id=server_charge))

                            # 前端负责人审批
                            client_state = init_state.transition.get(condition='同意').destination
                            sor = StateObjectUserRelation.objects.create(content_object=obj, state=client_state)
                            sor.users.add(User.objects.get(id=client_charge))

                            # 策划负责人审批
                            plan_state = client_state.transition.get(condition='同意').destination
                            sor = StateObjectUserRelation.objects.create(content_object=obj, state=plan_state)
                            sor.users.add(User.objects.get(id=plan_charge))

                            # 测试负责人审批
                            test_state = plan_state.transition.get(condition='同意').destination
                            sor = StateObjectUserRelation.objects.create(content_object=obj, state=test_state)
                            sor.users.add(User.objects.get(id=test_charge))

                            # 运维负责人审批
                            # if new_edition == "1":
                            #     ops_state = test_state.transition.get(condition='同意').destination
                            #     sor = StateObjectUserRelation.objects.create(content_object=obj, state=ops_state)
                            #     ops_charge = project.get_relate_role_user()
                            #     for o in ops_charge:
                            #         sor.users.add(User.objects.get(id=o.id))

                        # 设置obj到流程的初始化状态
                        wse = WorkflowStateEvent.objects.create(
                            content_object=obj, create_time=obj.create_time, creator=request.user, title=obj.title,
                            state=workflow_obj.init_state, is_current=True)

                        # 指定初始状态的审批用户
                        sor = get_sor(wse.state, obj)
                        if sor:
                            users = tuple(sor.users.all())
                            wse.users.add(*users)

                        # 申请人发送的第一个审批节点的审批用户如果是他自己
                        # 则第一个节点自动审批通过
                        init_state_user = get_state_user(wse.state, obj=wse.content_object, list_format=True)

                        if applicant in init_state_user:
                            transition = wse.state.transition.get(condition='同意')
                            msg, success, wse = do_transition(wse, transition, applicant)
                            # 指定下一个状态的审批用户
                            sor = get_sor(wse.state, obj)
                            if sor:
                                users = tuple(sor.users.all())
                                wse.users.add(*users)
                        else:
                            msg = 'ok'
                            success = True

                        # 发送邮件通知到第一个节点的审批人
                        to_list = [
                            x.email for x in get_state_user(wse.state, obj=wse.content_object) if
                            x.email and x.is_active
                        ]

                        if to_list:
                            subject, content = make_email_notify(True)
                            send_mail.delay(to_list, subject, content)

                        # 发送qq弹框提醒
                        users = ','.join(
                            [x.first_name for x in get_state_user(wse.state, obj=wse.content_object) if x.is_active])
                        if users:
                            data = get_qq_notify()
                            send_qq.delay(
                                users, data['window_title'], data['tips_title'], data['tips_content'], data['tips_url'])

                        # 发送wx弹框提醒
                        wx_users = '|'.join(
                            [x.first_name for x in get_state_user(wse.state, obj=wse.content_object) if
                             x.is_active])
                        if wx_users:
                            data = get_wx_notify()
                            send_weixin_message.delay(touser=wx_users, content=data)

                        # 发送企业微信审批
                        # touser = '|'.join(
                        #     [x.first_name for x in get_state_user(wse.state, obj=wse.content_object) if
                        #      x.is_active and x.organizationmptt_set.first().wechat_approve == 1])
                        # if touser:
                        #     result = get_wx_task_card_data(touser, wse)
                        #     if result['success']:
                        #         send_task_card_to_wx_user.delay(touser, result['data'])

                        return JsonResponse({"data": msg, "success": success})

                if name == '服务器申请工单':
                    create_time = datetime.now()
                    creator = request.user
                    applicant = creator
                    title = pdata.get('title')
                    project = pdata.get('project')
                    purpose = pdata.get('purpose')
                    ip_type = pdata.get('ip_type')
                    config = pdata.get('config')
                    # number = pdata.get('number')
                    requirements = pdata.get('requirements')

                    project = GameProject.objects.get(id=project)

                    if wse:
                        pass
                    else:
                        obj = Machine.objects.create(
                            create_time=create_time, creator=creator, applicant=applicant,
                            title=title, project=project, purpose=purpose, config=json.dumps(config),
                            ip_type=ip_type, requirements=requirements)

                        if NEW_WORKFLOW == 1:
                            new_set_state_obj_user(obj, workflow_obj, applicant, project)
                        else:
                            """2018.12修改，关联新组织架构表，部门的负责人"""
                            # 1 部门的负责人
                            org = OrganizationMptt.objects.filter(user=applicant)
                            if not org:
                                raise Exception('用户没有在新组织架构中')
                            else:
                                org = OrganizationMptt.objects.get(user=applicant)
                                if not org.parent:
                                    raise UserNotInGroup('用户没有在部门里面')
                                else:
                                    if org.parent.leader == 0 or org.parent.parent.leader == 0:
                                        raise GroupExtentionError("申请人所在的部门没有设置负责人")
                            if org.parent.is_department_group == 0:
                                department_leader_id = org.parent.leader
                            else:
                                if org.parent.parent.is_department_group == 0:
                                    department_leader_id = org.parent.parent.leader
                                else:
                                    if org.parent.parent.parent.is_department_group == 0:
                                        department_leader_id = org.parent.parent.parent.leader
                                    else:
                                        raise Exception('用户部门设置不正确')
                            department_leader = User.objects.get(pk=department_leader_id)

                            # 部门负责人审批的state，是init_state
                            group_leader_state = workflow_obj.init_state
                            # 创建三者之前的关系
                            sor = StateObjectUserRelation.objects.create(content_object=obj, state=group_leader_state)
                            sor.users.add(department_leader)

                            # 2 项目负责人审批
                            project_leader = project.leader
                            if not project_leader:
                                raise WorkflowStateUserRelationError('项目负责人不存在')
                            # 项目负责人审批的state,这里对应的是部门负责人审批的condition状态是同意的destination的state
                            project_leader_state = group_leader_state.transition.get(condition='同意').destination
                            # 创建三者之前的关系
                            sor = StateObjectUserRelation.objects.create(content_object=obj, state=project_leader_state)
                            sor.users.add(project_leader)

                            # 3 中心负责人审批 根据项目的所在部门来确定
                            """2018.12修改，关联新组织架构表，中心负责人"""
                            if not project.organizationmptt_set.all():
                                raise Exception('所选的游戏项目没有所属部门')
                            center_leader_id = project.organizationmptt_set.all()[0].leader
                            if center_leader_id == 0:
                                raise GroupExtentionError("游戏项目所属部门没有设置负责人")
                            center_leader = User.objects.get(pk=center_leader_id)
                            # 中心负责人审批的state, 这里对应的是项目负责人审批state的conditon为
                            # 同意的destination的state
                            center_leader_state = project_leader_state.transition.get(condition='同意').destination
                            # 创建三者之间的关系
                            sor = StateObjectUserRelation.objects.create(content_object=obj, state=center_leader_state)
                            sor.users.add(center_leader)

                        # 设置obj到流程的初始化状态
                        wse = WorkflowStateEvent.objects.create(
                            content_object=obj, create_time=obj.create_time, creator=request.user, title=obj.title,
                            state=workflow_obj.init_state, is_current=True)

                        # 指定初始状态的审批用户
                        sor = get_sor(wse.state, obj)
                        if sor:
                            users = tuple(sor.users.all())
                            wse.users.add(*users)

                        # 申请人发送的第一个审批节点的审批用户如果是他自己
                        # 则第一个节点自动审批通过
                        init_state_user = get_state_user(wse.state, obj=wse.content_object, list_format=True)

                        if applicant in init_state_user:
                            transition = wse.state.transition.get(condition='同意')
                            msg, success, wse = do_transition(wse, transition, applicant)
                            # 指定下一个状态的审批用户
                            sor = get_sor(wse.state, obj)
                            if sor:
                                users = tuple(sor.users.all())
                                wse.users.add(*users)
                        else:
                            msg = 'ok'
                            success = True

                        # 发送邮件通知到第一个节点的审批人
                        to_list = [
                            x.email for x in get_state_user(wse.state, obj=wse.content_object) if
                            x.email and x.is_active
                        ]

                        if to_list:
                            subject, content = make_email_notify(True)
                            send_mail.delay(to_list, subject, content)

                        # 发送qq弹框提醒
                        users = ','.join(
                            [x.first_name for x in get_state_user(wse.state, obj=wse.content_object) if x.is_active])
                        if users:
                            data = get_qq_notify()
                            send_qq.delay(
                                users, data['window_title'], data['tips_title'], data['tips_content'], data['tips_url'])

                        # 发送wx弹框提醒
                        # wx_users = '|'.join(
                        #     [x.first_name for x in get_state_user(wse.state, obj=wse.content_object) if
                        #      x.is_active and x.organizationmptt_set.first().wechat_approve == 0])
                        # if wx_users:
                        #     data = get_wx_notify()
                        #     send_weixin_message.delay(touser=wx_users, content=data)

                        # 发送企业微信审批
                        touser = '|'.join(
                            [x.first_name for x in get_state_user(wse.state, obj=wse.content_object) if
                             x.is_active and x.organizationmptt_set.first().wechat_approve == 1])
                        if touser:
                            result = get_wx_task_card_data(touser, wse)
                            if result['success']:
                                send_task_card_to_wx_user.delay(touser, result['data'])

                        return JsonResponse({"data": msg, "success": success})

                if name == '项目人员调整工单':
                    create_time = datetime.now()
                    creator = request.user
                    applicant = User.objects.get(id=pdata.get('applicant'))
                    new_department_group = OrganizationMptt.objects.get(id=pdata.get('new_department_group'))
                    delete_svn = pdata.get('delete_svn')
                    delete_serper = pdata.get('delete_serper')
                    title = pdata.get('title')

                    svn_projects = pdata.get('svn_projects')  # 如果没有，就是None
                    serper_projects = pdata.get('serper_projects')  # 如果没有，就是None

                    if svn_projects:
                        svn_projects = json.dumps(svn_projects)
                    else:
                        svn_projects = None

                    if serper_projects:
                        serper_projects = json.dumps(serper_projects)
                    else:
                        serper_projects = None
                    # 原来的项目分组
                    # raw_project_group = applicant.profile.project_group
                    if wse:
                        pass
                    else:
                        obj = ProjectAdjust.objects.create(
                            create_time=create_time, creator=creator, applicant=applicant,
                            title=title, delete_svn=delete_svn, svn_projects=svn_projects,
                            serper_projects=serper_projects, delete_serper=delete_serper,
                            new_department_group=new_department_group)

                        if NEW_WORKFLOW == 1:
                            new_set_state_obj_user(obj, workflow_obj, applicant)
                        else:
                            """2018.12修改，获取审批链，关联新组织架构 """
                            org = OrganizationMptt.objects.filter(user=applicant)
                            if not org:
                                raise Exception('用户没有在新组织架构中')
                            else:
                                org = OrganizationMptt.objects.get(user=applicant)
                                if not org.parent:
                                    raise UserNotInGroup('用户没有在部门里面')
                                else:
                                    if org.parent.leader == 0 or org.parent.parent.leader == 0:
                                        raise GroupExtentionError("申请人所在的部门没有设置负责人")
                            if org.parent.is_department_group == 0:
                                department_leader_id = org.parent.leader
                            else:
                                if org.parent.parent.is_department_group == 0:
                                    department_leader_id = org.parent.parent.leader
                                else:
                                    if org.parent.parent.parent.is_department_group == 0:
                                        department_leader_id = org.parent.parent.parent.leader
                                    else:
                                        raise Exception('用户部门设置不正确')
                            group_leader = User.objects.get(pk=department_leader_id)

                            # 1 部门负责人审批的state，是init_state
                            group_leader_state = workflow_obj.init_state
                            # 创建三者之前的关系
                            sor = StateObjectUserRelation.objects.create(content_object=obj, state=group_leader_state)
                            sor.users.add(group_leader)

                        # 设置obj到流程的初始化状态
                        wse = WorkflowStateEvent.objects.create(
                            content_object=obj, create_time=obj.create_time, creator=request.user, title=obj.title,
                            state=workflow_obj.init_state, is_current=True)

                        # 指定初始状态的审批用户
                        sor = get_sor(wse.state, obj)
                        if sor:
                            users = tuple(sor.users.all())
                            wse.users.add(*users)

                        # 申请人发送的第一个审批节点的审批用户如果是他自己
                        # 则第一个节点自动审批通过
                        init_state_user = get_state_user(wse.state, obj=wse.content_object, list_format=True)

                        if applicant in init_state_user:
                            set_init_approve = True
                            set_init_approve_user = applicant
                        elif obj.creator in init_state_user:
                            set_init_approve = True
                            set_init_approve_user = obj.creator
                        else:
                            set_init_approve = False

                        if set_init_approve:
                            transition = wse.state.transition.get(condition='同意')
                            msg, success, wse = do_transition(wse, transition, set_init_approve_user)
                            if wse.state.name == '完成':
                                content_object = wse.content_object
                                if content_object.delete_serper:
                                    if content_object.serper_projects is not None:
                                        clean_project_serper.delay(wse.id, json.loads(content_object.serper_projects))
                                if content_object.delete_svn:
                                    if content_object.svn_projects is not None:
                                        for proj_id in json.loads(content_object.svn_projects):
                                            clean_svn_workflow.delay(wse.id, proj_id)
                                # 如果都没有勾选清除svn或者服务器权限的，改为已处理状态
                                if not content_object.delete_serper and not content_object.delete_svn:
                                    content_object.status = '0'
                                    content_object.save()
                            # 指定下一个状态的审批用户
                            sor = get_sor(wse.state, obj)
                            if sor:
                                users = tuple(sor.users.all())
                                wse.users.add(*users)
                        else:
                            msg = 'ok'
                            success = True

                        # 发送邮件通知到第一个节点的审批人
                        to_list = [
                            x.email for x in get_state_user(wse.state, obj=wse.content_object) if
                            x.email and x.is_active
                        ]
                        if to_list:
                            subject, content = make_email_notify(True)
                            send_mail.delay(to_list, subject, content)

                        # 发送qq弹框提醒
                        users = ','.join(
                            [x.first_name for x in get_state_user(wse.state, obj=wse.content_object) if x.is_active])
                        if users:
                            data = get_qq_notify()
                            send_qq.delay(
                                users, data['window_title'], data['tips_title'], data['tips_content'], data['tips_url'])

                        # 发送wx弹框提醒
                        # wx_users = '|'.join(
                        #     [x.first_name for x in get_state_user(wse.state, obj=wse.content_object) if
                        #      x.is_active and x.organizationmptt_set.first().wechat_approve == 0])
                        # if wx_users:
                        #     data = get_wx_notify()
                        #     send_weixin_message.delay(touser=wx_users, content=data)

                        # 发送企业微信审批
                        touser = '|'.join(
                            [x.first_name for x in get_state_user(wse.state, obj=wse.content_object) if
                             x.is_active and x.organizationmptt_set.first().wechat_approve == 1])
                        if touser:
                            result = get_wx_task_card_data(touser, wse)
                            if result['success']:
                                send_task_card_to_wx_user.delay(touser, result['data'])

                        return JsonResponse({"data": msg, "success": success})

                if name == '数据库权限申请':
                    create_time = datetime.now()
                    creator = request.user
                    applicant = creator
                    title = pdata.get('title')
                    reason = pdata.get('reason')
                    content = pdata.get('content')
                    project = None
                    if wse:
                        pass
                    else:
                        obj = MysqlWorkflow.objects.create(
                            create_time=create_time, creator=creator, applicant=applicant,
                            title=title, reason=reason, content=json.dumps(content))

                        if NEW_WORKFLOW == 1:
                            new_set_state_obj_user(obj, workflow_obj, applicant, project)
                        else:
                            set_state_obj_user(obj, workflow_obj, applicant, project)

                        # 设置obj到流程的初始化状态
                        wse = WorkflowStateEvent.objects.create(
                            content_object=obj, create_time=obj.create_time, creator=request.user, title=obj.title,
                            state=workflow_obj.init_state, is_current=True)

                        # 指定初始状态的审批用户
                        sor = get_sor(wse.state, obj)
                        if sor:
                            users = tuple(sor.users.all())
                            wse.users.add(*users)

                        # 申请人发送的第一个审批节点的审批用户如果是他自己
                        # 则第一个节点自动审批通过
                        init_state_user = get_state_user(wse.state, obj=wse.content_object, list_format=True)

                        if applicant in init_state_user:
                            transition = wse.state.transition.get(condition='同意')
                            msg, success, wse = do_transition(wse, transition, applicant)
                            # 指定下一个状态的审批用户
                            sor = get_sor(wse.state, obj)
                            if sor:
                                users = tuple(sor.users.all())
                                wse.users.add(*users)
                        else:
                            msg = 'ok'
                            success = True

                        # 发送邮件通知到第一个节点的审批人
                        to_list = [
                            x.email for x in get_state_user(wse.state, obj=wse.content_object) if
                            x.email and x.is_active
                        ]

                        if to_list:
                            subject, content = make_email_notify(True)
                            send_mail.delay(to_list, subject, content)

                        # 发送qq弹框提醒
                        users = ','.join(
                            [x.first_name for x in get_state_user(wse.state, obj=wse.content_object) if x.is_active])
                        if users:
                            data = get_qq_notify()
                            send_qq.delay(
                                users, data['window_title'], data['tips_title'], data['tips_content'], data['tips_url'])

                        # 发送wx弹框提醒
                        # wx_users = '|'.join(
                        #     [x.first_name for x in get_state_user(wse.state, obj=wse.content_object) if
                        #      x.is_active and x.organizationmptt_set.first().wechat_approve == 0])
                        # if wx_users:
                        #     data = get_wx_notify()
                        #     send_weixin_message.delay(touser=wx_users, content=data)

                        # 发送企业微信审批
                        touser = '|'.join(
                            [x.first_name for x in get_state_user(wse.state, obj=wse.content_object) if
                             x.is_active and x.organizationmptt_set.first().wechat_approve == 1])
                        if touser:
                            result = get_wx_task_card_data(touser, wse)
                            if result['success']:
                                send_task_card_to_wx_user.delay(touser, result['data'])

                        return JsonResponse({"data": msg, "success": success})

        except Transition.DoesNotExist:
            msg = '找不到状态链'
            success = False
            return JsonResponse({"data": msg, "success": success})
        except IntegrityError:
            msg = '标题有重复，换一个标题'
            success = False
            return JsonResponse({"data": msg, "success": success})
        except Room.DoesNotExist:
            msg = '机房不存在'
            success = False
            return JsonResponse({"data": msg, "success": success})
        except User.DoesNotExist:
            msg = '申请人不存在'
            success = False
            return JsonResponse({"data": msg, "success": success})
        except GameProject.DoesNotExist:
            msg = '项目不存在'
            success = False
            return JsonResponse({"data": msg, "success": success})
        except ProjectGroup.DoesNotExist:
            msg = '项目分组不存在'
            success = False
            return JsonResponse({"data": msg, "success": success})
        except UserNotInGroup as e:
            msg = str(e)
            success = False
            return JsonResponse({"data": msg, "success": success})
        except WorkflowStateUserRelationError as e:
            msg = '项目没有负责人'
            success = False
            return JsonResponse({"data": msg, "success": success})
        except GameProjectError as e:
            msg = str(e)
            success = False
            return JsonResponse({"data": msg, "success": success})
        except WorkflowError as e:
            msg = '当前流程没有设置初始状态'
            success = False
            return JsonResponse({"data": msg, "success": success})
        except CurrentStateError as e:
            msg = str(e)
            success = False
            return JsonResponse({"data": msg, "success": success})
        except GroupExtentionError as e:
            msg = str(e)
            success = False
            return JsonResponse({"data": msg, "success": success})
        except Group.groupprofile.RelatedObjectDoesNotExist:
            msg = '分组没有扩展'
            success = False
            return JsonResponse({"data": msg, "success": success})
        except Exception as e:
            msg = str(e)
            success = False
            # print(e)
            return JsonResponse({"data": msg, "success": success})
        finally:
            if wse:
                # 自动添加svn接口
                if isinstance(wse.content_object, SVNWorkflow) and wse.state.name == '完成':
                    add_svn_workflow.delay(wse.id)
                # 添加服务器权限接口
                if isinstance(wse.content_object, ServerPermissionWorkflow) and wse.state.name == '完成':
                    # api_add_server_permission(new_wse)
                    workflow_add_server_permission.delay(wse.id)
                # 自动执行前端热更新
                if isinstance(wse.content_object, ClientHotUpdate) and wse.state.name == '完成':
                    # 工单完成以后，修改工单的状态
                    content_object = wse.content_object
                    content_object.status = '4'
                    content_object.save()
                    ws_notify()

                    """如果当前项目和地区没有锁，则找到下一个更新去执行"""
                    """
                    2019.3修改
                    修改获取运维管理机的方法:
                    通过content_object中关联的推送子任务表获取更新需要用到的运维管理机，
                    及rsync推送时所需要用到的参数
                    """
                    status_list = [x.ops.status for x in content_object.clienthotupdatersynctask_set.all()]
                    if len(list(set(status_list))) == 1 and '0' in status_list:
                        # do_hot_client.delay(new_wse.id)
                        msg, next_hot_update = get_next_hot_update(content_object.project,
                                                                   content_object.area_name)
                        if next_hot_update:
                            if next_hot_update.status == '4':
                                do_hot_update(next_hot_update)
                        else:
                            """更新任务没有自动执行原因字段"""
                            content_object.no_auto_execute_reason = msg
                            content_object.save(update_fields=['no_auto_execute_reason'])
                            # 发送邮件告警
                            # to_list = [x.email for x in content_object.project.related_user.all() if x.is_active]
                            to_list = list(
                                set([x.email for x in content_object.project.get_relate_role_user() if x.is_active]))
                            subject = '热更新审批完成后没有自动执行'
                            content = '项目:{} 地区:{}，热更新:{} 没有自动执行，请查看原因：可能是{}'.format(
                                content_object.project.project_name, content_object.area_name,
                                content_object.title,
                                msg)
                            send_mail.delay(to_list, subject, content)
                            # users = ','.join([x.first_name for x in wse.content_object.project.related_user.all() if x.is_active])
                            users = ','.join([x.first_name for x in wse.content_object.project.get_relate_role_user() if
                                              x.is_active])
                            send_qq.delay(
                                users, subject, subject, content, '')
                            # wx_users = '|'.join([x.first_name for x in wse.content_object.project.related_user.all() if x.is_active])
                            wx_users = '|'.join(
                                [x.first_name for x in wse.content_object.project.get_relate_role_user() if
                                 x.is_active])
                            send_weixin_message.delay(
                                touser=wx_users, content=subject + content)
                    else:
                        # 热更新审批完成后没有触发执行
                        # 需要发送告警给相应的运维负责人
                        # users = ','.join([x.first_name for x in wse.content_object.project.related_user.all() if x.is_active])
                        users = ','.join(
                            [x.first_name for x in wse.content_object.project.get_relate_role_user() if x.is_active])
                        window_title = '项目地区锁:热更新审批完成后不能自动执行'
                        tips_title = '项目地区锁:热更新审批完成后不能自动执行'
                        tips_content = '项目:{} 地区:{} 已经上锁，热更新:{} 不能自动执行 链接:请登录CMDB处理(只能使用谷歌或者火狐浏览器)'.format(
                            content_object.project.project_name, content_object.area_name,
                            content_object.title)
                        tips_url = 'https://192.168.100.66/myworkflows/hot_server_list/'
                        send_qq.delay(
                            users, window_title, tips_title, tips_content, tips_url)
                        # wx_users = '|'.join([x.first_name for x in wse.content_object.project.related_user.all() if x.is_active])
                        wx_users = '|'.join(
                            [x.first_name for x in wse.content_object.project.get_relate_role_user() if x.is_active])
                        send_weixin_message.delay(
                            touser=wx_users, content=tips_title + tips_content + tips_url)

                        # 发送邮件告警
                        # to_list = [x.email for x in content_object.project.related_user.all() if x.is_active]
                        to_list = list(
                            set([x.email for x in content_object.project.get_relate_role_user() if x.is_active]))
                        subject = '项目地区锁:热更新审批完成后不能自动执行'
                        content = '项目:{} 地区:{} 已经上锁，热更新:{} 不能自动执行'.format(
                            content_object.project.project_name, content_object.area_name,
                            content_object.title)
                        send_mail.delay(to_list, subject, content)

                        """更新任务没有自动执行原因字段"""
                        content_object.no_auto_execute_reason = tips_content
                        content_object.save(update_fields=['no_auto_execute_reason'])
                # 自动添加mysql权限
                if isinstance(wse.content_object, MysqlWorkflow) and wse.state.name == '完成':
                    add_mysql_permission.delay(wse.id)
                # 执行根据项目删除服务器权限和SVN权限
                if isinstance(wse.content_object, ProjectAdjust) and wse.state.name == '完成':
                    content_object = wse.content_object
                    if content_object.delete_serper:
                        if content_object.serper_projects is not None:
                            clean_project_serper.delay(wse.id,
                                                       json.loads(content_object.serper_projects))
                    if content_object.delete_svn:
                        if content_object.svn_projects is not None:
                            for proj_id in json.loads(content_object.svn_projects):
                                clean_svn_workflow.delay(wse.id, proj_id)

                    # 如果都没有勾选清除svn或者服务器权限的，改为已处理状态
                    if not content_object.delete_serper and not content_object.delete_svn:
                        content_object.status = '0'
                        content_object.save()

                    # 调整人员所属部门
                    if content_object.new_department_group is not None:
                        org = OrganizationMptt.objects.get(user_id=content_object.applicant_id)
                        org.parent = content_object.new_department_group
                        org.save()

                # 版本更新单发送qq/wx弹窗提醒
                if isinstance(wse.content_object, VersionUpdate) and wse.state.name == '完成':
                    # project_related_ops = wse.content_object.project.related_user.all()
                    project_related_ops = wse.content_object.project.get_relate_role_user()
                    data = get_version_update_notify(wse.title)
                    users = ','.join([x.first_name for x in project_related_ops if x.is_active])
                    send_qq.delay(users, data['window_title'], data['tips_title'], data['tips_content'],
                                  data['tips_url'])
                    wx_users = '|'.join([x.first_name for x in project_related_ops if x.is_active])
                    send_weixin_message.delay(touser=wx_users, content=data)
                # 自动执行后端热更新
                if isinstance(wse.content_object, ServerHotUpdate) and wse.state.name == '完成':
                    # 工单完成以后，修改工单的状态
                    content_object = wse.content_object
                    content_object.status = '4'
                    content_object.save()
                    ws_notify()

                    # 加载热更新的区服数据到redis中
                    # load_to_redis(new_wse.content_object)

                    # 如果当前项目和地区没有锁，则直接发送到任务队列里面
                    """
                    2019.3修改
                    根据后端热更新子任务表获取运维管理机状态
                    """
                    status_list = [x.ops.status for x in content_object.serverhotupdatersynctask_set.all()]
                    if len(list(set(status_list))) == 1 and '0' in status_list:
                        msg, next_hot_update = get_next_hot_update(content_object.project, content_object.area_name)
                        if next_hot_update:
                            if next_hot_update.status == '4':
                                do_hot_update(next_hot_update)
                            elif next_hot_update.status == '0':
                                content_object.no_auto_execute_reason = next_hot_update.title + '状态不是待更新！'
                                content_object.save()
                        else:
                            """更新任务没有自动执行原因字段"""
                            content_object.no_auto_execute_reason = msg
                            content_object.save()
                            # 发送邮件告警
                            # to_list = [x.email for x in content_object.project.related_user.all() if x.is_active]
                            to_list = list(
                                set([x.email for x in content_object.project.get_relate_role_user() if x.is_active]))
                            subject = '热更新审批完成后没有自动执行'
                            content = '项目:{} 地区:{}，热更新:{} 没有自动执行,请查看原因 {}'.format(
                                content_object.project.project_name, content_object.area_name, content_object.title,
                                msg)
                            send_mail.delay(to_list, subject, content)
                    else:
                        # 热更新审批完成后没有触发执行
                        # 需要发送告警给相应的运维负责人
                        # users = ','.join([x.first_name for x in wse.content_object.project.related_user.all() if x.is_active])
                        users = ','.join(
                            [x.first_name for x in wse.content_object.project.get_relate_role_user() if x.is_active])
                        window_title = '项目地区锁:热更新审批完成后不能自动执行'
                        tips_title = '项目地区锁:热更新审批完成后不能自动执行'
                        tips_content = '项目:{} 地区:{} 已经上锁，热更新:{} 不能自动执行 链接:请登录CMDB处理(只能使用谷歌或者火狐浏览器)'.format(
                            content_object.project.project_name, content_object.area_name, content_object.title)
                        tips_url = 'https://192.168.100.66/myworkflows/hot_server_list/'
                        send_qq.delay(
                            users, window_title, tips_title, tips_content, tips_url)
                        # wx_users = '|'.join([x.first_name for x in wse.content_object.project.related_user.all() if x.is_active])
                        wx_users = '|'.join(
                            [x.first_name for x in wse.content_object.project.get_relate_role_user() if x.is_active])
                        send_weixin_message.delay(
                            touser=wx_users, content=tips_title + tips_content + tips_url)

                        # 发送邮件告警
                        # to_list = [x.email for x in content_object.project.related_user.all() if x.is_active]
                        to_list = list(
                            set([x.email for x in content_object.project.get_relate_role_user() if x.is_active]))
                        subject = '项目地区锁:热更新审批完成后不能自动执行'
                        content = '项目:{} 地区:{} 已经上锁，热更新:{} 不能自动执行'.format(
                            content_object.project.project_name, content_object.area_name, content_object.title)
                        send_mail.delay(to_list, subject, content)

                        """更新任务没有自动执行原因字段"""
                        content_object.no_auto_execute_reason = tips_content
                        content_object.save(update_fields=['no_auto_execute_reason'])
                # 服务器申请工单完成后发送通知给相关人员
                if isinstance(wse.content_object, Machine) and wse.state.name == '完成':
                    machine_administrator_list = [u.first_name for u in
                                                  User.objects.filter(username__in=get_machine_administrator())]
                    users = ','.join(machine_administrator_list)
                    send_qq.delay(users, '你有一个服务器申请工单', '你有一个服务器申请工单',
                                  '链接:请登录CMDB处理(只能使用谷歌或者火狐浏览器)',
                                  'http://192.168.100.66/myworkflows/approve_list/')
                    wx_users = '|'.join(machine_administrator_list)
                    send_weixin_message.delay(touser=wx_users, content='你有一个服务器申请工单' + '你有一个服务器申请工单' +
                                                                       '链接:请登录CMDB处理(只能使用谷歌或者火狐浏览器)' +
                                                                       'http://192.168.100.66/myworkflows/approve_list/')
                    # 发送是否已构买任务卡片给相关人员
                    result = get_wx_task_card_data(wx_users, wse, purchase=True)
                    if result['success']:
                        send_task_card_to_wx_user.delay(wx_users, result['data'])


def apply_history(request):
    '我的工单申请历史,记录了我的所有的工单申请以及当前的状态'

    if request.method == "GET":
        head = {'value': '工单记录', 'username': request.user.username}
        return render(request, 'workflow_histroy.html', {'head': head})


def data_apply_history(request):
    '我的工单申请历史数据'

    if request.method == "POST":
        raw_get = request.POST.dict()

        search_value = raw_get.get('search[value]', '')
        start = int(raw_get.get('start', 0))
        draw = raw_get.get('draw', 0)
        length = int(raw_get.get('length', 10))

        sub_query = Q()

        sub_query.add(Q(title__icontains=search_value), Q.OR)
        sub_query.add(Q(create_time__contains=search_value), Q.OR)
        sub_query.add(Q(state__workflow__name__icontains=search_value), Q.OR)
        sub_query.add(Q(state__name__icontains=search_value), Q.OR)
        sub_query.add(Q(state_value__icontains=search_value), Q.OR)

        query = WorkflowStateEvent.objects.select_related('state').select_related(
            'state__workflow').filter(Q(is_current=True) & Q(creator=request.user) & sub_query).order_by(
            '-create_time')

        raw_data = query[start: start + length]
        recordsTotal = query.count()
        data = {"data": [i.show_all() for i in raw_data], 'draw': draw,
                'recordsTotal': recordsTotal, 'recordsFiltered': recordsTotal}
        return JsonResponse(data)


def apply_history_all(request):
    '工单申请汇总，只有管理员才有权限'

    if request.method == "GET":
        if request.user.is_superuser:
            head = {'value': '工单汇总', 'username': request.user.username, 'is_superuser': request.user.is_superuser}
            # admin_list = Group.objects.get(name='运维网络管理员组').user_set.all()
            admin_list = OrganizationMptt.objects.filter(is_active=1, parent__name='网络管理组')
            admin_list_dict = {}
            for admin in admin_list:
                admin_list_dict[admin.user_id] = admin.name

            all_workflow = [x.show_id_and_name() for x in Workflow.objects.all()]
            workflow_id_model_dict = get_workflow_process_status_dict()

            return render(request,
                          'workflow_histroy_all.html',
                          {'head': head, 'admin_list_dict': admin_list_dict,
                           'all_workflow': all_workflow, 'workflow_id_model_dict': json.dumps(workflow_id_model_dict)})
        else:
            return render(request, '403.html')


def data_apply_history_all(request):
    '我的工单申请历史数据'

    if request.method == "POST":
        raw_get = request.POST.dict()

        # search_value = raw_get.get('search[value]', '')
        workflow_id_list = request.POST.getlist('workflow[]', '')
        workflow = [w.name for w in Workflow.objects.filter(id__in=workflow_id_list)]
        workflow_status = raw_get.get('workflow_status', '100')
        filter_state_value = request.POST.getlist('filter_state_value[]', '全部')
        time = raw_get.get('time', '')
        creator = raw_get.get('creator', '')
        applicant = raw_get.get('applicant', '')
        title = raw_get.get('title', '')
        state = raw_get.get('state', '')
        svn_processed = json.loads(raw_get.get('svn_processed'))
        serper_processed = json.loads(raw_get.get('serper_processed'))
        admin = int(raw_get.get('admin', ''))

        start = int(raw_get.get('start', 0))
        draw = raw_get.get('draw', 0)
        length = int(raw_get.get('length', 10))

        sub_query = Q()

        if 'SVN申请' in workflow or not workflow:
            ctype = ContentType.objects.get(model='SVNWorkflow')
            if workflow_status != '100':
                if workflow_status == '0':
                    sub_query.add((Q(content_type=ctype) & Q(svn_workflow__status=0)), Q.OR)
                else:
                    sub_query.add((Q(content_type=ctype) & Q(svn_workflow__status__in=(1, 2))), Q.OR)
            else:
                sub_query.add(Q(content_type=ctype), Q.OR)
        if '服务器权限申请' in workflow or not workflow:
            ctype = ContentType.objects.get(model='ServerPermissionWorkflow')
            if workflow_status != '100':
                if workflow_status == '0':
                    sub_query.add((Q(content_type=ctype) & Q(ser_per_workflow__status=0)), Q.OR)
                else:
                    sub_query.add((Q(content_type=ctype) & Q(ser_per_workflow__status__in=(1, 2))), Q.OR)
            else:
                sub_query.add(Q(content_type=ctype), Q.OR)
        if '电脑故障申报' in workflow or not workflow:
            ctype = ContentType.objects.get(model='FailureDeclareWorkflow')
            if workflow_status != '100':
                if workflow_status == '0':
                    sub_query.add((Q(content_type=ctype) & Q(failure_declare_workflow__status=0)), Q.OR)
                else:
                    sub_query.add((Q(content_type=ctype) & Q(failure_declare_workflow__status__in=(1, 2))), Q.OR)
            else:
                sub_query.add(Q(content_type=ctype), Q.OR)
        if 'wifi申请和网络问题申报' in workflow or not workflow:
            ctype = ContentType.objects.get(model='Wifi')
            if workflow_status != '100':
                if workflow_status == '0':
                    sub_query.add((Q(content_type=ctype) & Q(wifi_workflow__status=0)), Q.OR)
                else:
                    sub_query.add((Q(content_type=ctype) & Q(wifi_workflow__status__in=(1, 2))), Q.OR)
            else:
                sub_query.add(Q(content_type=ctype), Q.OR)
        if '办公电脑和配件申请' in workflow or not workflow:
            ctype = ContentType.objects.get(model='ComputerParts')
            if workflow_status != '100':
                if workflow_status == '0':
                    sub_query.add((Q(content_type=ctype) & Q(computer_parts_workflow__status=0)), Q.OR)
                else:
                    sub_query.add((Q(content_type=ctype) & Q(computer_parts_workflow__status__in=(1, 2))), Q.OR)
            else:
                sub_query.add(Q(content_type=ctype), Q.OR)
        if '前端热更新' in workflow or not workflow:
            ctype = ContentType.objects.get(model='ClientHotUpdate')
            if workflow_status != '100':
                if workflow_status == '0':
                    sub_query.add((Q(content_type=ctype) & Q(hot_client_workflow__status=3)), Q.OR)
                else:
                    sub_query.add((Q(content_type=ctype) & Q(hot_client_workflow__status__in=(0, 1, 2, 4))), Q.OR)
            else:
                sub_query.add(Q(content_type=ctype), Q.OR)
        if '后端热更新' in workflow or not workflow:
            ctype = ContentType.objects.get(model='ServerHotUpdate')
            if workflow_status != '100':
                if workflow_status == '0':
                    sub_query.add((Q(content_type=ctype) & Q(hot_server_workflow__status=3)), Q.OR)
                else:
                    sub_query.add((Q(content_type=ctype) & Q(hot_server_workflow__status__in=(0, 1, 2, 4))), Q.OR)
            else:
                sub_query.add(Q(content_type=ctype), Q.OR)
        if '版本更新单申请' in workflow or not workflow:
            ctype = ContentType.objects.get(model='VersionUpdate')
            if workflow_status != '100':
                if workflow_status == '0':
                    sub_query.add((Q(content_type=ctype) & Q(version_update_workflow__status=0)), Q.OR)
                else:
                    sub_query.add((Q(content_type=ctype) & Q(version_update_workflow__status__in=(1, 2))), Q.OR)
            else:
                sub_query.add(Q(content_type=ctype), Q.OR)
        if '服务器申请工单' in workflow or not workflow:
            ctype = ContentType.objects.get(model='Machine')
            if workflow_status != '100':
                if workflow_status == '0':
                    sub_query.add((Q(content_type=ctype) & Q(machine_workflow__status=0)), Q.OR)
                else:
                    sub_query.add((Q(content_type=ctype) & Q(machine_workflow__status__in=(1, 2))), Q.OR)
            else:
                sub_query.add(Q(content_type=ctype), Q.OR)
        if '项目人员调整工单' in workflow or not workflow:
            ctype = ContentType.objects.get(model='ProjectAdjust')
            if workflow_status != '100':
                if workflow_status == '0':
                    sub_query.add((Q(content_type=ctype) & Q(project_adjust_workflow__status=0)), Q.OR)
                else:
                    sub_query.add((Q(content_type=ctype) & Q(project_adjust_workflow__status__in=(1, 2))), Q.OR)
            else:
                sub_query.add(Q(content_type=ctype), Q.OR)
        if '数据库权限申请' in workflow or not workflow:
            ctype = ContentType.objects.get(model='MysqlWorkflow')
            if workflow_status != '100':
                if workflow_status == '0':
                    sub_query.add((Q(content_type=ctype) & Q(mysql_workflow__status=0)), Q.OR)
                else:
                    sub_query.add((Q(content_type=ctype) & Q(mysql_workflow__status__in=(1, 2))), Q.OR)
            else:
                sub_query.add(Q(content_type=ctype), Q.OR)

        if time:
            sub_query.add(Q(create_time__contains=time), Q.AND)

        if creator:
            sub_query.add(Q(creator__username__icontains=creator), Q.AND)

        if applicant:
            sub_query.add((
                    Q(svn_workflow__applicant__username__icontains=applicant) |
                    Q(ser_per_workflow__applicant__username__icontains=applicant) |
                    Q(failure_declare_workflow__applicant__username__icontains=applicant) |
                    Q(hot_client_workflow__applicant__username__icontains=applicant) |
                    Q(hot_server_workflow__applicant__username__icontains=applicant) |
                    Q(version_update_workflow__applicant__username__icontains=applicant) |
                    Q(wifi_workflow__applicant__username__icontains=applicant) |
                    Q(machine_workflow__applicant__username__icontains=applicant) |
                    Q(project_adjust_workflow__applicant__username__icontains=applicant) |
                    Q(computer_parts_workflow__applicant__username__icontains=applicant)), Q.AND)

        if title:
            sub_query.add(Q(title__icontains=title), Q.AND)

        if state:
            sub_query.add(Q(state__name__icontains=state), Q.AND)

        sub_query_status = Q()
        if filter_state_value != '全部':
            if '完成' in filter_state_value:
                sub_query_status.add(Q(state__name='完成'), Q.OR)
            if '审核中' in filter_state_value:
                sub_query_status.add((~Q(state__name='完成') & Q(state_value=None)), Q.OR)
            if '拒绝' in filter_state_value:
                sub_query_status.add((Q(state_value='拒绝') & Q(is_cancel=0)), Q.OR)
            if '取消' in filter_state_value:
                sub_query_status.add((Q(state_value='拒绝') & Q(is_cancel=1)), Q.OR)

        if svn_processed:
            ctype = ContentType.objects.get(model='SVNWorkflow')
            query = WorkflowStateEvent.objects.select_related(
                'state').select_related('state__workflow').filter(
                Q(content_type=ctype, is_current=True, state__name='完成', svn_workflow__status=1) & sub_query & sub_query_status).order_by(
                '-create_time')
        elif serper_processed:
            ctype = ContentType.objects.get(model='ServerPermissionWorkflow')
            query = WorkflowStateEvent.objects.select_related(
                'state').select_related('state__workflow').filter(
                Q(content_type=ctype, is_current=True, state__name='完成',
                  ser_per_workflow__status=2) & sub_query & sub_query_status).order_by(
                '-create_time')
        elif admin:
            admin = User.objects.get(id=admin)
            list_content_object = get_content_object_by_user_from_sor(admin)
            query = WorkflowStateEvent.objects.select_related(
                'state').select_related('state__workflow').filter(
                Q(failure_declare_workflow__in=list_content_object, is_current=True) &
                sub_query & sub_query_status).order_by('-create_time')
        else:
            query = WorkflowStateEvent.objects.select_related(
                'state').select_related('state__workflow').filter(Q(is_current=True) & sub_query & sub_query_status).\
                order_by('-create_time')

        raw_data = query[start: start + length]
        recordsTotal = query.count()

        data = {"data": [i.show_workflow_history_all() for i in raw_data], 'draw': draw,
                'recordsTotal': recordsTotal, 'recordsFiltered': recordsTotal}
        return JsonResponse(data)


def approve_list(request):
    '我的待审批列表'

    if request.method == "GET":
        head = {'value': '待审批列表', 'username': request.user.username}
        return render(request, 'approve_list.html', {'head': head})


def data_approve_list(request):
    """我的待审批条件
    wse的is_current为True并且state_vlaue为None
    """

    if request.method == "POST":
        raw_get = request.POST.dict()

        search_value = raw_get.get('search[value]', '')
        start = int(raw_get.get('start', 0))
        draw = raw_get.get('draw', 0)
        length = int(raw_get.get('length', 10))

        sub_query = Q()
        sub_query.add(Q(create_time__contains=search_value), Q.OR)
        sub_query.add(Q(title__icontains=search_value), Q.OR)
        sub_query.add(Q(state__workflow__name__icontains=search_value), Q.OR)
        sub_query.add(Q(state_value__icontains=search_value), Q.OR)
        sub_query.add(Q(creator__username__icontains=search_value), Q.OR)

        # 从wse的users中找到wse
        sor_query = WorkflowStateEvent.objects.prefetch_related('users').filter(
            Q(is_current=True) & Q(state_value=None) & sub_query).exclude(state__name='完成').order_by('-create_time')
        sor_query = [x for x in sor_query if request.user in x.users.all()]

        # 然后通过每个state下指定的用户去查
        # states = get_specified_user_related_state(request.user)
        # states_query = WorkflowStateEvent.objects.filter(
        #     Q(state__in=states, is_current=True, state_value=None) & sub_query).order_by('-create_time')

        # 合并两个查询结果
        # sor_query.extend(list(states_query))
        all_query = list(set(sor_query))
        all_query.sort(key=lambda x: x.create_time, reverse=True)

        raw_data = all_query[start: start + length]
        # recordsTotal = all_query.count()
        recordsTotal = len(all_query)

        data = {"data": sorted([i.show_approve() for i in raw_data], key=itemgetter('create_time'), reverse=True),
                'draw': draw, 'recordsTotal': recordsTotal,
                'recordsFiltered': recordsTotal}
        return JsonResponse(data)


def approved_list(request):
    '我的审批记录列表'

    if request.method == "GET":
        head = {'value': '审批记录', 'username': request.user.username}
        return render(request, 'approved_list.html', {'head': head})


def data_approved_list(request):
    """我的审批记录
    用户所有关联的state并且state_value不为空

    获取审批记录有两种情况:
    1 state有指定的users, 例如CEO审批，只要从wse中找到ceo的state即可
    2 state没有指定的users, 例如项目负责人审批，需要通过sor中的obj和state来从wse中获取
    """

    if request.method == "POST":
        raw_get = request.POST.dict()

        search_value = raw_get.get('search[value]', '')
        start = int(raw_get.get('start', 0))
        draw = raw_get.get('draw', 0)
        length = int(raw_get.get('length', 10))

        sub_query = Q()
        sub_query.add(Q(create_time__contains=search_value), Q.OR)
        sub_query.add(Q(approve_time__contains=search_value), Q.OR)
        sub_query.add(Q(title__icontains=search_value), Q.OR)
        sub_query.add(Q(state__workflow__name__icontains=search_value), Q.OR)
        sub_query.add(Q(state_value__icontains=search_value), Q.OR)
        sub_query.add(Q(creator__username__icontains=search_value), Q.OR)

        all_query = WorkflowStateEvent.objects.select_related('creator').select_related('state').filter(
            Q(approve_user=request.user) & sub_query).order_by('-create_time')

        raw_data = all_query[start: start + length]
        recordsTotal = all_query.count()
        data = {
            "data": [i.show_approve() for i in raw_data], 'draw': draw,
            'recordsTotal': recordsTotal, 'recordsFiltered': recordsTotal
        }
        return JsonResponse(data)


def game_server_list(request):
    '区服列表页面'
    if request.method == "GET":
        head = {'value': '区服列表', 'username': request.user.username}
        all_project_id = [x['project'] for x in GameServer.objects.values('project').annotate(dcount=Count('project'))]
        all_project = [{'id': x.id, 'text': x.project_name} for x in GameProject.objects.filter(id__in=all_project_id)]
        all_srv_status = dict(GameServer.STATUS)
        all_room = [{'id': x.id, 'text': x.area.chinese_name + '-' + x.room_name} for x in Room.objects.all()]
        all_game_type = [
            {'id': x.id, 'text': x.project.project_name + '-' + x.game_type_text} for x in GameServerType.objects.all()
        ]
        all_area = Area.objects.all()
        if request.user.is_superuser:
            is_superuser = json.dumps(True)
        else:
            is_superuser = json.dumps(False)
        return render(request, 'game_server_list.html', {
            'head': head, 'all_project': all_project, 'all_room': all_room,
            'all_srv_status': all_srv_status, 'all_game_type': all_game_type, 'is_superuser': is_superuser,
            'all_area': all_area})


def game_server_type(request):
    """游戏区服类型
    """
    if request.method == "GET":
        if request.user.is_superuser:
            head = {'value': '区服类型', 'username': request.user.username}
            return render(request, 'game_server_type.html', {"head": head})
        else:
            return render(request, '403.html')


def data_game_server_type(request):
    """游戏区服类型数据
    """

    if request.method == "GET":
        if request.user.is_superuser:
            raw_get = request.GET.dict()
            # search_value = raw_get.get('search[value]', '')
            # start = int(raw_get.get('start', 0))
            draw = raw_get.get('draw', 0)
            # length = int(raw_get.get('length', 10))

            raw_data = ''

            recordsTotal = GameServerType.objects.count()
            raw_data = GameServerType.objects.all()
            # recordsFiltered = recordsTotal
            data = {"data": [i.show_all() for i in raw_data], 'draw': draw, 'recordsTotal': recordsTotal,
                    'recordsFiltered': recordsTotal}
            return JsonResponse(data)


def add_or_edit_game_server_type(request):
    """添加或者修改区服类型
    """
    if request.method == "POST":
        raw_data = json.loads(request.body.decode('utf-8'))
        msg = 'ok'
        editFlag = raw_data.pop('editFlag')
        id = raw_data.pop('id', '0')
        try:
            project = raw_data.get('project', '0')
            project = GameProject.objects.get(id=project)
            raw_data['project'] = project
            if editFlag:
                gst = GameServerType.objects.filter(id=id)
                gst.update(**raw_data)
                success = True
            else:
                GameServerType.objects.create(**raw_data)
                success = True
        except GameServerType.DoesNotExist:
            msg = '找不到游戏区服类型'
            success = False
        except GameProject.DoesNotExist:
            msg = '游戏项目不存在'
            success = False
        except IntegrityError:
            msg = '记录有重新'
            success = False
        return JsonResponse({'data': success, 'msg': msg})


def get_game_server_type(request):
    """获取游戏区服类型
    """
    if request.method == "POST":
        if request.user.is_superuser:
            id = json.loads(request.body.decode('utf-8')).get('id', '0')
            obj = GameServerType.objects.get(id=id)
            edit_data = obj.edit_data()

            return JsonResponse(edit_data)
        else:
            raise PermissionDenied


def del_game_server_type(request):
    """删除游戏区服类型
    """
    if request.method == "POST":
        try:
            if request.user.is_superuser:
                with transaction.atomic():
                    del_data = json.loads(request.body.decode('utf-8'))
                    objs = GameServerType.objects.filter(id__in=del_data)
                    objs.delete()

                success = True
                msg = 'ok'
            else:
                raise PermissionDenied
        except PermissionDenied:
            msg = '权限拒绝'
            success = False
        except Exception as e:
            msg = str(e)
            success = False

        return JsonResponse({'data': success, 'msg': msg})


def game_server_list_api(request):
    '区服列表api文档'
    if request.method == "GET":
        if request.user.is_superuser:
            return render(request, 'gameserver.html')
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


def game_server_ops_manager_lock(request):
    """项目地区锁页面
    """

    if request.method == "GET":
        if request.user.is_superuser:
            head = {"value": "项目地区锁", "username": request.user.username}
            data = dict(OpsManager.STATUS)
            return render(request, 'project_area_lock.html', {"head": head, "data": data})
        else:
            return render(request, '403.html')


def data_project_area_lock(request):
    """项目地区锁数据
    """

    raw_get = request.GET.dict()
    draw = raw_get.get('draw', 0)

    raw_data = ''

    if request.method == "GET":
        list_id = [x['id'] for x in
                   OpsManager.objects.select_related('room').values('project', 'room__area__chinese_name',
                                                                    'url').annotate(id=Max('id'))]
        query = OpsManager.objects.filter(id__in=list_id)
        recordsTotal = query.count()
        raw_data = query.all()
        data = {"data": [i.show_lock() for i in raw_data], 'draw': draw, 'recordsTotal': recordsTotal,
                'recordsFiltered': recordsTotal}
        return JsonResponse(data)


def get_one_project_area_lock(request):
    """获取项目地区锁
    """

    if request.method == "POST":
        id = json.loads(request.body.decode('utf-8')).get('id')
        ops_manager = OpsManager.objects.get(id=id)
        edit_data = ops_manager.show_lock()
        return JsonResponse(edit_data)


def edit_one_project_area_lock(request):
    """修改项目地区lock
    """
    if request.method == "POST":
        msg = "ok"
        raw_data = json.loads(request.body.decode('utf-8'))
        id = raw_data.get('id')
        ops_manager = OpsManager.objects.get(id=id)

        status = raw_data.get('status')

        list_ops_manager = OpsManager.objects.filter(url__icontains=ops_manager.url)

        update_data = {"status": status}

        list_ops_manager.update(**update_data)
        success = True

        return JsonResponse({'data': success, 'msg': msg})


def hot_client_list(request):
    """前端热更新任务页面
    """

    if request.method == "GET":
        if request.user.is_superuser:
            head = {"value": "前端热更新任务", "username": request.user.username}
            priority = dict(ClientHotUpdate.PRIORITY)
            status = dict(ClientHotUpdate.STATUS)
            data = {"priority": priority, "status": status}
            return render(request, 'hot_client_list.html', {"head": head, "data": data})
        else:
            return render(request, '403.html')


def hot_server_list(request):
    """后端热更新任务页面
    """

    if request.method == "GET":
        head = {"value": "热更新任务", "username": request.user.username}
        all_project = [{'id': x.id, 'text': x.project_name} for x in get_gamserver_project()]
        priority = dict(ServerHotUpdate.PRIORITY)
        status = dict(ServerHotUpdate.STATUS)
        data = {"priority": priority, "status": status, "all_project": all_project}
        if request.user.is_superuser:
            is_superuser = json.dumps(True)
        else:
            is_superuser = json.dumps(False)
        client_cnt = ClientHotUpdate.objects.filter(status='4').count()
        server_cnt = ServerHotUpdate.objects.filter(status='4').count()
        sum = client_cnt + server_cnt
        if sum > 0:
            msg = '有待更新状态的热更新任务，鼠标移到待更新按钮上查看原因，若已更新完成，请忽略此信息！'
        else:
            msg = ''
        return render(request, 'hot_server_list.html',
                      {"head": head, "data": data, "is_superuser": is_superuser, 'msg': msg})


def host_server_detail(request):
    """后端热更新的详细
    """

    if request.method == "GET":
        id = request.GET.get('id')
        hot_server = ServerHotUpdate.objects.get(id=id)
        if request.user.is_superuser or request.user.id == hot_server.applicant.id:
            title = hot_server.title
            head = {"value": title, "username": request.user.username}
            return render(request, 'hot_server_detail.html', {"head": head})
        else:
            return render(request, '403.html')


def data_host_server_detail(request):
    if request.method == "POST":
        raw_get = request.POST.dict()
        hot_server_id = raw_get.get('hot_server_id')
        hot_server = ServerHotUpdate.objects.get(id=hot_server_id)
        if request.user.is_superuser or request.user.id == hot_server.applicant.id:
            draw = raw_get.get('draw', 0)
            # update_server_list = hot_server.show_detail()
            # 如果是更新完成，则从db中读取，不然在redis中读取
            if hot_server.final_result is not None:
                result_update_file_list = json.loads(hot_server.result_update_file_list)
            else:
                result_update_file_list = get_uuid_related_value(hot_server.uuid)
            recordsTotal = len(result_update_file_list)
            data = {
                "data": result_update_file_list, 'draw': draw,
                'recordsTotal': recordsTotal, 'recordsFiltered': recordsTotal
            }
            return JsonResponse(data)


def get_hot_server_process(request):
    """获取后端热更新进度
    """
    if request.method == "GET":
        id = request.GET.get('id')
        hot_server = ServerHotUpdate.objects.get(id=id)

        # 如果完成
        if hot_server.final_result is not None:
            result = hot_server.get_detail_data()
        else:
            # 如果没有完成，从redis中读取
            result = get_hot_server_process_from_redis(hot_server.uuid)

        return JsonResponse(result)


def get_hot_server_task(request):
    """获取前端热更新数据
    """

    if request.method == "POST":
        raw_data = json.loads(request.body.decode('utf-8'))
        id = raw_data.get('id')
        update_type = raw_data.get('update_type')
        if update_type == '前端':
            obj = ClientHotUpdate
        elif update_type == '后端':
            obj = ServerHotUpdate
        else:
            raise Exception('未知的热更新类型')
        hot_obj = obj.objects.get(id=id)
        edit_data = hot_obj.show_task()
        return JsonResponse(edit_data)


def get_hot_client_task(request):
    """获取后端热更新数据
    """

    if request.method == "POST":
        id = json.loads(request.body.decode('utf-8')).get('id')
        hot_client = ClientHotUpdate.objects.get(id=id)
        edit_data = hot_client.show_task()
        return JsonResponse(edit_data)


def edit_hot_client_task(request):
    """编辑热更新任务
    """
    if request.method == "POST":
        msg = "ok"
        raw_data = json.loads(request.body.decode('utf-8'))
        id = raw_data.get('id')
        priority = raw_data.get('priority')
        status = raw_data.get('status')

        hot_client = ClientHotUpdate.objects.get(id=id)

        # 对于已经完成的前端热更新，不能修改优先级和状态
        if hot_client.status == '3':
            pass
        else:
            hot_client.priority = priority
            hot_client.status = status

        # 测试情况，可以修改
        hot_client.priority = priority
        hot_client.status = status

        hot_client.save()

        success = True

        return JsonResponse({'data': success, 'msg': msg})


def edit_hot_server_task(request):
    """编辑热更新任务
    """
    if request.method == "POST":
        msg = "ok"
        raw_data = json.loads(request.body.decode('utf-8'))
        id = raw_data.get('id')
        priority = raw_data.get('priority')
        status = raw_data.get('status')
        update_type = raw_data.get('update_type')

        if update_type == "前端":
            obj = ClientHotUpdate
        elif update_type == '后端':
            obj = ServerHotUpdate
        else:
            success = False
            msg = '未知的热更新类型'
            return JsonResponse({'data': success, 'msg': msg})

        hot_obj = obj.objects.get(id=id)

        # 对于已经完成的前端热更新，不能修改优先级和状态
        if hot_obj.status == '3':
            pass
        else:
            hot_obj.priority = priority
            hot_obj.status = status

        # 测试情况，可以修改
        hot_obj.priority = priority
        hot_obj.status = status

        hot_obj.save()

        success = True

        return JsonResponse({'data': success, 'msg': msg})


def execute_hot_client_task(request):
    """执行前端热更新任务
    """
    if request.method == "POST":
        if request.user.is_superuser:
            try:
                msg = 'ok'
                success = False
                raw_data = json.loads(request.body.decode('utf-8'))
                id = raw_data.get('id')

                hot_client = ClientHotUpdate.objects.get(id=id)

                # 暂停的优先级不能执行
                if hot_client.priority == '3':
                    raise Exception('暂停状态，不能执行')

                # 只有状态为2,4也就是更新失败或者待更新的任务才可以执行
                if hot_client.status in ['2', '4']:
                    hot_client.status = '1'
                    hot_client.save()
                    success = True
                    do_hot_client.delay(0, hot_client.id, 'hot_client')
                elif hot_client.status == '0':
                    raise Exception('不能执行未处理的任务')
                elif hot_client.status == '1':
                    raise Exception('更新中，不能执行')
                elif hot_client.status == '3':
                    raise Exception('更新成功，不需要执行')
                else:
                    raise Exception('状态不对，不能执行')
            except ClientHotUpdate.DoesNotExist:
                msg = '没有找到该任务'
            except Exception as e:
                msg = str(e)

            return JsonResponse({"success": success, "msg": msg})


def execute_hot_server_task(request):
    """执行热更新任务
    """
    if request.method == "POST":
        if request.user.is_superuser:
            try:
                msg = 'ok'
                success = False
                raw_data = json.loads(request.body.decode('utf-8'))
                id = raw_data.get('id')
                update_type = raw_data.get('update_type')

                if update_type == '前端':
                    obj = ClientHotUpdate
                elif update_type == '后端':
                    obj = ServerHotUpdate
                else:
                    raise Exception('未知的热更新类型')

                hot_obj = obj.objects.get(id=id)

                # 暂停的优先级不能执行
                if hot_obj.priority == '3':
                    raise Exception('暂停状态，不能执行')

                # 只有待更新状态才能开始执行
                if hot_obj.status == '4':
                    do_hot_update(hot_obj)
                    success = True
                else:
                    raise Exception('状态不是待更新，不能执行')
            except ServerHotUpdate.DoesNotExist:
                msg = '没有找到该任务'
            except ClientHotUpdate.DoesNotExist:
                msg = '没有找到该任务'
            except Exception as e:
                traceback.print_exc()
                msg = str(e)

            return JsonResponse({"success": success, "msg": msg})


def myhotupdate(request):
    """某个热更新的具体详细
    """
    if request.method == "GET":
        id = request.GET.get('id', None)
        if id is None:
            head = {'value': '我的热更新申请工单汇总', 'username': request.user.username}
            return render(request, 'myhotupdate_all.html', {'head': head})
        else:
            content_object = WorkflowStateEvent.objects.get(id=id).content_object
            if request.user == content_object.creator:
                if content_object.status == '0':
                    return HttpResponse('你的工单还没有审批完成,不能执行')
                head = {'title': content_object.title, 'username': request.user.username}
                return render(request, 'myhotupdate.html', {'head': head})
            else:
                return render(request, '403.html')


def data_myhotupdate(request):
    """某个热更新的数据
    """

    if request.method == "POST":
        raw_get = request.POST.dict()
        id = raw_get.get('id', None)
        if id is None:
            search_value = raw_get.get('search[value]', '')
            start = int(raw_get.get('start', 0))
            draw = raw_get.get('draw', 0)
            length = int(raw_get.get('length', 10))

            # 热更新的类型
            hotupdate_ctype_list = ContentType.objects.filter(model__in=['clienthotupdate', 'serverhotupdate'])

            sub_query = Q()

            sub_query.add(Q(title__icontains=search_value), Q.OR)
            sub_query.add(Q(create_time__contains=search_value), Q.OR)
            sub_query.add(Q(state__workflow__name__icontains=search_value), Q.OR)
            sub_query.add(Q(state__name__icontains=search_value), Q.OR)
            sub_query.add(Q(state_value__icontains=search_value), Q.OR)

            query = WorkflowStateEvent.objects.select_related('state').select_related(
                'state__workflow').filter(Q(is_current=True) & Q(creator=request.user) & Q(
                content_type__in=hotupdate_ctype_list) & sub_query).order_by('-create_time')

            raw_data = query[start: start + length]
            recordsTotal = query.count()
            data = {"data": [i.show_all() for i in raw_data], 'draw': draw,
                    'recordsTotal': recordsTotal, 'recordsFiltered': recordsTotal}
        else:
            draw = raw_get.get('draw', 0)
            content_object = WorkflowStateEvent.objects.get(id=id).content_object
            query = [content_object]
            raw_data = query
            data = {"data": [i.show_task() for i in raw_data], 'draw': draw, 'recordsTotal': 1, 'recordsFiltered': 1}
        return JsonResponse(data)


def data_myhotupdate_block(request):
    """某个热更新的之前阻塞的任务
    用来查看任务队列的阻塞情况
    """
    if request.method == "POST":
        raw_get = request.POST.dict()
        id = raw_get.get('id')
        draw = raw_get.get('draw', 0)
        content_object = WorkflowStateEvent.objects.get(id=id).content_object

        # 如果本次更新成功或者暂停执行，不用返回数据
        if content_object.status == '3' or content_object.priority == '3':
            data = {"data": [], 'draw': draw, 'recordsTotal': 0, 'recordsFiltered': 0}
            return JsonResponse(data)

        list_hot_update = []

        project = content_object.project
        area_name = content_object.area_name

        # 前端热更新根据项目地区排除掉状态为3(也就是更新成功)或者优先级为3(也就是暂停的工单)
        list_hot_client = ClientHotUpdate.objects.filter(
            project=project, area_name=area_name).exclude(Q(status=3) | Q(priority=3))
        # 后端热更新根据项目地区排除掉状态为3(也就是更新成功)或者优先级为3(也就是暂停的工单)
        list_hot_server = ServerHotUpdate.objects.filter(
            project=project, area_name=area_name).exclude(Q(status=3) | Q(priority=3))

        # 合并这两个工单
        list_hot_update.extend(list_hot_client)
        list_hot_update.extend(list_hot_server)

        # 按照排序算法找出第一个工单
        list_hot_update = sorted(list_hot_update, key=lambda obj: obj.create_time)
        list_hot_update = sorted(list_hot_update, key=lambda obj: obj.priority, reverse=True)

        # 找到本次的热更新在list_hot_update中的索引
        try:
            current_index = list_hot_update.index(content_object)
            raw_data = list_hot_update[:current_index]
        except ValueError:
            raw_data = []

        recordsTotal = len(raw_data)
        data = {"data": [i.show_task() for i in raw_data], 'draw': draw, 'recordsTotal': recordsTotal,
                'recordsFiltered': recordsTotal}
        return JsonResponse(data)


def data_hot_client_list(request):
    """前端热更新数据
    """
    if request.method == "POST":
        if request.user.is_superuser:
            raw_get = request.POST.dict()

            search_value = raw_get.get('search[value]', '')
            start = int(raw_get.get('start', 0))
            draw = raw_get.get('draw', 0)
            length = int(raw_get.get('length', 10))

            raw_data = ''

            # 添加sub_query
            # sub_query = Q()

            if search_value:
                pass
            else:
                query = ClientHotUpdate.objects.exclude(status='0').order_by('-create_time')
            raw_data = query[start: start + length]
            recordsTotal = query.count()
            # recordsFiltered = len(raw_data)
            data = {"data": [i.show_task() for i in raw_data], 'draw': draw, 'recordsTotal': recordsTotal,
                    'recordsFiltered': recordsTotal}
            return JsonResponse(data)


def data_hot_server_list(request):
    """热更新数据
    """
    if request.method == "POST":
        if True:
            raw_get = request.POST.dict()

            search_value = raw_get.get('search[value]', '')
            start = int(raw_get.get('start', 0))
            draw = raw_get.get('draw', 0)
            length = int(raw_get.get('length', 10))

            # 自定义的查询参数
            filter_hotupdate_type = raw_get.get('filter_hotupdate_type', '全部')
            filter_project = raw_get.get('filter_project', '全部')
            filter_area_name = raw_get.get('filter_area_name', '')
            filter_title = raw_get.get('filter_title', '')
            filter_priority = raw_get.get('filter_priority', '全部')
            filter_status = raw_get.get('filter_status', '全部')
            filter_start_time = raw_get.get('filter_start_time', '')
            filter_end_time = raw_get.get('filter_end_time', '')

            raw_data = ''

            # 添加sub_query
            sub_query = Q()

            # if filter_hotupdate_type == '前端':
            #     sub_query.add(Q(ctype=filter_ctype), Q.AND)

            if filter_project != '全部':
                sub_query.add(Q(project=GameProject.objects.get(id=filter_project)), Q.AND)

            if filter_area_name:
                sub_query.add(Q(area_name__icontains=filter_area_name), Q.AND)

            if filter_title:
                sub_query.add(Q(title__icontains=filter_title), Q.AND)

            if filter_priority != '全部':
                sub_query.add(Q(priority=filter_priority), Q.AND)

            if filter_status != '全部':
                sub_query.add(Q(status=filter_status), Q.AND)

            if filter_start_time:
                sub_query.add(Q(create_time__gte=filter_start_time), Q.AND)

            if filter_end_time:
                sub_query.add(Q(create_time__lte=filter_end_time), Q.AND)

            if not sub_query:
                today = datetime.now()
                thirty_days_ago = timedelta(days=30)
                interval = (today - thirty_days_ago).strftime('%Y-%m-%d %H:%M')
                sub_query.add(Q(create_time__gte=interval), Q.AND)

            # 添加全局搜索
            global_query = Q()
            if search_value:
                STATUS_DIC = dict((v, k) for k, v in ServerHotUpdate.STATUS)
                PRIORITY_DIC = dict((v, k) for k, v in ServerHotUpdate.PRIORITY)
                status_list = [
                    v for k, v in STATUS_DIC.items() if (k.startswith(search_value) or k.endswith(search_value))
                ]
                priority_list = [
                    v for k, v in PRIORITY_DIC.items() if (k.startswith(search_value) or k.endswith(search_value))
                ]
                global_query.add(Q(project__project_name__icontains=search_value), Q.OR)
                global_query.add(Q(area_name__icontains=search_value), Q.OR)
                global_query.add(Q(title__icontains=search_value), Q.OR)
                global_query.add(Q(priority__in=priority_list), Q.OR)
                global_query.add(Q(status__in=status_list), Q.OR)

            # 第三版查询方法

            if filter_hotupdate_type == '前端':
                reversed_hot_server_iter = ServerHotUpdate.objects.none()
                reversed_hot_client_iter = ClientHotUpdate.objects.select_related(
                    'project').exclude(status='0').filter(global_query & sub_query).order_by('-create_time')
                hot_server_count = 0
                hot_client_count = len(reversed_hot_client_iter)
            elif filter_hotupdate_type == '后端':
                reversed_hot_client_iter = ClientHotUpdate.objects.none()
                reversed_hot_server_iter = ServerHotUpdate.objects.select_related(
                    'project').exclude(status='0').filter(global_query & sub_query).order_by('-create_time')
                hot_client_count = 0
                hot_server_count = len(reversed_hot_server_iter)
            else:
                reversed_hot_server_iter = ServerHotUpdate.objects.select_related(
                    'project').exclude(status='0').filter(global_query & sub_query).order_by('-create_time')
                reversed_hot_client_iter = ClientHotUpdate.objects.select_related(
                    'project').exclude(status='0').filter(global_query & sub_query).order_by('-create_time')
                hot_server_count = len(reversed_hot_server_iter)
                hot_client_count = len(reversed_hot_client_iter)

            heapq_merge = heapq.merge(
                reversed_hot_server_iter, reversed_hot_client_iter, key=lambda obj: obj.create_time, reverse=True)

            raw_data = islice(heapq_merge, start, start + length)

            recordsTotal = hot_server_count + hot_client_count
            data = {"data": [i.show_task() for i in raw_data], 'draw': draw, 'recordsTotal': recordsTotal,
                    'recordsFiltered': recordsTotal}
            return JsonResponse(data)


def data_game_server_list(request):
    """区服列表页面数据"""
    if request.method == 'POST':
        raw_get = request.POST.dict()
        search_value = raw_get.get('search[value]', '')
        start = int(raw_get.get('start', 0))
        draw = raw_get.get('draw', 0)
        length = int(raw_get.get('length', 10))

        raw_data = ''

        filter_project_type = raw_get.get('filter_project_type', '')
        filter_project = raw_get.get('filter_project', '')
        filter_srv_status = raw_get.get('filter_srv_status', '')
        filter_game_type = raw_get.get('filter_game_type', '')
        filter_pf_name = raw_get.get('filter_pf_name', '')
        filter_srv_id = raw_get.get('filter_srv_id', '')
        filter_srv_name = raw_get.get('filter_srv_name', '')
        filter_room = raw_get.get('filter_room', '')
        filter_internal_ip = raw_get.get('filter_internal_ip', '')
        filter_telecom_ip = raw_get.get('filter_telecom_ip', '')
        filter_unicom_ip = raw_get.get('filter_unicom_ip', '')
        filter_merge_id = raw_get.get('filter_merge_id', '')
        filter_merge_time = raw_get.get('filter_merge_time', '')
        filter_client_version = raw_get.get('filter_client_version', '')
        filter_server_version = raw_get.get('filter_server_version', '')
        filter_cdn_root_url = raw_get.get('filter_cdn_root_url', '')
        filter_cdn_dir = raw_get.get('filter_cdn_dir', '')
        filter_open_time = raw_get.get('filter_open_time', '')
        filter_area_name = raw_get.get('filter_area_name', '')
        filter_master_server = json.loads(raw_get.get('filter_master_server'))
        filter_sid = raw_get.get('filter_sid', '')
        filter_project2 = raw_get.get('filter_project2', '')
        filter_srv_status2 = request.POST.getlist('filter_srv_status2[]', '100')
        filter_room2 = raw_get.get('filter_room2', '')

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
            sub_query.add(Q(project__in=projects_obj_list), Q.OR)

        if filter_project_type != '100':
            sub_query.add(Q(project_type=filter_project_type), Q.AND)

        if filter_project != '0':
            sub_query.add(Q(project=GameProject.objects.get(id=filter_project)), Q.AND)

        if filter_srv_status != '100':
            sub_query.add(Q(srv_status=filter_srv_status), Q.AND)

        if filter_game_type != '0':
            sub_query.add(Q(game_type=GameServerType.objects.get(id=filter_game_type)), Q.AND)

        if filter_pf_name:
            sub_query.add(Q(pf_name__icontains=filter_pf_name), Q.AND)

        if filter_srv_id:
            sub_query.add(Q(srv_id__icontains=filter_srv_id), Q.AND)

        if filter_srv_name:
            sub_query.add(Q(srv_name__icontains=filter_srv_name), Q.AND)

        if filter_room != '0':
            sub_query.add(Q(room=Room.objects.get(id=filter_room)), Q.AND)

        if filter_internal_ip:
            sub_query.add(Q(host__internal_ip__icontains=filter_internal_ip), Q.AND)

        if filter_telecom_ip:
            sub_query.add(Q(host__telecom_ip__icontains=filter_telecom_ip), Q.AND)

        if filter_unicom_ip:
            sub_query.add(Q(host__unicom_ip__icontains=filter_unicom_ip), Q.AND)

        if filter_merge_id:
            sub_query.add(Q(merge_id__icontains=filter_merge_id), Q.AND)

        if filter_merge_time:
            sub_query.add(Q(merge_time__contains=filter_merge_time), Q.AND)

        if filter_client_version:
            sub_query.add(Q(client_version__icontains=filter_client_version), Q.AND)

        if filter_server_version:
            sub_query.add(Q(server_version__icontains=filter_server_version), Q.AND)

        if filter_cdn_root_url:
            sub_query.add(Q(cdn_root_url__icontains=filter_cdn_root_url), Q.AND)

        if filter_cdn_dir:
            sub_query.add(Q(cdn_dir__icontains=filter_cdn_dir), Q.AND)

        if filter_open_time:
            sub_query.add(Q(open_time__contains=filter_open_time), Q.AND)

        if filter_area_name != '0':
            sub_query.add(Q(host__belongs_to_room__area__chinese_name__icontains=filter_area_name), Q.AND)

        if filter_master_server:
            sub_query.add(Q(merge_id=None), Q.AND)

        if filter_sid != '':
            sub_query.add(Q(sid__contains=filter_sid), Q.AND)

        if filter_project2 != '0':
            sub_query.add(Q(project=GameProject.objects.get(id=filter_project2)), Q.AND)

        if filter_srv_status2 != '100':
            sub_query.add(Q(srv_status__in=filter_srv_status2), Q.AND)

        if filter_room2 != '0':
            sub_query.add(Q(room=Room.objects.get(id=filter_room2)), Q.AND)

        if search_value:
            PTYPE_DIC = dict((v, k) for k, v in GameServer.PTYPE)
            ptype_list = [
                v for k, v in PTYPE_DIC.items() if (k.startswith(search_value) or k.endswith(search_value))
            ]

            STATUS_DIC = dict((v, k) for k, v in GameServer.STATUS)
            srv_status_list = [
                v for k, v in STATUS_DIC.items() if (k.startswith(search_value) or k.endswith(search_value))
            ]
            search_value = search_value.split('-')[-1]
            query = GameServer.objects.select_related(
                'project').select_related(
                'host').select_related(
                'room').filter((
                                       Q(project_type__in=ptype_list) |
                                       Q(project__project_name__icontains=search_value) |
                                       Q(room__room_name__icontains=search_value) |
                                       Q(game_type__game_type_code__icontains=search_value) |
                                       Q(srv_status__in=srv_status_list) |
                                       Q(pf_name__icontains=search_value) |
                                       Q(srv_id__icontains=search_value) |
                                       Q(srv_name__icontains=search_value) |
                                       Q(ip__icontains=search_value) |
                                       Q(host__telecom_ip__icontains=search_value) |
                                       Q(host__unicom_ip__icontains=search_value) |
                                       Q(merge_id__icontains=search_value) |
                                       Q(merge_time__contains=search_value) |
                                       Q(client_version__icontains=search_value) |
                                       Q(server_version__icontains=search_value) |
                                       Q(cdn_root_url__icontains=search_value) |
                                       Q(cdn_dir__icontains=search_value) |
                                       Q(open_time__contains=search_value) |
                                       Q(host__belongs_to_room__area__chinese_name__icontains=search_value) |
                                       Q(sid__icontains=search_value)) & sub_query).order_by('project', '-id')
        else:
            query = GameServer.objects.select_related(
                'project').select_related(
                'host').select_related(
                'room').filter(sub_query).order_by('project', '-id')

        raw_data = query[start: start + length]
        recordsTotal = query.count()

        data = {
            "data": [i.show_all() for i in raw_data], 'draw': draw,
            'recordsTotal': recordsTotal, 'recordsFiltered': recordsTotal
        }
        return JsonResponse(data)


def workflow_approve(request):
    """审批页面

    有两种情况下用户可以打开审批页面
    1、申请的当前state下的用户
    2、用户之前审批过，仍然可以打开，但是不能继续审批
    """

    if request.method == "GET":
        id = request.GET.get('id')
        wse = WorkflowStateEvent.objects.get(id=id)

        workflow = wse.state.workflow

        # 获取申请的当前节点
        state_user = is_state_user(wse, request.user)

        # 已经审批过的用户
        approved_user = has_approved_user(wse, request.user)

        if state_user or approved_user:
            if workflow.name == 'SVN申请':

                if wse.state_value:
                    has_approved = True
                else:
                    has_approved = False

                creator = wse.content_object.creator
                applicant = wse.content_object.applicant

                """2018.12修改，合并部门和部门管理分组"""
                org = OrganizationMptt.objects.get(user_id=wse.content_object.applicant.id)
                belongs_to_new_organization = org.get_ancestors_except_self()

                svn_scheme_id = wse.content_object.svn_scheme.id if wse.content_object.svn_scheme else '0'
                svn_scheme = wse.content_object.svn_scheme.name if wse.content_object.svn_scheme else '没有选择svn方案'
                project = wse.content_object.project.project_name
                title = wse.content_object.title
                reason = wse.content_object.reason if wse.content_object.reason else ''
                state_value = wse.state_value
                content = json.loads(wse.content_object.content)
                opinion = wse.opinion
                process_info = get_state_process(wse)

                # 增加运维执行按钮
                if wse.state.name == '运维':
                    can_execute = True
                else:
                    can_execute = False

                # 获取该state下所有的transition
                transitions = wse.state.transition.order_by('name')

                head = {"value": '审批', 'wse': id, 'username': request.user.username}

                data = {
                    'creator': creator,
                    'applicant': applicant,
                    'group': belongs_to_new_organization,
                    'group_section': belongs_to_new_organization,
                    'svn_scheme_id': svn_scheme_id,
                    'svn_scheme': svn_scheme,
                    'project': project,
                    'title': title,
                    'reason': reason,
                    'content': content,
                    'state_value': state_value,
                    'opinion': opinion,
                    'process_info': process_info,
                    'has_approved': has_approved,
                    'can_execute': can_execute,
                }

                return render(request,
                              'svn_workflow_approve.html', {'head': head, 'data': data, 'transitions': transitions})
            if workflow.name == '服务器权限申请':

                if wse.state_value:
                    has_approved = True
                else:
                    has_approved = False

                project_id = wse.content_object.project.id
                project_name = wse.content_object.project.project_name

                applicant = wse.content_object.applicant

                title = wse.content_object.title
                reason = wse.content_object.reason

                state_value = wse.state_value

                key = wse.content_object.key
                is_root = wse.content_object.is_root

                room_id = wse.content_object.room.id if wse.content_object.room else '0'
                room_name = wse.content_object.room.room_name if wse.content_object.room else '选择机房'

                ips_value = wse.content_object.ips
                ips = json.loads(ips_value)

                # 这里需要做一些兼容，以前的工单没有起止时间
                # 如果没有的话，就以Unix Time的开始时间来表示
                if wse.content_object.start_time:
                    start_time = wse.content_object.start_time.strftime('%Y-%m-%d %H:%M')
                else:
                    start_time = "1970-1-1 00:00"

                if wse.content_object.end_time:
                    end_time = wse.content_object.end_time.strftime('%Y-%m-%d %H:%M')
                else:
                    end_time = "1970-1-1 00:00"

                temporary = wse.content_object.temporary

                group = wse.content_object.group

                all_ip = wse.content_object.all_ip

                # # 申请人部门，如果有的话，没有为空
                # if applicant.groups.all():
                #     one_group = applicant.groups.all()[0].name
                # else:
                #     one_group = ''
                #
                # # 申请人的部门管理分组
                # if applicant.profile.group_section is not None:
                #     group_section = applicant.profile.group_section.name
                # else:
                #     group_section = '没有分配到管理分组'
                org = OrganizationMptt.objects.get(user=applicant)
                one_group = org.get_ancestors_except_self()

                # 获取该state下所有的transition
                transitions = wse.state.transition.order_by('name')

                head = {"value": '审批', 'wse': wse.id, 'username': request.user.username}

                data = {
                    'project_id': project_id,
                    'project_name': project_name,
                    'applicant': applicant,
                    'one_group': one_group,
                    # 'group_section': group_section,
                    'title': title,
                    'reason': reason,
                    'state_value': state_value,
                    'key': key,
                    'is_root': is_root,
                    'room_id': room_id,
                    'room_name': room_name,
                    'ips': ips,
                    'all_ip': all_ip,
                    'start_time': start_time,
                    'end_time': end_time,
                    'temporary': temporary,
                    'group': group,
                    'has_approved': has_approved,
                }

                return render(request,
                              'ser_perm_workflow_approve.html',
                              {'head': head, 'data': data, 'transitions': transitions})

            if workflow.name == "电脑故障申报":
                if wse.state_value:
                    has_approved = True
                else:
                    has_approved = False

                if wse.content_object.status == 0:
                    has_handle = True
                else:
                    has_handle = False

                creator = wse.content_object.creator
                applicant = wse.content_object.applicant
                title = wse.content_object.title
                classification = wse.content_object.get_classification_display()
                content = wse.content_object.content
                state_value = wse.state_value
                transition_status = wse.state.name

                transitions = wse.state.transition.order_by('name')

                head = {"value": '审批', 'wse': id, 'username': request.user.username}

                data = {
                    'creator': creator,
                    'applicant': applicant,
                    'title': title,
                    'classification': classification,
                    'content': content,
                    'has_approved': has_approved,
                    'state_value': state_value,
                    'has_handle': has_handle,
                    'transition_status': transition_status,
                }

                return render(request,
                              'failure_decalre_workflow_approve.html',
                              {'head': head, 'data': data, 'transitions': transitions})

            if isinstance(wse.content_object, ClientHotUpdate):
                if wse.state_value:
                    has_approved = True
                else:
                    has_approved = False

                content_object = wse.content_object
                project_name_en = content_object.project.project_name_en
                applicant = content_object.applicant
                title = content_object.title
                reason = content_object.reason
                attention = content_object.attention
                project = content_object.project.project_name
                area_name = content_object.area_name + content_object.rsync_area_name
                client_version = content_object.client_version
                content = json.loads(content_object.content)
                pair_code = content_object.pair_code if content_object.pair_code else '无'
                order = content_object.order if content_object.order else '无'
                update_file_list = hot_update_file_list_to_string(json.loads(content_object.update_file_list))
                transitions = wse.state.transition.order_by('name')
                state_value = wse.state_value

                data = {
                    'applicant': applicant,
                    'title': title,
                    'reason': reason,
                    'attention': attention,
                    'project': project,
                    'area_name': area_name,
                    'client_version': client_version,
                    'content': content,
                    'state_value': state_value,
                    'has_approved': has_approved,
                    'pair_code': pair_code,
                    'order': order,
                    'update_file_list': update_file_list,
                }

                head = {'value': title, 'wse': id, 'username': request.user.username}
                html_template = project_name_en + '_client_hot_update_workflow_approve.html'
                client_hotupdate_template = content_object.project.get_client_hotupdate_template(tag=True)
                if client_hotupdate_template:
                    return render(request, client_hotupdate_template + '_client_hot_update_workflow_approve.html',
                                  {'data': data, 'head': head, 'transitions': transitions})
                try:
                    return render(request, html_template, {'data': data, 'head': head, 'transitions': transitions})
                except:
                    return render(request, 'common_client_hot_update_workflow_approve.html',
                                  {'data': data, 'head': head, 'transitions': transitions})

            if isinstance(wse.content_object, ServerHotUpdate):
                if wse.state_value:
                    has_approved = True
                else:
                    has_approved = False

                content_object = wse.content_object
                project_name_en = content_object.project.project_name_en
                applicant = content_object.applicant
                title = content_object.title
                reason = content_object.reason
                attention = content_object.attention
                project = content_object.project.project_name
                area_name = content_object.area_name + content_object.rsync_area_name
                server_version = content_object.server_version
                hot_server_type = content_object.get_hot_server_type_display()
                hot_server_type_code = content_object.hot_server_type
                pair_code = content_object.pair_code if content_object.pair_code else '无'
                order = content_object.order if content_object.order else '无'
                state_value = wse.state_value
                on_new_server = content_object.serverhotupdatereplication.on_new_server

                transitions = wse.state.transition.order_by('name')

                if hot_server_type_code == '0':
                    # 只热更
                    show_file_list = True
                    show_erlang_list = False

                    update_file_list = hot_update_file_list_to_string(json.loads(content_object.update_file_list))
                    erlang_cmd_list = ""
                elif hot_server_type_code == '1':
                    # 先热更,再执行erl命令
                    show_file_list = True
                    show_erlang_list = True

                    update_file_list = hot_update_file_list_to_string(json.loads(content_object.update_file_list))
                    erlang_cmd_list = content_object.erlang_cmd_list
                elif hot_server_type_code == '2':
                    # 只执行erl命令
                    show_file_list = False
                    show_erlang_list = True

                    update_file_list = ""
                    erlang_cmd_list = content_object.erlang_cmd_list
                elif hot_server_type_code == '3':
                    # 先执行erl命令,再热更
                    show_file_list = True
                    show_erlang_list = True

                    update_file_list = hot_update_file_list_to_string(json.loads(content_object.update_file_list))
                    erlang_cmd_list = content_object.erlang_cmd_list
                else:
                    show_file_list = True
                    show_erlang_list = True

                    update_file_list = hot_update_file_list_to_string(json.loads(content_object.update_file_list))
                    erlang_cmd_list = content_object.erlang_cmd_list

                # update_server_list = hot_server_update_server_list_to_string(
                #     json.loads(content_object.update_server_list))
                update_server_list = hot_server_update_server_list_to_tree(
                    json.loads(content_object.update_server_list))

                data = {
                    'id': id,
                    'applicant': applicant,
                    'title': title,
                    'reason': reason,
                    'attention': attention,
                    'project': project,
                    'area_name': area_name,
                    'server_version': server_version,
                    'hot_server_type': hot_server_type,
                    'erlang_cmd_list': erlang_cmd_list,
                    'update_file_list': update_file_list,
                    'show_file_list': show_file_list,
                    'show_erlang_list': show_erlang_list,
                    'has_approved': has_approved,
                    'pair_code': pair_code,
                    'order': order,
                    'state_value': state_value,
                    'on_new_server': on_new_server,
                }

                head = {'value': title, 'wse': id, 'username': request.user.username}
                html_template = project_name_en + '_server_hot_update_workflow_approve.html'

                try:
                    return render(request, html_template, {
                        'data': data, 'head': head, 'transitions': transitions,
                        'update_server_list': update_server_list})
                except:
                    return render(request, 'common_server_hot_update_workflow_approve.html', {
                        'data': data, 'head': head, 'transitions': transitions,
                        'update_server_list': update_server_list})

            if isinstance(wse.content_object, Wifi):
                if wse.state_value:
                    has_approved = True
                else:
                    has_approved = False

                if wse.content_object.status == 0:
                    has_handle = True
                else:
                    has_handle = False

                if wse.content_object.wifi_add_result:
                    has_add_mac = True
                else:
                    has_add_mac = False

                creator = wse.content_object.creator
                applicant = wse.content_object.applicant
                title = wse.content_object.title
                name = wse.content_object.name
                reason = wse.content_object.reason
                mac = wse.content_object.mac
                state_value = wse.state_value
                transition_status = wse.state.name

                transitions = wse.state.transition.order_by('name')

                head = {"value": '审批', 'wse': id, 'username': request.user.username}

                data = {
                    'creator': creator,
                    'applicant': applicant,
                    'title': title,
                    'name': name,
                    'reason': reason,
                    'mac': mac,
                    'state_value': state_value,
                    'has_approved': has_approved,
                    'has_handle': has_handle,
                    'transition_status': transition_status,
                    'has_add_mac': has_add_mac,
                }

                return render(request,
                              'wifi_workflow_approve.html', {'head': head, 'data': data, 'transitions': transitions})

            if isinstance(wse.content_object, Machine):
                if wse.state_value:
                    has_approved = True
                else:
                    has_approved = False

                applicant = wse.content_object.applicant.username
                title = wse.content_object.title
                project = wse.content_object.project.project_name
                purpose = wse.content_object.purpose
                config = json.loads(wse.content_object.config)
                number = str(wse.content_object.number) + '台'
                ip_type = wse.content_object.get_ip_type_display()
                requirements = wse.content_object.requirements
                state_value = wse.state_value

                transitions = wse.state.transition.order_by('name')

                data = {
                    'id': id,
                    'applicant': applicant,
                    'title': title,
                    'project': project,
                    'purpose': purpose,
                    'config': config,
                    'number': number,
                    'ip_type': ip_type,
                    'requirements': requirements,
                    'state_value': state_value,
                    'has_approved': has_approved,
                }

                head = {"value": '审批', 'wse': id, 'username': request.user.username}

                return render(request,
                              'machine_workflow_approve.html', {'head': head, 'data': data, 'transitions': transitions})
            if isinstance(wse.content_object, ProjectAdjust):
                if wse.state_value:
                    has_approved = True
                else:
                    has_approved = False
                applicant = wse.content_object.applicant.username
                title = wse.content_object.title
                # raw_project_group_obj = wse.content_object.raw_project_group
                # if raw_project_group_obj:
                #     raw_project_group = raw_project_group_obj.project.project_name + '-' + raw_project_group_obj.name
                # else:
                #     raw_project_group = '没有项目分组'
                delete_svn = wse.content_object.delete_svn
                delete_serper = wse.content_object.delete_serper
                # if wse.content_object.new_group_section is not None:
                #     new_group_section_obj = wse.content_object.new_group_section
                #     new_group_section = new_group_section_obj.group.name + '-' + new_group_section_obj.name
                # else:
                #     new_group_section = ''
                """
                2018.12修改
                """
                if wse.content_object.new_department_group is not None:
                    new_department_group = wse.content_object.new_department_group.get_ancestors_name()
                else:
                    new_department_group = ''
                state_value = wse.state_value

                # 要删除的svn和服务器权限的项目
                if wse.content_object.svn_projects is None:
                    svn_projects_id = []
                else:
                    svn_projects_id = json.loads(wse.content_object.svn_projects)

                if wse.content_object.serper_projects is None:
                    serper_projects_id = []
                else:
                    serper_projects_id = json.loads(wse.content_object.serper_projects)

                svn_projects_obj = GameProject.objects.filter(id__in=svn_projects_id)
                serper_projects_obj = GameProject.objects.filter(id__in=serper_projects_id)

                svn_projects = [{'id': x.id, 'text': x.project_name} for x in svn_projects_obj]
                serper_projects = [{'id': x.id, 'text': x.project_name} for x in serper_projects_obj]

                transitions = wse.state.transition.order_by('name')
                data = {
                    'id': id,
                    'applicant': applicant,
                    'title': title,
                    # 'raw_project_group': raw_project_group,
                    'delete_svn': delete_svn,
                    'delete_serper': delete_serper,
                    'new_department_group': new_department_group,
                    'state_value': state_value,
                    'has_approved': has_approved,
                    'svn_projects': svn_projects,
                    'serper_projects': serper_projects,
                }
                head = {"value": '审批', 'wse': id, 'username': request.user.username}
                return render(request,
                              'project_adjust_workflow_approve.html',
                              {'head': head, 'data': data, 'transitions': transitions})

            if isinstance(wse.content_object, ComputerParts):
                if wse.state_value:
                    has_approved = True
                else:
                    has_approved = False

                if wse.content_object.status == 0:
                    has_handle = True
                else:
                    has_handle = False

                creator = wse.content_object.creator
                applicant = wse.content_object.applicant
                title = wse.content_object.title
                reason = wse.content_object.reason
                state_value = wse.state_value

                transitions = wse.state.transition.order_by('name')
                transition_status = wse.state.name

                head = {"value": '审批', 'wse': id, 'username': request.user.username}

                data = {
                    'creator': creator,
                    'applicant': applicant,
                    'title': title,
                    'reason': reason,
                    'state_value': state_value,
                    'has_approved': has_approved,
                    'transition_status': transition_status,
                    'has_handle': has_handle,
                }

                return render(request,
                              'computer_parts_workflow_approve.html',
                              {'head': head, 'data': data, 'transitions': transitions})
            if isinstance(wse.content_object, VersionUpdate):
                if wse.state_value:
                    has_approved = True
                else:
                    has_approved = False

                id = wse.id
                applicant = wse.content_object.applicant.username
                title = wse.content_object.title
                content = wse.content_object.content
                project = wse.content_object.project.project_name
                project_id = wse.content_object.project.id
                area = wse.content_object.area.chinese_name if wse.content_object.area else ''
                area_id = wse.content_object.area.id if wse.content_object.area else 0
                start_time = wse.content_object.start_time.strftime('%Y-%m-%d %H:%M:%S')
                end_time = wse.content_object.end_time.strftime('%Y-%m-%d %H:%M:%S')
                client_version = wse.content_object.client_version if wse.content_object.client_version else ''
                server_version = wse.content_object.server_version if wse.content_object.server_version else ''
                client_attention = wse.content_object.client_attention if wse.content_object.client_attention else ''
                client_content = json.loads(
                    wse.content_object.client_content) if wse.content_object.client_content else ''
                server_attention = wse.content_object.server_attention if wse.content_object.server_attention else ''
                server_list = wse.content_object.server_list
                server_content = wse.content_object.server_content if wse.content_object.server_content else ''
                server_exclude_content = wse.content_object.server_exclude_content if wse.content_object.server_exclude_content else ''
                # flag, server_list = wse.content_object.format_server_list()
                state_value = wse.state_value
                ask_reset = wse.content_object.get_ask_reset_display() if wse.content_object.ask_reset else 'no'
                server_range_text = wse.content_object.get_server_range_display() if wse.content_object.server_range else ''
                server_range = wse.content_object.server_range if wse.content_object.server_range else ''
                server_range_option = VersionUpdate.SERVER_RANGE
                on_new_server = wse.content_object.on_new_server
                server_erlang = wse.content_object.server_erlang if wse.content_object.server_erlang else ''

                # 如果是运维负责人审批节点，需要填写：
                # 1. 后端更新区服（全服、部分区服、排除区服），区服id，是否同步新服，是否区服重排
                # 2. 前端更新的cdn目录，版本号等
                if wse.state.name == '运维负责人':
                    if wse.state_value:
                        ops_edit = False
                    else:
                        ops_edit = True
                else:
                    ops_edit = False
                # 如果是后端负责人审批节点，需要填写版本号和更新注意事项
                if wse.state.name == '后端负责人':
                    if wse.state_value:
                        edit_server = False
                    else:
                        edit_server = True
                else:
                    edit_server = False
                # 如果是前端负责人审批节点，需要填写版本号和更新注意事项
                if wse.state.name == '前端负责人':
                    edit_client = True
                    if wse.state_value:
                        edit_client = False
                    else:
                        edit_client = True
                else:
                    edit_client = False

                data = {
                    'id': id,
                    'applicant': applicant,
                    'title': title,
                    'content': content,
                    'project': project,
                    'project_id': project_id,
                    'server_list': server_list,
                    'start_time': start_time,
                    'end_time': end_time,
                    'client_version': client_version,
                    'server_version': server_version,
                    'client_attention': client_attention,
                    'server_attention': server_attention,
                    'ops_edit': ops_edit,
                    'edit_server': edit_server,
                    'edit_client': edit_client,
                    'state_value': state_value,
                    'has_approved': has_approved,
                    'area': area,
                    'area_id': area_id,
                    'client_content': client_content,
                    'server_content': server_content,
                    'server_exclude_content': server_exclude_content,
                    'ask_reset': ask_reset,
                    'server_range': server_range,
                    'server_range_text': server_range_text,
                    'server_range_option': server_range_option,
                    'on_new_server': on_new_server,
                    'server_erlang': server_erlang
                }
                transitions = wse.state.transition.order_by('name')
                head = {"value": '审批', 'wse': id, 'username': request.user.username}
                if wse.content_object.new_edition:
                    if wse.content_object.project.project_name_en in ('csxy', 'csxybt'):
                        return render(request,
                                      'version_update_workflow_approve_v2_csxy.html',
                                      {'head': head, 'data': data, 'transitions': transitions})
                    else:
                        return render(request,
                                      'version_update_workflow_approve_v2.html',
                                      {'head': head, 'data': data, 'transitions': transitions})
                return render(request,
                              'version_update_workflow_approve.html',
                              {'head': head, 'data': data, 'transitions': transitions})
            if isinstance(wse.content_object, MysqlWorkflow):
                if wse.state_value:
                    has_approved = True
                else:
                    has_approved = False

                creator = wse.content_object.creator
                applicant = wse.content_object.applicant
                title = wse.content_object.title
                reason = wse.content_object.reason
                content = json.loads(wse.content_object.content)
                state_value = wse.state_value

                # # 申请人部门，如果有的话，没有为空
                # if wse.content_object.applicant.groups.all():
                #     group = wse.content_object.applicant.groups.all()[0].name
                # else:
                #     group = ''
                #
                # if wse.content_object.applicant.profile.group_section is not None:
                #     group_section = wse.content_object.applicant.profile.group_section.name
                # else:
                #     group_section = '没有分配到管理分组'
                """2018.12修改，合并部门和部门管理分组"""
                org = OrganizationMptt.objects.get(user_id=wse.content_object.applicant.id)
                belongs_to_new_organization = org.get_ancestors_except_self()

                transitions = wse.state.transition.order_by('name')

                head = {"value": '审批', 'wse': id, 'username': request.user.username}

                data = {
                    'creator': creator,
                    'applicant': applicant,
                    'title': title,
                    'group': belongs_to_new_organization,
                    'group_section': belongs_to_new_organization,
                    'content': content,
                    'reason': reason,
                    'state_value': state_value,
                    'has_approved': has_approved,
                }

                return render(request,
                              'mysql_workflow_approve.html', {'head': head, 'data': data, 'transitions': transitions})
        else:
            return render(request, '403.html')

    if request.method == "POST":
        wse_log = WorkflowApproveLog()

        '执行审批状态转化'
        pdata = json.loads(request.body.decode('utf-8'))
        wse = pdata.get('wse')
        transition = pdata.get('transition')
        opinion = pdata.get('opinion', None)
        has_handle = pdata.get('has_handle', '0')
        has_add_mac = pdata.get('has_add_mac', '0')
        is_cancel = pdata.get('is_cancel', '0')
        if not opinion:
            opinion = None

        """发生转化的条件
        1 wse的is_current 为True
        2 transition在当前的wse的state中
        3 user在当前的wse的state中
        """

        transition = Transition.objects.get(id=transition)
        wse = WorkflowStateEvent.objects.get(id=wse)

        # 版本更新工单，需要保存版本号和注意事项
        if isinstance(wse.content_object, VersionUpdate):
            if wse.state.name == '运维负责人':
                on_new_server = pdata.get('on_new_server', False)
                server_range = pdata.get('server_range', '')
                server_content = pdata.get('server_content', '')
                # 去除空行和空格
                server_content = '\n'.join([x for x in map(lambda x: x.strip(), server_content.split('\n'))
                                            if x is not None and x != ''])
                client_content = pdata.get('client_content', '')
                if client_content:
                    if wse.content_object.project.project_name_en not in ('csxy', 'csxybt'):
                        for c in client_content:
                            # 如果客户端类型没有值，则设置为空字符串
                            if c.get('client_type', '0') == '0':
                                c['client_type'] = ''
                            # 如果cdn目录包含客户端类型，则用/分割后分别重新设置客户端类型和cdn目录的值
                            if len(c.get('cdn_dir', '').split('/')) > 1:
                                c['client_type'] = c.get('cdn_dir').split('/')[-1]
                                c['cdn_dir'] = c.get('cdn_dir').split('/')[0]
                    client_content = json.dumps(client_content)
                content_object = wse.content_object
                content_object.on_new_server = on_new_server
                # 如果是排除区服，则保存到排除区服字段中
                if server_range == 'exclude':
                    content_object.server_exclude_content = server_content
                else:
                    content_object.server_content = server_content
                content_object.server_range = server_range
                content_object.client_content = client_content
                content_object.save()

            if wse.state.name == '后端负责人':
                server_version = pdata.get('server_version')
                server_attention = pdata.get('server_attention')
                content_object = wse.content_object
                content_object.server_version = server_version
                server_range = content_object.server_range

                # 如果是全服更新，在后端填入版本号之后，根据项目、地区、状态、版本号得到需要更新的区服srv_id列表
                if server_range == 'all':
                    server_content = '\n'.join([game_server.srv_id for game_server in
                                                GameServer.objects.select_related('host').filter(
                                                    project=content_object.project,
                                                    host__belongs_to_room__area=content_object.area,
                                                    srv_status=0)])
                    content_object.server_content = server_content
                # 如果是排除区服更新，需要根据项目、地区、状态、版本号得到全部区服srv_id列表，减去排除的区服srv_id
                if server_range == 'exclude':
                    all_srv_id_list = [game_server.srv_id for game_server in
                                       GameServer.objects.select_related('host').filter(
                                           project=content_object.project,
                                           host__belongs_to_room__area=content_object.area,
                                           srv_status=0)]
                    exclude_srv_id_list = [x for x in
                                           map(lambda x: x.strip(), content_object.server_exclude_content.split('\n'))
                                           if x is not None and x != '']
                    update_srv_id_set = list(
                        set([srv_id for srv_id in all_srv_id_list if srv_id not in exclude_srv_id_list]))
                    server_content = '\n'.join(update_srv_id_set)
                    content_object.server_content = server_content

                content_object.server_attention = server_attention
                ask_reset = pdata.get('ask_reset', False)
                server_erlang = pdata.get('server_erlang', '')
                if ask_reset:
                    content_object.ask_reset = ask_reset
                    content_object.server_erlang = server_erlang
                content_object.save()
            if wse.state.name == '前端负责人':
                content_object = wse.content_object
                client_version = pdata.get('client_version')
                client_attention = pdata.get('client_attention')
                client_content = pdata.get('client_content', '')
                if client_content:
                    client_content = json.dumps(client_content)
                content_object.client_content = client_content
                content_object.client_version = client_version
                content_object.client_attention = client_attention
                content_object.client_attention = client_attention
                content_object.save()

        # 获取本轮审批有权先审批的user object列表
        approve_user_list = [u for u in wse.users.all()]
        # 转化流程状态
        wse_log.logger.info(
            '第1节点： 审批人：{}，审批意见：{}，工单标题：{}，wse_id：{}，is_current：{}'.format(request.user.username, transition.condition,
                                                                          wse.title, wse.id, wse.is_current))
        msg, success, new_wse = do_transition(wse, transition, request.user, opinion=opinion)
        wse_log.logger.info(
            '第8节点： 审批人：{}，审批意见：{}，工单标题：{}，wse_id：{}，is_current：{}'.format(request.user.username, transition.condition,
                                                                          wse.title, wse.id, wse.is_current))

        if success:
            # 如果不是取消工单，则从审批人列表中排除当前审批人
            if str(is_cancel) == '0':
                approve_user_list.remove(request.user)
                # 如果前一审批节点有多个审批人，则把最新审批结果通知到除当前审批人之外的审批人
                if approve_user_list:
                    # 邮件通知
                    to_list = [x.email for x in approve_user_list]
                    subject = wse.content_object.title + '#审批结果'
                    content = '你的小伙伴： {}，已经 {} 工单申请#{}'.format(request.user.username, transition.condition,
                                                               wse.content_object.title)
                    send_mail.delay(to_list, subject, content)
                    # 都要发送qq弹框提醒
                    users = ','.join([x.first_name for x in approve_user_list])
                    send_qq.delay(users, subject, subject, content, '')
                    # 发送wx弹框提醒
                    wx_users = '|'.join([x.first_name for x in approve_user_list])
                    send_weixin_message.delay(touser=wx_users, content=content)

            # 审批完成后把sor中的users审批用户复制到wse的users审批用户中
            sor = get_sor(new_wse.state, new_wse.content_object)
            if sor:
                users = tuple(sor.users.all())
                new_wse.users.add(*users)

            # 审批完成后，如果不是版本更新单，更新企业微信任务卡片状态
            if not isinstance(new_wse.content_object, VersionUpdate):
                touser = [u.first_name for u in wse.users.all()]
                update_wx_taskcard_status(touser, wse)

            # 如果是同意的话，发送通知到下一个节点
            if transition.condition == '同意':
                wse_users = new_wse.users.all()

                if wse_users:
                    if isinstance(new_wse.content_object, ClientHotUpdate) or \
                            isinstance(new_wse.content_object, ServerHotUpdate):
                        # 邮件通知
                        to_list = [x.email for x in wse_users if not x.profile.hot_update_email_approve]
                        if to_list:
                            subject, content = make_email_notify(True)
                            send_mail.delay(to_list, subject, content)

                        # 邮件审批
                        approve_list = [x.email for x in wse_users if x.profile.hot_update_email_approve]
                        if approve_list:
                            subject, content = make_email(new_wse)
                            send_mail.delay(approve_list, subject, content)

                        # 都要发送qq弹框提醒
                        users = ','.join([x.first_name for x in wse_users])
                        data = get_qq_notify()
                        send_qq.delay(
                            users, data['window_title'], data['tips_title'], data['tips_content'], data['tips_url'])
                        # 发送wx弹框提醒
                        # wx_users = '|'.join([x.first_name for x in wse_users])
                        # if wx_users:
                        #     data = get_wx_notify()
                        #     send_weixin_message.delay(touser=wx_users, content=data)

                    # wifi工单达到运维后发送给网络管理员
                    elif isinstance(new_wse.content_object, Wifi) and new_wse.state.name == '运维':
                        users = ','.join(
                            [x.first_name for x in User.objects.filter(username__in=get_yl_network_administrator()) if
                             x.is_active])
                        wx_users = '|'.join(
                            [x.first_name for x in User.objects.filter(username__in=get_yl_network_administrator()) if
                             x.is_active])
                        send_qq.delay(users, '你有一个wifi申请或网络问题申报工单需要处理', '你有一个wifi申请或网络问题申报工单需要处理',
                                      '链接:请登录CMDB处理(只能使用谷歌或者火狐浏览器)', 'http://192.168.100.66/myworkflows/approve_list/')
                        # send_weixin_message.delay(touser=wx_users,
                        #                           content='你有一个wifi申请或网络问题申报工单需要处理' + '链接:请登录CMDB处理(只能使用谷歌或者火狐浏览器)' +
                        #                                   'http://192.168.100.66/myworkflows/approve_list/')

                    else:
                        subject, content = make_email_notify(True)
                        to_list = [x.email for x in wse_users]
                        send_mail.delay(to_list, subject, content)

                        # 都要发送qq弹框提醒
                        users = ','.join([x.first_name for x in wse_users])
                        data = get_qq_notify()
                        send_qq.delay(
                            users, data['window_title'], data['tips_title'], data['tips_content'], data['tips_url'])

                        # 如果是版本更新单，发送wx弹框提醒
                        if isinstance(new_wse.content_object, VersionUpdate):
                            wx_users = '|'.join([x.first_name for x in wse_users if
                                                 x.is_active and x.organizationmptt_set.first().wechat_approve == 1])
                            if wx_users:
                                data = get_wx_notify()
                                send_weixin_message.delay(touser=wx_users, content=data)

                    # 如果不是版本更新单，发送企业微信审批
                    if not isinstance(new_wse.content_object, VersionUpdate):
                        touser = '|'.join([u.first_name for u in wse_users if
                                           u.is_active and u.organizationmptt_set.first().wechat_approve == 1])
                        result = get_wx_task_card_data(touser, new_wse)
                        if result['success']:
                            send_task_card_to_wx_user.delay(touser, result['data'])

                else:
                    # 添加服务器权限接口
                    if isinstance(new_wse.content_object, ServerPermissionWorkflow) and new_wse.state.name == '完成':
                        # api_add_server_permission(new_wse)
                        workflow_add_server_permission.delay(new_wse.id)

                    # 自动添加svn接口
                    if isinstance(new_wse.content_object, SVNWorkflow) and new_wse.state.name == '完成':
                        add_svn_workflow.delay(new_wse.id)

                    # 版本更新单发送qq/wx弹窗提醒
                    if isinstance(new_wse.content_object, VersionUpdate) and new_wse.state.name == '完成':
                        project_related_ops = new_wse.content_object.project.get_relate_role_user()
                        data = get_version_update_notify(new_wse.title)
                        users = ','.join([x.first_name for x in project_related_ops if x.is_active])
                        send_qq.delay(users, data['window_title'], data['tips_title'], data['tips_content'],
                                      data['tips_url'])
                        wx_users = '|'.join([x.first_name for x in project_related_ops if x.is_active])
                        send_weixin_message.delay(touser=wx_users,
                                                  content=data['tips_title'] + ',' + data['tips_content'] + ',' + data[
                                                      'tips_url'])
                        if NEW_VERSION_UPDATE and new_wse.content_object.project.auto_version_update \
                                and new_wse.content_object.is_maintenance \
                                and new_wse.content_object.start_time <= datetime.now() <= new_wse.content_object.end_time \
                                and new_wse.content_object.status == 2 and new_wse.content_object.new_edition:
                            version_update_task.delay(new_wse.content_object.id, 'all')

                    # 自动执行前端热更新
                    if isinstance(new_wse.content_object, ClientHotUpdate) and new_wse.state.name == '完成':
                        # 工单完成以后，修改工单的状态
                        content_object = new_wse.content_object
                        content_object.status = '4'
                        content_object.save()
                        ws_notify()

                        """如果当前项目和地区没有锁，则找到下一个更新去执行"""
                        # list_ops_manager = OpsManager.objects.filter(
                        #     project=content_object.project, area=content_object.area_name)
                        """
                        2019.3修改
                        修改获取运维管理机的方法:
                        通过content_object中关联的推送子任务表获取更新需要用到的运维管理机，
                        及rsync推送时所需要用到的参数
                        """
                        status_list = [x.ops.status for x in content_object.clienthotupdatersynctask_set.all()]
                        if len(list(set(status_list))) == 1 and '0' in status_list:
                            # do_hot_client.delay(new_wse.id)
                            msg, next_hot_update = get_next_hot_update(content_object.project, content_object.area_name)
                            if next_hot_update:
                                if next_hot_update.status == '4':
                                    do_hot_update(next_hot_update)
                            else:
                                """更新任务没有自动执行原因字段"""
                                content_object.no_auto_execute_reason = msg
                                content_object.save(update_fields=['no_auto_execute_reason'])
                                # 发送邮件告警
                                # to_list = [x.email for x in content_object.project.related_user.all() if x.is_active]
                                to_list = list(set(
                                    [x.email for x in content_object.project.get_relate_role_user() if x.is_active]))
                                subject = '热更新审批完成后没有自动执行'
                                content = '项目:{} 地区:{}，热更新:{} 没有自动执行，请查看原因：可能是{}'.format(
                                    content_object.project.project_name, content_object.area_name, content_object.title,
                                    msg)
                                send_mail.delay(to_list, subject, content)
                                # users = ','.join([x.first_name for x in new_wse.content_object.project.related_user.all() if x.is_active])
                                users = ','.join(
                                    [x.first_name for x in new_wse.content_object.project.get_relate_role_user() if
                                     x.is_active])
                                send_qq.delay(
                                    users, subject, subject, content, '')
                                # wx_users = '|'.join([x.first_name for x in new_wse.content_object.project.related_user.all() if x.is_active])
                                wx_users = '|'.join(
                                    [x.first_name for x in new_wse.content_object.project.get_relate_role_user() if
                                     x.is_active])
                                send_weixin_message.delay(
                                    touser=wx_users, content=subject + content)
                        else:
                            # 热更新审批完成后没有触发执行
                            # 需要发送告警给相应的运维负责人
                            # users = ','.join([x.first_name for x in new_wse.content_object.project.related_user.all() if x.is_active])
                            users = ','.join(
                                [x.first_name for x in new_wse.content_object.project.get_relate_role_user() if
                                 x.is_active])
                            window_title = '项目地区锁:热更新审批完成后不能自动执行'
                            tips_title = '项目地区锁:热更新审批完成后不能自动执行'
                            tips_content = '项目:{} 地区:{} 已经上锁，热更新:{} 不能自动执行 链接:请登录CMDB处理(只能使用谷歌或者火狐浏览器)'.format(
                                content_object.project.project_name, content_object.area_name, content_object.title)
                            tips_url = 'https://192.168.100.66/myworkflows/hot_server_list/'
                            send_qq.delay(
                                users, window_title, tips_title, tips_content, tips_url)
                            # wx_users = '|'.join([x.first_name for x in new_wse.content_object.project.related_user.all() if x.is_active])
                            wx_users = '|'.join(
                                [x.first_name for x in new_wse.content_object.project.get_relate_role_user() if
                                 x.is_active])
                            send_weixin_message.delay(
                                touser=wx_users, content=tips_title + tips_content + tips_url)

                            # 发送邮件告警
                            # to_list = [x.email for x in content_object.project.related_user.all() if x.is_active]
                            to_list = list(
                                set([x.email for x in content_object.project.get_relate_role_user() if x.is_active]))
                            subject = '项目地区锁:热更新审批完成后不能自动执行'
                            content = '项目:{} 地区:{} 已经上锁，热更新:{} 不能自动执行'.format(
                                content_object.project.project_name, content_object.area_name, content_object.title)
                            send_mail.delay(to_list, subject, content)

                            """更新任务没有自动执行原因字段"""
                            content_object.no_auto_execute_reason = tips_content
                            content_object.save(update_fields=['no_auto_execute_reason'])

                    # 自动添加mysql权限
                    if isinstance(new_wse.content_object, MysqlWorkflow) and new_wse.state.name == '完成':
                        add_mysql_permission.delay(new_wse.id)

                    # 自动执行后端热更新
                    if isinstance(new_wse.content_object, ServerHotUpdate) and new_wse.state.name == '完成':
                        # 工单完成以后，修改工单的状态
                        content_object = new_wse.content_object
                        content_object.status = '4'
                        content_object.save()
                        ws_notify()

                        # 加载热更新的区服数据到redis中
                        # load_to_redis(new_wse.content_object)

                        # 如果当前项目和地区没有锁，则直接发送到任务队列里面
                        """
                        2019.3修改
                        根据后端热更新子任务表获取运维管理机状态
                        """
                        status_list = [x.ops.status for x in content_object.serverhotupdatersynctask_set.all()]
                        if len(list(set(status_list))) == 1 and '0' in status_list:
                            msg, next_hot_update = get_next_hot_update(content_object.project, content_object.area_name)
                            if next_hot_update:
                                if next_hot_update.status == '4':
                                    do_hot_update(next_hot_update)
                                elif next_hot_update.status == '0':
                                    content_object.no_auto_execute_reason = next_hot_update.title + '状态不是待更新！'
                                    content_object.save()
                            else:
                                """更新任务没有自动执行原因字段"""
                                content_object.no_auto_execute_reason = msg
                                content_object.save()
                                # 发送邮件告警
                                # to_list = [x.email for x in content_object.project.related_user.all() if x.is_active]
                                to_list = list(set(
                                    [x.email for x in content_object.project.get_relate_role_user() if x.is_active]))
                                subject = '热更新审批完成后没有自动执行'
                                content = '项目:{} 地区:{}，热更新:{} 没有自动执行,请查看原因 {}'.format(
                                    content_object.project.project_name, content_object.area_name, content_object.title,
                                    msg)
                                send_mail.delay(to_list, subject, content)
                        else:
                            # 热更新审批完成后没有触发执行
                            # 需要发送告警给相应的运维负责人
                            # users = ','.join([x.first_name for x in new_wse.content_object.project.related_user.all() if x.is_active])
                            users = ','.join(
                                [x.first_name for x in new_wse.content_object.project.get_relate_role_user() if
                                 x.is_active])
                            window_title = '项目地区锁:热更新审批完成后不能自动执行'
                            tips_title = '项目地区锁:热更新审批完成后不能自动执行'
                            tips_content = '项目:{} 地区:{} 已经上锁，热更新:{} 不能自动执行 链接:请登录CMDB处理(只能使用谷歌或者火狐浏览器)'.format(
                                content_object.project.project_name, content_object.area_name, content_object.title)
                            tips_url = 'https://192.168.100.66/myworkflows/hot_server_list/'
                            send_qq.delay(
                                users, window_title, tips_title, tips_content, tips_url)
                            # wx_users = '|'.join([x.first_name for x in new_wse.content_object.project.related_user.all() if x.is_active])
                            wx_users = '|'.join(
                                [x.first_name for x in new_wse.content_object.project.get_relate_role_user() if
                                 x.is_active])
                            send_weixin_message.delay(
                                touser=wx_users, content=tips_title + tips_content + tips_url)

                            # 发送邮件告警
                            # to_list = [x.email for x in content_object.project.related_user.all() if x.is_active]
                            to_list = list(
                                set([x.email for x in content_object.project.get_relate_role_user() if x.is_active]))
                            subject = '项目地区锁:热更新审批完成后不能自动执行'
                            content = '项目:{} 地区:{} 已经上锁，热更新:{} 不能自动执行'.format(
                                content_object.project.project_name, content_object.area_name, content_object.title)
                            send_mail.delay(to_list, subject, content)

                            """更新任务没有自动执行原因字段"""
                            content_object.no_auto_execute_reason = tips_content
                            content_object.save(update_fields=['no_auto_execute_reason'])

                    # 执行根据项目删除服务器权限和SVN权限
                    if isinstance(new_wse.content_object, ProjectAdjust) and new_wse.state.name == '完成':
                        content_object = new_wse.content_object
                        # proj_id = content_object.raw_project_group.project.id if content_object.raw_project_group else None
                        if content_object.delete_serper:
                            if content_object.serper_projects is not None:
                                clean_project_serper.delay(new_wse.id, json.loads(content_object.serper_projects))
                        if content_object.delete_svn:
                            if content_object.svn_projects is not None:
                                for proj_id in json.loads(content_object.svn_projects):
                                    clean_svn_workflow.delay(new_wse.id, proj_id)

                        # 如果都没有勾选清除svn或者服务器权限的，改为已处理状态
                        if not content_object.delete_serper and not content_object.delete_svn:
                            content_object.status = '0'
                            content_object.save()

                        # 调整人员所属部门
                        if content_object.new_department_group is not None:
                            org = OrganizationMptt.objects.get(user_id=content_object.applicant_id)
                            org.parent = content_object.new_department_group
                            org.save()

                    # 服务器申请工单完成后发送通知给相关人员
                    if isinstance(new_wse.content_object, Machine) and new_wse.state.name == '完成':
                        machine_administrator_list = [u.first_name for u in
                                                      User.objects.filter(username__in=get_machine_administrator())]
                        users = ','.join(machine_administrator_list)
                        send_qq.delay(users, '你有一个服务器申请工单', '你有一个服务器申请工单',
                                      '链接:请登录CMDB处理(只能使用谷歌或者火狐浏览器)', 'http://192.168.100.66/myworkflows/approve_list/')
                        wx_users = '|'.join(machine_administrator_list)
                        send_weixin_message.delay(touser=wx_users, content='你有一个服务器申请工单' + '你有一个服务器申请工单' +
                                                                           '链接:请登录CMDB处理(只能使用谷歌或者火狐浏览器)' +
                                                                           'http://192.168.100.66/myworkflows/approve_list/')
                        # 发送是否已构买任务卡片给相关人员
                        result = get_wx_task_card_data(wx_users, new_wse, purchase=True)
                        if result['success']:
                            send_task_card_to_wx_user.delay(wx_users, result['data'])

                    # 申请Cy-work的wifi工单完成后，判断是否自动开通，是则自动发送接口开通
                    if isinstance(new_wse.content_object,
                                  Wifi) and new_wse.content_object.name == 'Cy-work' and new_wse.state.name == '完成':
                        if has_add_mac == '1':
                            applicant_first_name = new_wse.content_object.applicant.first_name
                            touser = '|'.join([u.first_name for u in wse.users.all()])
                            add_mac.delay(applicant_first_name, new_wse.content_object.mac, new_wse.content_object.id,
                                          touser=touser)
                            # 将工单状态设置为完成
                            failure_declare_finish(request, update_taskcard=False)

                    # 判断是否已经处理，调用函数
                    if has_handle == '1':
                        failure_declare_finish(request, update_taskcard=False)

            else:
                """判断是否为取消工单操作, 0为非取消，走正常拒绝流程，1为取消，修改is_cancel状态"""
                if str(is_cancel) == '0':
                    to_list = new_wse.creator.email if User.objects.get(id=new_wse.creator.id).is_active else ''
                    if to_list:
                        to_list = [to_list]
                        subject, content = make_email_notify(False)
                        send_mail.delay(to_list, subject, content)

                    # 发送qq弹框提醒
                    users = new_wse.creator.first_name if User.objects.get(id=new_wse.creator.id).is_active else ''

                    window_title = "你的申请被拒绝"
                    tips_title = "你的申请被拒绝"
                    tips_content = "链接:请登录CMDB查看(只能使用谷歌或者火狐浏览器)"
                    tips_url = "http://192.168.100.66/myworkflows/approve_list/"
                    send_qq.delay(users, window_title, tips_title, tips_content, tips_url)
                    # 发送wx弹框提醒
                    wx_users = new_wse.creator.first_name if User.objects.get(id=new_wse.creator.id).is_active else ''
                    send_weixin_message.delay(touser=wx_users, content=tips_title + tips_content + tips_url)

                else:
                    new_wse.is_cancel = 1
                    new_wse.save()
                    # 企业微信通知当前审批人，无需处理该工单的任务卡片
                    new_wse.users.all()
                    wx_users = '|'.join([x.first_name for x in new_wse.users.all()])
                    if wx_users:
                        cancel_wx_msg = '工单#{}，已被申请人{}取消，您无需处理审批，若您已处理，请忽略此消息！'.format(new_wse.title,
                                                                                       new_wse.content_object.creator.username)
                        send_weixin_message.delay(touser=wx_users, content=cancel_wx_msg)

                # 前端热更新或者后端热更新工单拒绝以后
                # 需要把PRIORITY改为3，也就是暂停的级别
                # 这么做是为了防止阻塞后面正常审批完成的工单执行
                if isinstance(new_wse.content_object, ClientHotUpdate) or isinstance(new_wse.content_object,
                                                                                     ServerHotUpdate):
                    content_object = new_wse.content_object
                    content_object.priority = '3'
                    content_object.save()

        return JsonResponse({'data': msg, 'success': success})


def version_update_summarize(request):
    """版本热更新单汇总
    """
    if request.method == "GET":
        head = {'username': request.user.username, 'value': '版本更新单汇总'}
        all_project = [{'id': x.id, 'text': x.project_name} for x in GameProject.objects.filter(status=1)]
        return render(request, 'version_update_summarize.html', {'head': head, 'all_project': all_project})


def data_version_update_summarize(request):
    """版本热更新单汇总数据
    """
    if request.method == "POST":
        raw_get = request.POST.dict()
        project = raw_get.get('project')
        search_value = raw_get.get('search[value]', '')
        start = int(raw_get.get('start', 0))
        draw = raw_get.get('draw', 0)
        length = int(raw_get.get('length', 10))
        raw_data = ''

        if project == '0':
            query = WorkflowStateEvent.objects.none()
        else:
            project = GameProject.objects.get(id=project)
            IS_VALID = WorkflowStateEvent.IS_VALID
            is_valid = 0
            for i in IS_VALID:
                if i[1] == search_value:
                    is_valid = i[0]
            if search_value:
                query = WorkflowStateEvent.objects.filter(
                    version_update_workflow__project=project, is_current=True).filter(
                    Q(create_time__contains=search_value) | Q(creator__username__icontains=search_value) |
                    Q(title__icontains=search_value) | Q(state__name__icontains=search_value) |
                    Q(is_valid=is_valid)
                ).order_by('-create_time')
            else:
                query = WorkflowStateEvent.objects.filter(
                    version_update_workflow__project=project, is_current=True).order_by('-create_time')
        raw_data = query[start: start + length]
        recordsTotal = query.count()
        # recordsFiltered = len(raw_data)
        data = {"data": [i.show_version_update_summarize() for i in raw_data], 'draw': draw,
                'recordsTotal': recordsTotal, 'recordsFiltered': recordsTotal}
        return JsonResponse(data)


def myworkflow_history(request):
    """这里做一次转发

    通过wse的id，获取到content_type和object_id
    然后在myworkflow的视图中通过content_type和object_id来获取wse

    解决流程到了下个节点以后返回403的问题
    """

    if request.method == "GET":
        id = request.GET.get('id')
        wse = WorkflowStateEvent.objects.get(id=id)

        ctype = ContentType.objects.get_for_model(wse.content_object)
        ctype_id = ctype.id
        object_id = wse.object_id

        return HttpResponseRedirect(
            '/myworkflows/myworkflow/?object_id=%s&id=%s&ctype_id=%s' % (object_id, id, ctype_id))


def myworkflow_hotupdate(request):
    """根据update_type和id跳转到
    具体的查看热更新页面
    """
    if request.method == "GET":
        id = request.GET.get('id')
        update_type = request.GET.get('update_type')

        if update_type == '前端':
            ctype = ContentType.objects.get_for_model(ClientHotUpdate)
        else:
            ctype = ContentType.objects.get_for_model(ServerHotUpdate)

        ctype_id = ctype.id
        object_id = id
        wse_id = WorkflowStateEvent.objects.get(content_type=ctype, is_current=True, object_id=object_id).id
        return HttpResponseRedirect(
            '/myworkflows/myworkflow/?object_id=%s&id=%s&ctype_id=%s' % (object_id, wse_id, ctype_id))


def myworkflow(request):
    """查看我的申请
    用来查看申请信息和重新提交

    重新提交的条件:
    wse 为当前状态并且state_value == 拒绝
    """

    if request.method == "GET":
        id = request.GET.get('id')
        object_id = request.GET.get('object_id')
        ctype_id = request.GET.get('ctype_id')

        ctype = ContentType.objects.get(id=ctype_id)

        wse = WorkflowStateEvent.objects.get(content_type=ctype, object_id=object_id, is_current=True)

        # wse = WorkflowStateEvent.objects.get(id=id)

        # 只能查看自己的申请或者管理员也可以查看别人的申请
        # if wse.creator == request.user or request.user.is_superuser:
        if wse.state.workflow.name == "SVN申请":
            # recommit = True if (wse.state_value == '拒绝' and not request.user.is_superuser) else False
            recommit = False
            if wse.is_current:
                title = wse.content_object.title
                content = json.loads(wse.content_object.content)
                reason = wse.content_object.reason
                svn_scheme_id = wse.content_object.svn_scheme.id if wse.content_object.svn_scheme else '0'
                svn_scheme = wse.content_object.svn_scheme.name if wse.content_object.svn_scheme else '没有选择svn方案'
                id = wse.id
                applicant_id = wse.content_object.applicant.id
                applicant = wse.content_object.applicant.username

                """2018.12修改，合并部门和部门管理分组"""
                org = OrganizationMptt.objects.get(user_id=wse.content_object.applicant.id)
                belongs_to_new_organization = org.get_ancestors_except_self()

                if request.user.is_superuser:
                    can_execute = True
                else:
                    can_execute = False

                project_id = wse.content_object.project.id
                project_name = wse.content_object.project.project_name
                state_step = '==>'.join([x.name for x in get_workflow_state_order(wse.state.workflow)])
                get_workflow_state_order(wse.state.workflow)
                current_state = wse.state.name
                opinion = wse.opinion
                state_value = wse.state_value if wse.state_value else ''
                data = {
                    'title': title,
                    'content': content,
                    'reason': reason,
                    'svn_scheme_id': svn_scheme_id,
                    'svn_scheme': svn_scheme,
                    'applicant_id': applicant_id,
                    'applicant': applicant,
                    'group': belongs_to_new_organization,
                    'group_section': belongs_to_new_organization,
                    'project_id': project_id,
                    'project_name': project_name,
                    'id': id,
                    'recommit': recommit,
                    'state_step': state_step,
                    'current_state': current_state,
                    'opinion': opinion,
                    'state_value': state_value,
                    'can_execute': can_execute,
                }

                head = {'value': title, 'username': request.user.username}

                return render(request, 'myworkflow.html', {'data': data, 'head': head})
            else:
                return render(request, '403.html')

        if wse.state.workflow.name == "服务器权限申请":
            recommit = False
            if wse.is_current:
                id = wse.id

                project_id = wse.content_object.project.id
                project_name = wse.content_object.project.project_name

                applicant = wse.content_object.applicant.username

                title = wse.content_object.title
                reason = wse.content_object.reason

                key = wse.content_object.key
                is_root = wse.content_object.is_root

                room_id = wse.content_object.room.id if wse.content_object.room else '0'
                room_name = wse.content_object.room.room_name if wse.content_object.room else '选择机房'

                ips = json.loads(wse.content_object.ips)

                all_ip = wse.content_object.all_ip

                # 添加执行的按钮
                if request.user.is_superuser:
                    can_execute = True
                else:
                    can_execute = False

                # 如果流程走完以后并且状态不是2，需要把ip添加的是否成功的信息展示
                if wse.state.name == '完成' and wse.content_object.status != 2:
                    ip_status = 'true'
                else:
                    ip_status = 'false'

                # 这里需要做一些兼容，以前的工单没有起止时间
                # 如果没有的话，就以Unix Time的开始时间来表示
                if wse.content_object.start_time:
                    start_time = wse.content_object.start_time.strftime('%Y-%m-%d %H:%M')
                else:
                    start_time = "1970-1-1 00:00"

                if wse.content_object.end_time:
                    end_time = wse.content_object.end_time.strftime('%Y-%m-%d %H:%M')
                else:
                    end_time = "1970-1-1 00:00"

                temporary = wse.content_object.temporary

                group = wse.content_object.group
                opinion = wse.opinion

                """2018.12修改，合并部门和部门管理分组"""
                org = OrganizationMptt.objects.get(user_id=wse.content_object.applicant.id)
                belongs_to_new_organization = org.get_ancestors_except_self()

                data = {
                    'project_id': project_id,
                    'project_name': project_name,
                    'applicant': applicant,
                    'title': title,
                    'reason': reason,
                    'key': key,
                    'start_time': start_time,
                    'end_time': end_time,
                    'temporary': temporary,
                    'group': group,
                    'one_group': belongs_to_new_organization,
                    'group_section': belongs_to_new_organization,
                    'opinion': opinion,
                    'is_root': is_root,
                    'room_id': room_id,
                    'room_name': room_name,
                    'ips': ips,
                    "can_execute": can_execute,
                    'ips_value': wse.content_object.ips,
                    'all_ip': all_ip,
                    'ip_status': ip_status,
                    'id': id,
                    'recommit': recommit,
                    'first_name': request.user.first_name,
                }

                head = {'value': title, 'username': request.user.username}

                return render(request, 'ser_perm_myworkflow.html', {'data': data, 'head': head})
            else:
                return render(request, '403.html')

        if isinstance(wse.content_object, FailureDeclareWorkflow):
            # recommit = True if wse.state_value == '拒绝' else False
            recommit = False
            if wse.is_current:
                id = wse.id
                applicant_id = wse.content_object.applicant.id
                applicant = wse.content_object.applicant.username
                title = wse.content_object.title
                classification = wse.content_object.get_classification_display()
                content = wse.content_object.content
                current_state = wse.state.name
                opinion = wse.opinion
                state_value = wse.state_value if wse.state_value else ''

                sor_user = StateObjectUserRelation.objects.get(
                    failure_declare_sor=wse.content_object, state=wse.state.workflow.init_state).users.all()

                if wse.state.name == '完成' and request.user in sor_user and wse.content_object.status == 1:
                    can_execute = True
                else:
                    can_execute = False

                data = {
                    'title': title,
                    'classification': classification,
                    'content': content,
                    'applicant_id': applicant_id,
                    'applicant': applicant,
                    'id': id,
                    'recommit': recommit,
                    'can_execute': can_execute,
                    'state_value': state_value,
                    'opinion': opinion,
                }
                head = {'value': title, 'username': request.user.username}

                return render(request, 'failure_decalre_myworkflow.html', {'data': data, 'head': head})
            else:
                return render(request, '403.html')

        if isinstance(wse.content_object, ClientHotUpdate):
            if wse.is_current:
                id = wse.id
                content_object = wse.content_object

                project_name_en = content_object.project.project_name_en

                applicant = content_object.applicant
                title = content_object.title
                reason = content_object.reason
                attention = content_object.attention
                project = content_object.project.project_name
                area_name = content_object.get_area_name()
                client_version = content_object.client_version
                content = json.loads(content_object.content)
                pair_code = content_object.pair_code if content_object.pair_code else '无'
                order = content_object.order if content_object.order else '无'
                update_file_list = hot_update_file_list_to_string(json.loads(content_object.update_file_list))
                opinion = wse.opinion

                data = {
                    'id': id,
                    'applicant': applicant,
                    'title': title,
                    'reason': reason,
                    'attention': attention,
                    'project': project,
                    'area_name': area_name,
                    'client_version': client_version,
                    'content': content,
                    'pair_code': pair_code,
                    'order': order,
                    'update_file_list': update_file_list,
                    'opinion': opinion,
                }

                head = {'value': title, 'username': request.user.username}
                html_template = project_name_en + '_client_hot_update_myworkflow.html'
                client_hotupdate_template = content_object.project.get_client_hotupdate_template(tag=True)
                if client_hotupdate_template:
                    return render(request, client_hotupdate_template + '_client_hot_update_myworkflow.html',
                                  {'data': data, 'head': head})
                try:
                    return render(request, html_template, {'data': data, 'head': head})
                except:
                    return render(request, 'common_client_hot_update_myworkflow.html', {'data': data, 'head': head})
            else:
                return render(request, '403.html')

        if isinstance(wse.content_object, ServerHotUpdate):
            if wse.is_current:
                id = wse.id
                content_object = wse.content_object
                project_name_en = content_object.project.project_name_en

                applicant = content_object.applicant
                title = content_object.title
                reason = content_object.reason
                attention = content_object.attention
                project = content_object.project.project_name
                area_name = content_object.get_area_name()
                server_version = content_object.server_version
                hot_server_type = content_object.get_hot_server_type_display()
                hot_server_type_code = content_object.hot_server_type
                pair_code = content_object.pair_code if content_object.pair_code else '无'
                order = content_object.order if content_object.order else '无'
                opinion = wse.opinion
                on_new_server = content_object.serverhotupdatereplication.on_new_server

                if hot_server_type_code == '0':
                    # 只热更
                    show_file_list = True
                    show_erlang_list = False

                    update_file_list = hot_update_file_list_to_string(json.loads(content_object.update_file_list))
                    erlang_cmd_list = ""
                elif hot_server_type_code == '1':
                    # 先热更,再执行erl命令
                    show_file_list = True
                    show_erlang_list = True

                    update_file_list = hot_update_file_list_to_string(json.loads(content_object.update_file_list))
                    erlang_cmd_list = content_object.erlang_cmd_list
                elif hot_server_type_code == '2':
                    # 只执行erl命令
                    show_file_list = False
                    show_erlang_list = True

                    update_file_list = ""
                    erlang_cmd_list = content_object.erlang_cmd_list
                elif hot_server_type_code == '3':
                    # 先执行erl命令,再热更
                    show_file_list = True
                    show_erlang_list = True

                    update_file_list = hot_update_file_list_to_string(json.loads(content_object.update_file_list))
                    erlang_cmd_list = content_object.erlang_cmd_list
                else:
                    show_file_list = True
                    show_erlang_list = True

                    update_file_list = hot_update_file_list_to_string(json.loads(content_object.update_file_list))
                    erlang_cmd_list = content_object.erlang_cmd_list

                # update_server_list = hot_server_update_server_list_to_string(
                #     json.loads(content_object.update_server_list))
                update_server_list = hot_server_update_server_list_to_tree(
                    json.loads(content_object.update_server_list))

                data = {
                    'id': id,
                    'applicant': applicant,
                    'title': title,
                    'reason': reason,
                    'attention': attention,
                    'project': project,
                    'area_name': area_name,
                    'server_version': server_version,
                    'hot_server_type': hot_server_type,
                    'erlang_cmd_list': erlang_cmd_list,
                    'update_file_list': update_file_list,
                    'show_file_list': show_file_list,
                    'show_erlang_list': show_erlang_list,
                    'pair_code': pair_code,
                    'order': order,
                    'opinion': opinion,
                    'on_new_server': on_new_server,
                }

                head = {'value': title, 'username': request.user.username}
                html_template = project_name_en + '_server_hot_update_myworkflow.html'
                try:
                    return render(request, html_template, {
                        'data': data, 'head': head, 'update_server_list': update_server_list})
                except:
                    return render(request, 'common_server_hot_update_myworkflow.html', {
                        'data': data, 'head': head, 'update_server_list': update_server_list})
            else:
                return render(request, '403.html')

        if isinstance(wse.content_object, Wifi):
            recommit = False
            if wse.is_current:
                id = wse.id
                applicant_id = wse.content_object.applicant.id
                applicant = wse.content_object.applicant.username
                title = wse.content_object.title
                name = wse.content_object.name
                reason = wse.content_object.reason
                mac = wse.content_object.mac
                current_state = wse.state.name
                opinion = wse.opinion
                state_value = wse.state_value if wse.state_value else ''
                wifi_add_result = wse.content_object.wifi_add_result

                sor_user = StateObjectUserRelation.objects.get(
                    wifi_sor=wse.content_object, state=wse.state.workflow.init_state).users.all()

                # 添加已处理的按钮
                if request.user.username in get_yl_network_administrator() and wse.content_object.status == 1 and wse.state.name == '完成':
                    is_handle = True
                else:
                    is_handle = False
                # 添加执行的按钮
                if request.user.username in get_yl_network_administrator() and wse.content_object.status == 1 and wse.content_object.name == 'Cy-work':
                    can_execute = True
                else:
                    can_execute = False

                data = {
                    'title': title,
                    'name': name,
                    'reason': reason,
                    'mac': mac,
                    'applicant_id': applicant_id,
                    'applicant': applicant,
                    'id': id,
                    'recommit': recommit,
                    'can_execute': can_execute,
                    'is_handle': is_handle,
                    'state_value': state_value,
                    'opinion': opinion,
                    'wifi_add_result': wifi_add_result,
                }
                head = {'value': title, 'username': request.user.username}

                return render(request, 'wifi_myworkflow.html', {'data': data, 'head': head})
            else:
                return render(request, '403.html')
        if isinstance(wse.content_object, Machine):
            recommit = False
            if wse.is_current:
                id = wse.id
                applicant = wse.content_object.applicant.username
                title = wse.content_object.title
                project = wse.content_object.project.project_name
                purpose = wse.content_object.purpose
                config = json.loads(wse.content_object.config)
                number = str(wse.content_object.number) + '台'
                ip_type = wse.content_object.get_ip_type_display()
                requirements = wse.content_object.requirements
                current_state = wse.state.name
                opinion = wse.opinion
                state_value = wse.state_value if wse.state_value else ''

                if wse.state.name == '完成' and request.user.username in get_machine_administrator():
                    can_execute = True
                else:
                    can_execute = False

                data = {
                    'id': id,
                    'applicant': applicant,
                    'title': title,
                    'project': project,
                    'purpose': purpose,
                    'config': config,
                    'number': number,
                    'ip_type': ip_type,
                    'requirements': requirements,
                    'state_value': state_value,
                    'can_execute': can_execute,
                    'opinion': opinion,
                }

                head = {'value': title, 'username': request.user.username}

                return render(request, 'machine_myworkflow.html', {'data': data, 'head': head})

        if isinstance(wse.content_object, ComputerParts):
            recommit = False
            if wse.is_current:
                id = wse.id
                applicant_id = wse.content_object.applicant.id
                applicant = wse.content_object.applicant.username
                title = wse.content_object.title
                reason = wse.content_object.reason
                current_state = wse.state.name
                opinion = wse.opinion
                state_value = wse.state_value if wse.state_value else ''

                if (
                        wse.state.name == '完成' and request.user.username in get_yl_network_administrator() + get_cc_network_administrator() and
                        wse.content_object.status == 1):
                    can_execute = True
                else:
                    can_execute = False

                data = {
                    'title': title,
                    'reason': reason,
                    'applicant_id': applicant_id,
                    'applicant': applicant,
                    'id': id,
                    'recommit': recommit,
                    'can_execute': can_execute,
                    'state_value': state_value,
                    'opinion': opinion,
                }
                head = {'value': title, 'username': request.user.username}

                return render(request, 'computer_parts_myworkflow.html', {'data': data, 'head': head})
            else:
                return render(request, '403.html')
        if isinstance(wse.content_object, VersionUpdate):
            recommit = False
            if wse.is_current:
                id = wse.id
                applicant = wse.content_object.applicant.username
                title = wse.content_object.title
                content = wse.content_object.content
                project = wse.content_object.project.project_name
                start_time = wse.content_object.start_time.strftime('%Y-%m-%d %H:%M:%S')
                end_time = wse.content_object.end_time.strftime('%Y-%m-%d %H:%M:%S')
                client_version = wse.content_object.client_version if wse.content_object.client_version else ''
                server_version = wse.content_object.server_version if wse.content_object.server_version else ''
                client_attention = wse.content_object.client_attention if wse.content_object.client_attention else ''
                client_content = json.loads(
                    wse.content_object.client_content) if wse.content_object.client_content else ''
                server_attention = wse.content_object.server_attention if wse.content_object.server_attention else ''
                new_edition = wse.content_object.new_edition
                server_list = wse.content_object.server_list
                opinion = wse.opinion
                ask_reset = wse.content_object.get_ask_reset_display() if wse.content_object.ask_reset else 'no'
                if request.user.is_superuser and wse.state.name == '完成':
                    if wse.content_object.project.auto_version_update:
                        can_execute = True
                        can_handle = False
                    else:
                        can_execute = False
                        can_handle = True
                else:
                    can_execute = False
                    can_handle = False
                area = wse.content_object.area.chinese_name if wse.content_object.area else ''
                server_range_text = wse.content_object.get_server_range_display() if wse.content_object.server_range else ''
                server_range = wse.content_object.server_range if wse.content_object.server_range else ''
                server_content = wse.content_object.server_content if wse.content_object.server_content else ''
                server_exclude_content = wse.content_object.server_exclude_content if wse.content_object.server_exclude_content else ''
                on_new_server = wse.content_object.on_new_server
                server_erlang = wse.content_object.server_erlang if wse.content_object.server_erlang else ''
                data = {
                    'id': id,
                    'applicant': applicant,
                    'title': title,
                    'content': content,
                    'project': project,
                    'server_list': server_list,
                    'start_time': start_time,
                    'end_time': end_time,
                    'client_version': client_version,
                    'server_version': server_version,
                    'client_attention': client_attention,
                    'server_attention': server_attention,
                    'opinion': opinion,
                    'new_edition': new_edition,
                    'client_content': client_content,
                    'ask_reset': ask_reset,
                    'can_execute': can_execute,
                    'can_handle': can_handle,
                    'area': area,
                    'server_range': server_range,
                    'server_range_text': server_range_text,
                    'server_content': server_content,
                    'server_exclude_content': server_exclude_content,
                    'on_new_server': on_new_server,
                    'server_erlang': server_erlang,
                }
                head = {'value': title, 'username': request.user.username}
                if new_edition:
                    if wse.content_object.project.project_name_en in ('csxy', 'csxybt'):
                        return render(request, 'version_update_myworkflow_v2_csxy.html', {'data': data, 'head': head})
                    else:
                        return render(request, 'version_update_myworkflow_v2.html', {'data': data, 'head': head})
                return render(request, 'version_update_myworkflow.html', {'data': data, 'head': head})
            else:
                return render(request, '403.html')
        if isinstance(wse.content_object, ProjectAdjust):
            recommit = False
            if wse.is_current:
                id = wse.id
                applicant = wse.content_object.applicant.username
                title = wse.content_object.title
                # raw_project_group_obj = wse.content_object.raw_project_group
                # if raw_project_group_obj:
                #     raw_project_group = raw_project_group_obj.project.project_name + '-' + raw_project_group_obj.name
                # else:
                #     raw_project_group = '没有项目分组'

                delete_svn = wse.content_object.delete_svn
                delete_serper = wse.content_object.delete_serper

                # if wse.content_object.new_group_section is not None:
                #     new_group_section_obj = wse.content_object.new_group_section
                #     new_group_section = new_group_section_obj.group.name + '-' + new_group_section_obj.name
                # else:
                #     new_group_section = ''
                """
                2018.12修改
                """
                if wse.content_object.new_department_group is not None:
                    new_department_group = wse.content_object.new_department_group.get_ancestors_name()
                else:
                    new_department_group = ''

                opinion = wse.opinion

                # 要删除的svn和服务器权限的项目
                if wse.content_object.svn_projects is None:
                    svn_projects_id = []
                else:
                    svn_projects_id = json.loads(wse.content_object.svn_projects)

                if wse.content_object.serper_projects is None:
                    serper_projects_id = []
                else:
                    serper_projects_id = json.loads(wse.content_object.serper_projects)

                svn_projects_obj = GameProject.objects.filter(id__in=svn_projects_id)
                serper_projects_obj = GameProject.objects.filter(id__in=serper_projects_id)

                svn_projects = [{'id': x.id, 'text': x.project_name} for x in svn_projects_obj]
                serper_projects = [{'id': x.id, 'text': x.project_name} for x in serper_projects_obj]

                data = {
                    'id': id,
                    'applicant': applicant,
                    'title': title,
                    # 'raw_project_group': raw_project_group,
                    'delete_svn': delete_svn,
                    'delete_serper': delete_serper,
                    'new_department_group': new_department_group,
                    'opinion': opinion,
                    'svn_projects': svn_projects,
                    'serper_projects': serper_projects,
                }
                head = {'value': title, 'username': request.user.username}

                return render(request, 'project_adjust_myworkflow.html', {'data': data, 'head': head})
        if isinstance(wse.content_object, MysqlWorkflow):
            # recommit = True if wse.state_value == '拒绝' else False
            recommit = False
            if wse.is_current:
                id = wse.id
                applicant_id = wse.content_object.applicant.id
                applicant = wse.content_object.applicant.username
                title = wse.content_object.title
                reason = wse.content_object.reason
                content = json.loads(wse.content_object.content)
                current_state = wse.state.name
                opinion = wse.opinion
                state_value = wse.state_value if wse.state_value else ''

                # # 申请人部门，如果有的话，没有为空
                # if wse.content_object.applicant.groups.all():
                #     group = wse.content_object.applicant.groups.all()[0].name
                # else:
                #     group = ''
                #
                # if wse.content_object.applicant.profile.group_section is not None:
                #     group_section = wse.content_object.applicant.profile.group_section.name
                # else:
                #     group_section = '没有分配到管理分组'
                """2018.12修改，合并部门和部门管理分组"""
                org = OrganizationMptt.objects.get(user_id=wse.content_object.applicant.id)
                belongs_to_new_organization = org.get_ancestors_except_self()

                if request.user.is_superuser:
                    can_execute = True
                else:
                    can_execute = False

                data = {
                    'title': title,
                    'content': content,
                    'applicant': applicant,
                    'group': belongs_to_new_organization,
                    'group_section': belongs_to_new_organization,
                    'id': id,
                    'recommit': recommit,
                    'can_execute': can_execute,
                    'state_value': state_value,
                    'opinion': opinion,
                    'reason': reason,
                }
                head = {'value': title, 'username': request.user.username}

                return render(request, 'mysql_myworkflow.html', {'data': data, 'head': head})
            else:
                return render(request, '403.html')


def workflow_state_approve_process(request):
    '获取流程进度'

    if request.method == "POST":
        pdata = json.loads(request.body.decode('utf-8'))
        wse = pdata.get('wse')
        wse = WorkflowStateEvent.objects.get(id=wse)
        step, current_index = get_workflow_state_approve_process(wse)
        success = True
        return JsonResponse({'data': step, 'success': success, 'current_index': current_index})


def send_mail_for_wse(request):
    '发送邮件'
    if request.method == 'POST':
        wse = json.loads(request.body.decode('utf-8'))
        wse = WorkflowStateEvent.objects.get(id=wse)

        if wse.send_mail == 1:
            msg = '已经发送'
            success = False
        else:
            try:
                # 找出当前节点的审批人
                to_list = [x.email for x in get_state_user(wse.state, obj=wse.content_object) if
                           x.email and x.is_active]
                if to_list:
                    """给celery发送队列消息,发送邮件"""
                    subject, content = make_email(wse)

                    send_mail.delay(to_list, subject, content)

                    wse.send_mail = 1
                    wse.save(update_fields=['send_mail'])

                    success = True
                    msg = ''
                else:
                    msg = '找不到收件人'
                    success = False
            except Exception as e:
                msg = str(e)
                success = False

        return JsonResponse({'data': msg, 'success': success})


def test_load(request):
    if request.method == "POST":
        result = True
        data = '执行成功'
        svn_log = SVNLog()
        wse = json.loads(request.body.decode('utf-8'))
        wse = WorkflowStateEvent.objects.get(id=wse.get('wse'))
        content_object = wse.content_object

        try:
            if wse.state.workflow.name == "SVN申请":
                payload = format_svn(wse.content_object)
                url = 'https://192.168.40.11/api/addprivilege/'
                headers = {
                    'Accept': 'application/json',
                    'Authorization': 'Token d11205fc792d2d2def44ca55e5252dcbdcea6961',
                    'Connection': 'keep-alive',
                }
                r = requests.post(url, headers=headers, data=payload, verify=False)
                svn_log.logger.info('%s: %d: %s' % (wse.content_object.title, r.status_code, r.text))
                msg = r.json()
                result = msg['result']
                data = msg['data']
                if result:
                    content_object.status = 0
                else:
                    content_object.status = 2
                content_object.save(update_fields=['status'])
            if wse.state.workflow.name == "数据库权限申请":
                result, data = add_mysql_permission(wse.id)
        except requests.exceptions.ConnectionError:
            data = 'time out'
            result = False
            if isinstance(wse.content_object, SVNWorkflow):
                content_object.status = 2
            if isinstance(wse.content_object, MysqlWorkflow):
                content_object.status = 1
            content_object.save(update_fields=['status'])
        except Exception as e:
            data = str(e)
            result = False
            if isinstance(wse.content_object, SVNWorkflow):
                content_object.status = 2
            if isinstance(wse.content_object, MysqlWorkflow):
                content_object.status = 1
            content_object.save(update_fields=['status'])

        return JsonResponse({"result": result, "data": data})


def add_server_permission(request):
    '添加服务器权限'
    if request.method == "POST":
        wse = json.loads(request.body.decode('utf-8'))
        wse = WorkflowStateEvent.objects.get(id=wse.get('wse'))
        if isinstance(wse.content_object, ServerPermissionWorkflow):
            result, data = api_add_server_permission(wse)
            return JsonResponse({"result": result, "data": data})
        if isinstance(wse.content_object, Machine):
            wse.content_object.status = 0
            wse.content_object.save()
            machine_administrator_list = [u.first_name for u in
                                          User.objects.filter(username__in=get_machine_administrator())]
            touser = machine_administrator_list
            update_wx_taskcard_status(touser, wse, purchase=True)
            return JsonResponse({"result": True, "data": '完成'})


def failure_declare_finish(request, update_taskcard=True):
    """设置工单状态为已处理"""
    if request.method == "POST":
        wse = json.loads(request.body.decode('utf-8'))
        wse = WorkflowStateEvent.objects.get(id=wse.get('wse'))
        network_administrator_list = get_cc_network_administrator() + get_yl_network_administrator()
        if update_taskcard:
            touser = [u.first_name for u in User.objects.filter(username__in=network_administrator_list)]
            update_wx_taskcard_status(touser, wse, handle=True)
        if isinstance(wse.content_object, FailureDeclareWorkflow):
            wse.content_object.status = 0
            wse.content_object.save()
            return JsonResponse({"result": True, "data": '完成'})
        elif isinstance(wse.content_object, Wifi):
            wse.content_object.status = 0
            wse.content_object.save()
            return JsonResponse({"result": True, "data": '完成'})
        elif isinstance(wse.content_object, ComputerParts):
            wse.content_object.status = 0
            wse.content_object.save()
            return JsonResponse({"result": True, "data": '完成'})
        elif isinstance(wse.content_object, VersionUpdate):
            wse.content_object.status = 0
            wse.content_object.save()
            return JsonResponse({"result": True, "data": '完成'})


def transfer_to_other_admin(request):
    """电脑故障工单转交给其他网管处理
    """
    if request.method == "POST":
        try:
            pdata = json.loads(request.body.decode('utf-8'))
            wse = WorkflowStateEvent.objects.get(id=pdata.get('wse'))
            to_anthoer_admin = User.objects.get(id=pdata.get('to_anthoer_admin'))
            if wse.state.workflow.name == 'wifi申请和网络问题申报':
                sor = get_sor(wse.state, wse.content_object)
            elif isinstance(wse.content_object, ComputerParts):
                sor = get_sor(wse.state, wse.content_object)
            else:
                sor = get_sor(wse.state, wse.content_object)
            if sor:
                sor.users.clear()
                sor.users.add(to_anthoer_admin)
                wse.users.clear()
                wse.users.add(to_anthoer_admin)
                data = ''
                success = True
                # 如果不是版本更新单，发送企业微信审批
                if not isinstance(wse.content_object, VersionUpdate):
                    touser = '|'.join([u.first_name for u in wse.users.all()])
                    if touser:
                        result = get_wx_task_card_data(touser, wse)
                        if result['success']:
                            send_task_card_to_wx_user.delay(touser, result['data'])
            else:
                raise Exception("找不到sor")
        except WorkflowStateEvent.DoesNotExist:
            data = '找不到wse'
            success = False
        except User.DoesNotExist:
            data = '找不到转交网管'
            success = False
        except Exception as e:
            data = str(e)
            success = False
        return JsonResponse({"data": data, "success": success})


def get_project_area_lock(request):
    """获取项目和地区的锁
    """
    if request.method == "GET":
        project = request.GET.get('project', None)
        area_name = request.GET.get('area_name', None)
        msg = ''

        try:
            project = GameProject.objects.get(id=project)
            all_ops_manager = OpsManager.objects.filter(project=project, room__area__chinese_name=area_name)

            if not all_ops_manager:
                raise Exception('没有找到运维管理机')
            else:
                for x in all_ops_manager:
                    if x.status != '0':
                        raise Exception('运维管理机%s在%s中' % (x.url, x.get_status_display()))
                success = True

        except GameProject.DoesNotExist:
            msg = '游戏项目不存在'
            success = False
        except Exception as e:
            msg = str(e)
            success = False
        return JsonResponse({"success": success, "msg": msg})


def get_pair_code_order_available(request):
    """根据项目地区和绑定代号以及先后顺序判断可用性
    还有根据前后端热更新来判断
    """
    if request.method == "GET":
        project = request.GET.get('project', None)
        area_name = request.GET.get('area_name', None)
        pair_code = request.GET.get('pair_code', None)
        order = request.GET.get('order', None)
        update_type = request.GET.get('update_type', None)

        try:
            project = GameProject.objects.get(id=project)
            msg, success = _pair_code_order_updatetype_available(project, area_name, pair_code, order, update_type)
        except MultipleObjectsReturned:
            msg = '找到包含相同代号的热更新'
            success = False
        except GameProject.DoesNotExist:
            msg = '游戏项目不存在'
            success = False
        except Exception as e:
            msg = str(e)
            success = False
        return JsonResponse({"success": success, "msg": msg})


def get_client_type(request):
    """获取客户端类型
    安卓或者iOS
    """
    if request.method == "POST":
        pdata = json.loads(request.body.decode('utf-8'))
        project = pdata.get('project')

        project = GameProject.objects.get(id=project)

        client_type = GameServer.objects.filter(project=project)[0].project_type

        return JsonResponse({"client_type": client_type})


def upload_hot_server(request):
    """上传热更新文件
    上传的文件传送目录规范:
    主目录是/data/www/cmdb/myworkflows/upload/hot_server
    然后根据uuid来生成目录下面的文件
    """
    if request.method == "POST":
        try:
            success = True
            file_data = request.FILES.get('file_name')  # file_data是UploadedFile对象
            uuid = request.POST.get('uuid')
            file_name = file_data.name
            pdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'upload', 'hot_server', uuid)

            # 创建对应的文件夹
            os.makedirs(pdir, exist_ok=True)

            file_path = os.path.join(pdir, file_name)

            # 如果是大文件，通过生成器去读
            """
            if file_data.multiple_chunks(chunk_size='1k'):
                with open(file_path, 'wb+') as f:
                    for chunk in file_data.chunks():
                        f.write(chunk)
            else:
                with open(file_path, 'wb+') as f:
                    f.write(file_data.read())
            """
            with open(file_path, 'wb+') as f:
                for chunk in file_data.chunks():
                    f.write(chunk)

            # 返回文件的MD5值
            fmd5 = hashlib.md5(open(file_path, 'rb').read()).hexdigest()
        except Exception as e:
            success = False
            fmd5 = '上传文件失败'

        return JsonResponse({"file_name": file_name, "fmd5": fmd5, "success": success})


def hot_update_api(request):
    """热更新文档
    """
    if request.method == "GET":
        if request.user.is_superuser:
            return render(request, 'hot_update_api.html')
        else:
            return render(request, '403.html')


def change_approve(request):
    """更改审批人
    """
    if request.method == "GET":
        id = request.GET.get('id')
        wse = WorkflowStateEvent.objects.get(id=id)
        if request.user == wse.content_object.creator:
            current_state = wse.state
            order_state = get_workflow_state_order(current_state.workflow)
            not_approve_state = order_state[order_state.index(current_state):]

            if len(not_approve_state) == 1 and not_approve_state[0].name == '完成':
                return HttpResponse('你的工单已经审批完成')

            if isinstance(wse.content_object, VersionUpdate):
                id = wse.id
                project_id = wse.content_object.project.id
                current_state_id = wse.state.id
                current_state_name = wse.state.name
                # sor = get_sor(wse.state, wse.content_object)
                user = wse.users.all()[0]

                data = {
                    "id": wse.id,
                    "applicant": wse.content_object.applicant,
                    "title": wse.content_object.title,
                    "project_id": project_id,
                    "current_state_id": current_state_id,
                    "current_state_name": current_state_name,
                    "user_id": user.id,
                    "user_name": user.username,
                }
                head = {'value': '更改审批人', 'username': request.user.username}
                return render(request, 'version_update_change_approve.html', {"data": data, "head": head})
            if isinstance(wse.content_object, ClientHotUpdate) or isinstance(wse.content_object, ServerHotUpdate):
                id = wse.id
                project_id = wse.content_object.project.id
                current_state_name = wse.state.name
                workflow_name = wse.state.workflow.name
                users = ','.join([x.username for x in wse.users.all()])

                data = {
                    'id': wse.id,
                    'applicant': wse.content_object.applicant,
                    'title': wse.content_object.title,
                    'project_id': project_id,
                    'current_state_name': current_state_name,
                    'workflow_name': workflow_name,
                    'users': users,
                }
                head = {'value': '更改审批人', 'username': request.user.username}
                if wse.content_object.project.project_name_en == 'csxy':
                    return render(request, 'csxy_hot_update_change_approve.html', {"data": data, "head": head})
                else:
                    return render(request, 'hot_update_change_approve.html', {"data": data, "head": head})
        else:
            return render(request, '403.html')
    if request.method == "POST":
        pdata = json.loads(request.body.decode('utf-8'))
        wse = pdata.get('wse')
        change_approve = pdata.get('change_approve')

        wse = WorkflowStateEvent.objects.get(id=wse)
        change_approve = User.objects.get(id=change_approve)
        sor = get_sor(wse.state, wse.content_object)
        # 清除之前的审批用户
        sor.users.clear()
        wse.users.clear()
        # 添加现在的用户
        sor.users.add(change_approve)
        wse.users.add(change_approve)

        # 发送qq提醒
        users = ','.join([x.first_name for x in [change_approve]])
        data = get_qq_notify()
        send_qq.delay(
            users, data['window_title'], data['tips_title'], data['tips_content'], data['tips_url'])
        # 发送wx弹框提醒
        wx_users = '|'.join([x.first_name for x in [change_approve]])
        if wx_users:
            if isinstance(wse.content_object, VersionUpdate):
                data = get_wx_notify()
                send_weixin_message.delay(touser=wx_users, content=data)
            # 如果不是版本更新单，发送微信任务卡片
            if not isinstance(wse.content_object, VersionUpdate):
                result = get_wx_task_card_data(wx_users, wse, change_approve=True)
                if result['success']:
                    send_task_card_to_wx_user.delay(wx_users, result['data'])

        return JsonResponse({"success": True, "data": "ok"})


def hotupdate_cmdb_log(request):
    """cmdb热更新日志
    """
    if request.method == "GET":
        head = {'value': '热更新log', 'username': request.user.username}
        return render(request, 'hotupdate_cmdb_log.html', {"head": head})


def real_time_log(request):
    """测试实时log
    """
    if request.method == "GET":
        head = {'value': '实时log', 'username': request.user.username}
        return render(request, 'real_time_log.html', {"head": head})


def download_hotupdate(request):
    """导出热更新excel的数据
    需要有项目上的权限!
    请求的数据
    {
        'filter_hotupdate_type': '全部', 'filter_priority': '全部', 'filter_start_time': '',
        'filter_project': '23', 'filter_end_time': '', 'filter_area_name': '', 'filter_title': '', 'filter_status': '全部'
    }
    """
    if request.method == "POST":
        pdata = json.loads(request.body.decode('utf-8'))
        filter_project = pdata.get('filter_project', 0)

        try:
            project = GameProject.objects.get(id=filter_project)
            perm = 'users.view_' + project.project_name_en
            if request.user.has_perm(perm):
                # 自定义的查询参数
                filter_hotupdate_type = pdata.get('filter_hotupdate_type', '全部')
                filter_area_name = pdata.get('filter_area_name', '')
                filter_title = pdata.get('filter_title', '')
                filter_priority = pdata.get('filter_priority', '全部')
                filter_status = pdata.get('filter_status', '全部')
                filter_start_time = pdata.get('filter_start_time', '')
                filter_end_time = pdata.get('filter_end_time', '')

                # 添加sub_query
                sub_query = Q()

                # 添加项目的过滤
                sub_query.add(Q(project=project), Q.AND)

                if filter_area_name:
                    sub_query.add(Q(area_name__icontains=filter_area_name), Q.AND)

                if filter_title:
                    sub_query.add(Q(title__icontains=filter_title), Q.AND)

                if filter_priority != '全部':
                    sub_query.add(Q(priority=filter_priority), Q.AND)

                if filter_status != '全部':
                    sub_query.add(Q(status=filter_status), Q.AND)

                if filter_start_time:
                    sub_query.add(Q(create_time__gte=filter_start_time), Q.AND)

                if filter_end_time:
                    sub_query.add(Q(create_time__lte=filter_end_time), Q.AND)

                if filter_hotupdate_type == '前端':
                    reversed_hot_server_iter = ServerHotUpdate.objects.none()
                    reversed_hot_client_iter = ClientHotUpdate.objects.select_related(
                        'project').exclude(status='0').filter(sub_query).order_by('-create_time')
                elif filter_hotupdate_type == '后端':
                    reversed_hot_client_iter = ClientHotUpdate.objects.none()
                    reversed_hot_server_iter = ServerHotUpdate.objects.select_related(
                        'project').exclude(status='0').filter(sub_query).order_by('-create_time')
                else:
                    reversed_hot_server_iter = ServerHotUpdate.objects.select_related(
                        'project').exclude(status='0').filter(sub_query).order_by('-create_time')
                    reversed_hot_client_iter = ClientHotUpdate.objects.select_related(
                        'project').exclude(status='0').filter(sub_query).order_by('-create_time')

                heapq_merge = heapq.merge(
                    reversed_hot_server_iter, reversed_hot_client_iter, key=lambda obj: obj.create_time, reverse=True)

                data, success = gen_hotupdate_excel(project.project_name_en, heapq_merge)
            else:
                raise Exception('权限拒绝')
        except Exception as e:
            data = str(e)
            success = False
        return JsonResponse({'data': data, 'success': success})


def get_csxy_game_server_platform(request):
    """获取超神项目的平台下拉列表
    """
    if request.method == "POST":
        data = []

        q = request.POST.get('q', '')
        project = request.POST.get('project', 0)
        area_name = request.POST.get('area_name', 'xxxxxx')

        project = GameProject.objects.get(id=project)

        all_pf_name = GameServer.objects.values('pf_name').filter(
            project=project, area_name=area_name, pf_name__icontains=q).annotate(count=Count('pf_name'))

        for x in all_pf_name:
            data.append({'id': x['pf_name'], 'text': x['pf_name']})

        return JsonResponse(data, safe=False)


def get_csxy_type(request):
    """获取超神项目的平台下拉列表
    """
    if request.method == "POST":
        data = []

        q = request.POST.get('q', '')
        area_name = request.POST.get('area_name', 'xxxxxx')
        area_name_en = Area.objects.get(chinese_name=area_name).short_name
        area_name_en = area_name_en.lower()

        data = [{'id': x, 'text': x} for x in CSXY_TYPES.get(area_name_en, []) if q in x]

        return JsonResponse(data, safe=False)


def get_workflow_approve_user(request):
    """获取流程的审批用户
    """
    if request.method == "POST":
        raw_data = json.loads(request.body.decode('utf-8'))
        if NEW_WORKFLOW == 1:
            workflow = Workflow.objects.get(id=raw_data.pop('workflow'))
            success, msg, approve_user_list, approve_chain_dict = get_approve_user_chain(workflow, **raw_data)
        else:
            workflow = Workflow.objects.get(id=raw_data.get('workflow'))
            workflow_model = workflow.workflow_type.model
            success, msg = workflow_approve_user(workflow_model, **raw_data)
        return JsonResponse({'success': success, 'data': msg})


def svn_repo(request):
    if request.method == "GET":
        if request.user.is_superuser:
            head = {'username': request.user.username}
            html_file = 'svn_repo.html'
            return render(request, html_file, {'head': head, 'user': request.user})
        else:
            return render(request, '403.html', {'head': {'username': request.user.username}})


def data_svn_repo(request):
    if request.method == "GET":
        if request.user.is_superuser:
            raw_get = request.GET.dict()
            draw = raw_get.get('draw', 0)
            raw_data = SVNRepo.objects.all()
            recordsTotal = len(raw_data)
            data = {"data": [i.show_all() for i in raw_data], 'draw': draw, 'recordsTotal': recordsTotal,
                    'recordsFiltered': recordsTotal}
            return JsonResponse(data)
        else:
            return render(request, '403.html')


def get_svn_repo(request):
    if request.method == 'POST':
        if request.user.is_superuser:
            raw_data = json.loads(request.body.decode('utf-8'))
            svn_id = raw_data.get('id')
            svn_repo = SVNRepo.objects.get(pk=svn_id)
            edit_data = svn_repo.edit_data()
            return JsonResponse(edit_data)
        else:
            raise PermissionDenied


def add_or_edit_repo(request):
    """增加或者修改仓库信息"""

    if request.method == "POST":
        raw_data = json.loads(request.body.decode('utf-8'))
        msg = 'ok'
        editFlag = raw_data.pop('editFlag')
        id = raw_data.pop('id')

        try:
            if editFlag:
                repo = SVNRepo.objects.filter(id=id)
                repo.update(**raw_data)
                success = True
            else:
                if request.user.is_superuser:
                    SVNRepo.objects.create(**raw_data)
                    success = True
                else:
                    raise PermissionDenied
        except PermissionDenied:
            msg = '你没有增加svn仓库的权限'
            success = False
        except Exception as e:
            msg = str(e)
            success = False

        return JsonResponse({'data': success, 'msg': msg})


def del_svn_repo(request):
    """删除svn仓库"""

    if request.method == "POST":
        del_data = json.loads(request.body.decode('utf-8'))
        try:
            objs = SVNRepo.objects.filter(id__in=del_data)
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


def game_server_install(request):
    if request.user.is_superuser:
        return render(request, 'game_server_install.html', {})
    else:
        return render(request, '403.html')


def list_game_server(request):
    """
    根据地区和项目条件列出区服
    """

    if request.method == "POST":
        data = []

        q = request.POST.get('q', None)
        project_id = request.POST.get('project', None)
        area_name = request.POST.get('area_name', None)

        if q:
            game_server = [x for x in
                           GameServer.objects.select_related('host__belongs_to_room__area').filter(srv_status=0,
                                                                                                   merge_id=None,
                                                                                                   project__id=project_id,
                                                                                                   host__belongs_to_room__area__chinese_name=area_name).filter(
                               Q(project__project_name_en__icontains=q) | Q(project__project_name__icontains=q) | Q(
                                   srv_id__icontains=q) | Q(sid__icontains=q))
                           ]
        else:
            game_server = GameServer.objects.filter(srv_status=0, project__id=project_id, merge_id=None,
                                                    host__belongs_to_room__area__chinese_name=area_name)

        for x in game_server:
            data.append({'id': x.id, 'text': 'cmdb区服id：' + str(x.srv_id or '') + ' - ' + 'web区服id：' + str(x.sid or '')})

        return JsonResponse(data, safe=False)


def list_area_name_by_project(request):
    """根据项目列出地区"""
    if request.method == "POST":
        data = []
        q = request.POST.get('q', None)
        project_id = request.POST.get('project', None)

        if q:
            area_list = [x['host__belongs_to_room__area__chinese_name'] for x in
                         GameServer.objects.select_related('host').filter(srv_status=0, project__id=project_id).values(
                             'host__belongs_to_room__area__chinese_name').annotate(
                             count=Count('host__belongs_to_room__area__chinese_name')) if
                         re.search(q, x['host__belongs_to_room__area__chinese_name'])]
        else:
            area_list = [x['host__belongs_to_room__area__chinese_name'] for x in
                         GameServer.objects.select_related('host').filter(srv_status=0, project__id=project_id).values(
                             'host__belongs_to_room__area__chinese_name').annotate(
                             count=Count('host__belongs_to_room__area__chinese_name'))]
        for x in area_list:
            data.append({'id': x, 'text': x})
        return JsonResponse(data, safe=False)


def game_server_action(request):
    """区服管理操作，开关服，重启，清档"""
    if request.method == "POST":
        msg = 'ok'
        try:
            source_ip = get_ip(request)
            raw_data = json.loads(request.body.decode('utf-8'))
            action_type = raw_data.get('action_type', '')
            batch = raw_data.get('batch', '')
            game_server_id = raw_data.get('game_server_id', '')
            if batch:
                game_server_id_list = game_server_id
            else:
                game_server_id_list = [game_server_id]

            """异步调用运维管理机接口"""
            game_server_action_task.delay(action_type, game_server_id_list, batch, request.user.id, source_ip)

            return JsonResponse({'success': True, 'msg': msg})
        except Exception as e:
            return JsonResponse({'success': False, 'msg': str(e)})


def list_cdn_root_url(request):
    """
    根据项目列出所有cdn根目录
    """

    if request.method == "POST":
        data = []

        project = request.POST.get('project')
        area_name = request.POST.get('area_name')

        project = GameProject.objects.get(id=project)

        cdn_version = list(
            GameServer.objects.values(
                'cdn_root_url').filter(
                project=project, srv_status=0, area_name=area_name, merge_id=None).annotate(id=Max('id'))
        )

        for x in cdn_version:
            data.append({'id': x['cdn_root_url'], 'text': x['cdn_root_url']})

        return JsonResponse(data, safe=False)


def game_server_action_record(request):
    """区服管理操作记录"""
    if request.method == 'GET':
        if request.user.is_superuser:
            game_project = GameProject.objects.filter(is_game_project=1)
            status_list = GameServerActionRecord.ACTION_RESULT
            user = User.objects.filter(is_active=1)
            return render(request, 'game_server_action_record.html',
                          {'game_project': game_project, 'status_list': status_list, 'user': user})
        else:
            return render(request, '403.html')


def data_game_server_action_record(request):
    """区服管理操作记录的数据"""
    if request.method == "POST":
        if request.user.is_superuser:
            raw_get = request.POST.dict()

            search_value = raw_get.get('search[value]', '')
            start = int(raw_get.get('start', 0))
            draw = raw_get.get('draw', 0)
            length = int(raw_get.get('length', 10))

            filter_uuid = raw_get.get('filter_uuid', '')
            filter_project = raw_get.get('filter_project', '全部')
            filter_game_server = raw_get.get('filter_game_server', '')
            filter_status = raw_get.get('filter_status', '全部')
            filter_operation_user = raw_get.get('filter_operation_user', '全部')
            filter_start_operation_time = raw_get.get('filter_start_operation_time', '')
            filter_end_operation_time = raw_get.get('filter_end_operation_time', '')

            # 添加sub_query
            sub_query = Q()

            if filter_uuid != '':
                sub_query.add(Q(uuid__icontains=filter_uuid), Q.AND)

            if filter_project != '全部':
                project = GameProject.objects.get(pk=filter_project)
                sub_query.add(Q(game_server__project=project), Q.AND)

            if filter_game_server != '':
                sub_query.add(Q(game_server__srv_id__icontains=filter_game_server), Q.AND)

            if filter_status != '全部':
                sub_query.add(Q(result=filter_status), Q.AND)

            if filter_operation_user != '全部':
                user = User.objects.get(pk=filter_operation_user)
                sub_query.add(Q(operation_user=user), Q.AND)

            if filter_start_operation_time != '':
                sub_query.add(Q(operation_time__gte=filter_start_operation_time), Q.AND)

            if filter_end_operation_time != '':
                sub_query.add(Q(operation_time__lte=filter_end_operation_time), Q.AND)

            if search_value:
                action_type_list = [x[0] for x in GameServerActionRecord.ACTION_TYPE if x[1] == search_value]
                action_result_list = [x[0] for x in GameServerActionRecord.ACTION_RESULT if x[1] == search_value]
                query = GameServerActionRecord.objects.select_related('game_server').prefetch_related(
                    'operation_user').filter((
                        Q(uuid__icontains=search_value) |
                        Q(game_server__project__project_name__icontains=search_value) |
                        Q(game_server__project__project_name_en__icontains=search_value) |
                        Q(game_server__srv_id__icontains=search_value) |
                        Q(game_server__sid__icontains=search_value) |
                        Q(game_server__host__belongs_to_room__area__chinese_name=search_value) |
                        Q(game_server__host__belongs_to_room__area__short_name=search_value) |
                        Q(operation_type__in=action_type_list) |
                        Q(operation_user__username__icontains=search_value) |
                        Q(operation_user__first_name__icontains=search_value) |
                        Q(result__in=action_result_list) |
                        Q(remark__icontains=search_value) & sub_query)
                ).order_by('-operation_time').distinct()

            else:
                query = GameServerActionRecord.objects.select_related(
                    'game_server').prefetch_related('operation_user').filter(sub_query).order_by('-operation_time')

            raw_data = query[start: start + length]
            recordsTotal = query.count()
            data = {"data": [i.show_all() for i in raw_data], 'draw': draw, 'recordsTotal': recordsTotal,
                    'recordsFiltered': recordsTotal}
            return JsonResponse(data)


def celery_worker_status(request):
    """cdn api接口信息"""
    if request.user.is_superuser:
        all_workers = CeleryWorkerStatus.objects.order_by('status')
        return render(request, 'celery_worker_status.html', {'all_workers': all_workers})
    else:
        return render(request, '403.html')


def sync_running_worker(request):
    """同步正在运行的worker"""
    result = get_celery_worker_status()
    # 获取需要发送告警信息的用户
    users = [x.receive_user for x in CeleryReceiveNoticeUser.objects.all()]
    wx_touser = '|'.join([x.first_name for x in users])
    qq_user = ','.join([x.first_name for x in users])
    to_list = [x.email for x in users]
    # 判断同步是否成功
    if 'ERROR_KEY' in result.keys() or 'ERROR' in result.keys():
        return JsonResponse({'success': False, 'msg': '同步失败，请重新同步！'})
    else:
        try:
            # 提取同步结果
            celery_dict = {}
            for k, v in result.items():
                total = result[k]['total']
                if total:
                    celery_dict[k] = {'total': list(result[k]['total'].values())[0]}
                else:
                    celery_dict[k] = {'total': 0}
            running_worker_list = [x for x in celery_dict.keys()]
            db_workers_list = [x.celery_hostname for x in CeleryWorkerStatus.objects.all()]
            # 保存数据库
            for worker in db_workers_list:
                if worker not in running_worker_list:
                    obj = CeleryWorkerStatus.objects.get(celery_hostname=worker)
                    obj.status = 0
                    obj.off_count += 1
                    obj.save()
                    # 发送worker离线消息，判断告警次数是否为6的倍数或等于1，是则发送告警
                    if obj.off_count % 6 == 0 or obj.off_count == 1:
                        content = worker + '离线'
                        send_mail.delay(to_list, content, content)
                        send_weixin_message.delay(touser=wx_touser, content=content)
                        send_qq.delay(qq_user, 'worker离线', 'worker离线', content, '')
                else:
                    obj = CeleryWorkerStatus.objects.get(celery_hostname=worker)
                    obj.total = celery_dict[worker]['total']
                    if obj.status == 0:
                        obj.status = 1
                        obj.off_count = 0
                        # 发送worker上线消息
                        content = worker + '恢复'
                        send_mail.delay(to_list, content, content)
                        send_weixin_message.delay(touser=wx_touser, content=content)
                        send_qq.delay(qq_user, 'worker恢复', 'worker恢复', content, '')
                    obj.save()
            for worker in running_worker_list:
                if worker not in db_workers_list:
                    CeleryWorkerStatus.objects.create(celery_hostname=worker, total=celery_dict[worker]['total'])
            return JsonResponse({'success': True, 'msg': '同步成功'})
        except Exception as e:
            return JsonResponse({'success': False, 'msg': str(e)})


def save_celery_notice_receive_user(request):
    """保存接收celery告警信息的人员"""
    if request.method == 'POST':
        if request.user.is_superuser:
            success = True
            msg = 'ok'
            try:
                raw_data = json.loads(request.body.decode('utf-8'))
                receive_user_list = raw_data.get('receive_user', '')
                CeleryReceiveNoticeUser.objects.all().delete()
                for receive_user_id in receive_user_list:
                    CeleryReceiveNoticeUser.objects.create(receive_user_id=receive_user_id)
            except Exception as e:
                success = False
                msg = str(e)
            finally:
                return JsonResponse({'success': success, 'msg': msg})


def get_celery_notice_receive_user(request):
    """获取接收celery告警信息人员的名单"""
    if request.method == 'GET':
        if request.user.is_superuser:
            success = True
            msg = 'ok'
            try:
                receive_user = [{'id': x.receive_user.id, 'username': x.receive_user.username} for x in
                                CeleryReceiveNoticeUser.objects.all()]
                return JsonResponse({'success': success, 'msg': msg, 'receive_user': receive_user})
            except Exception as e:
                msg = str(e)
                success = False
                return JsonResponse({'success': success, 'msg': msg})


def delete_worker_monitor(request):
    """取消需要监控的worker"""
    msg = 'ok'
    success = True
    try:
        if request.user.is_superuser and request.method == 'POST':
            del_data = json.loads(request.body.decode('utf-8'))
            cdn_api = CeleryWorkerStatus.objects.filter(id__in=del_data)
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


def list_room_name_by_project(request):
    """根据项目列出机房"""
    if request.method == "POST":
        data = []
        q = request.POST.get('q', None)
        project = request.POST.get('project', None)
        try:
            project = GameProject.objects.get(pk=project)
        except:
            project = GameProject.objects.get(project_name=project)

        if q:
            room_list = [x['room__area__chinese_name'] + '-' + x['room__room_name'] for x in
                         GameServer.objects.filter(srv_status=0, project=project).values(
                             'room__room_name', 'room__area__chinese_name').annotate(
                             count=Count('room__room_name')) if
                         re.search(q, x['room__room_name']) or re.search(q, x['room__area__chinese_name'])]
        else:
            room_list = [x['room__area__chinese_name'] + '-' + x['room__room_name'] for x in
                         GameServer.objects.filter(srv_status=0, project=project).values(
                             'room__room_name', 'room__area__chinese_name').annotate(
                             count=Count('room__room_name'))]
        for x in room_list:
            data.append({'id': x, 'text': x})
        return JsonResponse(data, safe=False)


def host_compression_apply(request):
    """提交主机迁服/回收申请"""
    if request.method == 'POST':
        success = True
        msg = 'ok'
        try:
            if not request.user.has_perm('users.host_compression_apply'):
                raise PermissionDenied('权限受限')
            raw_data = json.loads(request.body.decode('utf-8'))
            ops_id = raw_data.pop('ops_id', '')
            ops_user = User.objects.get(pk=ops_id)
            raw_data['ops'] = ops_user
            ip = raw_data.pop('ip', '')
            raw_data['type'] = int(raw_data['type'])
            type = raw_data.get('type')
            raw_data['apply_user'] = request.user.username
            project_id = raw_data.pop('project', '')
            project = GameProject.objects.get(pk=project_id)
            raw_data['project'] = project
            room = raw_data.get('room', '')
            room_name = room.split('-')[-1]
            area = room.split('-')[0]
            room = Room.objects.get(room_name=room_name, area__chinese_name=area)
            raw_data['room'] = room
            """ip列表格式化，去空格，去重复"""
            ip = ip.split('\n')
            ip = [not_empty(x) for x in ip if x != '' and x is not None]
            ip = list(set(ip))
            """创建申请单，保存IP地址明细，创建日志记录"""
            apply_obj = HostCompressionApply.objects.create(**raw_data)
            for x in ip:
                detail = HostCompressionDetail.objects.create(apply=apply_obj, ip=x)
                """如果是迁服回收，则创建迁服明细表记录"""
                if type == 2:
                    host = Host.objects.filter(telecom_ip=x)
                    if host:
                        host = host[0]
                    else:
                        raise Exception('IP：%s，主机不存在' % x)
                    for sid in host.get_sid_list():
                        HostMigrateSrvDetail.objects.create(migrate_host=detail, sid=sid)
            HostCompressionLog.objects.create(host_compression=apply_obj)

            """邮件/QQ/微信通知运维负责人"""
            subject = '您有一个新的主机{}任务！'.format(apply_obj.get_type_display())
            if apply_obj.type == 2:
                content = '您所负责的主机%s任务%s，将在%s自动执行，请届时留意任务结果！' % (
                    apply_obj.get_type_display(), apply_obj.title, str(apply_obj.action_time))
            else:
                content = '您所负责的主机%s任务%s，将在%s自动执行，请届时留意任务结果！' % (
                    apply_obj.get_type_display(), apply_obj.title, str(apply_obj.recover_time))
            to_list = [ops_user.email]
            users = ops_user.first_name
            wx_users = ops_user.first_name
            if not PRODUCTION_ENV:
                to_list = ['chenjiefeng@forcegames.cn']
                users = 'chenjiefeng'
                wx_users = users
            if to_list:
                send_mail.delay(to_list, subject, content)
            if users:
                send_qq.delay(users, subject, subject, content, '')
            if wx_users:
                send_weixin_message.delay(touser=wx_users, content=subject + content)
        except Host.DoesNotExist:
            success = False
            msg = '主机不存在，请确认IP地址'
        except Exception as e:
            success = False
            msg = str(e)
        finally:
            return JsonResponse({'success': success, 'msg': msg})


def host_compression_apply_list(request):
    """主机迁服/回收申请记录列表页"""
    if request.method == 'GET':
        if request.user.has_perm('users.view_host_compression'):
            all_users = [{'id': x.id, 'text': x.username} for x in User.objects.all()]
            return render(request, 'host_compression_apply_list.html', {'all_users': all_users})
        else:
            return render(request, '403.html')


def data_host_compression_apply_list(request):
    """主机迁服/回收申请的列表数据"""
    if request.method == "POST":
        raw_get = request.POST.dict()

        search_value = raw_get.get('search[value]', '')
        start = int(raw_get.get('start', 0))
        draw = raw_get.get('draw', 0)
        length = int(raw_get.get('length', 10))

        filter_title = raw_get.get('filter_title', '')
        filter_ops = raw_get.get('filter_ops', 0)
        filter_type = raw_get.get('filter_type', 0)
        filter_action_status = raw_get.get('filter_action_status', 0)
        filter_recover_status = raw_get.get('filter_recover_status', 0)
        filter_start_action_time = raw_get.get('filter_start_action_time', '')
        filter_end_action_time = raw_get.get('filter_end_action_time', '')
        filter_start_recover_time = raw_get.get('filter_start_recover_time', '')
        filter_end_recover_time = raw_get.get('filter_end_recover_time', '')
        filter_start_apply_time = raw_get.get('filter_start_apply_time', '')
        filter_end_apply_time = raw_get.get('filter_end_apply_time', '')
        filter_apply_user = raw_get.get('filter_apply_user', '')
        filter_project = raw_get.get('filter_project', '')
        filter_room = raw_get.get('filter_room', '')
        filter_apply_user = raw_get.get('filter_apply_user', 0)

        # 添加sub_query
        sub_query = Q()
        # if not request.user.is_superuser:
        #     sub_query.add(Q(apply_user=request.user), Q.AND)

        if filter_title != '':
            sub_query.add(Q(title__icontains=filter_title), Q.AND)
        if int(filter_ops) != 0:
            ops_user = User.objects.get(pk=filter_ops)
            sub_query.add(Q(ops=ops_user), Q.AND)
        if int(filter_apply_user) != 0:
            apply_user = User.objects.get(pk=filter_apply_user)
            sub_query.add(Q(apply_user=apply_user.username), Q.AND)
        if int(filter_project) != 0:
            project = GameProject.objects.get(pk=filter_project)
            sub_query.add(Q(project=project), Q.AND)
        if filter_room != "0":
            filter_room = filter_room.split('-')[-1]
            room = Room.objects.filter(room_name__contains=filter_room)
            if room:
                sub_query.add(Q(room=room), Q.AND)
        if int(filter_type) != 0:
            sub_query.add(Q(type=filter_type), Q.AND)
        if int(filter_action_status) != 0:
            sub_query.add(Q(action_status=filter_action_status), Q.AND)
        if int(filter_recover_status) != 0:
            sub_query.add(Q(recover_status=filter_recover_status), Q.AND)
        if filter_start_action_time != '':
            sub_query.add(Q(action_time__gte=filter_start_action_time), Q.AND)
        if filter_end_action_time != '':
            sub_query.add(Q(action_time__lte=filter_end_action_time), Q.AND)
        if filter_start_recover_time != '':
            sub_query.add(Q(recover_time__gte=filter_start_recover_time), Q.AND)
        if filter_end_recover_time != '':
            sub_query.add(Q(recover_time__lte=filter_end_recover_time), Q.AND)
        if filter_start_apply_time != '':
            sub_query.add(Q(apply_time__gte=filter_start_apply_time), Q.AND)
        if filter_end_apply_time != '':
            sub_query.add(Q(apply_time__lte=filter_end_apply_time), Q.AND)

        if search_value:
            search_value = search_value.split('-')[-1]
            query = HostCompressionApply.objects.prefetch_related('hostcompressiondetail_set').filter(
                (
                        Q(title__icontains=search_value) |
                        Q(ops__username__icontains=search_value) |
                        Q(ops__first_name__icontains=search_value) |
                        Q(hostcompressiondetail__ip__icontains=search_value) |
                        Q(project__project_name__icontains=search_value) |
                        Q(project__project_name_en__icontains=search_value) |
                        Q(room__room_name__icontains=search_value)
                ) & sub_query
            ).order_by('-id').distinct()

        else:
            query = HostCompressionApply.objects.filter(sub_query).order_by('-id')

        raw_data = query[start: start + length]
        recordsTotal = query.count()
        data = {"data": [i.show_all() for i in raw_data], 'draw': draw, 'recordsTotal': recordsTotal,
                'recordsFiltered': recordsTotal}
        return JsonResponse(data)


def host_compression_apply_detail(request, apply_id):
    """主机迁服/回收申请详情页"""
    if request.method == 'GET':
        if request.user.has_perm('users.view_host_compression'):
            apply_obj = HostCompressionApply.objects.get(pk=apply_id)
            type = apply_obj.type
            detail_data = apply_obj.detail_data()
            total = len(detail_data)
            recover_finish = len([x for x in detail_data if x['recover_status'] in ('回收成功', '回收失败')])
            recover_success = len([x for x in detail_data if x['recover_status'] == '回收成功'])
            recover_failure = len([x for x in detail_data if x['recover_status'] == '回收失败'])
            if apply_obj.type == 2:
                migration_finish = len([x for x in detail_data if x['migration_status'] in ('迁服成功', '迁服失败')])
                migration_success = len([x for x in detail_data if x['migration_status'] == '迁服成功'])
                migration_failure = len([x for x in detail_data if x['migration_status'] == '迁服失败'])
                return render(request, 'host_compression_apply_detail.html',
                              {'apply_obj': apply_obj, 'detail_data': detail_data, 'total': total,
                               'migration_finish': migration_finish, 'migration_success': migration_success,
                               'migration_failure': migration_failure, 'recover_finish': recover_finish,
                               'recover_success': recover_success, 'recover_failure': recover_failure, 'type': type})
            else:
                return render(request, 'host_compression_apply_detail.html',
                              {'apply_obj': apply_obj, 'detail_data': detail_data, 'total': total,
                               'recover_finish': recover_finish, 'recover_success': recover_success,
                               'recover_failure': recover_failure, 'type': type})
        else:
            return render(request, '403.html')


def edit_host_compression_apply(request):
    """修改主机迁服/回收申请单状态"""
    if request.method == 'POST':
        try:
            if not request.user.is_superuser:
                raise PermissionDenied('权限受限')
            raw_data = json.loads(request.body.decode('utf-8'))
            apply_id = raw_data.pop('apply_id', '')
            apply_obj = HostCompressionApply.objects.filter(id=apply_id)
            type = apply_obj[0].type
            if int(type) != 2:
                raw_data.pop('action_time')
                raw_data.pop('action_deadline')
            ops_id = raw_data.pop('ops', 0)
            ops_user = User.objects.get(pk=ops_id)
            raw_data['ops'] = ops_user
            apply_obj.update(**raw_data)
            """如果修改状态为未迁服或未回收，则修改子任务相应的状态"""
            if apply_obj[0].action_status == 1:
                for task in apply_obj[0].hostcompressiondetail_set.all():
                    if task.migration_status != 1:
                        task.migration_status = 2
                        task.migration_remark = '无'
                        task.save(update_fields=['migration_status', 'migration_remark'])
                        for srv_detail in task.hostmigratesrvdetail_set.all():
                            if srv_detail.status != 1:
                                srv_detail.status = 2
                                srv_detail.save(update_fields=['status'])
            if apply_obj[0].recover_status == 1:
                for task in apply_obj[0].hostcompressiondetail_set.all():
                    if task.recover_status != 1:
                        task.recover_status = 2
                        task.recover_remark = '无'
                        task.save(update_fields=['recover_status', 'recover_remark'])
            return JsonResponse({'success': True, 'msg': 'ok'})
        except Exception as e:
            return JsonResponse({'success': False, 'msg': str(e)})


def get_data_host_compression_apply(request):
    """获取主机迁服/回收申请单的编辑数据"""
    if request.method == 'POST':
        try:
            raw_data = json.loads(request.body.decode('utf-8'))
            apply_id = raw_data.get('apply_id', 0)
            apply_obj = HostCompressionApply.objects.get(pk=apply_id)
            data = apply_obj.edit_data()
            data['success'] = True
            return JsonResponse(data)
        except Exception as e:
            return JsonResponse({'success': True, 'msg': str(e)})


def list_host_compression_type(request):
    """列出主机迁服/回收申请的操作类型"""
    if request.method == 'POST':
        status_list = []
        status_tuple = HostCompressionApply.TYPE
        for x in status_tuple:
            status_list.append({'id': x[0], 'text': x[1]})
        return JsonResponse(status_list, safe=False)


def list_host_compression_action_status(request):
    """列出主机迁服状态"""
    if request.method == 'POST':
        action_status_tuple = HostCompressionApply.ACTION_STATUS
        action_status_list = [{'id': x[0], 'text': x[1]} for x in action_status_tuple]
        return JsonResponse(action_status_list, safe=False)


def list_host_compression_recover_status(request):
    """列出主机回收类型"""
    if request.method == 'POST':
        recover_status_tuple = HostCompressionApply.RECOVER_STATUS
        recover_status_list = [{'id': x[0], 'text': x[1]} for x in recover_status_tuple]
        return JsonResponse(recover_status_list, safe=False)


def execute_host_compression(request):
    """手动执行主机迁服/回收任务"""
    if request.method == 'POST':
        success = True
        msg = '开始执行，请查看详情关注结果！'
        try:
            if not request.user.is_superuser:
                raise PermissionDenied
            raw_data = json.loads(request.body.decode('utf-8'))
            apply_id = raw_data.get('apply_id')
            apply_obj = HostCompressionApply.objects.get(pk=apply_id)
            type = apply_obj.type
            """根据当前任务异步请求相应接口，并修改相应任务状态"""
            if type == 2:
                """迁服回收"""
                if apply_obj.action_status == 1:
                    """未迁服则迁服"""
                    print('迁服')
                    do_host_migrate.delay(apply_obj.uuid)
                    apply_obj.action_status = 2
                    apply_obj.save(update_fields=['action_status'])
                    ws_update_host_compression_list()
                    write_host_compression_log('INFO', request.user.username + '-手动执行迁服任务', apply_obj)
                elif apply_obj.action_status == 3 and apply_obj.recover_status == 1:
                    """迁服成功及未回收则回收"""
                    print('回收')
                    do_host_recover.delay(apply_obj.uuid)
                    apply_obj.recover_status = 2
                    apply_obj.save(update_fields=['recover_status'])
                    ws_update_host_compression_list()
                    write_host_compression_log('INFO', request.user.username + '-手动执行回收任务', apply_obj)
                else:
                    raise Exception('任务必须处于未迁服或未回收状态')
            elif type in (1, 3):
                """关服回收/空闲回收"""
                if apply_obj.recover_status == 1:
                    """未回收则回收"""
                    print('回收')
                    do_host_recover.delay(apply_obj.uuid)
                    apply_obj.recover_status = 2
                    apply_obj.save(update_fields=['recover_status'])
                    ws_update_host_compression_list()
                    write_host_compression_log('INFO', request.user.username + '-手动执行回收任务', apply_obj)
                else:
                    raise Exception('任务必须处于未回收状态')
            else:
                raise Exception('未知任务类型')

        except PermissionDenied:
            success = False
            msg = '权限受限'
        except Exception as e:
            success = False
            msg = str(e)
        finally:
            return JsonResponse({'success': success, 'msg': msg})


def host_compression_cmdb_log(request, id):
    """主机迁服回收日志页面"""
    if request.method == 'GET':
        if request.user.is_superuser:
            apply_obj = HostCompressionApply.objects.get(pk=id)
            log = apply_obj.hostcompressionlog.log
            return render(request, 'host_compression_cmdb_log.html', {'id': apply_obj.id, 'log': log})
        else:
            return render(request, '403.html')


def game_server_off_callback_api_doc(request):
    """项目下架回调接口文档"""
    if request.method == 'GET':
        if request.user.is_superuser:
            return render(request, 'cmdb_gameserveroff_callbackapi_doc.html')
        else:
            return render(request, '403.html')


def workflow_node_config(request, workflow_id):
    """流程配置"""
    if request.method == 'GET':
        if request.user.is_superuser:
            workflow = Workflow.objects.get(pk=workflow_id)
            step = []
            try:
                order_state = get_workflow_state_order(workflow)
                for index, value in enumerate(order_state):
                    step_info = {}
                    step_info["id"] = order_state[index].id
                    step_info["order"] = index + 1
                    step_info["name"] = order_state[index].name
                    step.append(step_info)
            except:
                pass
            return render(request, 'workflow_node_config.html', {'workflow': workflow, 'step': step})
        else:
            return render(request, '403.html')

    if request.method == 'POST':
        if request.user.is_superuser:
            workflow = Workflow.objects.get(pk=workflow_id)
            order_state = get_workflow_state_order(workflow)
            step = []
            for s in order_state:
                step_info = {}
                step_info["title"] = s.name
                step_info["content"] = ""
                step.append(step_info)

            max_index = len(list(step))
            return JsonResponse({'step': step, 'max_index': max_index})


def change_workflow_explain(request, workflow_id):
    """修改工单流程描述说明"""
    if request.method == 'POST':
        if request.user.is_superuser:
            workflow = Workflow.objects.get(pk=workflow_id)
            explain = request.POST.get('workflow_explain', '')
            workflow.describtion = explain
            workflow.save()
            return HttpResponseRedirect('/myworkflows/workflow_list/')


def list_state_by_workflow(request):
    """根据流程id列出所有流程状态"""
    if request.method == "POST":
        data = []
        q = request.POST.get('q', None)
        workflow_id = request.POST.get('workflow_id', None)

        if q:
            state = [x for x in
                     State.objects.filter(workflow_id=workflow_id) if
                     re.search(q, x.name)]
        else:
            state = [x for x in State.objects.filter(workflow_id=workflow_id)]
        for x in state:
            data.append({'id': x.id, 'text': x.name})
        return JsonResponse(data, safe=False)


def add_workflow_state(request):
    """保存新增或者编辑的流程状态信息"""
    if request.method == 'POST':
        msg = 'ok'
        success = True
        try:
            if not request.user.is_superuser:
                raise Exception('权限受限')
            raw_data = json.loads(request.body.decode('utf-8'))
            state_name = raw_data.pop('state_name')
            workflow_id = raw_data.pop('workflow_id')
            workflow = Workflow.objects.get(pk=workflow_id)
            """检查审批链中是否已存在该状态"""
            order_state = get_workflow_state_order(workflow)
            order_state_name = [s.name for s in order_state]
            if state_name in order_state_name:
                raise Exception('审批链已经存在<%s>状态，请不要重复添加！' % state_name)
            _add_workflow_state(workflow, state_name)

        except Exception as e:
            msg = str(e)
            success = False
        finally:
            return JsonResponse({'success': success, 'msg': msg})


def list_all_state(request):
    """根列出所有流程状态"""
    if request.method == "POST":
        data = []
        q = request.POST.get('q', None)

        if q:
            all_state = [x['name'] for x in
                         State.objects.values('name').annotate(count=Count('name')) if re.search(q, x['name'])]
        else:
            all_state = [x['name'] for x in State.objects.values('name').annotate(count=Count('name'))]
        for x in all_state:
            data.append({'id': x, 'text': x})
        return JsonResponse(data, safe=False)


def del_state(request):
    """
    1.将前一条状态的指针指向后一条状态
    2.后一条状态的指针指向前一条状态
    3.删除流程状态
    """
    if request.method == 'POST':
        try:
            msg = 'ok'
            success = True
            if not request.user.is_superuser:
                raise Exception('权限受限')
            raw_data = json.loads(request.body.decode('utf-8'))
            state_id = raw_data.get('state_id')
            state = State.objects.get(id=state_id)
            _delete_workflow_state(state)
        except Exception as e:
            msg = str(e)
            success = False
        finally:
            return JsonResponse({'success': success, 'msg': msg})


def edit_workflow_state(request):
    """编辑流程审核步骤"""
    if request.method == 'POST':
        msg = 'ok'
        success = True
        try:
            if not request.user.is_superuser:
                raise Exception('权限受限')
            raw_data = json.loads(request.body.decode('utf-8'))
            workflow_id = raw_data.get('workflow_id')
            workflow = Workflow.objects.get(pk=workflow_id)
            current_order_state = get_workflow_state_order(workflow)
            current_order_state.reverse()
            edit_state_data = raw_data.get('edit_state_data')
            edit_state_data = list(filter(None, edit_state_data))
            """检查顺序编号是否存在重复"""
            order_number_list = []
            for x in edit_state_data:
                if x[0] not in order_number_list:
                    order_number_list.append(x[0])
                else:
                    raise Exception('审批顺序不能存在相同编号，请重新编辑！')
            edit_state_data.sort(key=lambda l: l[0])
            """先删除审批链中当前状态的所有指针后，再重新添加"""
            for state in current_order_state:
                _delete_workflow_state(state)
            """因已经删除审批链中所有指针，包括初始状态，所以需要重新获取workflow对象"""
            workflow = Workflow.objects.get(pk=workflow_id)
            for state_list in edit_state_data:
                _add_workflow_state(workflow, state_list[1])

        except Exception as e:
            msg = str(e)
            success = False
        finally:
            return JsonResponse({'success': success, 'msg': msg})


def project_celery_queue_map(request):
    """项目与celery任务队列关系页面"""
    if request.method == 'GET':
        if request.user.is_superuser:
            all_map = ProjectCeleryQueueMap.objects.order_by('project__project_name_en')
            use = ProjectCeleryQueueMap.USE
            return render(request, 'project_celery_queue_map.html', {'all_map': all_map, 'use': use})
        else:
            return render(request, '403.html')


def data_project_celery_queue_map(request):
    """项目与celery任务队列关系数据"""
    if request.method == 'POST':
        if request.user.is_superuser:
            draw = 0
            raw_data = ProjectCeleryQueueMap.objects.order_by('project__project_name_en')
            recordsTotal = raw_data.count()
            data = {"data": [i.show_all() for i in raw_data], 'draw': draw, 'recordsTotal': recordsTotal,
                    'recordsFiltered': recordsTotal}
            return JsonResponse(data)


def add_or_edit_project_celery_queue_map(request):
    """增加或者编辑项目和celery队列关系"""
    if request.method == 'POST':
        msg = 'ok'
        success = True
        try:
            if not request.user.is_superuser:
                raise PermissionError
            raw_data = json.loads(request.body.decode('utf-8'))
            EditFlag = raw_data.pop('EditFlag')
            project = GameProject.objects.get(pk=raw_data.pop('project_id'))
            worker = CeleryWorkerStatus.objects.get(pk=raw_data.pop('worker_id'))
            raw_data['project'] = project
            raw_data['worker'] = worker
            map_id = raw_data.pop('map_id', '')
            if EditFlag:
                map = ProjectCeleryQueueMap.objects.filter(id=map_id)
                map.update(**raw_data)
            else:
                ProjectCeleryQueueMap.objects.create(**raw_data)
        except PermissionError:
            success = False
            msg = '权限受限'
        except Exception as e:
            success = False
            msg = str(e)
        finally:
            return JsonResponse({'success': success, 'msg': msg})


def get_project_celery_queue_map(request):
    """获取项目与celery队列关系编辑数据"""
    if request.method == 'POST':
        msg = 'ok'
        success = True
        data = ''
        try:
            if not request.user.is_superuser:
                raise PermissionError
            raw_data = json.loads(request.body.decode('utf-8'))
            map_id = raw_data.get('id')
            map = ProjectCeleryQueueMap.objects.get(id=map_id)
            data = map.edit_data()
        except PermissionError:
            success = False
            msg = '权限受限'
        except Exception as e:
            success = False
            msg = str(e)
        finally:
            return JsonResponse({'success': success, 'msg': msg, 'data': data})


def delete_get_cdn_list_api(request):
    """删除项目与celery队列关系信息"""
    if request.method == 'POST':
        msg = 'ok'
        success = True
        try:
            if not request.user.is_superuser:
                raise PermissionError
            raw_data = json.loads(request.body.decode('utf-8'))
            map = ProjectCeleryQueueMap.objects.filter(id__in=raw_data)
            map.delete()
        except PermissionError:
            success = False
            msg = '权限受限'
        except Exception as e:
            success = False
            msg = str(e)
        finally:
            return JsonResponse({'success': success, 'msg': msg})


def get_reject_transition_id(request):
    """根据wse获取拒绝条件的transition id"""
    if request.method == "POST":
        success = True
        msg = 'ok'
        transition_id = ''
        try:
            raw_data = json.loads(request.body.decode('utf-8'))
            wse_id = raw_data.get('wse_id', '')
            wse = WorkflowStateEvent.objects.get(pk=wse_id)
            if wse.state.transition.filter(condition='拒绝'):
                transition_id = wse.state.transition.filter(condition='拒绝')[0].id
            else:
                raise Exception('没有找到对应的transition流程')
        except Exception as e:
            success = False
            msg = str(e)
        finally:
            return JsonResponse({'success': success, 'msg': msg, 'transition_id': transition_id})


def workflow_state_specified_user(request):
    """流程状态指定用户"""
    if request.method == 'GET':
        if request.user.is_superuser:
            specified_user_state_list = [x.show_specified_user() for x in State.objects.all() if
                                         x.show_specified_user()['specified_user'] is not None]
            return render(request, 'workflow_state_specified_user.html',
                          {'specified_user_state_list': specified_user_state_list})
        else:
            return render(request, '403.html')


def list_workflow(request):
    """列出所有流程"""
    if request.method == 'POST':
        data = []
        q = request.POST.get('q', None)
        if q:
            workflow_list = Workflow.objects.filter(name__icontains=q)
        else:
            workflow_list = Workflow.objects.all()
        for x in workflow_list:
            data.append({'id': x.id, 'text': x.name})
        return JsonResponse(data, safe=False)


def list_workflow_state(request):
    """根据workflow列出state"""
    if request.method == 'POST':
        data = []
        q = request.POST.get('q', None)
        workflow_id = request.POST.get('workflow_id', '0')
        if q:
            state_list = State.objects.filter(workflow_id=workflow_id, name__icontains=q)
        else:
            state_list = State.objects.filter(workflow_id=workflow_id)
        for x in state_list:
            data.append({'id': x.id, 'text': x.name})
        return JsonResponse(data, safe=False)


def add_or_edit_specified_user(request):
    """增加或者编辑流程额外审批人"""
    if request.method == 'POST':
        msg = 'ok'
        success = True
        try:
            if not request.user.is_superuser:
                raise PermissionError
            raw_data = json.loads(request.body.decode('utf-8'))
            EditFlag = raw_data.pop('EditFlag')
            state_id = raw_data.pop('state_id')
            state = State.objects.get(pk=state_id)
            sepecified_user_list = User.objects.filter(id__in=raw_data.pop('specified_user'))
            if EditFlag:
                state.specified_users.clear()
            for user in sepecified_user_list:
                state.specified_users.add(user)
        except PermissionError:
            success = False
            msg = '权限受限'
        except Exception as e:
            success = False
            msg = str(e)
        finally:
            return JsonResponse({'success': success, 'msg': msg})


def get_state_specified_user(request):
    """获取流程状态节点额外审批人编辑数据"""
    if request.method == 'POST':
        msg = 'ok'
        success = True
        data = ''
        try:
            if not request.user.is_superuser:
                raise PermissionError
            raw_data = json.loads(request.body.decode('utf-8'))
            state_id = raw_data.get('state_id')
            state = State.objects.get(id=state_id)
            data = state.edit_data()
        except PermissionError:
            success = False
            msg = '权限受限'
        except Exception as e:
            success = False
            msg = str(e)
        finally:
            return JsonResponse({'success': success, 'msg': msg, 'data': data})


def delete_specified_user(request):
    """删除流程节点额外审批人信息"""
    if request.method == 'POST':
        msg = 'ok'
        success = True
        try:
            if not request.user.is_superuser:
                raise PermissionError
            raw_data = json.loads(request.body.decode('utf-8'))
            state = State.objects.filter(id__in=raw_data)
            for s in state:
                s.specified_users.clear()
        except PermissionError:
            success = False
            msg = '权限受限'
        except Exception as e:
            success = False
            msg = str(e)
        finally:
            return JsonResponse({'success': success, 'msg': msg})


def special_user_config(request):
    """工单流程特殊人员配置页"""
    if request.method == 'GET':
        if request.user.is_superuser:
            special_config = SpecialUserParamConfig.objects.all()
            return render(request, 'special_user_config.html', {'special_config': special_config})
        else:
            return render(request, '403.html')


def add_or_edit_special_user(request):
    """增加或者编辑流程特殊人员配置信息"""
    if request.method == 'POST':
        msg = 'ok'
        success = True
        try:
            if not request.user.is_superuser:
                raise PermissionError
            raw_data = json.loads(request.body.decode('utf-8'))
            config_id = raw_data.pop('config_id')
            EditFlag = raw_data.pop('EditFlag')
            sepecial_user_list = User.objects.filter(id__in=raw_data.pop('special_user'))
            if EditFlag:
                config = SpecialUserParamConfig.objects.filter(id=config_id)
                config.update(**raw_data)
                config = config[0]
                config.user.clear()
                for user in sepecial_user_list:
                    config.user.add(user)
            else:
                config = SpecialUserParamConfig.objects.create(**raw_data)
                for user in sepecial_user_list:
                    config.user.add(user)
        except PermissionError:
            success = False
            msg = '权限受限'
        except Exception as e:
            success = False
            msg = str(e)
        finally:
            return JsonResponse({'success': success, 'msg': msg})


def get_workflow_special_user(request):
    """获取工单流程特殊人员配置信息"""
    if request.method == 'POST':
        msg = 'ok'
        success = True
        data = ''
        try:
            if not request.user.is_superuser:
                raise PermissionError
            raw_data = json.loads(request.body.decode('utf-8'))
            config_id = raw_data.get('config_id')
            config = SpecialUserParamConfig.objects.get(id=config_id)
            data = config.edit_data()
        except PermissionError:
            success = False
            msg = '权限受限'
        except Exception as e:
            success = False
            msg = str(e)
        finally:
            return JsonResponse({'success': success, 'msg': msg, 'data': data})


def delete_workflow_special_user(request):
    """删除工单流程中特殊人员配置"""
    if request.method == 'POST':
        msg = 'ok'
        success = True
        try:
            if not request.user.is_superuser:
                raise PermissionError
            raw_data = json.loads(request.body.decode('utf-8'))
            config = SpecialUserParamConfig.objects.filter(id__in=raw_data)
            if config:
                config.delete()
        except PermissionError:
            success = False
            msg = '权限受限'
        except Exception as e:
            success = False
            msg = str(e)
        finally:
            return JsonResponse({'success': success, 'msg': msg})


def list_game_project_by_area(request):
    """根据地区列出游戏项目"""
    if request.method == "POST":
        data = []
        q = request.POST.get('q', None)
        area_id = request.POST.get('area_id', None)

        if str(area_id) != '0':
            if q:
                all_game_project = [x['belongs_to_game_project__project_name'] for x in
                                    Host.objects.filter(status=1, belongs_to_room__area__id=area_id).values(
                                        'belongs_to_game_project__project_name').annotate(
                                        count=Count('belongs_to_game_project__project_name')) if
                                    re.search(q, x['belongs_to_game_project__project_name'])]
            else:
                all_game_project = [x['belongs_to_game_project__project_name'] for x in
                                    Host.objects.filter(status=1, belongs_to_room__area__id=area_id).values(
                                        'belongs_to_game_project__project_name').annotate(
                                        count=Count('belongs_to_game_project__project_name'))]
        else:
            if q:
                all_game_project = [x.project_name for x in GameProject.objects.filter(project_name__icontains=q)]
            else:
                all_game_project = [x.project_name for x in GameProject.objects.all()]

        for x in all_game_project:
            data.append({'id': x, 'text': x})
        return JsonResponse(data, safe=False)


def list_room_name_by_project_and_area(request):
    """根据项目和地区列出机房"""
    if request.method == "POST":
        data = []
        q = request.POST.get('q', None)
        project_name = request.POST.get('project', None)
        area_id = request.POST.get('area', None)

        # 添加sub_query
        sub_query = Q()

        if str(area_id) != "0":
            area = Area.objects.get(pk=area_id)
            sub_query.add(Q(belongs_to_room__area=area), Q.AND)
        if project_name != "全部":
            project = GameProject.objects.get(project_name=project_name)
            sub_query.add(Q(belongs_to_game_project=project), Q.AND)

        if q:
            room_list = [x['belongs_to_room__area__chinese_name'] + '-' + x['belongs_to_room__room_name'] for x in
                         Host.objects.filter(status=1).filter(sub_query).values(
                             'belongs_to_room__room_name', 'belongs_to_room__area__chinese_name').annotate(
                             count=Count('belongs_to_room__room_name')) if
                         re.search(q, x['belongs_to_room__room_name']) or re.search(q, x[
                             'belongs_to_room__area__chinese_name'])]
        else:
            room_list = [x['belongs_to_room__area__chinese_name'] + '-' + x['belongs_to_room__room_name'] for x in
                         Host.objects.filter(status=1).filter(sub_query).values(
                             'belongs_to_room__room_name', 'belongs_to_room__area__chinese_name').annotate(
                             count=Count('belongs_to_room__room_name'))]
        for x in room_list:
            data.append({'id': x, 'text': x})
        return JsonResponse(data, safe=False)


def cmdb_hotupdate_join_project_doc(request):
    """cmdb热更新对接项目文档"""
    if request.method == 'GET':
        if request.user.is_superuser:
            return render(request, 'cmdb_hotupdate_join_project_doc.html')
        else:
            return render(request, '403.html')


def execute_add_mac_to_wifi(request):
    """执行添加mac地址到wifi"""
    if request.method == "POST":
        wse = json.loads(request.body.decode('utf-8'))
        wse = WorkflowStateEvent.objects.get(id=wse.get('wse'))
        applicant_first_name = wse.content_object.applicant.first_name
        result = add_mac(applicant_first_name, wse.content_object.mac, wse.content_object.id)
        # 将工单状态设置为完成
        if wse.state.name == '完成':
            failure_declare_finish(request, update_taskcard=False)
        return JsonResponse({"result": result['ret'], "data": result['msg']})


def get_game_server_action_history(request):
    """获取区服操作历史记录"""
    if request.method == "POST":
        if request.user.is_superuser:
            game_server_id = json.loads(request.body.decode('utf-8')).get('id')
            record = GameServerActionRecord.objects.filter(game_server__id=game_server_id).order_by('-operation_time')
            data = {'data': [i.show_all() for i in record]}
            return JsonResponse(data)
        else:
            raise PermissionDenied


def cmdb_game_server_action_callback_api_doc(request):
    """"cmdb区服管理操作回调api文档"""
    if request.method == 'GET':
        if request.user.is_superuser:
            return render(request, 'cmdb_modsrv_opentime_callback_api_doc.html')
        else:
            return render(request, '403.html')


def game_server_migrate(request):
    """单个区服迁服操作"""
    if request.method == "POST":
        msg = 'ok'
        try:
            raw_data = json.loads(request.body.decode('utf-8'))
            game_server_id = raw_data.get('game_server_id', '')
            do_game_server_migrate.delay(game_server_id, request.user.id)

            return JsonResponse({'success': True, 'msg': msg})
        except Exception as e:
            return JsonResponse({'success': False, 'msg': str(e)})


def list_celery_worker(request):
    """下拉展示celery worker"""

    if request.method == "POST":
        data = []

        q = request.POST.get('q', None)

        if q:
            all_celery_worker = CeleryWorkerStatus.objects.filter(
                Q(celery_hostname__icontains=q), status=1)
        else:
            all_celery_worker = CeleryWorkerStatus.objects.filter(status=1)

        for x in all_celery_worker:
            data.append({'id': x.id, 'text': x.celery_hostname})

        return JsonResponse(data, safe=False)


def list_celery_queue(request):
    """下拉展示celery queue"""

    if request.method == "POST":
        data = []

        worker_id = request.POST.get('worker', None)
        worker = CeleryWorkerStatus.objects.get(pk=worker_id)

        all_celery_queue = get_celery_worker_relate_tasks().get(worker.celery_hostname, None)

        for x in all_celery_queue:
            data.append({'id': x, 'text': x})

        return JsonResponse(data, safe=False)


def change_workflow_apply_valid_status(request):
    """设置工单是否有效"""
    msg = 'ok'
    success = True
    try:
        if request.user.is_superuser:
            raw_data = json.loads(request.body.decode('utf-8'))
            is_valid = raw_data.get('is_valid')
            wse = WorkflowStateEvent.objects.filter(pk=raw_data.get('id'))
            wse.update(**{'is_valid': is_valid})
        else:
            raise PermissionError
    except PermissionDenied:
        msg = '你没有增加游戏项目的权限'
        success = False
    except Exception as e:
        msg = str(e)
        success = False
    finally:
        return JsonResponse({'data': success, 'msg': msg})


def wechat_account_transfer(request):
    """cmdb帐号与企业微信帐号转换"""
    if request.method == 'GET':
        if request.user.is_superuser:
            wechat_acounts = WechatAccountTransfer.objects.all()
            return render(request, 'wechat_account_transfer.html', {'wechat_acounts': wechat_acounts})
        else:
            return render(request, '403.html')


def add_or_edit_wechat_account_transer(request):
    """增加或者编辑cmdb帐号与企业微信的转换关系"""
    if request.method == 'POST':
        msg = 'ok'
        success = True
        try:
            if not request.user.is_superuser:
                raise PermissionError
            raw_data = json.loads(request.body.decode('utf-8'))
            EditFlag = raw_data.pop('EditFlag')
            cmdb_account = raw_data.pop('cmdb_account')
            cmdb_account = User.objects.get(pk=cmdb_account)
            if WechatAccountTransfer.objects.filter(cmdb_account=cmdb_account):
                EditFlag = True
            if EditFlag:
                account = WechatAccountTransfer.objects.filter(cmdb_account=cmdb_account)
                account.update(**raw_data)
            else:
                raw_data['cmdb_account'] = cmdb_account
                WechatAccountTransfer.objects.create(**raw_data)
        except PermissionError:
            success = False
            msg = '权限受限'
        except Exception as e:
            success = False
            msg = str(e)
        finally:
            return JsonResponse({'success': success, 'msg': msg})


def get_wechat_account_transfer(request):
    """获取cmdb与企业微信帐号转换关系数据"""
    if request.method == 'POST':
        msg = 'ok'
        success = True
        data = ''
        try:
            if not request.user.is_superuser:
                raise PermissionError
            raw_data = json.loads(request.body.decode('utf-8'))
            id = raw_data.get('id')
            wat = WechatAccountTransfer.objects.get(id=id)
            data = wat.edit_data()
        except PermissionError:
            success = False
            msg = '权限受限'
        except Exception as e:
            success = False
            msg = str(e)
        finally:
            return JsonResponse({'success': success, 'msg': msg, 'data': data})


def delete_wechat_account_transfer(request):
    """删除cmdb与企业微信帐号转换的数据"""
    if request.method == 'POST':
        msg = 'ok'
        success = True
        try:
            if not request.user.is_superuser:
                raise PermissionError
            raw_data = json.loads(request.body.decode('utf-8'))
            account = WechatAccountTransfer.objects.filter(id__in=raw_data)
            account.delete()
        except PermissionError:
            success = False
            msg = '权限受限'
        except Exception as e:
            success = False
            msg = str(e)
        finally:
            return JsonResponse({'success': success, 'msg': msg})


def hotupdate_templates_bind(request, project_id):
    """热更新工单模板绑定"""
    if request.method == 'GET':
        if request.user.is_superuser:
            client_templates = HotUpdateTemplate.objects.filter(type=1).order_by('name')
            server_templates = HotUpdateTemplate.objects.filter(type=2).order_by('name')
            project_name = GameProject.objects.get(pk=project_id).project_name
            project_client_template_id = GameProject.objects.get(pk=project_id).get_client_hotupdate_template(id=True)
            project_server_template_id = GameProject.objects.get(pk=project_id).get_server_hotupdate_template(id=True)
            return render(request, 'hotupdate_templates_bind.html',
                          {'client_templates': client_templates, 'server_templates': server_templates,
                           'project_id': project_id, 'project_client_template_id': project_client_template_id,
                           'project_server_template_id': project_server_template_id, 'project_name': project_name})
        else:
            return render(request, '403.html')


def save_project_relate_hotupdate_template(request):
    """保存项目关联热更新模板"""
    if request.method == 'POST':
        success = True
        data = ''
        try:
            raw_data = json.loads(request.body.decode('utf-8'))
            project = GameProject.objects.get(pk=raw_data.get('project_id'))
            client_template = HotUpdateTemplate.objects.filter(pk=raw_data.get('client_template_id'))
            server_template = HotUpdateTemplate.objects.filter(pk=raw_data.get('server_template_id'))
            project.hotupdate_template.clear()
            if client_template:
                project.hotupdate_template.add(client_template[0])
            if server_template:
                project.hotupdate_template.add(server_template[0])

        except HotUpdateTemplate.DoesNotExist:
            success = False
            data = '热更新模板不存在'
        except Exception as e:
            success = False
            data = str(e)
        finally:
            return JsonResponse({'success': success, 'data': data})


def list_room_name_by_project_from_host(request):
    """根据项目通过主机列出机房"""
    if request.method == "POST":
        data = []
        q = request.POST.get('q', None)
        project = request.POST.get('project', None)
        try:
            project = GameProject.objects.get(pk=project)
        except:
            project = GameProject.objects.get(project_name=project)

        if q:
            room_list = [x['belongs_to_room__area__chinese_name'] + '-' + x['belongs_to_room__room_name'] for x in
                         Host.objects.filter(status=1, belongs_to_game_project=project).values(
                             'belongs_to_room__room_name', 'belongs_to_room__area__chinese_name').annotate(
                             count=Count('belongs_to_room__room_name')) if
                         re.search(q, x['belongs_to_room__room_name']) or re.search(q, x[
                             'belongs_to_room__area__chinese_name'])]
        else:
            room_list = [x['belongs_to_room__area__chinese_name'] + '-' + x['belongs_to_room__room_name'] for x in
                         Host.objects.filter(status=1, belongs_to_game_project=project).values(
                             'belongs_to_room__room_name', 'belongs_to_room__area__chinese_name').annotate(
                             count=Count('belongs_to_room__room_name'))]
        for x in room_list:
            data.append({'id': x, 'text': x})
        return JsonResponse(data, safe=False)


def check_webapi_client_type(request):
    """根据项目和地区获取是否有配置客户端类型"""
    if request.method == 'POST':
        success = True
        data = 'ok'
        client_type = True
        try:
            pdata = json.loads(request.body.decode('utf-8'))
            project = GameProject.objects.get(pk=pdata.get('project_id', ''))
            area = Area.objects.get(chinese_name=pdata.get('area', ''))
            web_api = WebGetCdnListAPI.objects.filter(project=project, area=area)
            if not web_api or not web_api[0].dev_flag:
                client_type = False
        except Exception as e:
            success = False
            data = str(e)
        finally:
            return JsonResponse({'success': success, 'data': data, 'client_type': client_type})


def version_update_check_push_dir(request):
    """
    版本更新单-根据前后段版本号检查推送目录是否存在
    request.body参数：
        version_update_type: client或server  # 前端或后端
        version: 版本号
        project_id: 项目id
        area_id: 地区id
    返回：
        {'success': success, 'msg': msg}
    """
    if request.method == 'POST':
        success = True
        msg = 'ok'
        try:
            raw_data = json.loads(request.body.decode('utf-8'))
            version_update_type = raw_data.get('version_update_type', '')
            version = raw_data.get('version', '')
            project = GameProject.objects.get(pk=raw_data.pop('project_id', 0))
            area = Area.objects.get(pk=raw_data.pop('area_id', 0))
            if project.auto_version_update:
                success, msg = version_update_check_push_dir_util(version_update_type, version, project, area)

        except Exception as e:
            success = False
            msg = str(e)
        finally:
            return JsonResponse({'success': success, 'msg': msg})


def do_version_update(request):
    """手动执行版本更新请求"""
    if request.method == 'POST':
        success = True
        msg = 'ok'
        try:
            raw_data = json.loads(request.body.decode('utf-8'))
            wse = WorkflowStateEvent.objects.get(id=raw_data.get('wse'))
            version_update_type = raw_data.get('version_update_type')
            content_obj = wse.content_object
            # 若项目设置为自动版本更新，则发送请求
            if wse.content_object.project.auto_version_update:
                result = version_update_task(content_obj.id, version_update_type)
                if not result['success']:
                    raise Exception(result['msg'])
            msg = '发送版本更新成功！'

        except Exception as e:
            success = False
            msg = str(e)
        finally:
            return JsonResponse({'success': success, 'msg': msg})


def recv_web_maintenance_api_doc(request):
    """接收web挂维护通知api文档"""
    if request.method == 'GET':
        if request.user.has_perm('users.api_doc'):
            return render(request, 'web_maintenance_cmdb.html')
        else:
            return render(request, '403.html')


def version_update_plan_doc(request):
    """获取版本更新计划API文档"""
    if request.method == 'GET':
        if request.user.is_superuser:
            return render(request, 'cmdb_version_update_plan_doc.html')
        else:
            return render(request, '403.html')
