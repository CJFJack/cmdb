from django.shortcuts import render
from webapi.models import WebGetCdnListAPI
from assets.models import GameProject
from assets.models import Area
from django.http import JsonResponse

import json


def web_get_cdn_list_api(request):
    """web-获取cdn目录api接口-列表页面"""
    if request.method == 'GET':
        if request.user.is_superuser:
            all_api = WebGetCdnListAPI.objects.all()
            all_version = WebGetCdnListAPI.VERSION
            return render(request, 'web_get_cdn_list_api.html', {'all_api': all_api, 'all_version': all_version})
        else:
            return render(request, '403.html')


def data_web_get_cdn_list_api(request):
    """项目与celery任务队列关系数据"""
    if request.method == 'POST':
        if request.user.is_superuser:
            draw = 0
            raw_data = WebGetCdnListAPI.objects.all()
            recordsTotal = raw_data.count()
            data = {"data": [i.show_all() for i in raw_data], 'draw': draw, 'recordsTotal': recordsTotal,
                    'recordsFiltered': recordsTotal}
            return JsonResponse(data)


def add_or_edit_get_cdn_list_api(request):
    """增加或者编辑获取cdn目录api配置信息"""
    if request.method == 'POST':
        msg = 'ok'
        success = True
        try:
            if not request.user.is_superuser:
                raise PermissionError
            raw_data = json.loads(request.body.decode('utf-8'))
            EditFlag = raw_data.pop('EditFlag')
            project = GameProject.objects.get(pk=raw_data.pop('project_id'))
            area = Area.objects.get(pk=raw_data.pop('area_id'))
            raw_data['project'] = project
            raw_data['area'] = area
            api_id = raw_data.pop('api_id')
            if EditFlag:
                api = WebGetCdnListAPI.objects.filter(id=api_id)
                api.update(**raw_data)
            else:
                WebGetCdnListAPI.objects.create(**raw_data)
        except PermissionError:
            success = False
            msg = '权限受限'
        except Exception as e:
            success = False
            msg = str(e)
        finally:
            return JsonResponse({'success': success, 'msg': msg})


def delete_get_cdn_list_api(request):
    """删除获取cdn目录api配置信息"""
    if request.method == 'POST':
        msg = 'ok'
        success = True
        try:
            if not request.user.is_superuser:
                raise PermissionError
            raw_data = json.loads(request.body.decode('utf-8'))
            api = WebGetCdnListAPI.objects.filter(id__in=raw_data)
            api.delete()
        except PermissionError:
            success = False
            msg = '权限受限'
        except Exception as e:
            success = False
            msg = str(e)
        finally:
            return JsonResponse({'success': success, 'msg': msg})


def get_get_cdn_list_api(request):
    """获取获取cdn目录api编辑数据"""
    if request.method == 'POST':
        msg = 'ok'
        success = True
        data = ''
        try:
            if not request.user.is_superuser:
                raise PermissionError
            raw_data = json.loads(request.body.decode('utf-8'))
            api_id = raw_data.get('id')
            api = WebGetCdnListAPI.objects.get(id=api_id)
            data = api.edit_data()
        except PermissionError:
            success = False
            msg = '权限受限'
        except Exception as e:
            success = False
            msg = str(e)
        finally:
            return JsonResponse({'success': success, 'msg': msg, 'data': data})
