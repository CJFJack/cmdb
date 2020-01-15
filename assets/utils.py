# -*- encoding: utf-8- -*-

from assets.models import *
from users.models import UserProfileHost
from users.models import OrganizationMptt
from channels import Channel
from assets.TXcloudCdnRefresh import QcloudRefreshResultQueryByTime
from assets.BScloudCdnRefresh import BScloudRefreshResultQueryByTime
from assets.salt_api_tasks import salt_init

from requests.packages.urllib3.util import Retry
from requests.adapters import HTTPAdapter
from requests import Session

import requests
import json
import datetime
import xlrd
import os


def get_permission_detail():
    """获取服务器权限
    根据机房，项目，部门来区分
    数据格式如下：
    [
        {'title': '机房', 'filter_id': room-id, 'filter_name': 'room'， 'flotcontainer': 'room_flotcontainer'},
        {'title': '部门', 'filter_id': group-id, 'filter_name': 'group'， 'flotcontainer': 'group_flotcontainer'},
        {'title': '项目', 'filter_id': project-id, 'filter_name': 'project'， 'flotcontainer': 'project_flotcontainer'},
    ]
    """

    permission_detail = [
        {'title': '机房', 'id': 'room-id', 'filter_name': 'room', 'flotcontainer': 'room_flotcontainer'},
        {'title': '部门', 'id': 'group-id', 'filter_name': 'group', 'flotcontainer': 'group_flotcontainer'},
        {'title': '项目', 'id': 'project-id', 'filter_name': 'project', 'flotcontainer': 'project_flotcontainer'},
    ]

    return permission_detail


def get_data_permission_detail(id):
    """根据某个特性来展示数据
    格式:
    [
        {'name': '机房1', 'number': 20},
        {'name': '机房2', 'number': 20},
        {'name': '机房3', 'number': 20},
    ]
    """
    data = []
    if id == 'room-id':
        all_room = Room.objects.all()
        for x in all_room:
            number = UserProfileHost.objects.select_related(
                'host__belongs_to_room').filter(host__belongs_to_room=x, is_valid=1).count()
            if number:
                data.append({'name': x.area.chinese_name + '-' + x.room_name, 'number': number, 'id': x.id})

    if id == 'project-id':
        all_project = GameProject.objects.filter(status=1)
        for x in all_project:
            number = UserProfileHost.objects.select_related(
                'host__belongs_to_game_project').filter(host__belongs_to_game_project=x, is_valid=1).count()
            if number:
                data.append({'name': x.project_name, 'number': number, 'id': x.id})

    if id == 'group-id':
        all_objs = UserProfileHost.objects.select_related('organization').filter(organization__type=2, is_valid=1)
        department_perms = dict()
        for obj in all_objs:
            department_obj = obj.organization.get_department_obj()
            if department_obj:
                if department_obj.name not in department_perms.keys():
                    department_perms[department_obj.name] = 1
                else:
                    department_perms[department_obj.name] += 1
        for k, v in department_perms.items():
            org = OrganizationMptt.objects.get(name=k)
            data.append({'name': k, 'number': v, 'id': org.id})

    return data


def get_data_permission_detail_pie(id):
    """根据某个特性来展示数据
    格式:
    [
        {'label': '机房1', 'data': 20},
        {'label': '机房2', 'data': 20},
        {'label': '机房3', 'data': 20},
    ]
    """

    data = []

    if id == 'room_flotcontainer':
        all_room = Room.objects.all()
        for x in all_room:
            number = UserProfileHost.objects.select_related(
                'host__belongs_to_room').filter(host__belongs_to_room=x, is_valid=1).count()
            if number:
                data.append({'label': x.area.chinese_name + '-' + x.room_name, 'data': number, 'id': x.id})

    if id == 'project_flotcontainer':
        all_project = GameProject.objects.filter(status=1)
        for x in all_project:
            number = UserProfileHost.objects.select_related(
                'host__belongs_to_game_project').filter(host__belongs_to_game_project=x, is_valid=1).count()
            if number:
                data.append({'label': x.project_name, 'data': number, 'id': x.id})

    if id == 'group_flotcontainer':
        all_objs = UserProfileHost.objects.select_related('organization').filter(organization__type=2, is_valid=1)
        department_perms = dict()
        for obj in all_objs:
            department_obj = obj.organization.get_department_obj()
            if department_obj:
                department_name = department_obj.name
                if department_name not in department_perms.keys():
                    department_perms[department_name] = 1
                else:
                    department_perms[department_name] += 1
        for k, v in department_perms.items():
            org = OrganizationMptt.objects.get(name=k)
            data.append({'label': k, 'data': v, 'id': org.id})

    return data


def get_user_svn_project(user):
    """根据一个user
    从svn系统中获取这个user的所有
    项目的svn，返回一个项目英文list
    ===>
    ['id1', 'id2']
    返回None代表操作失败
    """
    try:
        url = 'https://192.168.40.11/api/getUserProjects/'
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Token d11205fc792d2d2def44ca55e5252dcbdcea6961'
        }
        payload = {
            'username': user.first_name,
        }

        r = requests.post(url, headers=headers, data=payload, verify=False)

        request_result = r.json()

        if request_result['success']:
            list_svn_repo_name = request_result['result']
            list_project_id = [x.id for x in GameProject.objects.filter(svn_repo__in=list_svn_repo_name)]
            return list_project_id
        else:
            return None
    except Exception as e:
        return None


def get_user_serper_project(user):
    """根据一个user
    从cmdb系统中获取这个user的服务器权限
    对应的所有项目list
    ===>
    ['id1', 'id2']
    """
    list_project_id_dict = Host.objects.values(
        'belongs_to_game_project').filter(
        id__in=[x['host'] for x in UserProfileHost.objects.values('host').filter(
            user_profile=user.profile, is_valid=1)])
    list_project_id = list(set([x['belongs_to_game_project'] for x in list_project_id_dict]))

    return list_project_id


def group_in_charge_projects(group):
    """一个部门负责的项目
    """
    projects = []

    group_sections = group.groupsection_set.all()

    for section in group_sections:
        for x in ProjectGroup.objects.filter(group_section=section):
            if x.project not in projects:
                projects.append(x.project)

    return projects


def ws_update_task_result(update_msg):
    """刷新salt任务执行结果
    """
    msg = {"message": update_msg, 'group_name': 'salt_task'}
    Channel('update_execute_salt_task').send(msg)


def change_cdn_status_to_cn(status):
    """转换cdn刷新状态为中文"""
    if str(status) == '1' or str(status) == 'completed':
        return '刷新成功'
    elif str(status) == '0' or str(status) == 'waiting' or str(status) == 'processing':
        return '刷新中'
    else:
        return '刷新失败'


def query_tx_cdn_refresh_record(startDate, endDate, secret_id, secret_key):
    """查询腾讯云cdn刷新记录"""
    result = QcloudRefreshResultQueryByTime(startDate, endDate, secret_id, secret_key)
    if result['success']:
        data = result['msg']
        data = list(reversed(data))
        total = len(data)
        return {'total': total, 'success': True, 'data': [
            {'url': x['url_list'], 'status': change_cdn_status_to_cn(x['status']), 'commit_time': x['datetime']} for x
            in data]}
    else:
        msg = result['msg']
        return {'success': False, 'msg': msg}


def query_bs_cdn_refresh_record(token, start_time, end_time):
    """查询白山云cdn刷新记录"""
    result = BScloudRefreshResultQueryByTime(token, start_time, end_time)
    if result['success']:
        data = result['msg']
        data = list(reversed(data))
        total = len(data)
        return {'total': total, 'success': True, 'data': [
            {'url': x['url'], 'status': change_cdn_status_to_cn(x['status']), 'commit_time': ''} for x
            in data]}
    else:
        msg = result['msg']
        return {'success': False, 'msg': msg}


def format_host_record(host_history_record):
    """格式化主机记录，合并相同时间生成的记录内容"""
    record_list = []
    i = 0
    for r in host_history_record:
        r = r.show_record()
        if record_list and r['create_time'] == record_list[i - 1]['create_time'] and r['operation_user'] == \
                record_list[i - 1]['operation_user'] and r['type'] == record_list[i - 1]['type']:
            alter_detail = r['alter_detail'] + record_list[i - 1]['alter_detail']
            record_list[i - 1]['alter_detail'] = alter_detail
        else:
            record_list.append(r)
            i += 1
    return record_list


def get_ip(request):
    """获取请求cmdb的源IP"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        # 真实IP
        ip = x_forwarded_for.split(',')[0]
    else:
        # 代理IP
        ip = request.META.get('REMOTE_ADDR')
    return ip


def format_saltstack_configfile_path(config_path):
    """格式化saltstack配置文件的存放路径"""
    config_path = config_path.split('/')
    config_path = list(filter(None, config_path))
    config_path.remove('srv')
    config_path.remove('salt')
    return '.'.join([x for x in config_path])


def format_saltstack_execute_result(result):
    """
    格式化saltstack执行结构
    输入：
    {
        "129.204.174.6": false,
        "119.29.79.89": {
            "cmd_|-test_|-w_|-run": {
                "name": "w",
                "changes": {
                    "stdout": " 10:30:08 up 128 days, 22:06,  5 users,  load average: 0.35, 0.42, 0.38\nUSER     TTY      FROM              LOGIN@   IDLE   JCPU   PCPU WHAT\nroot     pts/2    58.63.33.154     09:47    1:59   0.03s  0.03s -bash\nroot     pts/12   58.63.33.154     06May19 19:16m  1:44m  0.00s tail -f /var/lo\nroot     pts/24   58.63.33.154     28Apr19 19:29m  0.65s  0.00s tail -f /tmp/gr\nroot     pts/27   58.63.33.154     25Apr19 53:46   2:15m  0.67s -bash\nroot     pts/44   58.63.33.154     09:58   31:58   0.01s  0.01s -bash",
                    "pid": 1165,
                    "retcode": 0,
                    "stderr": ""
                },
                "__run_num__": 0,
                "duration": 69.916,
                "comment": "Command \"w\" run",
                "__sls__": "test",
                "start_time": "10:30:07.933336",
                "__id__": "test",
                "result": true
            }
        },
        "129.204.139.22": {
            "cmd_|-test_|-w_|-run": {
                "name": "w",
                "changes": {
                    "stdout": " 10:30:08 up 45 days, 17:14,  0 users,  load average: 0.01, 0.02, 0.00\nUSER     TTY      FROM              LOGIN@   IDLE   JCPU   PCPU WHAT",
                    "pid": 12072,
                    "retcode": 0,
                    "stderr": ""
                },
                "__run_num__": 0,
                "duration": 39.964,
                "comment": "Command \"w\" run",
                "__sls__": "test",
                "start_time": "10:30:08.040703",
                "__id__": "test",
                "result": true
            }
        }
    }
    输出：
    [
        {"ip": "129.204.174.6", "status": False, 'result": "aaaaa"}
        {"ip": "129.204.139.22", "status": True, "result": "bbbbb"}
        {"ip": "119.29.79.89", "status": True, "result': "ccccc"}
    ]
    """
    l = []
    for ip, r in result.items():
        result = {}
        result[ip] = r
        result = json.dumps(result, indent=4, ensure_ascii=False)
        if '"result": true' in result:
            l.append({'ip': ip, 'status': True, 'result': result})
        else:
            l.append({'ip': ip, 'status': False, 'result': result})
    return l


def format_salt_command(command):
    """
    格式化salt命令
    输入：
    salt '*' cmd.run 'df -h'
    输出：
    {
        'minion': '*', 'method': 'cmd.run', 'arg': ['df -h'], 'tgt_type': 'glob'
    }
    """
    type_tuple_short = ('-E', '-L', '-S', '-G', '-I', '-N', '-C', '-J', '--grain-pcre', '-R')
    type_tuple = (
        'pcre', 'list', 'ipcidr', 'grain', 'pillar', 'nodegroup', 'compound', 'pillar_pcre', '--grain-pcre', 'range')
    try:
        i = type_tuple_short.index(command[1])
    except:
        tgt_type = 'glob'
        minion = command[1]
        method = command[2]
        arg = command[3:]
    else:
        tgt_type = type_tuple[i]
        minion = command[2]
        method = command[3]
        arg = command[4:]
    if not arg:
        arg = None
    return {'minion': minion, 'method': method, 'arg': arg, 'tgt_type': tgt_type}


def ws_update_salt_command_execute_result(update_msg, uuid):
    """刷新salt命令执行结果
    """
    msg = {"message": update_msg, 'group_name': 'execute_salt_command', 'uuid': uuid}
    Channel('update_execute_salt_command').send(msg)


def get_host_statistics_by_project_chart_series(yAxis_data):
    """
    获取主机统计图表series数据
    return:
    [
        {
            name: '可用',
            type: 'bar',
            stack: '总量',
            label: {
                normal: {
                    show: false,
                    position: 'insideRight'
                }
            },
            data: [320, 302, 301, 334, 390, 330, 320]
        },
        {
            name: '未初始化',
            type: 'bar',
            stack: '总量',
            label: {
                normal: {
                    show: false,
                    position: 'insideRight'
                }
            },
            data: [120, 132, 101, 134, 90, 230, 210]
        }
    ]
    """
    series = []
    for status_tuple in Host.STATUS:
        status_id = status_tuple[0]
        status_name = status_tuple[1]
        series_dict = {'type': 'bar', 'stack': '总量', 'label': {'normal': {'show': False, 'position': 'insideLeft'}}}
        series_dict['name'] = status_name
        belongs_to_project_statistics = [
            Host.objects.select_related('belongs_to_game_project').filter(belongs_to_game_project__project_name=project,
                                                                          status=status_id).count() for project in
            yAxis_data]
        series_dict['data'] = belongs_to_project_statistics
        series.append(series_dict)
    series.sort(key=lambda x: x['name'], reverse=False)
    return series


def get_host_statistics_by_room_chart_series(yAxis_data):
    """
    获取主机统计图表series数据
    return:
    [
        {
            name: '可用',
            type: 'bar',
            stack: '总量',
            label: {
                normal: {
                    show: false,
                    position: 'insideRight'
                }
            },
            data: [320, 302, 301, 334, 390, 330, 320]
        },
        {
            name: '未初始化',
            type: 'bar',
            stack: '总量',
            label: {
                normal: {
                    show: false,
                    position: 'insideRight'
                }
            },
            data: [120, 132, 101, 134, 90, 230, 210]
        }
    ]
    """
    series = []
    for status_tuple in Host.STATUS:
        status_id = status_tuple[0]
        status_name = status_tuple[1]
        series_dict = {'url': 'fsfasdfdas', 'type': 'bar', 'stack': '总量',
                       'label': {'normal': {'show': False, 'position': 'insideLeft'}}}
        series_dict['name'] = status_name
        belongs_to_room_statistics = [
            Host.objects.select_related('belongs_to_room').filter(belongs_to_room__room_name=room.split('-')[-1],
                                                                  belongs_to_room__area__chinese_name=room.split('-')[
                                                                      0], status=status_id).count() for room in
            yAxis_data]
        series_dict['data'] = belongs_to_room_statistics
        series.append(series_dict)
    series.sort(key=lambda x: x['name'], reverse=False)
    return series


def ws_update_host_initialize_log(id, log):
    """刷新前端页面主机初始化日志内容"""
    msg = {"message": 'update_log', 'host_initialize_id': id, 'log': log}
    Channel('update_host_initialize_log').send(msg)


def write_host_initialize_log(level, content, obj):
    """记录主机初始化日志内容"""
    log_obj = obj.hostinitializelog
    now = str(datetime.datetime.now())[:23]
    complete_log = now + ' - ' + obj.telecom_ip + ' - ' + level + ' - ' + content + '\n'
    log_obj.content += complete_log
    log_obj.save()
    """刷新区服下线日志"""
    ws_update_host_initialize_log(obj.id, log_obj.content)


def ws_update_host_initialize_list():
    """刷新主机初始化列表"""
    msg = {"message": 'update_table', 'group_name': 'host_initialize_list'}
    Channel('update_host_initialize_list').send(msg)


def saltstack_test_ping(telecom_ip):
    """调用salt-api测试主机连通性"""
    salt = salt_init()
    client = [telecom_ip]
    fun = 'test.ping'
    """执行命令"""
    result = salt.salt_command(client, fun, tgt_type='list')
    if result.get(telecom_ip, False) is True:
        return True, 'test.ping 测试连通性成功'
    return False, 'test.ping 测试连通性失败: ' + json.dumps(result.get(telecom_ip, False))


def format_saltstack_host_initialize_result(result, telecom_ip):
    """
    格式化saltstack主机初始化输出结果
    :param result:
    {
        'outputter': 'highstate',
        'data': {
            '106.52.136.242': {
                'cmd_|-big_ram_|-big_ram_|-script': {
                    '__id__': 'big_ram',
                    '__sls__': 'init.big_ram',
                    'result': True,
                    ...
                    ...
                },
                ...
                ...
            }
        }
    }
    :return:
    True,
    {
        'yum_epel': {
            '__sls__': 'init.yum',
            'step_result': True
        },
        'hostname': {
            '__sls__': 'init.set_path',
            'step_result': True
        },
        'iptable-game': {
            '__sls__': 'game',
            'step_result': True
        },
        ...
        ...
    }
    """
    success = True
    try:
        data = result.get('data', '')
        if not data:
            raise Exception
        if not isinstance(data, dict):
            raise Exception

        initialize_step_result = data.get(telecom_ip, '')
        if not initialize_step_result:
            raise Exception
        if not isinstance(initialize_step_result, dict):
            raise Exception

        step_dict = dict()
        for step, step_info in initialize_step_result.items():
            result_dict = dict()
            __id__ = step_info.get('__id__', '')
            __sls__ = step_info.get('__sls__', '')
            step_result = step_info.get('result', '')
            result_dict['__sls__'] = __sls__
            result_dict['result'] = step_result
            step_dict[__id__] = result_dict

        return success, step_dict

    except Exception as e:
        success = False
        return success, result


def format_saltstack_host_check_result(result, telecom_ip):
    """
    格式化saltstack主机环境检测输出结果
    :param result:
    {
        "data": {
            "106.52.136.242": {
                "cmd_|-check_host_|-check_host_|-script": {
                    "comment": "Command 'check_host' run",
                    "__id__": "check_host",
                    "start_time": "15:49:27.613102",
                    "changes": {
                        "stderr": "",
                        "stdout": "[Info] 机器 mysql服务正常\n[Info] 机器 ulimit设置正常\n[Info] 机器 sysctl设置正常\n[Info] 机器 mongo 服务正常\n[Info] 机器 erlang 组件正常\n[Info] 机器 iptables设置正常",
                        "pid": 21866,
                        "retcode": 0
                    },
                    "__run_num__": 0,
                    "__sls__": "check_host",
                    "result": true,
                    "name": "check_host",
                    "duration": 145.837
                }
            }
        },
        "outputter": "highstate"
    }
    :return:
    True, ['[Info] 机器 mysql服务正常', '[Info] 机器 ulimit设置正常', '[Info] 机器 sysctl设置正常', '[Info] 机器 mongo 服务正常', '[Info] 机器 erlang 组件正常', '[Info] 机器 iptables设置正常']
    """
    success = True
    try:
        stdout = result['data'][telecom_ip]['cmd_|-check_host_|-check_host_|-script']['changes']['stdout']
        stdout_list = stdout.split('\n')
        return success, stdout_list

    except Exception as e:
        success = False
        return success, result


def save_uploaded_file(f, file_path, save_filename):
    """
    Handle file upload
    """
    fpath = os.path.join(os.getcwd(), file_path, save_filename)
    with open(fpath, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)


def read_excel_table_data(f):
    """读取excel中的表格内容"""
    data = xlrd.open_workbook(f)
    table = data.sheet_by_name(u'Sheet1')
    thead = table.row_values(0)
    rows = table.nrows
    tbody = []
    for i in range(1, rows):
        tr = table.row_values(i)
        tbody.append(tr)
    return {'thead': thead, 'tbody': tbody}


def sync_pillar_config():
    """调用salt-api刷新pillar配置"""
    salt = salt_init()
    client = '*'
    fun = 'saltutil.refresh_pillar'
    """执行命令"""
    result = salt.salt_command(client, fun, tgt_type='glob')
    fail_result = {}
    for k, v in result.items():
        if not v:
            fail_result[k] = v

    if result:
        return json.dumps(fail_result, indent=4, ensure_ascii=False)
    else:
        return '全部刷新成功！'


def get_host_install_soft():
    """获取主机需要安装的软件信息"""
    data = ''
    success = True
    try:
        url = 'https://119.29.79.89/api/install/soft/'
        token = 'bda6d0ff9803476bc0763c4f1912a2c5ba7145bc'
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Token {}'.format(token)
        }
        s = Session()
        s.mount('https://', HTTPAdapter(max_retries=Retry(total=5, status_forcelist=[408])))
        r = s.post(url, headers=headers, json={}, timeout=30, verify=False)
        if r.status_code != 200:
            raise Exception(str(r))
        res = r.json()
        if res['Accepted']:
            data = res['data']

    except Exception as e:
        success = False
        data = str(e)
    finally:
        return success, data


def call_host_start_pro(game_project):
    """调用startproAPI接口，生成主机初始化所需要的sls文件"""
    success = True
    msg = 'ok'
    try:
        url = 'https://119.29.79.89/api/install/StartPro/'
        token = 'bda6d0ff9803476bc0763c4f1912a2c5ba7145bc'
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Token {}'.format(token)
        }
        post_data = {
            'INAME': game_project.project_name_en,
            'WEB_IP': '"' + game_project.web_ip + '"',
            'MANAGER_WAN_IP': game_project.manager_wan_ip,
            'ZABBIX_PROXY_IP': game_project.zabbix_proxy_ip,
            'MANAGER_LAN_IP': game_project.manager_lan_ip,
            'AREA': game_project.area.short_name if game_project.area else '',
            'SOFTLIST': json.loads(game_project.softlist) if game_project.softlist else {},
        }
        print(post_data)
        s = Session()
        s.mount('https://', HTTPAdapter(max_retries=Retry(total=5, status_forcelist=[408])))
        r = s.post(url, headers=headers, json=post_data, timeout=30, verify=False)
        if r.status_code != 200:
            raise Exception(str(r))
        res = r.json()
        print(res)
        if not res['Accepted']:
            raise Exception(res['data'])
        msg = res['data']

    except Exception as e:
        success = False
        msg = str(e)
    finally:
        return success, msg
