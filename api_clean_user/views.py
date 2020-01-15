# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# from rest_framework.authentication import TokenAuthentication
# from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.http import JsonResponse

from django.db import transaction

import json

from django.contrib.auth.models import User

from users.models import UserClearStatus
from assets.utils import get_ip

from users.channels_utils import ws_notify_clean_user

from cmdb.logs import CleanUserLog
from cmdb.logs import CleanProjectServer
from cmdb.api_permissions import api_permission

from myworkflows.models import ProjectAdjust

# Create your views here.


class CleanUserCallBack(APIView):
    """清除用户服务器权限回调

    运维管理机返回的数据格式:
    {
        'ops_manager_ip': {'success': True, 'result': ''},
        'username': username,
    }
    或者
    {
        'ops_manager_ip2': {'success': False, 'result': '删除用户失败'},
        'username': username,
    }

    cmdb返回给运维管理机的数据
    {"resp": 0 , "reason": "ok"}
    或者
    {"resp": 1 , "reason": "回调内存错误"}

    """

    def post(self, request, format=None):
        reason = "ok"
        resp = 0
        log = CleanUserLog()

        data = json.loads(request.data)
        source_ip = get_ip(request)
        log.logger.info('收到回调: ' + json.dumps(data) + '，源IP: ' + source_ip)
        username = data.pop('username', '')

        try:
            with transaction.atomic():
                user = User.objects.select_for_update().get(first_name=username)
                # profile = user.profile
                ucs = UserClearStatus.objects.select_for_update().get(profile=user.profile)
                server_permission = json.loads(ucs.server_permission)
                server_permission.update(**data)
                ucs.server_permission = json.dumps(server_permission)
                ucs.save(update_fields=['server_permission'])
                # 刷新页面
            ws_notify_clean_user(user.id)

        except User.DoesNotExist:
            log.logger.error('%s用户不存在' % (username))
            resp = 1
            reason = "用户%s不存在" % (username)
            log.logger.info("用户%s不存在" % (username))
        except UserClearStatus.DoesNotExist:
            log.logger.error('用户%s清除状态不存在，没有创建' % (username))
            reason = "用户%s清除状态不存在，没有创建" % (username)
            resp = 1
            log.logger.info("用户%s清除状态不存在，没有创建" % (username))
        except Exception as e:
            reason = str(e)
            resp = 1
            log.logger.info('管理机清除用户%s后回调cmdb失败' % (username, str(e)))
        return JsonResponse({"resp": resp, "reason": reason})


class CleanUserByProjectCallBack(APIView):
    """根据项目清除服务器权限
    运维管理机返回的数据格式:
    {
        'ops_manager_ip': {'success': True, 'result': ''},
        'username': username,
        "id": id,
    }
    或者
    {
        'ops_manager_ip2': {'success': False, 'result': '删除用户失败'},
        'username': username,
        "id": id,
    }

    cmdb返回给运维管理机的数据
    {"resp": 0 , "reason": "ok"}
    或者
    {"resp": 1 , "reason": "回调内存错误"}
    """

    def post(self, request, format=None):
        reason = "ok"
        resp = 0
        log = CleanProjectServer()

        data = json.loads(request.data)
        username = data.pop('username', '')
        content_object_id = data.pop('id', 0)

        try:
            with transaction.atomic():
                content_object = ProjectAdjust.objects.select_for_update().get(id=content_object_id)
                delete_serper_info = json.loads(content_object.delete_serper_info)
                delete_serper_info.update(**data)
                content_object.delete_serper_info = delete_serper_info
                # 查看清除是否成功
                key = next(iter(data))
                success = data.get(key).get('success', False)
                """
                (0, '已处理'),
                (1, '故障中'),
                (2, '未处理'),
                初始状态是2
                """
                if content_object.status != 1:
                    if success:
                        content_object.status = 0
                    else:
                        content_object.status = 1
        except ProjectAdjust.DoesNotExist:
            log.logger.error('%d找不到项目调整工单id' % (content_object_id))
            resp = 1
            reason = "找不到项目调整工单id%d" % (content_object_id)
        except Exception as e:
            reason = str(e)
            resp = 1
            log.logger.error('管理机清除用户%s后回调cmdb失败%s' % (username, str(e)))
            content_object.status = 1
        content_object.save()
        return JsonResponse({"resp": resp, "reason": reason})


class GetNotActiveUser(APIView):
    """获取离职用户
    """

    def get(self, request, format=None):
        return JsonResponse([x.first_name for x in User.objects.filter(is_active=0)], safe=False)


@api_permission(api_perms=['api_hotupdate_callback'])
class Test(APIView):
    """获取离职用户
    """

    # api_perms = ['api_hotupdate_callback']

    def get(self, request, format=None):
        return JsonResponse({"msg": "ooo"})
