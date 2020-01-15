# -*- coding: utf-8 -*-

from assets.models import GameProject
from assets.models import Area
from assets.utils import get_ip
from mysql.models import MysqlInstance
from mysql.models import MyqlHistoryRecord

# Create your views here.

from rest_framework.views import APIView
from django.http import JsonResponse
from django.core.exceptions import MultipleObjectsReturned
from django.db.models import Q

import json


class InstanceCreate(APIView):
    """创建mysql 实例
    """

    def post(self, request, format=None):
        reason = "ok"
        raw_data = json.loads(request.data)
        need_params = ('project', 'area', 'purpose', 'host', 'port', 'user', 'password')
        try:
            for param in need_params:
                if raw_data.get(param, None) is None:
                    raise Exception("%s: 参数没有" % (param))

            project = GameProject.objects.get(project_name_en=raw_data.get('project'))
            area = raw_data.get('area')
            cmdb_area = Area.objects.get(Q(chinese_name=area) | Q(short_name=area))
            purpose = raw_data.get('purpose')
            host = raw_data.get('host')
            port = raw_data.get('port')
            user = raw_data.get('user')
            password = raw_data.get('password')

            white_list = raw_data.get('white_list', None)

            if white_list is not None:
                if not isinstance(white_list, list):
                    raise Exception('white_list格式需要为list')

                white_list = json.dumps(white_list)

            myins = MysqlInstance.objects.create(
                project=project, area=area, purpose=purpose, white_list=white_list,
                host=host, port=port, user=user, password=password, cmdb_area=cmdb_area)
            reason = myins.show_api()
            resp = 1
            # 新增记录
            source_ip = get_ip(request)
            MyqlHistoryRecord.objects.create(mysql=myins, create_user=request.user, type=1, source_ip=source_ip)

        except Area.DoesNotExist:
            reason = '地区不存在，必须使用cmdb地区表中地区'
            resp = 13
        except GameProject.DoesNotExist:
            reason = '项目英文名不存在'
            resp = 13
        except Exception as e:
            reason = str(e)
            resp = 13
        return JsonResponse({"reason": reason, "resp": resp})


class InstanceModify(APIView):
    """修改mysql实例
    """

    def post(self, request, format=None):
        reason = "ok"
        raw_data = json.loads(request.data)
        # need_params = ('old_instance', 'new_instance')

        try:
            source_ip = get_ip(request)
            if raw_data.get('old_instance', None) is None:
                raise Exception('old_instance查询参数没有')
            if raw_data.get('new_instance', None) is None:
                raise Exception('new_instance修改参数没有')

            old_instance = raw_data.get('old_instance')
            new_instance = raw_data.get('new_instance')

            myins = MysqlInstance.objects.get(**old_instance)

            update_fields = ('project', 'area', 'purpose', 'host', 'port', 'user', 'password', 'white_list')
            update_data = {}

            for f in update_fields:
                field_data = new_instance.get(f, None)
                if field_data is not None:
                    if f == 'project':
                        field_data = GameProject.objects.get(project_name_en=field_data)
                        update_data[f] = field_data
                    elif f == 'white_list':
                        if not isinstance(field_data, list):
                            raise Exception('white_list格式需要为list')
                        update_data[f] = json.dumps(field_data)
                    elif f == 'area':
                        area = Area.objects.get(Q(chinese_name=field_data) | Q(short_name=field_data))
                        update_data['cmdb_area'] = area
                    else:
                        update_data[f] = field_data
                else:
                    if f == 'white_list':
                        update_data[f] = None

            for attr, value in update_data.items():
                old_content = myins.__getattribute__(attr)
                setattr(myins, attr, value)
                # 修改记录
                if attr == 'white_list' and value is None:
                    continue
                alter_field = MysqlInstance._meta.get_field(attr).help_text
                if attr == 'password':
                    old_content = value = ''
                MyqlHistoryRecord.objects.create(mysql=myins, create_user=request.user, type=2,
                                                 old_content=old_content, new_content=value, alter_field=alter_field,
                                                 source_ip=source_ip)
            myins.save()

            reason = myins.show_api()

            resp = 1

        except Area.DoesNotExist:
            reason = '地区不存在，必须使用cmdb地区表中地区'
            resp = 13
        except MysqlInstance.DoesNotExist:
            reason = '找不到mysql实例'
            resp = 13
        except GameProject.DoesNotExist:
            reason = '项目英文名不存在'
            resp = 13
        except MultipleObjectsReturned:
            reason = 'old_instance找到的记录不唯一'
            resp = 13
        except Exception as e:
            reason = str(e)
            resp = 13
        return JsonResponse({"reason": reason, "resp": resp})


class InstanceDelete(APIView):
    """删除某个数据库实例
    """

    def post(self, request, format=None):
        reason = "ok"
        raw_data = json.loads(request.data)
        need_params = ('host', 'port')
        try:
            source_ip = get_ip(request)
            for param in need_params:
                if raw_data.get(param, None) is None:
                    raise Exception("%s: 参数没有" % (param))

            myins = MysqlInstance.objects.get(host=raw_data.get('host'), port=raw_data.get('port'))
            # 删除记录
            MyqlHistoryRecord.objects.filter(mysql=myins).update(**{'remark': myins.host + ':' + myins.port})
            MyqlHistoryRecord.objects.create(create_user=request.user, type=3, remark=myins.host + ':' + myins.port,
                                             source_ip=source_ip)

            myins.delete()
            reason = 'delete ok'
            resp = 1

        except MysqlInstance.DoesNotExist:
            reason = '没有找到mysql实例'
            resp = 13
        except Exception as e:
            reason = str(e)
            resp = 13
        return JsonResponse({"reason": reason, "resp": resp})


class InstanceList(APIView):
    """查看mysql实例
    """

    def post(self, request, format=None):
        reason = "ok"
        raw_data = json.loads(request.data)

        try:
            myins = MysqlInstance.objects.filter(**raw_data)
            reason = [x.show_api() for x in myins]
            resp = 1
        except Exception as e:
            reason = str(e)
            resp = 13
        return JsonResponse({"reason": reason, "resp": resp})
