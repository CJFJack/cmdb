from django.shortcuts import render
from django.http import JsonResponse
from myworkflows.models import ClientHotUpdate
from myworkflows.models import ServerHotUpdate
from myworkflows.models import HostCompressionApply
from myworkflows.models import WorkflowStateEvent
from myworkflows.models import GameServerActionRecord
from myworkflows.models import VersionUpdate
from ops.models import GameServerOff
from ops.models import ModifyOpenSrvSchedule
from ops.models import GameServerMergeSchedule
from ops.models import InstallGameServer
from assets.models import SaltConfig
from assets.models import HostInitialize
from itertools import islice
from django.db.models import Q
from datetime import datetime, timedelta
import heapq


def dashboard_page(request):
    """仪表盘"""
    if request.method == 'GET':
        if request.user.is_superuser:
            """待审批工单"""
            sor_query = WorkflowStateEvent.objects.prefetch_related('users').filter(
                Q(is_current=True) & Q(state_value=None)).exclude(state__name='完成').order_by('-create_time')
            sor_query = [x for x in sor_query if request.user in x.users.all()]
            all_query = list(set(sor_query))
            all_query.sort(key=lambda x: x.create_time, reverse=True)
            all_query = all_query[:5]
            unapprove = [{'url': '/myworkflows/workflow_approve/?id=' + str(x.id), 'title': str(x.title)[:40] + '...',
                          't': int((datetime.now() - x.create_time).seconds / 60)} for x in all_query]
            """最近审批记录"""
            thirty_days_ago = datetime.now() - timedelta(days=30)
            all_query = WorkflowStateEvent.objects.select_related('creator').select_related('state').filter(
                Q(approve_user=request.user)).filter(create_time__gte=thirty_days_ago).order_by('-create_time')[:5]
            approved = [{'url': '/myworkflows/workflow_approve/?id=' + str(x.id), 'title': str(x.title)[:40] + '...',
                         's': x.get_state_value()} for x in all_query]
            """最近申请记录"""
            query = WorkflowStateEvent.objects.select_related('state').select_related(
                'state__workflow').filter(Q(is_current=True) & Q(creator=request.user)).filter(
                create_time__gte=thirty_days_ago).order_by('-create_time')[:5]
            apply_history = [{'url': '/myworkflows/myworkflow/?object_id=' + str(x.object_id) + '&id=' + str(
                x.id) + '&ctype_id=' + str(x.get_ctype_id()), 'title': str(x.title)[:40] + '...',
                              's': x.get_state_value()} for x in query]
            return render(request, 'dashboard.html',
                          {'unapprove': unapprove, 'approved': approved, 'apply_history': apply_history})
        else:
            return render(request, 'myindex.html')


def hot_update_pie(request):
    """热更新饼图数据"""
    if request.method == 'POST':
        success = True
        msg = 'ok'
        try:
            data_list = [
                {'name': '更新失败', 'value': 0, 'url': '/myworkflows/hot_server_list/?status=2'},
                {'name': '更新成功', 'value': 0, 'url': '/myworkflows/hot_server_list/?status=3'},
                {'name': '更新中', 'value': 0, 'url': '/myworkflows/hot_server_list/?status=1'},
                {'name': '待更新', 'value': 0, 'url': '/myworkflows/hot_server_list/?status=4'},
            ]
            legend = ['更新成功', '更新失败', '更新中', '待更新']
            text = '热更新统计'
            subtext = '最近30次热更新'
            reversed_hot_server_iter = ServerHotUpdate.objects.order_by('-create_time')[:200]
            reversed_hot_client_iter = ClientHotUpdate.objects.order_by('-create_time')[:200]

            heapq_merge = heapq.merge(
                reversed_hot_server_iter, reversed_hot_client_iter, key=lambda obj: obj.create_time, reverse=True)
            heapq_merge = islice(heapq_merge, 0, 32)
            for x in heapq_merge:
                if x.status == '1':
                    data_list[2]['value'] += 1
                if x.status == '2':
                    data_list[0]['value'] += 1
                if x.status == '3':
                    data_list[1]['value'] += 1
                if x.status == '4':
                    data_list[3]['value'] += 1
            return JsonResponse(
                {'data_list': data_list, 'legend': legend, 'text': text, 'subtext': subtext, 'success': success})
        except Exception as e:
            success = False
            msg = str(e)
            return JsonResponse({'msg': msg, 'success': success})


def host_migrate_pie(request):
    """主机迁服饼图数据"""
    if request.method == 'POST':
        success = True
        msg = 'ok'
        try:
            data_list = [
                {'name': '迁服失败', 'value': 0, 'url': '/myworkflows/host_compression_apply_list/?migrate_status=4'},
                {'name': '迁服成功', 'value': 0, 'url': '/myworkflows/host_compression_apply_list/?migrate_status=3'},
                {'name': '迁服中', 'value': 0, 'url': '/myworkflows/host_compression_apply_list/?migrate_status=2'},
                {'name': '待迁服', 'value': 0, 'url': '/myworkflows/host_compression_apply_list/?migrate_status=1'},
            ]
            legend = ['迁服成功', '迁服失败', '迁服中', '待迁服']
            text = '主机迁服统计'
            subtext = '最近30次主机迁服'
            host_migrate = HostCompressionApply.objects.filter(type=2).order_by('-apply_time')

            host_migrate = host_migrate[:30]
            for x in host_migrate:
                if x.action_status == 2:
                    data_list[2]['value'] += 1
                if x.action_status == 3:
                    data_list[1]['value'] += 1
                if x.action_status == 4:
                    data_list[0]['value'] += 1
                if x.action_status == 1:
                    data_list[3]['value'] += 1
            return JsonResponse(
                {'data_list': data_list, 'legend': legend, 'text': text, 'subtext': subtext, 'success': success})
        except Exception as e:
            success = False
            msg = str(e)
            return JsonResponse({'msg': msg, 'success': success})


def host_recover_pie(request):
    """主机回收饼图数据"""
    if request.method == 'POST':
        success = True
        msg = 'ok'
        try:
            data_list = [
                {'name': '回收失败', 'value': 0, 'url': '/myworkflows/host_compression_apply_list/?recover_status=4'},
                {'name': '回收成功', 'value': 0, 'url': '/myworkflows/host_compression_apply_list/?recover_status=3'},
                {'name': '回收中', 'value': 0, 'url': '/myworkflows/host_compression_apply_list/?recover_status=2'},
                {'name': '待回收', 'value': 0, 'url': '/myworkflows/host_compression_apply_list/?recover_status=1'},
            ]
            legend = ['回收成功', '回收失败', '回收中', '待回收']
            text = '主机回收统计'
            subtext = '最近30次主机回收'
            host_migrate = HostCompressionApply.objects.order_by('-apply_time')

            host_migrate = host_migrate[:30]
            for x in host_migrate:
                if x.recover_status == 2:
                    data_list[2]['value'] += 1
                if x.recover_status == 3:
                    data_list[1]['value'] += 1
                if x.recover_status == 4:
                    data_list[0]['value'] += 1
                if x.recover_status == 1:
                    data_list[3]['value'] += 1
            return JsonResponse(
                {'data_list': data_list, 'legend': legend, 'text': text, 'subtext': subtext, 'success': success})
        except Exception as e:
            success = False
            msg = str(e)
            return JsonResponse({'msg': msg, 'success': success})


def game_server_off_pie(request):
    """区服下线饼图数据"""
    if request.method == 'POST':
        success = True
        msg = 'ok'
        try:
            data_list = [
                {'name': '下架失败', 'value': 0, 'url': '/ops/game_server_off_list/?status=4'},
                {'name': '下架成功', 'value': 0, 'url': '/ops/game_server_off_list/?status=3'},
                {'name': '下架中', 'value': 0, 'url': '/ops/game_server_off_list/?status=2'},
                {'name': '待下架', 'value': 0, 'url': '/ops/game_server_off_list/?status=1'},
            ]
            legend = ['下架成功', '下架失败', '下架中', '待下架']
            text = '游戏项目下架统计'
            subtext = '最近30次项目下架'
            game_server_off = GameServerOff.objects.order_by('-create_time')

            game_server_off = game_server_off[:30]
            for x in game_server_off:
                if x.status == 2:
                    data_list[2]['value'] += 1
                if x.status == 3:
                    data_list[1]['value'] += 1
                if x.status == 4:
                    data_list[0]['value'] += 1
                if x.status == 1:
                    data_list[3]['value'] += 1
            return JsonResponse(
                {'data_list': data_list, 'legend': legend, 'text': text, 'subtext': subtext, 'success': success})
        except Exception as e:
            success = False
            msg = str(e)
            return JsonResponse({'msg': msg, 'success': success})


def modsrv_opentime_pie(request):
    """修改开服时间饼图数据"""
    if request.method == 'POST':
        success = True
        msg = 'ok'
        try:
            data_list = [
                {'name': '修改失败', 'value': 0, 'url': '/ops/modify_srv_open_time_schedule_list/?status=4'},
                {'name': '修改成功', 'value': 0, 'url': '/ops/modify_srv_open_time_schedule_list/?status=3'},
                {'name': '修改中', 'value': 0, 'url': '/ops/modify_srv_open_time_schedule_list/?status=2'},
                {'name': '待修改', 'value': 0, 'url': '/ops/modify_srv_open_time_schedule_list/?status=1'},
            ]
            legend = ['修改成功', '修改失败', '修改中', '待修改']
            text = '修改开服时间统计'
            subtext = '最近30次修改开服时间'
            modify_schedule = ModifyOpenSrvSchedule.objects.order_by('-create_time')

            modify_schedule = modify_schedule[:30]
            for x in modify_schedule:
                if x.status == 2:
                    data_list[2]['value'] += 1
                if x.status == 3:
                    data_list[1]['value'] += 1
                if x.status == 4:
                    data_list[0]['value'] += 1
                if x.status == 1:
                    data_list[3]['value'] += 1
            return JsonResponse(
                {'data_list': data_list, 'legend': legend, 'text': text, 'subtext': subtext, 'success': success})
        except Exception as e:
            success = False
            msg = str(e)
            return JsonResponse({'msg': msg, 'success': success})


def system_cron_pie(request):
    """系统作业饼图数据"""
    if request.method == 'POST':
        success = True
        msg = 'ok'
        try:
            data_list = [
                {'name': '全部失败', 'value': 0, 'url': '/assets/system_cron_list/?current_page&status=全部失败'},
                {'name': '全部成功', 'value': 0, 'url': '/assets/system_cron_list/?current_page&status=全部成功'},
                {'name': '部分失败', 'value': 0, 'url': '/assets/system_cron_list/?current_page&status=部分失败'},
            ]
            legend = ['全部失败', '全部成功', '部分失败']
            text = 'SaltStack任务统计'
            subtext = '最近30次执行结果'
            all_salt_config = SaltConfig.objects.all()
            history = [x.get_last_execute_result() for x in all_salt_config if x.get_last_execute_result()]

            history = history[:30]
            for x in history:
                if x == '全部失败':
                    data_list[0]['value'] += 1
                if x == '全部成功':
                    data_list[1]['value'] += 1
                if x == '部分失败':
                    data_list[2]['value'] += 1
            return JsonResponse(
                {'data_list': data_list, 'legend': legend, 'text': text, 'subtext': subtext, 'success': success})
        except Exception as e:
            success = False
            msg = str(e)
            return JsonResponse({'msg': msg, 'success': success})


def game_server_action_pie(request):
    """区服管理操作饼图数据"""
    if request.method == 'POST':
        success = True
        msg = 'ok'
        try:
            data_list = [
                {'name': '执行失败', 'value': 0, 'url': '/myworkflows/game_server_action_record/?status=0'},
                {'name': '执行成功', 'value': 0, 'url': '/myworkflows/game_server_action_record/?status=1'},
                {'name': '执行中', 'value': 0, 'url': '/myworkflows/game_server_action_record/?status=2'},
            ]
            legend = ['执行失败', '执行成功', '执行中']
            text = '区服管理操作统计'
            subtext = '最近30次开服/关服/重启/清档/迁服'
            record = GameServerActionRecord.objects.order_by('-operation_time')

            record = record[:30]
            for x in record:
                if x.get_result_display() == '执行失败':
                    data_list[0]['value'] += 1
                if x.get_result_display() == '执行成功':
                    data_list[1]['value'] += 1
                if x.get_result_display() == '执行中':
                    data_list[2]['value'] += 1
            return JsonResponse(
                {'data_list': data_list, 'legend': legend, 'text': text, 'subtext': subtext, 'success': success})
        except Exception as e:
            success = False
            msg = str(e)
            return JsonResponse({'msg': msg, 'success': success})


def host_initialize_pie(request):
    """主机初始化饼图数据"""
    if request.method == 'POST':
        success = True
        msg = 'ok'
        try:
            data_list = [
                {'name': '初始化失败', 'value': 0, 'url': ''},
                {'name': '初始化成功', 'value': 0, 'url': ''},
                {'name': '初始化中', 'value': 0, 'url': ''},
                {'name': '待处理', 'value': 0, 'url': ''},
            ]
            legend = ['初始化失败', '初始化成功', '初始化中', '待处理']
            text = '主机初始化统计'
            subtext = '最近30次主机初始化任务'
            host_initialize = HostInitialize.objects.order_by('-add_time')

            host_initialize = host_initialize[:30]
            for x in host_initialize:
                if x.get_whole_status() == '初始化失败':
                    data_list[0]['value'] += 1
                if x.get_whole_status() == '初始化成功':
                    data_list[1]['value'] += 1
                if x.get_whole_status() == '初始化中':
                    data_list[2]['value'] += 1
                if x.get_whole_status() == '待处理':
                    data_list[3]['value'] += 1
            return JsonResponse(
                {'data_list': data_list, 'legend': legend, 'text': text, 'subtext': subtext, 'success': success})
        except Exception as e:
            success = False
            msg = str(e)
            return JsonResponse({'msg': msg, 'success': success})


def game_server_merge_pie(request):
    """合服计划饼图数据"""
    if request.method == 'POST':
        success = True
        msg = 'ok'
        try:
            data_list = [
                {'name': '合服-发送失败', 'value': 0, 'url': ''},
                {'name': '合服-发送成功', 'value': 0, 'url': ''},
                {'name': '未发送', 'value': 0, 'url': ''},
                {'name': '回滚-发送成功', 'value': 0, 'url': ''},
                {'name': '回滚-发送失败', 'value': 0, 'url': ''},
            ]
            legend = ['合服-发送失败', '合服-发送成功', '未发送', '回滚-发送成功', '回滚-发送失败']
            text = '合服计划统计'
            subtext = '最近30次合服计划'
            game_server_merge = GameServerMergeSchedule.objects.order_by('-merge_time')

            game_server_merge = game_server_merge[:30]
            for x in game_server_merge:
                if x.status == 0:
                    data_list[2]['value'] += 1
                if x.status == 1:
                    data_list[1]['value'] += 1
                if x.status == 2:
                    data_list[0]['value'] += 1
                if x.status == 3:
                    data_list[3]['value'] += 1
                if x.status == 4:
                    data_list[4]['value'] += 1
            return JsonResponse(
                {'data_list': data_list, 'legend': legend, 'text': text, 'subtext': subtext, 'success': success})
        except Exception as e:
            success = False
            msg = str(e)
            return JsonResponse({'msg': msg, 'success': success})


def game_server_install_pie(request):
    """装服计划饼图数据"""
    if request.method == 'POST':
        success = True
        msg = 'ok'
        try:
            data_list = [
                {'name': '安装失败', 'value': 0, 'url': ''},
                {'name': '安装成功', 'value': 0, 'url': ''},
                {'name': '安装中', 'value': 0, 'url': ''},
                {'name': '未处理', 'value': 0, 'url': ''},
                {'name': '卸载中', 'value': 0, 'url': ''},
                {'name': '卸载成功', 'value': 0, 'url': ''},
                {'name': '卸载失败', 'value': 0, 'url': ''},
            ]
            legend = ['安装失败', '安装成功', '安装中', '未处理', '卸载中', '卸载成功', '卸载失败']
            text = '装/卸计划统计'
            subtext = '最近30次装/卸计划'
            game_server_install = InstallGameServer.objects.order_by('-id')

            game_server_install = game_server_install[:30]
            for x in game_server_install:
                if x.status == 0:
                    data_list[3]['value'] += 1
                if x.status == 1:
                    data_list[2]['value'] += 1
                if x.status == 2:
                    data_list[1]['value'] += 1
                if x.status == 3:
                    data_list[0]['value'] += 1
                if x.status == 4:
                    data_list[4]['value'] += 1
                if x.status == 5:
                    data_list[5]['value'] += 1
                if x.status == 6:
                    data_list[6]['value'] += 1
            return JsonResponse(
                {'data_list': data_list, 'legend': legend, 'text': text, 'subtext': subtext, 'success': success})
        except Exception as e:
            success = False
            msg = str(e)
            return JsonResponse({'msg': msg, 'success': success})


def version_update_pie(request):
    """版本更新饼图数据"""
    if request.method == 'POST':
        success = True
        msg = 'ok'
        try:
            data_list = [
                {'name': '故障中', 'value': 0, 'url': ''},
                {'name': '已处理', 'value': 0, 'url': ''},
                {'name': '待更新', 'value': 0, 'url': ''},
            ]
            legend = ['故障中', '已处理', '待更新']
            text = '版本更新(自动)统计'
            subtext = '最近30次版本更新(自动)'
            version_update = VersionUpdate.objects.filter(project__auto_version_update=True, new_edition=True).order_by(
                '-id')[:30]
            for x in version_update:
                if x.workflows.last().state.name != '完成':
                    continue
                if x.status == 0:
                    data_list[1]['value'] += 1
                if x.status == 1:
                    data_list[0]['value'] += 1
                if x.status == 2:
                    data_list[2]['value'] += 1
            return JsonResponse(
                {'data_list': data_list, 'legend': legend, 'text': text, 'subtext': subtext, 'success': success})
        except Exception as e:
            success = False
            msg = str(e)
            return JsonResponse({'msg': msg, 'success': success})
