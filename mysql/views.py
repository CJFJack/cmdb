from django.shortcuts import render_to_response
from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth.models import User

from mysql.models import MysqlInstance
from mysql.models import MyqlHistoryRecord
from assets.models import GameProject
from assets.models import Area
from assets.utils import get_ip

from mysql.mysql_utils import get_instance_dbs
from users.models import OrganizationMptt

import json


def instance(request):
    """数据库实例表格页面"""
    if request.user.is_superuser or request.user.has_perm('mysql.view_mysql_instance'):
        head = {'value': '数据库实例', 'username': request.user.username}
        projects = GameProject.objects.filter(status=1)
        areas = Area.objects.all()
        password_visible = False
        if request.user.has_perm('mysql.view_mysql_password'):
            password_visible = True
        return render(request, 'mysqlinstance.html',
                      {'head': head, 'projects': projects, 'areas': areas, 'password_visible': password_visible})
    else:
        return render(request, '403.html')


def data_instance(request):
    """数据库实例数据
    """
    if request.method == "POST":
        if (request.user.is_superuser or
                request.user.has_perm('mysql.view_mysql_instance')):
            raw_get = request.POST.dict()

            search_value = raw_get.get('search[value]', '')
            start = int(raw_get.get('start', 0))
            draw = raw_get.get('draw', 0)
            length = int(raw_get.get('length', 10))

            raw_data = ''
            sub_query = Q()
            """
            2018.12修改：
                1. superuser拥有整个操作整个页面的权限
                2. 拥有查看数据库实例页面权限的staff拥有查看所有数据库实例的权限
                3. 拥有查看数据库实例页面权限的普通用户只能查看所在部门负责项目的数据库实例
            """
            if not (request.user.is_superuser or request.user.is_staff):
                org_user_obj = OrganizationMptt.objects.get(user=request.user)
                projects_obj_list = org_user_obj.get_user_charge_project()
                sub_query.add(Q(project__in=projects_obj_list), Q.OR)

            if search_value:
                query = MysqlInstance.objects.select_related('project').filter(
                    (Q(project__project_name__icontains=search_value) |
                       Q(area__icontains=search_value) |
                       Q(purpose__icontains=search_value) |
                       Q(host__icontains=search_value) |
                       Q(port__icontains=search_value)) & sub_query).order_by('-id')
            else:
                query = MysqlInstance.objects.select_related('project').filter(sub_query).order_by('-id')

            raw_data = query[start: start + length]
            recordsTotal = query.count()
            if request.user.has_perm('mysql.view_mysql_password'):
                data = {"data": [i.show_all(password_visible=True) for i in raw_data], 'draw': draw,
                        'recordsTotal': recordsTotal,
                        'recordsFiltered': recordsTotal}
            else:
                data = {"data": [i.show_all(password_visible=False) for i in raw_data], 'draw': draw,
                        'recordsTotal': recordsTotal,
                        'recordsFiltered': recordsTotal}
            return JsonResponse(data)
        else:
            return JsonResponse([], safe=False)


def mysql_instance_api(request):
    """数据库实例api文档
    """
    if request.method == "GET":
        if request.user.is_superuser:
            return render(request, 'mysql_api_doc.html')
        else:
            return render(request, '403.html')


def list_mysql_instance(request):
    """下拉mysql实例列表
    """
    if request.method == "POST":
        data = []

        q = request.POST.get('q', '')

        all_inst = MysqlInstance.objects.filter(host__icontains=q)

        for x in all_inst:
            value = x.host + ":" + x.port
            text = '{value}({purpose})'.format(value=value, purpose=x.purpose)
            data.append({'id': x.id, 'text': text, 'value': value})

        return JsonResponse(data, safe=False)


def list_mysql_instance_db(request):
    """下拉mysql实例列表
    """
    if request.method == "POST":

        instance = request.POST.get('instance')  # host:port

        host = instance.split(':')[0]
        port = instance.split(':')[1]

        instance = MysqlInstance.objects.get(host=host, port=port)

        q = request.POST.get('q', None)

        ignore_dbs = ('mysql', 'information_schema', 'performance_schema', 'sys')

        instance_info = {}
        instance_info['host'] = instance.host
        instance_info['port'] = instance.port
        instance_info['user'] = instance.user
        instance_info['passwd'] = instance.password

        dbs = get_instance_dbs(**instance_info)

        valid_dbs = []

        for db in dbs:
            db_name = db['Database']
            if db_name not in ignore_dbs:
                if q is not None:
                    if q in db_name:
                        valid_dbs.append(db_name)
                else:
                    valid_dbs.append(db_name)

        return JsonResponse([{'id': x, 'text': x} for x in valid_dbs], safe=False)


def add_or_edit_mysql(request):
    """新增或编辑mysql实例信息"""
    if request.method == 'POST':
        success = True
        msg = 'ok'
        try:
            if not request.user.is_superuser:
                raise Exception('没有权限')
            raw_data = json.loads(request.body.decode('utf-8'))
            project = GameProject.objects.get(pk=raw_data.pop('project'))
            cmdb_area = Area.objects.get(pk=raw_data.pop('cmdb_area'))
            raw_data['project'] = project
            raw_data['cmdb_area'] = cmdb_area
            raw_data['area'] = cmdb_area.chinese_name
            raw_data['white_list'] = json.dumps(raw_data.pop('white_list').split(','))
            editFlag = raw_data.pop('editFlag')
            source_ip = get_ip(request)
            if editFlag:
                mysql = MysqlInstance.objects.filter(pk=raw_data.pop('id'))
                old_mysql = mysql[0].show_all()
                mysql.update(**raw_data)
                new_mysql = mysql[0].show_all()
                # 修改记录
                for k, v in new_mysql.items():
                    if old_mysql[k] != v:
                        old_content = old_mysql[k]
                        new_content = v
                        if k == 'account':
                            old_content = new_content = ''
                            alter_field = '帐号密码'
                        else:
                            alter_field = MysqlInstance._meta.get_field(k).help_text
                        MyqlHistoryRecord.objects.create(mysql=mysql[0], create_user=request.user, type=2,
                                                         old_content=old_content, new_content=new_content,
                                                         alter_field=alter_field, source_ip=source_ip)
            else:
                raw_data.pop('id', '')
                mysql = MysqlInstance.objects.create(**raw_data)
                # 新增记录
                MyqlHistoryRecord.objects.create(mysql=mysql, create_user=request.user, type=1, source_ip=source_ip)
        except Exception as e:
            success = False
            msg = str(e)
        finally:
            return JsonResponse({'success': success, 'msg': msg})


def get_instance_info(request):
    """获取数据库实例信息"""
    if request.method == 'POST':
        success = True
        data = dict()
        try:
            if not request.user.is_superuser:
                raise Exception('没有权限')
            raw_data = json.loads(request.body.decode('utf-8'))
            mysql_instance = MysqlInstance.objects.get(pk=raw_data.pop('id'))
            data = mysql_instance.edit_data()
        except Exception as e:
            success = False
            data = str(e)
        finally:
            return JsonResponse({'success': success, 'data': data})


def del_mysql_instance(request):
    """删除mysql实例"""
    if request.method == 'POST':
        success = True
        msg = 'ok'
        try:
            if not request.user.is_superuser:
                raise Exception('没有权限')
            id_list = json.loads(request.body.decode('utf-8'))
            mysql = MysqlInstance.objects.filter(id__in=id_list)
            # 删除记录
            source_ip = get_ip(request)
            for m in mysql:
                MyqlHistoryRecord.objects.filter(mysql=m).update(**{'remark': str(m.host or '') + ':' + m.port})
                MyqlHistoryRecord.objects.create(create_user=request.user, type=3, remark=str(m.host or '') + ':' + m.port,
                                                 source_ip=source_ip)
            mysql.delete()
        except Exception as e:
            success = False
            msg = str(e)
        finally:
            return JsonResponse({'success': success, 'msg': msg})


def mysql_history(request):
    """数据库实例变更记录"""
    if request.method == 'GET':
        if request.user.is_superuser:
            type = MyqlHistoryRecord.TYPE
            all_users = User.objects.all()
            return render(request, 'mysql_history.html', {'type': type, 'all_users': all_users})
        else:
            return render(request, '403.html')


def data_mysql_history(request):
    """数据库变更追踪数据"""
    if request.method == "POST":
        if request.user.is_superuser:
            raw_get = request.POST.dict()

            search_value = raw_get.get('search[value]', '')
            start = int(raw_get.get('start', 0))
            draw = raw_get.get('draw', 0)
            length = int(raw_get.get('length', 10))

            filter_type = raw_get.get('filter_type', '0')
            filter_create_user = raw_get.get('filter_create_user', '0')
            filter_instance = raw_get.get('filter_instance', '')
            filter_source_ip = raw_get.get('filter_source_ip', '')

            # 添加sub_query
            sub_query = Q()

            if filter_type != '0':
                sub_query.add(Q(type=filter_type), Q.AND)
            if filter_create_user != '0':
                sub_query.add(Q(create_user__id=filter_create_user), Q.AND)
            if filter_instance != '':
                sub_query.add((Q(mysql__host__icontains=filter_instance) | Q(
                    mysql__port__icontains=filter_instance) | Q(remark__icontains=filter_instance)), Q.AND)
            if filter_source_ip != '':
                sub_query.add(Q(source_ip__icontains=filter_source_ip), Q.AND)

            query = MyqlHistoryRecord.objects.select_related('mysql').select_related(
                'mysql__cmdb_area').select_related('mysql__project').filter(sub_query).order_by(
                '-create_time')

            raw_data = query[start: start + length]
            recordsTotal = query.count()
            data = {"data": [i.show_all() for i in raw_data], 'draw': draw, 'recordsTotal': recordsTotal,
                    'recordsFiltered': recordsTotal}
            return JsonResponse(data)


def get_mysql_history(request):
    """获取数据库变更记录"""
    if request.method == 'POST':
        success = True
        msg = 'ok'
        try:
            raw_data = json.loads(request.body.decode('utf-8'))
            mysql = MysqlInstance.objects.get(pk=raw_data.pop('id'))
            msg = [m.show_all() for m in mysql.myqlhistoryrecord_set.order_by('create_time')]
        except MysqlInstance.DoesNotExist:
            success = False
            msg = '数据库实例不存在'
        except Exception as e:
            success = False
            msg = str(e)
        finally:
            return JsonResponse({'success': success, 'msg': msg})
