# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.http import JsonResponse
import json
import os
import codecs

from cmdb.logs import PushAPILog

log = PushAPILog()

# Create your views here.


class get_lockstatus(APIView):
    """获取推送系统锁状态"""

    def post(self, request, format=None):

        data = request.data
        project = data.get('project')
        area = data.get('area')
        ver_type = data.get('ver_type')
        ver = data.get('ver')

        try:
            if project and area and ver_type and ver:
                LockFile = '/var/run/' + project + area + ver_type + ver + '.lock'

                if os.path.isfile(LockFile.encode("utf-8")):
                    lockInfo = json.load(codecs.open(LockFile.encode("utf-8"), 'r', "utf-8"))
                    Auser = lockInfo['user']

                    log.logger.info('查询锁状态为 locked, 信息: %s' % LockFile)
                    return JsonResponse({'ret': 'success', 'msg': 'locked', 'user': '%s' % Auser})
                else:
                    log.logger.info('查询锁状态为 unlock, 信息: %s' % LockFile)
                    return JsonResponse({'ret': 'success', 'msg': 'unlock'})
            else:
                log.logger.error(
                    'post参数不完整 project:%s area:%s ver_type:%s ver:%s' % (project, area, ver_type, ver))
                return JsonResponse({'ret': 'fail', 'msg': 'post参数不完整'})
        except Exception as e:
            log.logger.error('内部错误: %s' % e)
            return JsonResponse({'ret': 'fail', 'msg': '内部错误'})


class get_lock(APIView):
    """为推送系统加锁"""
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):

        data = request.data
        project = data.get('project')
        area = data.get('area')
        ver_type = data.get('ver_type')
        ver = data.get('ver')
        user = data.get('user')

        try:
            if project and area and ver_type and ver and user:
                LockFile = '/var/run/' + project + area + ver_type + ver + '.lock'

                if os.path.isfile(LockFile.encode("utf-8")):
                    lockInfo = json.load(codecs.open(LockFile.encode("utf-8"), 'r', "utf-8"))
                    Auser = lockInfo['user']

                    return JsonResponse({'ret': 'fail', 'msg': '已被上锁, 用户: %s' % Auser})
                else:

                    d = {'project': project, 'area': area, 'ver_type': ver_type, 'ver': ver, 'user': user}

                    # 序列化获得的lock信息
                    with codecs.open(LockFile.encode("utf-8"), 'w', "utf-8") as f:
                        json.dump(d, f, ensure_ascii=False)

                    log.logger.info('上锁成功, 锁文件: %s 用户: %s' % (LockFile, user))
                    return JsonResponse({'ret': 'success', 'msg': '上锁成功'})
            else:
                log.logger.error('post参数不完整 project:%s area:%s ver_type:%s ver:%s user:%s' % (
                    project, area, ver_type, ver, user))
                return JsonResponse({'ret': 'fail', 'msg': 'post参数不完整'})
        except Exception as e:
            log.logger.error('内部错误: %s' % e)
            return JsonResponse({'ret': 'fail', 'msg': '内部错误'})


class get_unlock(APIView):
    """推送系统解锁"""
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):

        data = request.data
        project = data.get('project')
        area = data.get('area')
        ver_type = data.get('ver_type')
        ver = data.get('ver')
        user = data.get('user')

        try:
            if project and area and ver_type and ver and user:
                LockFile = '/var/run/' + project + area + ver_type + ver + '.lock'

                if os.path.isfile(LockFile.encode("utf-8")):
                    lockInfo = json.load(codecs.open(LockFile.encode("utf-8"), 'r', "utf-8"))
                    Auser = lockInfo['user']

                    if user == Auser:
                        os.remove(LockFile.encode("utf-8"))
                        log.logger.info('取消锁成功, 锁文件: %s  user:%s' % (LockFile, user))
                        return JsonResponse({'ret': 'success', 'msg': '取消锁成功, 用户: %s' % user})
                else:
                    log.logger.error('取消无效锁, 信息: %s  user:%s' % (LockFile, user))
                    return JsonResponse({'ret': 'fail', 'msg': '锁不存在'})
            else:
                log.logger.error(
                    'post参数不完整 project:%s area:%s ver_type:%s ver:%s user:%s' % (project, area, ver_type, ver, user))
                return JsonResponse({'ret': 'fail', 'msg': 'post参数不完整'})
        except Exception as e:
            log.logger.error('内部错误: %s' % e)
            return JsonResponse({'ret': 'fail', 'msg': '内部错误'})
