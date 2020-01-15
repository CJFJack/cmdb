from django.shortcuts import render_to_response, render
from django.http import JsonResponse
from django.db.models import Q
from cmdb.logs import GameServerOffLog
from tasks import do_game_server_off
from tasks import do_modify_srv_open_time
from tasks import do_game_server_merge
from tasks import do_game_install
from tasks import do_game_uninstall
from ops.models import InstallGameServer, InstallGameServerRecord
from ops.models import GameServerOff
from ops.models import ModifyOpenSrvSchedule
from ops.models import GameServerMergeSchedule
from ops.utils import write_game_server_off_log
from ops.utils import ws_update_game_server_off_list
from ops.utils import ws_modify_srv_open_time_schedule_list
from ops.utils import write_modify_srv_open_time_schedule_log
from assets.models import GameProject
from assets.models import Room

import json
import datetime

from django.contrib.auth.decorators import permission_required
from django.utils.decorators import method_decorator


# Create your views here.


def install_gameserver_list(request):
    """开服计划
    """
    if request.user.is_superuser or request.user.has_perm('users.api_view_installgameserver_obj'):
        head = {'value': '开 / 卸服列表', 'username': request.user.username}
        status = {k: v for k, v in dict(InstallGameServer.STATUS).items()}
        data = {"status": status}
        return render(request, 'install_gameserver_list.html', {'head': head, 'data': data})
    else:
        return render(request, '403.html')


def install_gameserver_api(request):
    """API文档
    """
    if request.user.has_perm('users.api_doc'):
        return render(request, 'web_installgame_api_doc.html')
    else:
        return render(request, '403.html')


def data_install_gameserver_list(request):
    """开服计划数据
    """
    if request.method == "POST":
        if request.user.is_superuser or request.user.has_perm('users.api_view_installgameserver_obj'):
            raw_get = request.POST.dict()

            search_value = raw_get.get('search[value]', '')
            start = int(raw_get.get('start', 0))
            draw = raw_get.get('draw', 0)
            length = int(raw_get.get('length', 10))

            raw_data = ''

            if search_value:
                query = InstallGameServer.objects.select_related('project').filter(
                    Q(project__project_name__icontains=search_value) |
                    Q(area__icontains=search_value) |
                    Q(purpose__icontains=search_value) |
                    Q(host__icontains=search_value) |
                    Q(port__icontains=search_value))
            else:
                query = InstallGameServer.objects.select_related('project').all()

            raw_data = query[start: start + length]
            recordsTotal = query.count()
            data = {"data": [i.show_all() for i in raw_data], 'draw': draw, 'recordsTotal': recordsTotal,
                    'recordsFiltered': recordsTotal}
            return JsonResponse(data)
        else:
            return JsonResponse([], safe=False)


def get_install_game(request):
    """获取开服计划
    """
    if request.method == "POST":
        if request.user.is_superuser:
            raw_body = json.loads(request.body.decode('utf-8'))
            id = raw_body.get('id')
            instance = InstallGameServer.objects.get(id=id)
            edit_data = {
                'id': instance.id,
                'srv_name': instance.srv_name,
                'status': instance.status,
            }
            return JsonResponse(edit_data)


def edit_install_game(request):
    """修改开服计划
    """
    if request.method == "POST":
        if request.user.is_superuser:
            raw_body = json.loads(request.body.decode('utf-8'))
            id = raw_body.get('id')
            instance = InstallGameServer.objects.get(id=id)
            status = raw_body.get('status')
            instance.status = status
            instance.save()
            data = True
            msg = 'ok'
            return JsonResponse({'data': data, 'msg': msg})


def game_install(request):
    """开始装服
    """

    if request.method == "POST":
        if request.user.is_superuser or request.user.has_perm('users.api_edit_installgameserver_obj'):
            raw_body = json.loads(request.body.decode('utf-8'))
            do_game_install.delay(raw_body, request.user.id)
            for id in raw_body:
                InstallGameServerRecord.objects.create(OperationUser=request.user, InstallGameServer_id=id,
                                                       OperationType=0)
            return JsonResponse({'data': True, 'msg': 'ok'})
        else:
            return JsonResponse({'data': False, 'msg': '权限拒绝'})


def game_uninstall(request):
    """开始卸载服
    """

    if request.method == "POST":
        if request.user.is_superuser or request.user.has_perm('users.api_edit_installgameserver_obj'):
            raw_body = json.loads(request.body.decode('utf-8'))
            do_game_uninstall.delay(raw_body, request.user.id)
            for id in raw_body:
                InstallGameServerRecord.objects.create(OperationUser=request.user, InstallGameServer_id=id,
                                                       OperationType=4)
            return JsonResponse({'data': True, 'msg': 'ok'})
        else:
            return JsonResponse({'data': False, 'msg': '权限拒绝'})


def mysql_instance_api(request):
    """数据库实例api文档
    """
    if request.method == "GET":
        if request.user.is_superuser:
            return render(request, 'mysql_api_doc.html')
        else:
            return render(request, '403.html')


def install_game_server_record(request):
    """开服计划操作记录"""
    if request.user.is_superuser:
        install_game_server_record_list = InstallGameServerRecord.objects.order_by('-id')
        return render(request, 'install_gameserver_record_list.html',
                      {'install_game_server_record_list': install_game_server_record_list})
    else:
        return render(request, '403.html')


def game_server_off_list(request):
    """游戏区服下线计划列表页面"""
    if request.user.has_perm('users.api_view_gameserveroff_schedule'):
        status_list = []
        status_tuple = GameServerOff.STATUS
        for x in status_tuple:
            status_list.append({'id': x[0], 'text': x[1]})
        game_project = [{'id': x.id, 'text': x.project_name} for x in GameProject.objects.filter(is_game_project=1)]
        return render(request, 'game_server_off_list.html', {'status_list': status_list, 'game_project': game_project})
    else:
        return render(request, '403.html')


def data_game_server_off_list(request):
    """区服下线列表数据"""
    if request.method == "POST":
        raw_get = request.POST.dict()

        search_value = raw_get.get('search[value]', '')
        start = int(raw_get.get('start', 0))
        draw = raw_get.get('draw', 0)
        length = int(raw_get.get('length', 10))

        filter_uuid = raw_get.get('filter_uuid', '')
        filter_web_callback_url = raw_get.get('filter_web_callback_url', '')
        filter_status = raw_get.get('filter_status', 0)
        filter_project = raw_get.get('filter_project', 0)
        filter_game_server = raw_get.get('filter_game_server', '')
        filter_start_off_time = raw_get.get('filter_start_off_time', '')
        filter_end_off_time = raw_get.get('filter_end_off_time', '')
        filter_start_create_time = raw_get.get('filter_start_create_time', '')
        filter_end_create_time = raw_get.get('filter_end_create_time', '')

        # 添加sub_query
        sub_query = Q()

        if filter_uuid != '':
            sub_query.add(Q(uuid__icontains=filter_uuid), Q.AND)
        if filter_web_callback_url != '':
            sub_query.add(Q(web_callback_url__icontains=filter_web_callback_url), Q.AND)
        if filter_game_server != '':
            sub_query.add(Q(gameserveroffdetail__game_server__sid__icontains=filter_game_server), Q.AND)
        if str(filter_status) != '全部':
            sub_query.add(Q(status=filter_status), Q.AND)
        if str(filter_project) != '全部':
            sub_query.add(Q(gameserveroffdetail__game_server__project__id__icontains=filter_project), Q.AND)
        if filter_start_off_time != '':
            sub_query.add(Q(off_time__gte=filter_start_off_time), Q.AND)
        if filter_end_off_time != '':
            sub_query.add(Q(off_time__lte=filter_end_off_time), Q.AND)
        if filter_start_create_time != '':
            sub_query.add(Q(create_time__gte=filter_start_create_time), Q.AND)
        if filter_end_create_time != '':
            sub_query.add(Q(create_time__lte=filter_end_create_time), Q.AND)

        if search_value:
            query = GameServerOff.objects.prefetch_related('gameserveroffdetail_set').filter(
                (
                        Q(uuid__icontains=search_value) |
                        Q(gameserveroffdetail__game_server__project__project_name__icontains=search_value) |
                        Q(gameserveroffdetail__game_server__project__project_name_en__icontains=search_value) |
                        Q(
                            gameserveroffdetail__game_server__host__belongs_to_room__area__chinese_name__icontains=search_value) |
                        Q(gameserveroffdetail__game_server__srv_id__icontains=search_value) |
                        Q(gameserveroffdetail__game_server__sid__icontains=search_value) |
                        Q(uuid__icontains=search_value)
                ) & sub_query
            ).order_by('-id').distinct()

        else:
            query = GameServerOff.objects.filter(sub_query).order_by('-create_time').distinct()

        raw_data = query[start: start + length]
        recordsTotal = query.count()
        data = {"data": [i.show_all() for i in raw_data], 'draw': draw, 'recordsTotal': recordsTotal,
                'recordsFiltered': recordsTotal}
        return JsonResponse(data)


def get_data_game_server_off(request):
    """获取区服下线计划数据"""
    if request.method == 'POST':
        try:
            if not request.user.has_perm('users.api_edit_gameserveroff_schedule'):
                raise Exception('权限受限')
            raw_data = json.loads(request.body.decode('utf-8'))
            id = raw_data.get('id')
            game_server_off = GameServerOff.objects.get(pk=id)
            data = game_server_off.edit_data()
            data['success'] = True
            return JsonResponse(data)
        except Exception as e:
            return JsonResponse({'success': False, 'msg': str(e)})


def list_game_server_off_status(request):
    """列出区服下线任务所有可用状态"""
    if request.method == 'POST':
        status_tuple = GameServerOff.STATUS
        status_list = [{'id': x[0], 'text': x[1]} for x in status_tuple if x[0] != 4]
        return JsonResponse(status_list, safe=False)


def edit_game_server_off(request):
    """修改区服下线计划"""
    if request.method == 'POST':
        try:
            if not request.user.has_perm('users.api_edit_gameserveroff_schedule'):
                raise Exception('权限受限')
            raw_data = json.loads(request.body.decode('utf-8'))
            id = raw_data.pop('id')
            game_server_off = GameServerOff.objects.filter(id=id)
            game_server_off.update(**raw_data)
            """如果修改状态为未下线，则子任务相应状态也需要修改"""
            if game_server_off[0].status == 1:
                for task in game_server_off[0].gameserveroffdetail_set.all():
                    task.status = 2
                    task.save(update_fields=['status'])
            return JsonResponse({'success': True, 'msg': 'ok'})
        except Exception as e:
            return JsonResponse({'success': False, 'msg': str(e)})


def execute_game_server_off(request):
    """执行区服下线请求"""
    if request.method == 'POST':
        msg = '开始执行，请耐心等待！'
        success = True
        try:
            if not request.user.has_perm('users.api_edit_gameserveroff_schedule'):
                raise Exception('权限受限')
            log = GameServerOffLog()
            raw_data = json.loads(request.body.decode('utf-8'))
            id = raw_data.pop('id')
            off_schedule = GameServerOff.objects.get(pk=id)
            if off_schedule.status == 1:
                off_schedule.status = 2
                off_schedule.save(update_fields=['status'])
                """通知刷新列表页面"""
                ws_update_game_server_off_list()
            else:
                raise Exception('执行失败！任务不是处于未执行状态')
            log.logger.info(request.user.username + '-手动执行区服下线任务-' + off_schedule.uuid)
            """记录任务日志"""
            content = request.user.username + '，手动执行区服下线任务'
            level = 'INFO'
            write_game_server_off_log(level, content, off_schedule)
            """调用运维管理机API接口发送区服下线请求"""
            do_game_server_off.delay(off_schedule.uuid)

        except Exception as e:
            msg = str(e)
            success = False
        finally:
            return JsonResponse({'success': success, 'msg': msg})


def game_server_off_detail(request, id):
    """区服下线计划详情"""
    if request.method == 'GET':
        if request.user.has_perm('users.api_view_gameserveroff_schedule'):
            game_server_off_obj = GameServerOff.objects.prefetch_related('gameserveroffdetail_set').filter(pk=id)
            game_server_off_obj = game_server_off_obj[0]
            total = game_server_off_obj.gameserveroffdetail_set.all().count()
            finish = game_server_off_obj.gameserveroffdetail_set.exclude(status=2).count()
            success = game_server_off_obj.gameserveroffdetail_set.filter(status=1).count()
            failure = game_server_off_obj.gameserveroffdetail_set.filter(status=0).count()
            return render(request, 'game_server_off_detail.html',
                          {'game_server_off_obj': game_server_off_obj, 'total': total,
                           'finish': finish, 'success': success,
                           'failure': failure})
        else:
            return render(request, '403.html')


def game_server_off_cmdb_log(request, id):
    """区服下线任务日志"""
    if request.method == 'GET':
        if request.user.has_perm('users.api_view_gameserveroff_schedule'):
            game_server_off_obj = GameServerOff.objects.get(pk=id)
            id = game_server_off_obj.id
            log = game_server_off_obj.gameserverofflog.log
            return render(request, 'game_server_off_cmdb_log.html', {'log': log, 'id': id})
        else:
            return render(request, '403.html')


def cmdb_add_gameserveroff_doc(request):
    """cmdb增加区服下架计划文档"""
    if request.method == 'GET':
        if request.user.has_perm('users.api_doc'):
            return render(request, 'cmdb_add_gameserveroff_doc.html')
        else:
            return render(request, '403.html')


def modify_srv_open_time_schedule_list(request):
    """修改开服时间计划列表页面"""
    if request.user.has_perm('users.api_view_modify_srv_opentime_schedule'):
        status_list = []
        status_tuple = ModifyOpenSrvSchedule.STATUS
        for x in status_tuple:
            status_list.append({'id': x[0], 'text': x[1]})
        game_project = [{'id': x.id, 'text': x.project_name} for x in GameProject.objects.filter(is_game_project=1)]
        return render(request, 'modify_srv_open_time_schedule_list.html',
                      {'status_list': status_list, 'game_project': game_project})
    else:
        return render(request, '403.html')


def data_modify_srv_open_time_schedule_list(request):
    """修改开服时间计划列表数据"""
    if request.method == "POST":
        raw_get = request.POST.dict()

        search_value = raw_get.get('search[value]', '')
        start = int(raw_get.get('start', 0))
        draw = raw_get.get('draw', 0)
        length = int(raw_get.get('length', 10))

        filter_status = raw_get.get('filter_status', 0)
        filter_project = raw_get.get('filter_project', 0)
        filter_uuid = raw_get.get('filter_uuid', '')
        filter_start_open_time = raw_get.get('filter_start_open_time', '')
        filter_end_open_time = raw_get.get('filter_end_open_time', '')
        filter_start_create_time = raw_get.get('filter_start_create_time', '')
        filter_end_create_time = raw_get.get('filter_end_create_time', '')
        filter_game_server = raw_get.get('filter_game_server', '')

        # 添加sub_query
        sub_query = Q()

        if str(filter_status) != '全部':
            sub_query.add(Q(status=filter_status), Q.AND)
        if str(filter_project) != '全部':
            sub_query.add(Q(modifyopensrvscheduledetail__game_server__project__id__icontains=filter_project), Q.AND)
        if filter_uuid != '':
            sub_query.add(Q(uuid__icontains=filter_uuid), Q.AND)
        if filter_game_server != '':
            sub_query.add(Q(modifyopensrvscheduledetail__game_server__sid__icontains=filter_game_server), Q.AND)
        if filter_start_open_time != '':
            sub_query.add(Q(open_time__gte=filter_start_open_time), Q.AND)
        if filter_end_open_time != '':
            sub_query.add(Q(open_time__lte=filter_end_open_time), Q.AND)
        if filter_start_create_time != '':
            sub_query.add(Q(create_time__gte=filter_start_create_time), Q.AND)
        if filter_end_create_time != '':
            sub_query.add(Q(create_time__lte=filter_end_create_time), Q.AND)

        if search_value:
            query = ModifyOpenSrvSchedule.objects.prefetch_related('modifyopensrvscheduledetail_set').filter(
                (
                        Q(uuid__icontains=search_value) |
                        Q(modifyopensrvscheduledetail__game_server__project__project_name__icontains=search_value) |
                        Q(modifyopensrvscheduledetail__game_server__project__project_name_en__icontains=search_value) |
                        Q(
                            modifyopensrvscheduledetail__game_server__host__belongs_to_room__area__chinese_name__icontains=search_value) |
                        Q(modifyopensrvscheduledetail__game_server__srv_id__icontains=search_value) |
                        Q(modifyopensrvscheduledetail__game_server__sid__icontains=search_value) |
                        Q(uuid__icontains=search_value)
                ) & sub_query
            ).order_by('-id').distinct()

        else:
            query = ModifyOpenSrvSchedule.objects.filter(sub_query).order_by('-create_time').distinct()

        raw_data = query[start: start + length]
        recordsTotal = query.count()
        data = {"data": [i.show_all() for i in raw_data], 'draw': draw, 'recordsTotal': recordsTotal,
                'recordsFiltered': recordsTotal}
        return JsonResponse(data)


def get_data_modify_srv_open_time_schedule(request):
    """获取修改开服时间计划数据"""
    if request.method == 'POST':
        try:
            if not request.user.has_perm('users.api_edit_modify_srv_opentime_schedule'):
                raise Exception('权限受限')
            raw_data = json.loads(request.body.decode('utf-8'))
            id = raw_data.get('id')
            modify_schedule = ModifyOpenSrvSchedule.objects.get(pk=id)
            data = modify_schedule.edit_data()
            data['success'] = True
            return JsonResponse(data)
        except Exception as e:
            return JsonResponse({'success': False, 'msg': str(e)})


def list_modify_srv_open_time_schedule_status(request):
    """列出修改开服时间计划所有可用状态"""
    if request.method == 'POST':
        status_list = []
        status_tuple = ModifyOpenSrvSchedule.STATUS
        for x in status_tuple:
            status_list.append({'id': x[0], 'text': x[1]})
        return JsonResponse(status_list, safe=False)


def edit_modify_srv_open_time_schedule(request):
    """修改修改开副时间计划"""
    if request.method == 'POST':
        try:
            if not request.user.has_perm('users.api_edit_modify_srv_opentime_schedule'):
                raise Exception('权限受限')
            raw_data = json.loads(request.body.decode('utf-8'))
            id = raw_data.pop('id')
            modify_schedule = ModifyOpenSrvSchedule.objects.filter(id=id)
            modify_schedule.update(**raw_data)
            """如果修改状态为未下线，则子任务相应状态也需要修改"""
            if modify_schedule[0].status == 1:
                for task in modify_schedule[0].modifyopensrvscheduledetail_set.all():
                    task.status = 2
                    task.save(update_fields=['status'])
            return JsonResponse({'success': True, 'msg': 'ok'})
        except Exception as e:
            return JsonResponse({'success': False, 'msg': str(e)})


def modify_srv_open_time_schedule_detail(request, id):
    """修改开服时间计划详情"""
    if request.method == 'GET':
        if request.user.has_perm('users.api_view_modify_srv_opentime_schedule'):
            modify_schedule = ModifyOpenSrvSchedule.objects.prefetch_related('modifyopensrvscheduledetail_set').filter(
                pk=id)
            modify_schedule = modify_schedule[0]
            total = modify_schedule.modifyopensrvscheduledetail_set.all().count()
            finish = modify_schedule.modifyopensrvscheduledetail_set.exclude(status=2).count()
            success = modify_schedule.modifyopensrvscheduledetail_set.filter(status=1).count()
            failure = modify_schedule.modifyopensrvscheduledetail_set.filter(status=0).count()
            return render(request, 'modify_srv_open_time_schedule_detail.html',
                          {'modify_schedule': modify_schedule, 'total': total,
                           'finish': finish, 'success': success,
                           'failure': failure})
        else:
            return render(request, '403.html')


def modify_srv_open_time_schedule_cmdb_log(request, id):
    """修改开服时间计划日志"""
    if request.method == 'GET':
        if request.user.has_perm('users.api_view_modify_srv_opentime_schedule'):
            modify_schedule = ModifyOpenSrvSchedule.objects.get(pk=id)
            id = modify_schedule.id
            log = modify_schedule.modifyopensrvschedulelog.log
            return render(request, 'modify_srv_open_time_schedule_cmdb_log.html', {'log': log, 'id': id})
        else:
            return render(request, '403.html')


def execute_modify_srv_open_time_schedule(request):
    """手动执行修改开服时间请求"""
    if request.method == 'POST':
        msg = '开始执行，请耐心等待！'
        success = True
        try:
            if not request.user.has_perm('users.api_edit_modify_srv_opentime_schedule'):
                raise Exception('权限受限')
            raw_data = json.loads(request.body.decode('utf-8'))
            id = raw_data.pop('id')
            modify_schedule = ModifyOpenSrvSchedule.objects.get(pk=id)
            if modify_schedule.status == 1:
                modify_schedule.status = 2
                modify_schedule.save(update_fields=['status'])
                """通知刷新列表页面"""
                ws_modify_srv_open_time_schedule_list()
            else:
                raise Exception('执行失败！任务不是处于未执行状态')
            """记录任务日志"""
            content = request.user.username + '，手动执行修改开服时间任务'
            level = 'INFO'
            write_modify_srv_open_time_schedule_log(level, content, modify_schedule)
            """调用运维管理机API接口发送区服下线请求"""
            do_modify_srv_open_time.delay(modify_schedule.uuid)

        except Exception as e:
            msg = str(e)
            success = False
        finally:
            return JsonResponse({'success': success, 'msg': msg})


def cmdb_modsrv_opentime_api_doc(request):
    """cmdb修改开服时间api文档"""
    if request.user.has_perm('users.api_doc'):
        return render(request, 'cmdb_modsrv_opentime_api_doc.html')
    else:
        return render(request, '403.html')


def cmdb_modsrv_opentime_callback_api_doc(request):
    """cmdb修改开服时间回调api文档"""
    if request.user.is_superuser:
        return render(request, 'cmdb_modsrv_opentime_callback_api_doc.html')
    else:
        return render(request, '403.html')


def game_server_merge_list(request):
    """区服合并列表页面"""
    if request.user.has_perm('users.api_view_game_srv_merge_schedule'):
        status = GameServerMergeSchedule.STATUS
        all_project = GameProject.objects.filter(status=1, is_game_project=1)
        all_room = [{'id': x.id, 'text': x.area.chinese_name + '-' + x.room_name} for x in
                    Room.objects.select_related('area')]
        return render(request, 'game_server_merge_list.html', {'status': status, 'all_project': all_project,
                                                               'all_room': all_room})
    else:
        return render(request, '403.html')


def data_game_server_merge_list(request):
    """区服合并列表数据"""
    if request.method == "POST":
        raw_get = request.POST.dict()

        search_value = raw_get.get('search[value]', '')
        start = int(raw_get.get('start', 0))
        draw = raw_get.get('draw', 0)
        length = int(raw_get.get('length', 10))

        # 添加sub_query
        sub_query = Q()

        filter_status = raw_get.get('filter_status', 100)
        filter_project = raw_get.get('filter_project', 0)
        filter_room = raw_get.get('filter_room', 0)
        filter_main_srv = raw_get.get('filter_main_srv', '')
        filter_slave_srv = raw_get.get('filter_slave_srv', '')
        filter_group_id = raw_get.get('filter_group_id', '')

        if str(filter_status) != '100':
            sub_query.add(Q(status=filter_status), Q.AND)
        if str(filter_project) != '0':
            sub_query.add(Q(project_id=filter_project), Q.AND)
        if str(filter_room) != '0':
            sub_query.add(Q(room_id=filter_room), Q.AND)
        if filter_main_srv != '':
            sub_query.add(Q(main_srv__icontains=filter_main_srv), Q.AND)
        if filter_slave_srv != '':
            sub_query.add(Q(slave_srv__icontains=filter_slave_srv), Q.AND)
        if filter_group_id != '':
            sub_query.add(Q(group_id__icontains=filter_group_id), Q.AND)

        if search_value:
            status_tuple = GameServerMergeSchedule.STATUS
            status_list = [x[0] for x in status_tuple if search_value in x[1]]
            query = GameServerMergeSchedule.objects.select_related('project').select_related('room').filter(
                (
                        Q(project__project_name__icontains=search_value) |
                        Q(project__project_name_en__icontains=search_value) |
                        Q(room__area__chinese_name__icontains=search_value) |
                        Q(room__area__short_name__icontains=search_value) |
                        Q(room__room_name__icontains=search_value) |
                        Q(room__room_name_en__icontains=search_value) |
                        Q(main_srv__icontains=search_value) |
                        Q(slave_srv__icontains=search_value) |
                        Q(status__in=status_list) |
                        Q(group_id__icontains=search_value) |
                        Q(uuid__icontains=search_value)
                ) & sub_query
            ).order_by('-id').distinct()

        else:
            query = GameServerMergeSchedule.objects.filter(sub_query).order_by('-id').distinct()

        raw_data = query[start: start + length]
        recordsTotal = query.count()
        data = {"data": [i.show_all() for i in raw_data], 'draw': draw, 'recordsTotal': recordsTotal,
                'recordsFiltered': recordsTotal}
        return JsonResponse(data)


def get_edit_data_game_server_merge(request):
    """获取合服计划编辑数据"""
    if request.method == 'POST':
        try:
            if not request.user.is_superuser:
                raise Exception('权限受限')
            raw_data = json.loads(request.body.decode('utf-8'))
            id = raw_data.get('id')
            gsms = GameServerMergeSchedule.objects.get(pk=id)
            data = gsms.edit_data()
            data['success'] = True
            return JsonResponse(data)
        except Exception as e:
            return JsonResponse({'success': False, 'msg': str(e)})


def edit_game_server_merge_status(request):
    """修改合服计划状态"""
    if request.method == 'POST':
        try:
            if not request.user.is_superuser:
                raise Exception('权限受限')
            raw_data = json.loads(request.body.decode('utf-8'))
            id = raw_data.pop('id')
            gsms = GameServerMergeSchedule.objects.filter(id=id)
            gsms.update(**raw_data)
            return JsonResponse({'success': True, 'msg': 'ok'})
        except Exception as e:
            return JsonResponse({'success': False, 'msg': str(e)})


def cmdb_game_server_merge_api_doc(request):
    """cmdb接收web合服计划接口文档"""
    if request.user.has_perm('users.api_doc'):
        return render(request, 'cmdb_game_server_merge_api_doc.html')
    else:
        return render(request, '403.html')


def execute_game_server_merge_schedule(request):
    """发送合服计划到运维管理机"""
    if request.method == 'POST':
        success = True
        msg = ''
        raw_data = json.loads(request.body.decode('utf-8'))
        try:
            merge_id = raw_data.get('id', '')
            if isinstance(merge_id, list):
                obj = GameServerMergeSchedule.objects.filter(id__in=merge_id)
                uuid_list = list(set([x.uuid for x in obj]))
                if len(uuid_list) == 1:
                    uuid = uuid_list[0]
                    send_data = []
                    for x in obj:
                        send_data += json.loads(x.send_data())
                    send_data = json.dumps(send_data)
                else:
                    raise Exception('必须选择相同uuid的任务')
            else:
                obj = GameServerMergeSchedule.objects.get(pk=merge_id)
                uuid = obj.uuid
                send_data = obj.send_data()

            res = do_game_server_merge(send_data, uuid)
            success = res['success']
            msg = res['msg']

        except Exception as e:
            success = False
            msg = str(e)
        finally:
            return JsonResponse({'success': success, 'msg': msg})


def rollback_game_server_merge_schedule(request):
    """回滚合服计划到运维管理机"""
    if request.method == 'POST':
        success = True
        msg = ''
        raw_data = json.loads(request.body.decode('utf-8'))
        try:
            merge_id = raw_data.get('id', '')

            if isinstance(merge_id, list):
                obj = GameServerMergeSchedule.objects.filter(id__in=merge_id)
                uuid_list = list(set([x.uuid for x in obj]))
                if len(uuid_list) == 1:
                    uuid = uuid_list[0]
                    send_data = []
                    for x in obj:
                        send_data += json.loads(x.send_data())
                    send_data = json.dumps(send_data)
                else:
                    raise Exception('必须选择相同uuid的任务')
            else:
                obj = GameServerMergeSchedule.objects.get(pk=merge_id)
                uuid = obj.uuid
                send_data = obj.send_data()

            res = do_game_server_merge(send_data, uuid, type=2)
            success = res['success']
            msg = res['msg']

        except Exception as e:
            success = False
            msg = str(e)
        finally:
            return JsonResponse({'success': success, 'msg': msg})


def in_or_uninstall_gamesrv_callback_api_doc(request):
    """装/卸区服回调API文档"""
    if request.method == 'GET':
        if request.user.is_superuser:
            return render(request, 'cmdb_in_or_uninstallgamesrv_callback_api_doc.html')
        else:
            return render(request, '403.html')


def cmdb_release_doc(request):
    """cmdb部署文档"""
    if request.method == 'GET':
        if request.user.is_superuser:
            return render(request, 'cmdb_release.html')
        else:
            return render(request, '403.html')
