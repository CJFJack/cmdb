# -*- encoding: utf-8 -*-
"""
主要测试内容：
1. 前端关键页面访问
2. 前端对后端请求数据接口的异步调用
3. 后端生成申请单，同意，拒绝审批过程（不包括调用运维管理机等其他接口）
使用方法：
1. 修改参数 CMDB_URL 指定cmdb测试地址
2. 通过修改 TEST_WORKFLOW_OPTION 参数指定测试哪些流程
3. 运行脚本 /data/code/cy_devops/bin/python3 /data/www/cmdb/myworkflows/tests.py
"""
import requests
import os
import django
import uuid
import sys
from cmdb.settings import PRODUCTION_ENV

pathname = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, pathname)
sys.path.insert(0, os.path.abspath(os.path.join(pathname, '..')))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cmdb.settings")
django.setup()
CMDB_URL = 'http://127.0.0.1:8000'
"""
1	SVN申请
3	服务器权限申请
4	电脑故障申报
5	wifi申请和网络问题申报
6	办公电脑和配件申请
7	版本更新单申请
8	前端热更新
9	后端热更新
10	服务器申请工单
13	项目人员调整工单
14	数据库权限申请
"""
# TEST_WORKFLOW_OPTION = [1, 3, 4, 5, 6, 10, 13, 14, 16]
# TEST_WORKFLOW_OPTION = [7]
TEST_WORKFLOW_OPTION = [8]
# TEST_WORKFLOW_OPTION = [9]

from myworkflows.models import SVNWorkflow, ServerPermissionWorkflow, Workflow, FailureDeclareWorkflow
from myworkflows.models import Wifi, ComputerParts, Machine, ProjectAdjust, MysqlWorkflow, VersionUpdate
from myworkflows.models import ClientHotUpdate, ServerHotUpdate
from django.contrib.auth.models import User
from cmdb.settings import NEW_WORKFLOW
from cmdb.settings import NEW_VERSION_UPDATE

import json


class WorkflowListTest(object):
    """测试访问工单列表页面"""

    def __init__(self):
        self.success = True
        self.ssion = requests.session()
        data = {"username": "chenjiefeng", "password": "123123"}
        self.ssion.post(CMDB_URL + "/user_login/", data=data)

    def test_workflow_list(self):
        r = self.ssion.get(CMDB_URL + "/myworkflows/workflow_list/")
        if r.status_code == 200:
            return self.success, '工单列表页面访问成功'
        else:
            self.success = False
            return self.success, '工单列表页面访问出现错误' + str(r)


class SVNWorkflowTest(object):
    """测试提交SVN申请"""

    def __init__(self):
        self.success = True
        self.msg = 'ok'
        self.ssion = requests.session()
        data = {"username": "chenjiefeng", "password": "123123"}
        self.ssion.post(CMDB_URL + "/user_login/", data=data)

    def test_svn_workflow(self):
        try:
            """测试填单页面"""
            workflow = Workflow.objects.get(pk=1)
            workflow_id = workflow.id
            workflow_name = workflow.name
            r = self.ssion.get(CMDB_URL + "/myworkflows/workflow_template/?workflow=" + str(workflow_id))
            if r.status_code == 200:
                print('svn提交申请页访问成功')
            else:
                raise Exception('svn提交申请页访问出现错误' + str(r))
            """测试项目下拉框"""
            r = self.ssion.post(CMDB_URL + "/assets/list_game_project/")
            if r.status_code == 200:
                if r.json():
                    print('-svn提交申请页-项目下拉框请求成功')
                else:
                    raise Exception('-svn提交申请页-项目下拉框请求成功，但返回为空')
            else:
                raise Exception('-svn提交申请页-项目下拉请求出现错误' + str(r))
            """测试申请人下拉框"""
            r = self.ssion.post(CMDB_URL + "/assets/list_user/")
            if r.status_code == 200:
                if r.json():
                    print('-svn提交申请页-申请人下拉框请求成功')
                else:
                    raise Exception('-svn提交申请页-申请人下拉框请求成功，但返回为空')
            else:
                raise Exception('-svn提交申请页-申请人下拉框请求出现错误' + str(r))
            """测试生成审批链"""
            r = self.ssion.post(CMDB_URL + "/myworkflows/get_workflow_approve_user/",
                                json={'workflow': 1, 'applicant_id': 1155, 'project_id': 23})
            if r.status_code == 200:
                result = r.json()
                if result['success'] and result[
                    'data'] == '审批人员链: 陈捷丰==>黎小龙==>张圣洁 <strong>审批人员有错误?可能申请人所在的部门不对!请联系运维处理</strong>':
                    print('-svn提交申请页-生成审批链成功')
                else:
                    raise Exception('-svn提交申请页-生成审批链失败-' + result['data'])
            else:
                raise Exception('-svn提交申请页-生成审批链失败-' + str(r))
            """测试列出svn套餐方案"""
            r = self.ssion.post(CMDB_URL + "/myworkflows/list_svn_scheme/", data={'project': 23})
            if r.status_code == 200:
                print('-svn提交申请页-列出svn套餐方案成功')
            else:
                raise Exception('-svn提交申请页-列出svn套餐方案失败' + str(r))
            """测试提交svn申请"""
            test_id = uuid.uuid1()
            post_data = {
                'applicant': "1155",
                'content': [],
                'project': "24",
                'reason': "test",
                'svn_scheme': "26",
                'title': "test_svn_commit" + str(test_id),
                'workflow': "1",
            }
            r = self.ssion.post(CMDB_URL + "/myworkflows/start_workflow/", json=post_data)
            if r.status_code == 200:
                result = r.json()
                if result['success']:
                    print('svn提交申请成功')
                else:
                    raise Exception('svn提交申请失败' + result['data'])
            else:
                raise Exception('svn提交申请失败' + str(r))
            """测试访问svn审批页面"""
            obj = SVNWorkflow.objects.last()
            wse = obj.workflows.filter(is_current=1)[0]
            wse_id = wse.id
            r = self.ssion.get(CMDB_URL + "/myworkflows/workflow_approve/?id=" + str(wse_id))
            if r.status_code == 200:
                print('svn审批页面访问成功')
            else:
                raise Exception('svn审批页面访问失败' + str(r))
            """测试svn申请审批同意"""
            self.ssion.post(CMDB_URL + "/user_login/", data={'username': 'lixiaolong', 'password': '123123'})
            accept_transition = wse.state.transition.filter(condition='同意')[0].id
            post_data = {
                "opinion": "同意",
                "transition": accept_transition,
                "wse": wse_id,
            }
            r = self.ssion.post(CMDB_URL + "/myworkflows/workflow_approve/", json=post_data)
            if r.status_code == 200:
                result = r.json()
                if result['success']:
                    print('svn审批同意成功')
                else:
                    raise Exception('svn审批同意失败' + result['data'])
            else:
                raise Exception('svn审批同意失败' + str(r))
            """测试svn申请审批拒绝"""
            self.ssion.post(CMDB_URL + "/user_login/",
                            data={'username': 'zhangshengjie', 'password': '123123'})
            new_wse = obj.workflows.filter(is_current=1)[0]
            new_wse_id = new_wse.id
            reject_transition = new_wse.state.transition.filter(condition='拒绝')[0].id
            post_data = {
                "opinion": "拒绝",
                "transition": reject_transition,
                "wse": new_wse_id,
            }
            r = self.ssion.post(CMDB_URL + "/myworkflows/workflow_approve/", json=post_data)
            if r.status_code == 200:
                result = r.json()
                if result['success']:
                    print('svn审批拒绝成功')
                else:
                    raise Exception('svn审批拒绝失败' + result['data'])
            else:
                raise Exception('svn审批拒绝失败' + str(r))
            """测试访问工单详情（我的申请或者工单汇总）"""
            r = self.ssion.get(CMDB_URL + "/myworkflows/myworkflow_history?id=" + str(new_wse_id))
            if r.status_code == 200:
                print(workflow_name + '-访问工单详情成功')
            else:
                raise Exception(workflow_name + '-访问工单详情失败' + str(r))

            self.msg = 'svn申请测试通过'
        except Exception as e:
            self.success = False
            self.msg = str(e)
        finally:
            return self.success, self.msg


class ServerPermWorkflowTest(object):
    def __init__(self):
        self.success = True
        self.msg = 'ok'
        self.ssion = requests.session()
        data = {"username": "liangjun", "password": "123123"}
        self.ssion.post(CMDB_URL + "/user_login/", data=data)

    def test_server_perm_workflow(self):
        try:
            """测试填单页面"""
            workflow = Workflow.objects.get(pk=3)
            workflow_id = workflow.id
            workflow_name = workflow.name
            r = self.ssion.get(CMDB_URL + "/myworkflows/workflow_template/?workflow=" + str(workflow_id))
            if r.status_code == 200:
                print('服务器权限申请页访问成功')
            else:
                raise Exception('服务器权限申请页访问出现错误' + str(r))
            """测试项目下拉框"""
            r = self.ssion.post(CMDB_URL + "/assets/list_game_project/")
            if r.status_code == 200:
                if r.json():
                    print('-服务器权限申请页-项目下拉框请求成功')
                else:
                    raise Exception('-服务器权限申请页-项目下拉框请求成功，但返回为空')
            else:
                raise Exception('-服务器权限申请页-项目下拉请求出现错误' + str(r))
            """测试IP-机房下拉框"""
            r = self.ssion.post(CMDB_URL + "/assets/list_ip_room/", data={'project': 23})
            if r.status_code == 200:
                if r.json():
                    print('-服务器权限申请页-IP-机房下拉框请求成功')
                else:
                    raise Exception('-服务器权限申请页-IP-机房下拉框请求成功，但返回为空')
            else:
                raise Exception('-服务器权限申请页-IP-机房下拉请求出现错误' + str(r))
            """测试IP-机房-区服id下拉框"""
            r = self.ssion.post(CMDB_URL + "/assets/list_ip_room_game_server/",
                                data={'project': 23, 'page': 1})
            if r.status_code == 200:
                if r.json():
                    print('-服务器权限申请页-IP-机房-区服id下拉框请求成功')
                else:
                    raise Exception('-服务器权限申请页-IP-机房-区服id下拉框请求成功，但返回为空')
            else:
                raise Exception('-服务器权限申请页-IP-机房-区服id下拉请求出现错误' + str(r))
            """测试生成审批链"""
            r = self.ssion.post(CMDB_URL + "/myworkflows/get_workflow_approve_user/",
                                json={'username': '梁俊', 'workflow': 3})
            if r.status_code == 200:
                result = r.json()
                if result['success'] and result[
                    'data'] == '审批人员链: 梁保明==>黎小龙 <strong>审批人员有错误?可能申请人所在的部门不对!请联系运维处理</strong>':
                    print('-服务器权限申请页-生成审批链成功')
                else:
                    raise Exception('-服务器权限申请页-生成审批链失败' + result['data'])
            else:
                raise Exception('-服务器权限申请页-生成审批链失败' + str(r))
            """测试提交服务器权限申请"""
            test_id = uuid.uuid1()
            post_data = {
                "end_time": "",
                "group": "phpers",
                "ips": [{"id": "2388_internal_ip", "ip": "10.21.181.102:9022-尚航无锡YY云机房"}],
                "is_root": False,
                "key": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDRHl1ZPd8mjr00XklhVP9WOeduJe6WzEYsskzpxG4C2OvkUfP0ny/eJpL3lV5AfiXKVI9oBp18OmQI63hslEB7QRw74dYzKbfesyG57pC6kqFRpvNGAqwEa0TsC6HI4qGv19/Mp8TuuLIpyHYZ2o4kxhi0u0EC5s5i0xKAXzV8bTWbhkVTodeSUJPjLVWJgY4MmkX0o6DouenBIRkq/doS5LMv2X1Thsy/jXbtgCBIDVTvSNJUcYnfuFnHDk3JGB74c/zDApoTqVwrtLxWDzLEAmr9hcPXLhb8qvbD5+pWNzv3rwgoXI8rStPrpJ4pDF1WuB0pdh4J6p9DrMK3e4G/ liangjun",
                "project": "23",
                "reason": "test",
                "room": "0",
                "start_time": "",
                "temporary": False,
                "title": "test_serverperm" + str(test_id),
                "workflow": "3",
            }
            r = self.ssion.post(CMDB_URL + "/myworkflows/start_workflow/", json=post_data)
            if r.status_code == 200:
                result = r.json()
                if result['success']:
                    print('服务器权限提交申请成功')
                else:
                    raise Exception('服务器权限提交申请失败' + result['data'])
            else:
                raise Exception('服务器权限提交申请失败' + str(r))
            """测试访问服务器权限申请审批页面"""
            obj = ServerPermissionWorkflow.objects.last()
            wse = obj.workflows.filter(is_current=1)[0]
            wse_id = wse.id
            r = self.ssion.get(CMDB_URL + "/myworkflows/workflow_approve/?id=" + str(wse_id))
            if r.status_code == 200:
                print('服务器权限审批页面访问成功')
            else:
                raise Exception('服务器权限审批页面访问失败' + str(r))
            """测试服务器权限申请审批同意"""
            self.ssion.post(CMDB_URL + "/user_login/",
                            data={'username': 'liangbaoming', 'password': '123123'})
            accept_transition = wse.state.transition.filter(condition='同意')[0].id
            post_data = {
                "opinion": "同意",
                "transition": accept_transition,
                "wse": wse_id,
            }
            r = self.ssion.post(CMDB_URL + "/myworkflows/workflow_approve/", json=post_data)
            if r.status_code == 200:
                result = r.json()
                if result['success']:
                    print('服务器权限审批同意成功')
                else:
                    raise Exception('服务器权限审批同意失败' + result['data'])
            else:
                raise Exception('服务器权限审批同意失败' + str(r))
            """测试服务器权限申请审批拒绝"""
            self.ssion.post(CMDB_URL + "/user_login/",
                            data={'username': 'lixiaolong', 'password': '123123'})
            new_wse = obj.workflows.filter(is_current=1)[0]
            new_wse_id = new_wse.id
            reject_transition = new_wse.state.transition.filter(condition='拒绝')[0].id
            post_data = {
                "opinion": "拒绝",
                "transition": reject_transition,
                "wse": new_wse_id,
            }
            r = self.ssion.post(CMDB_URL + "/myworkflows/workflow_approve/", json=post_data)
            if r.status_code == 200:
                result = r.json()
                if result['success']:
                    print('服务器权限审批拒绝成功')
                else:
                    raise Exception('服务器权限审批拒绝失败' + result['data'])
            else:
                raise Exception('服务器权限审批拒绝失败' + str(r))
            """测试访问工单详情（我的申请或者工单汇总）"""
            r = self.ssion.get(CMDB_URL + "/myworkflows/myworkflow_history?id=" + str(new_wse_id))
            if r.status_code == 200:
                print(workflow_name + '-访问工单详情成功')
            else:
                raise Exception(workflow_name + '-访问工单详情失败' + str(r))

            self.msg = '服务器权限申请测试通过'
        except Exception as e:
            self.success = False
            self.msg = str(e)
        finally:
            return self.success, self.msg


class ComputerFailWorkflowTest(object):
    """电脑故障申报测试"""

    def __init__(self):
        self.success = True
        self.msg = 'ok'
        self.ssion = requests.session()
        data = {"username": "chenjiefeng", "password": "123123"}
        self.ssion.post(CMDB_URL + "/user_login/", data=data)

    def test_computer_fail_workflow(self):
        try:
            """测试填单页面"""
            workflow = Workflow.objects.get(pk=4)
            workflow_id = workflow.id
            workflow_name = workflow.name
            r = self.ssion.get(CMDB_URL + "/myworkflows/workflow_template/?workflow=" + str(workflow_id))
            if r.status_code == 200:
                print(workflow_name + '-填单页访问成功')
            else:
                raise Exception(workflow_name + '-填单页访问出现错误' + str(r))
            """测试指定网络管理员下拉框"""
            r = self.ssion.post(CMDB_URL + "/assets/list_administrator/")
            if r.status_code == 200:
                if r.json():
                    print('-' + workflow_name + '-填单页-指定网络管理员下拉框请求成功')
                else:
                    raise Exception('-' + workflow_name + '-填单页-指定网络管理员下拉框请求成功，但返回为空')
            else:
                raise Exception('-' + workflow_name + '-填单页-指定网络管理员下拉框请求出现错误' + str(r))
            """测试提交电脑故障申报"""
            test_id = uuid.uuid1()
            post_data = {
                "applicant": "1155",
                "assigned_to": "377",
                "classification": "1",
                "content": "test",
                "title": "test_compterfail" + str(test_id),
                "workflow": "4",
            }
            r = self.ssion.post(CMDB_URL + "/myworkflows/start_workflow/", json=post_data)
            if r.status_code == 200:
                result = r.json()
                if result['success']:
                    print(workflow_name + '-提交申请成功')
                else:
                    raise Exception(workflow_name + '-提交申请失败' + result['data'])
            else:
                raise Exception(workflow_name + '-提交申请失败' + str(r))
            """测试访问电脑故障申报审批页面"""
            obj = FailureDeclareWorkflow.objects.last()
            wse = obj.workflows.filter(is_current=1)[0]
            wse_id = wse.id
            r = self.ssion.get(CMDB_URL + "/myworkflows/workflow_approve/?id=" + str(wse_id))
            if r.status_code == 200:
                print(workflow_name + '-审批页面访问成功')
            else:
                raise Exception(workflow_name + '-审批页面访问失败' + str(r))
            """测试电脑故障申报转单给其他网管"""
            self.ssion.post(CMDB_URL + "/user_login/",
                            data={'username': 'liangjialong', 'password': '123123'})
            post_data = {
                "wse": wse_id,
                "to_anthoer_admin": "1215",
            }
            r = self.ssion.post(CMDB_URL + "/myworkflows/transfer_to_other_admin/", json=post_data)
            if r.status_code == 200:
                result = r.json()
                if result['success']:
                    print(workflow_name + '-转单网络管理员成功')
                else:
                    raise Exception(workflow_name + '-转单网络管理员失败' + result['data'])
            else:
                raise Exception(workflow_name + '-审批同意失败' + str(r))
            """测试电脑故障申报审批同意"""
            self.ssion.post(CMDB_URL + "/user_login/",
                            data={'username': 'laimingyao', 'password': '123123'})
            accept_transition = wse.state.transition.filter(condition='同意')[0].id
            post_data = {
                "opinion": "同意",
                "transition": accept_transition,
                "wse": wse_id,
                "has_handle": "1"
            }
            r = self.ssion.post(CMDB_URL + "/myworkflows/workflow_approve/", json=post_data)
            if r.status_code == 200:
                result = r.json()
                if result['success']:
                    print(workflow_name + '-审批同意成功')
                else:
                    raise Exception(workflow_name + '-审批同意失败' + result['data'])
            else:
                raise Exception(workflow_name + '-审批同意失败' + str(r))
            """测试访问工单详情（我的申请或者工单汇总）"""
            r = self.ssion.get(CMDB_URL + "/myworkflows/myworkflow_history?id=" + str(wse_id))
            if r.status_code == 200:
                print(workflow_name + '-访问工单详情成功')
            else:
                raise Exception(workflow_name + '-访问工单详情失败' + str(r))

            self.msg = workflow_name + '测试通过'
        except Exception as e:
            self.success = False
            self.msg = str(e)
        finally:
            return self.success, self.msg


class WifiAndNetworkWorkflowTest(object):
    """wifi和网络问题申报测试"""

    def __init__(self):
        self.success = True
        self.msg = 'ok'
        self.ssion = requests.session()
        data = {"username": "chenjiefeng", "password": "123123"}
        self.ssion.post(CMDB_URL + "/user_login/", data=data)

    def test_wifi_and_network_workflow(self):
        try:
            """测试填单页面"""
            workflow = Workflow.objects.get(pk=5)
            workflow_id = workflow.id
            workflow_name = workflow.name
            r = self.ssion.get(CMDB_URL + "/myworkflows/workflow_template/?workflow=" + str(workflow_id))
            if r.status_code == 200:
                print(workflow_name + '-填单页访问成功')
            else:
                raise Exception(workflow_name + '-填单页访问出现错误' + str(r))
            """测试提交wifi申请"""
            test_id = uuid.uuid1()
            post_data = {
                "applicant": "1155",
                "mac": "11:11:11:11:11:11",
                "name": "Cy-Public",
                "reason": "test",
                "title": "testwifi" + str(test_id),
                "workflow": "5",
            }
            r = self.ssion.post(CMDB_URL + "/myworkflows/start_workflow/", json=post_data)
            if r.status_code == 200:
                result = r.json()
                if result['success']:
                    print(workflow_name + '-wifi提交申请成功')
                else:
                    raise Exception(workflow_name + '-wifi提交申请失败' + result['data'])
            else:
                raise Exception(workflow_name + '-wifi提交申请失败' + str(r))
            """测试访问wifi问题申报审批页面"""
            obj = Wifi.objects.last()
            wse = obj.workflows.filter(is_current=1)[0]
            wse_id = wse.id
            r = self.ssion.get(CMDB_URL + "/myworkflows/workflow_approve/?id=" + str(wse_id))
            if r.status_code == 200:
                print(workflow_name + '-wifi申请-审批页面访问成功')
            else:
                raise Exception(workflow_name + '-wifi问题申报-审批页面访问失败' + str(r))
            """测试wifi和网络问题申报审批同意"""
            self.ssion.post(CMDB_URL + "/user_login/",
                            data={'username': 'lixiaolong', 'password': '123123'})
            accept_transition = wse.state.transition.filter(condition='同意')[0].id
            post_data = {
                "opinion": "同意",
                "transition": accept_transition,
                "wse": wse_id,
            }
            r = self.ssion.post(CMDB_URL + "/myworkflows/workflow_approve/", json=post_data)
            if r.status_code == 200:
                result = r.json()
                if result['success']:
                    print(workflow_name + '-审批同意成功')
                else:
                    raise Exception(workflow_name + '-审批同意失败' + result['data'])
            else:
                raise Exception(workflow_name + '-审批同意失败' + str(r))
            """测试wifi和网络问题申报审批拒绝"""
            self.ssion.post(CMDB_URL + "/user_login/",
                            data={'username': 'laimingyao', 'password': '123123'})
            new_wse = obj.workflows.filter(is_current=1)[0]
            new_wse_id = new_wse.id
            reject_transition = new_wse.state.transition.filter(condition='拒绝')[0].id
            post_data = {
                "opinion": "拒绝",
                "transition": reject_transition,
                "wse": new_wse_id,
            }
            r = self.ssion.post(CMDB_URL + "/myworkflows/workflow_approve/", json=post_data)
            if r.status_code == 200:
                result = r.json()
                if result['success']:
                    print(workflow_name + '-审批拒绝成功')
                else:
                    raise Exception(workflow_name + '-审批拒绝失败' + result['data'])
            else:
                raise Exception(workflow_name + '-审批拒绝失败' + str(r))
            """测试访问工单详情（我的申请或者工单汇总）"""
            r = self.ssion.get(CMDB_URL + "/myworkflows/myworkflow_history?id=" + str(new_wse_id))
            if r.status_code == 200:
                print(workflow_name + '-访问工单详情成功')
            else:
                raise Exception(workflow_name + '-访问工单详情失败' + str(r))
            """测试提交网络问题申请"""
            self.ssion.post(CMDB_URL + "/user_login/", data={'username': 'chenjiefeng', 'password': '123123'})
            test_id = uuid.uuid1()
            post_data = {
                "applicant": "1155",
                "ip": "192.168.1.1",
                "name": "Null",
                "reason": "test",
                "title": "testnetwork" + str(test_id),
                "workflow": "5",
            }
            r = self.ssion.post(CMDB_URL + "/myworkflows/start_workflow/", json=post_data)
            if r.status_code == 200:
                result = r.json()
                if result['success']:
                    print(workflow_name + '-网络问题提交申请成功')
                else:
                    raise Exception(workflow_name + '-网络问题提交申请失败' + result['data'])
            else:
                raise Exception(workflow_name + '-网络问题提交申请失败' + str(r))
            """测试访问网络问题申报审批页面"""
            obj = Wifi.objects.last()
            new_wse = obj.workflows.filter(is_current=1)[0]
            new_wse_id = new_wse.id
            r = self.ssion.get(CMDB_URL + "/myworkflows/workflow_approve/?id=" + str(new_wse_id))
            if r.status_code == 200:
                print(workflow_name + '-网络问题申报-审批页面访问成功')
            else:
                raise Exception(workflow_name + '-网络问题申报-审批页面访问失败' + str(r))
            """测试取消申请工单"""
            new_wse = obj.workflows.filter(is_current=1)[0]
            new_wse_id = new_wse.id
            r = self.ssion.post(CMDB_URL + "/myworkflows/get_reject_transition_id/", json={'wse_id': new_wse_id})
            if r.status_code == 200:
                result = r.json()
                if result['success']:
                    transition_id = result['transition_id']
                else:
                    raise Exception(workflow_name + '-获取拒绝transition失败' + result['msg'])
            else:
                raise Exception(workflow_name + '-获取拒绝transition失败' + str(r))
            post_data = {
                'wse': new_wse_id,
                'transition': transition_id,
                'is_cancel': '1',
            }
            r = self.ssion.post(CMDB_URL + "/myworkflows/workflow_approve/", json=post_data)
            if r.status_code == 200:
                result = r.json()
                if result['success']:
                    print(workflow_name + '-取消工单申请成功')
                else:
                    raise Exception(workflow_name + '-取消工单申请失败' + result['data'])
            else:
                raise Exception(workflow_name + '-取消工单申请失败' + str(r))

            self.msg = workflow_name + '测试通过'
        except Exception as e:
            self.success = False
            self.msg = str(e)
        finally:
            return self.success, self.msg


class ComputerPartsWorkflowTest(object):
    """电脑和配件申请测试"""

    def __init__(self):
        self.success = True
        self.msg = 'ok'
        self.ssion = requests.session()
        data = {"username": "chenjiefeng", "password": "123123"}
        self.ssion.post(CMDB_URL + "/user_login/", data=data)

    def test_computer_parts_workflow(self):
        try:
            """测试填单页面"""
            workflow = Workflow.objects.get(pk=6)
            workflow_id = workflow.id
            workflow_name = workflow.name
            r = self.ssion.get(CMDB_URL + "/myworkflows/workflow_template/?workflow=" + str(workflow_id))
            if r.status_code == 200:
                print(workflow_name + '-填单页访问成功')
            else:
                raise Exception(workflow_name + '-填单页访问出现错误' + str(r))
            """测试生成审批链"""
            r = self.ssion.post(CMDB_URL + "/myworkflows/get_workflow_approve_user/",
                                json={'workflow': 6, 'applicant_id': 1155})
            if r.status_code == 200:
                result = r.json()
                if NEW_WORKFLOW == 1:
                    text = '审批人员链: 陈捷丰==>黎小龙==>梁家龙 <strong>审批人员有错误?可能申请人所在的部门不对!请联系运维处理</strong>'
                else:
                    text = '审批人员链: 陈捷丰==>黎小龙 <strong>审批人员有错误?可能申请人所在的部门不对!请联系运维处理</strong>'
                if result['success'] and result['data'] == text:
                    print('-' + workflow_name + '-提交申请页-生成审批链成功')
                else:
                    raise Exception('-' + workflow_name + '-提交申请页-生成审批链失败' + result['data'])
            else:
                raise Exception('-' + workflow_name + '-提交申请页-生成审批链失败' + str(r))
            """测试提交电脑配件申请"""
            test_id = uuid.uuid1()
            post_data = {
                "applicant": "1155",
                "reason": "test",
                "title": "testcomputerparts" + str(test_id),
                "workflow": "6",
            }
            r = self.ssion.post(CMDB_URL + "/myworkflows/start_workflow/", json=post_data)
            if r.status_code == 200:
                result = r.json()
                if result['success']:
                    print(workflow_name + '-提交申请成功')
                else:
                    raise Exception(workflow_name + '-提交申请失败' + result['data'])
            else:
                raise Exception(workflow_name + '-提交申请失败' + str(r))
            """测试访问电脑配件申请审批页面"""
            obj = ComputerParts.objects.last()
            wse = obj.workflows.filter(is_current=1)[0]
            wse_id = wse.id
            r = self.ssion.get(CMDB_URL + "/myworkflows/workflow_approve/?id=" + str(wse_id))
            if r.status_code == 200:
                print(workflow_name + '-审批页面访问成功')
            else:
                raise Exception(workflow_name + '-审批页面访问失败' + str(r))
            """测试电脑配件申请审批同意"""
            self.ssion.post(CMDB_URL + "/user_login/",
                            data={'username': 'lixiaolong', 'password': '123123'})
            accept_transition = wse.state.transition.filter(condition='同意')[0].id
            post_data = {
                "opinion": "同意",
                "transition": accept_transition,
                "wse": wse_id,
            }
            r = self.ssion.post(CMDB_URL + "/myworkflows/workflow_approve/", json=post_data)
            if r.status_code == 200:
                result = r.json()
                if result['success']:
                    print(workflow_name + '-审批同意成功')
                else:
                    raise Exception(workflow_name + '-审批同意失败' + result['data'])
            else:
                raise Exception(workflow_name + '-审批同意失败' + str(r))
            """测试电脑配件申请转单给其他网管"""
            self.ssion.post(CMDB_URL + "/user_login/",
                            data={'username': 'liangjialong', 'password': '123123'})
            new_wse = obj.workflows.filter(is_current=1)[0]
            new_wse_id = new_wse.id
            post_data = {
                "wse": new_wse_id,
                "to_anthoer_admin": "1215",
            }
            r = self.ssion.post(CMDB_URL + "/myworkflows/transfer_to_other_admin/", json=post_data)
            if r.status_code == 200:
                result = r.json()
                if result['success']:
                    print(workflow_name + '-转单网络管理员成功')
                else:
                    raise Exception(workflow_name + '-转单网络管理员失败' + result['data'])
            else:
                raise Exception(workflow_name + '-审批同意失败' + str(r))
            """测试电脑配件申请审批拒绝"""
            self.ssion.post(CMDB_URL + "/user_login/",
                            data={'username': 'laimingyao', 'password': '123123'})
            new_wse = obj.workflows.filter(is_current=1)[0]
            new_wse_id = new_wse.id
            reject_transition = new_wse.state.transition.filter(condition='拒绝')[0].id
            post_data = {
                "opinion": "拒绝",
                "transition": reject_transition,
                "wse": new_wse_id,
            }
            r = self.ssion.post(CMDB_URL + "/myworkflows/workflow_approve/", json=post_data)
            if r.status_code == 200:
                result = r.json()
                if result['success']:
                    print(workflow_name + '-审批拒绝成功')
                else:
                    raise Exception(workflow_name + '-审批拒绝失败' + result['data'])
            else:
                raise Exception(workflow_name + '-审批拒绝失败' + str(r))
            """测试访问工单详情（我的申请或者工单汇总）"""
            r = self.ssion.get(CMDB_URL + "/myworkflows/myworkflow_history?id=" + str(new_wse_id))
            if r.status_code == 200:
                print(workflow_name + '-访问工单详情成功')
            else:
                raise Exception(workflow_name + '-访问工单详情失败' + str(r))

            self.msg = workflow_name + '测试通过'
        except Exception as e:
            self.success = False
            self.msg = str(e)
        finally:
            return self.success, self.msg


class MachineWorkflowTest(object):
    """服务器申请测试"""

    def __init__(self):
        self.success = True
        self.msg = 'ok'
        self.ssion = requests.session()
        data = {"username": "chenjiefeng", "password": "123123"}
        self.ssion.post(CMDB_URL + "/user_login/", data=data)

    def test_machine_workflow(self):
        try:
            """测试填单页面"""
            workflow = Workflow.objects.get(pk=10)
            workflow_id = workflow.id
            workflow_name = workflow.name
            r = self.ssion.get(CMDB_URL + "/myworkflows/workflow_template/?workflow=" + str(workflow_id))
            if r.status_code == 200:
                print(workflow_name + '-填单页访问成功')
            else:
                raise Exception(workflow_name + '-填单页访问出现错误' + str(r))
            """测试生成审批链"""
            r = self.ssion.post(CMDB_URL + "/myworkflows/get_workflow_approve_user/",
                                json={'workflow': 10, 'applicant_id': 1155, 'project_id': 23})
            if r.status_code == 200:
                result = r.json()
                if result['success'] and result[
                    'data'] == '审批人员链: 黎小龙==>张圣洁 <strong>审批人员有错误?可能申请人所在的部门不对!请联系运维处理</strong>':
                    print('-' + workflow_name + '-提交申请页-生成审批链成功')
                else:
                    raise Exception('-' + workflow_name + '-提交申请页-生成审批链失败' + result['data'])
            else:
                raise Exception('-' + workflow_name + '-提交申请页-生成审批链失败' + str(r))
            """测试提交服务器申请"""
            test_id = uuid.uuid1()
            post_data = {
                "applicant": "1155",
                "config": [
                    {"config_cpu_value": "1", "config_mem_value": "1", "config_disk_value": "1", "config_number": "1"}],
                "ip_type": "1",
                "project": "23",
                "purpose": "test",
                "requirements": "test",
                "title": "testmachine" + str(test_id),
                "workflow": "10",
            }
            r = self.ssion.post(CMDB_URL + "/myworkflows/start_workflow/", json=post_data)
            if r.status_code == 200:
                result = r.json()
                if result['success']:
                    print(workflow_name + '-提交申请成功')
                else:
                    raise Exception(workflow_name + '-提交申请失败' + result['data'])
            else:
                raise Exception(workflow_name + '-提交申请失败' + str(r))
            """测试访问服务器申请审批页面"""
            obj = Machine.objects.last()
            wse = obj.workflows.filter(is_current=1)[0]
            wse_id = wse.id
            r = self.ssion.get(CMDB_URL + "/myworkflows/workflow_approve/?id=" + str(wse_id))
            if r.status_code == 200:
                print(workflow_name + '-审批页面访问成功')
            else:
                raise Exception(workflow_name + '-审批页面访问失败' + str(r))
            """测试电脑配件申请审批同意"""
            self.ssion.post(CMDB_URL + "/user_login/",
                            data={'username': 'lixiaolong', 'password': '123123'})
            accept_transition = wse.state.transition.filter(condition='同意')[0].id
            post_data = {
                "opinion": "同意",
                "transition": accept_transition,
                "wse": wse_id,
            }
            r = self.ssion.post(CMDB_URL + "/myworkflows/workflow_approve/", json=post_data)
            if r.status_code == 200:
                result = r.json()
                if result['success']:
                    print(workflow_name + '-审批同意成功')
                else:
                    raise Exception(workflow_name + '-审批同意失败' + result['data'])
            else:
                raise Exception(workflow_name + '-审批同意失败' + str(r))
            """测试服务器申请审批拒绝"""
            self.ssion.post(CMDB_URL + "/user_login/",
                            data={'username': 'zhangshengjie', 'password': '123123'})
            new_wse = obj.workflows.filter(is_current=1)[0]
            new_wse_id = new_wse.id
            reject_transition = new_wse.state.transition.filter(condition='拒绝')[0].id
            post_data = {
                "opinion": "拒绝",
                "transition": reject_transition,
                "wse": new_wse_id,
            }
            r = self.ssion.post(CMDB_URL + "/myworkflows/workflow_approve/", json=post_data)
            if r.status_code == 200:
                result = r.json()
                if result['success']:
                    print(workflow_name + '-审批拒绝成功')
                else:
                    raise Exception(workflow_name + '-审批拒绝失败' + result['data'])
            else:
                raise Exception(workflow_name + '-审批拒绝失败' + str(r))
            """测试访问工单详情（我的申请或者工单汇总）"""
            r = self.ssion.get(CMDB_URL + "/myworkflows/myworkflow_history?id=" + str(new_wse_id))
            if r.status_code == 200:
                print(workflow_name + '-访问工单详情成功')
            else:
                raise Exception(workflow_name + '-访问工单详情失败' + str(r))

            self.msg = workflow_name + '测试通过'
        except Exception as e:
            self.success = False
            self.msg = str(e)
        finally:
            return self.success, self.msg


class ProjectAdjustWorkflowTest(object):
    """项目调整申请测试"""

    def __init__(self):
        self.success = True
        self.msg = 'ok'
        self.ssion = requests.session()
        data = {"username": "chenjiefeng", "password": "123123"}
        self.ssion.post(CMDB_URL + "/user_login/", data=data)

    def test_project_adjust_workflow(self):
        try:
            """测试填单页面"""
            workflow = Workflow.objects.get(pk=13)
            workflow_id = workflow.id
            workflow_name = workflow.name
            r = self.ssion.get(CMDB_URL + "/myworkflows/workflow_template/?workflow=" + str(workflow_id))
            if r.status_code == 200:
                print(workflow_name + '-填单页访问成功')
            else:
                raise Exception(workflow_name + '-填单页访问出现错误' + str(r))
            """测试生成审批链"""
            r = self.ssion.post(CMDB_URL + "/myworkflows/get_workflow_approve_user/",
                                json={'workflow': 13, 'applicant_id': 1155})
            if r.status_code == 200:
                result = r.json()
                print(result['data'])
                print('审批人员链: 黎小龙 <strong>审批人员有错误?可能申请人所在的部门不对!请联系运维处理</strong>')
                if result['success'] and result[
                    'data'] == '审批人员链: 黎小龙 <strong>审批人员有错误?可能申请人所在的部门不对!请联系运维处理</strong>':
                    print('-' + workflow_name + '-提交申请页-生成审批链成功')
                else:
                    raise Exception('-' + workflow_name + '-提交申请页-生成审批链失败-' + result['data'])
            else:
                raise Exception('-' + workflow_name + '-提交申请页-生成审批链失败-' + str(r))
            """测试获取svn和服务器权限"""
            r = self.ssion.post(CMDB_URL + "/users/user_svn_serper_projects/", json={'user': 1155})
            if r.status_code == 200:
                result = r.json()
                if result['success']:
                    print('-' + workflow_name + '-提交申请页-获取svn和服务器权限成功')
                else:
                    raise Exception('-' + workflow_name + '-提交申请页-获取svn和服务器权限失败' + result['data'])
            else:
                raise Exception('-' + workflow_name + '-提交申请页-获取svn和服务器权限失败' + str(r))
            """测试列出所有部门下拉框"""
            r = self.ssion.post(CMDB_URL + "/users/list_department_group_all/")
            if r.status_code == 200:
                print('-' + workflow_name + '-提交申请页-列出所有部门下拉框成功')
            else:
                raise Exception('-' + workflow_name + '-提交申请页-列出所有部门下拉框失败' + str(r))
            """测试提交项目调整申请"""
            test_id = uuid.uuid1()
            post_data = {
                "applicant": "1155",
                "delete_serper": False,
                "delete_svn": False,
                "new_department_group": "20",
                "serper_projects": ["23", "25"],
                "svn_projects": ["23", "25"],
                "title": "testprojectadjust" + str(test_id),
                "workflow": "13",
            }
            r = self.ssion.post(CMDB_URL + "/myworkflows/start_workflow/", json=post_data)
            if r.status_code == 200:
                result = r.json()
                if result['success']:
                    print(workflow_name + '-提交申请成功')
                else:
                    raise Exception(workflow_name + '-提交申请失败' + result['data'])
            else:
                raise Exception(workflow_name + '-提交申请失败' + str(r))
            """测试访问项目调整申请审批页面"""
            obj = ProjectAdjust.objects.last()
            wse = obj.workflows.filter(is_current=1)[0]
            wse_id = wse.id
            r = self.ssion.get(CMDB_URL + "/myworkflows/workflow_approve/?id=" + str(wse_id))
            if r.status_code == 200:
                print(workflow_name + '-审批页面访问成功')
            else:
                raise Exception(workflow_name + '-审批页面访问失败' + str(r))
            """测试项目调整申请审批同意"""
            self.ssion.post(CMDB_URL + "/user_login/",
                            data={'username': 'lixiaolong', 'password': '123123'})
            accept_transition = wse.state.transition.filter(condition='同意')[0].id
            post_data = {
                "opinion": "同意",
                "transition": accept_transition,
                "wse": wse_id,
            }
            r = self.ssion.post(CMDB_URL + "/myworkflows/workflow_approve/", json=post_data)
            if r.status_code == 200:
                result = r.json()
                if result['success']:
                    print(workflow_name + '-审批同意成功')
                else:
                    raise Exception(workflow_name + '-审批同意失败' + result['data'])
            else:
                raise Exception(workflow_name + '-审批同意失败' + str(r))
            """测试访问工单详情（我的申请或者工单汇总）"""
            r = self.ssion.get(CMDB_URL + "/myworkflows/myworkflow_history?id=" + str(wse_id))
            if r.status_code == 200:
                print(workflow_name + '-访问工单详情成功')
            else:
                raise Exception(workflow_name + '-访问工单详情失败' + str(r))

            self.msg = workflow_name + '测试通过'
        except Exception as e:
            self.success = False
            self.msg = str(e)
        finally:
            return self.success, self.msg


class MySQLWorkflowTest(object):
    """数据库申请测试"""

    def __init__(self):
        self.success = True
        self.msg = 'ok'
        self.ssion = requests.session()
        data = {"username": "liangjun", "password": "123123"}
        self.ssion.post(CMDB_URL + "/user_login/", data=data)

    def test_mysql_workflow(self):
        try:
            """测试填单页面"""
            workflow = Workflow.objects.get(pk=14)
            workflow_id = workflow.id
            workflow_name = workflow.name
            r = self.ssion.get(CMDB_URL + "/myworkflows/workflow_template/?workflow=" + str(workflow_id))
            if r.status_code == 200:
                print(workflow_name + '-填单页访问成功')
            else:
                raise Exception(workflow_name + '-填单页访问出现错误' + str(r))
            """测试生成审批链"""
            r = self.ssion.post(CMDB_URL + "/myworkflows/get_workflow_approve_user/",
                                json={'workflow': 14, 'username': '梁俊'})
            if r.status_code == 200:
                result = r.json()
                if result['success'] and result[
                    'data'] == '审批人员链: 梁保明==>黎小龙 <strong>审批人员有错误?可能申请人所在的部门不对!请联系运维处理</strong>':
                    print('-' + workflow_name + '-提交申请页-生成审批链成功')
                else:
                    raise Exception('-' + workflow_name + '-提交申请页-生成审批链失败' + result['data'])
            else:
                raise Exception('-' + workflow_name + '-提交申请页-生成审批链失败' + str(r))
            """测试获取数据库实例列表"""
            r = self.ssion.post(CMDB_URL + "/mysql/list_mysql_instance/")
            if r.status_code == 200:
                print('-' + workflow_name + '-提交申请页-获取数据库实例列表成功')
            else:
                raise Exception('-' + workflow_name + '-提交申请页-获取数据库实例列表失败' + str(r))
            """测试根据实例获取库列表"""
            r = self.ssion.post(CMDB_URL + "/mysql/list_mysql_instance_db/",
                                data={'instance': 'gz-cdb-gxrtm5gk.sql.tencentcdb.com:63356'})
            if r.status_code == 200:
                print('-' + workflow_name + '-提交申请页-根据实例获取库成功')
            else:
                raise Exception('-' + workflow_name + '-提交申请页-根据实例获取库失败' + str(r))
            """测试提交数据库申请"""
            test_id = uuid.uuid1()
            post_data = {
                "reason": "test",
                "title": "testmysql" + str(test_id),
                "workflow": "14",
                "content": [{"instance": "129.204.180.165:3306", "passwd": "BOI6hBllH5nmndeeU2", "permission": "select", "dbs": ["gms_data_22", "log_api_22", "recharge_22", "web_gms_api_22"]}]
            }
            r = self.ssion.post(CMDB_URL + "/myworkflows/start_workflow/", json=post_data)
            if r.status_code == 200:
                result = r.json()
                if result['success']:
                    print(workflow_name + '-提交申请成功')
                else:
                    raise Exception(workflow_name + '-提交申请失败' + result['data'])
            else:
                raise Exception(workflow_name + '-提交申请失败' + str(r))
            """测试访问数据库申请审批页面"""
            obj = MysqlWorkflow.objects.last()
            wse = obj.workflows.filter(is_current=1)[0]
            wse_id = wse.id
            r = self.ssion.get(CMDB_URL + "/myworkflows/workflow_approve/?id=" + str(wse_id))
            if r.status_code == 200:
                print(workflow_name + '-审批页面访问成功')
            else:
                raise Exception(workflow_name + '-审批页面访问失败' + str(r))
            """测试数据库申请审批同意"""
            self.ssion.post(CMDB_URL + "/user_login/",
                            data={'username': 'liangbaoming', 'password': '123123'})
            accept_transition = wse.state.transition.filter(condition='同意')[0].id
            post_data = {
                "opinion": "同意",
                "transition": accept_transition,
                "wse": wse_id,
            }
            r = self.ssion.post(CMDB_URL + "/myworkflows/workflow_approve/", json=post_data)
            if r.status_code == 200:
                result = r.json()
                if result['success']:
                    print(workflow_name + '-审批同意成功')
                else:
                    raise Exception(workflow_name + '-审批同意失败' + result['data'])
            else:
                raise Exception(workflow_name + '-审批同意失败' + str(r))
            """测试数据库申请审批拒绝"""
            self.ssion.post(CMDB_URL + "/user_login/",
                            data={'username': 'lixiaolong', 'password': '123123'})
            new_wse = obj.workflows.filter(is_current=1)[0]
            new_wse_id = new_wse.id
            reject_transition = new_wse.state.transition.filter(condition='拒绝')[0].id
            post_data = {
                "opinion": "拒绝",
                "transition": reject_transition,
                "wse": new_wse_id,
            }
            r = self.ssion.post(CMDB_URL + "/myworkflows/workflow_approve/", json=post_data)
            if r.status_code == 200:
                result = r.json()
                if result['success']:
                    print(workflow_name + '-审批拒绝成功')
                else:
                    raise Exception(workflow_name + '-审批拒绝失败' + result['data'])
            else:
                raise Exception(workflow_name + '-审批拒绝失败' + str(r))
            """测试访问工单详情（我的申请或者工单汇总）"""
            r = self.ssion.get(CMDB_URL + "/myworkflows/myworkflow_history?id=" + str(new_wse_id))
            if r.status_code == 200:
                print(workflow_name + '-访问工单详情成功')
            else:
                raise Exception(workflow_name + '-访问工单详情失败' + str(r))

            self.msg = workflow_name + '测试通过'
        except Exception as e:
            self.success = False
            self.msg = str(e)
        finally:
            return self.success, self.msg


class VersionUpdateWorkflowTest(object):
    """版本更新单申请测试"""

    def __init__(self):
        self.success = True
        self.msg = 'ok'
        self.ssion = requests.session()
        data = {"username": "chenjiefeng", "password": "123123"}
        self.ssion.post(CMDB_URL + "/user_login/", data=data)

    def test_version_update_workflow(self):
        try:
            """测试填单页面"""
            workflow = Workflow.objects.get(pk=7)
            workflow_id = workflow.id
            workflow_name = workflow.name
            r = self.ssion.get(CMDB_URL + "/myworkflows/workflow_template/?workflow=" + str(workflow_id))
            if r.status_code == 200:
                print(workflow_name + '-填单页访问成功')
            else:
                raise Exception(workflow_name + '-填单页访问出现错误' + str(r))
            """测试根据项目获取后端负责人列表"""
            r = self.ssion.post(CMDB_URL + "/myworkflows/list_project_group_user/",
                                data={'project': '23', 'project_group': '服务端技术组'})
            if r.status_code == 200:
                results = r.json()
                if 'test-后端负责人' in [r['text'] for r in results]:
                    print('-' + workflow_name + '-提交申请页-根据项目获取后端负责人列表成功')
                else:
                    raise Exception('-' + workflow_name + '-提交申请页-根据项目获取后端负责人列表数据有误')
            else:
                raise Exception('-' + workflow_name + '-提交申请页-根据项目获取后端负责人列表失败' + str(r))
            """测试根据项目获取前端负责人列表"""
            r = self.ssion.post(CMDB_URL + "/myworkflows/list_project_group_user/",
                                data={'project': '23', 'project_group': '客户端技术组'})
            if r.status_code == 200:
                results = r.json()
                if 'test-前端负责人' in [r['text'] for r in results]:
                    print('-' + workflow_name + '-提交申请页-根据项目获取前端负责人列表成功')
                else:
                    raise Exception('-' + workflow_name + '-提交申请页-根据项目获取前端负责人列表数据有误')
            else:
                raise Exception('-' + workflow_name + '-提交申请页-根据项目获取前端负责人列表失败' + str(r))
            """测试根据项目获取策划负责人列表"""
            r = self.ssion.post(CMDB_URL + "/myworkflows/list_project_group_user/",
                                data={'project': '23', 'project_group': '策划组'})
            if r.status_code == 200:
                results = r.json()
                if 'test-策划' in [r['text'] for r in results]:
                    print('-' + workflow_name + '-提交申请页-根据项目获取策划负责人列表成功')
                else:
                    raise Exception('-' + workflow_name + '-提交申请页-根据项目获取策划负责人列表数据有误')
            else:
                raise Exception('-' + workflow_name + '-提交申请页-根据项目获取策划负责人列表失败' + str(r))
            """测试根据项目获取测试负责人列表"""
            r = self.ssion.post(CMDB_URL + "/myworkflows/list_project_group_user/",
                                data={'project': '23', 'project_group': '测试组'})
            if r.status_code == 200:
                results = r.json()
                if 'test-测试' in [r['text'] for r in results]:
                    print('-' + workflow_name + '-提交申请页-根据项目获取测试负责人列表成功')
                else:
                    raise Exception('-' + workflow_name + '-提交申请页-根据项目获取测试负责人列表数据有误')
            else:
                raise Exception('-' + workflow_name + '-提交申请页-根据项目获取测试负责人列表失败' + str(r))
            """测试提交版本更新单申请"""
            client_charge_id = User.objects.get(username='test-前端负责人').id
            plan_charge_id = User.objects.get(username='test-策划').id
            server_charge_id = User.objects.get(username='test-后端负责人').id
            test_charge_id = User.objects.get(username='test-测试').id
            test_id = uuid.uuid1()
            new_edition = "1" if NEW_VERSION_UPDATE else "0"
            server_list = [{"pf_name": "37", "srv_name": "37", "srv_id": "37_1", "gtype": "game", "ip": "10.25.136.91"}] if NEW_VERSION_UPDATE else 'test'
            post_data = {
                "client_charge": client_charge_id,
                "content": "test",
                "end_time": "2019-04-19 12:00",
                "plan_charge": plan_charge_id,
                "project": "23",
                "server_charge": server_charge_id,
                "server_list": server_list,
                "start_time": "2019-04-19 12:00",
                "test_charge": test_charge_id,
                "title": "testversionupdate" + str(test_id),
                "workflow": "7",
                "new_edition": new_edition,
            }
            r = self.ssion.post(CMDB_URL + "/myworkflows/start_workflow/", json=post_data)
            if r.status_code == 200:
                result = r.json()
                if result['success']:
                    print(workflow_name + '-提交申请成功')
                else:
                    raise Exception(workflow_name + '-提交申请失败' + result['data'])
            else:
                raise Exception(workflow_name + '-提交申请失败' + str(r))
            """测试访问版本更新单申请审批页面"""
            obj = VersionUpdate.objects.last()
            wse = obj.workflows.filter(is_current=1)[0]
            wse_id = wse.id
            r = self.ssion.get(CMDB_URL + "/myworkflows/workflow_approve/?id=" + str(wse_id))
            if r.status_code == 200:
                print(workflow_name + '-审批页面访问成功')
            else:
                raise Exception(workflow_name + '-审批页面访问失败' + str(r))
            """测试版本更新单后端负责人审批同意"""
            self.ssion.post(CMDB_URL + "/user_login/",
                            data={'username': 'test-后端负责人', 'password': '123123'})
            accept_transition = wse.state.transition.filter(condition='同意')[0].id
            post_data = {
                "opinion": "同意",
                "transition": accept_transition,
                "wse": wse_id,
                "server_version": "test",
                "server_attention": "test"
            }
            r = self.ssion.post(CMDB_URL + "/myworkflows/workflow_approve/", json=post_data)
            if r.status_code == 200:
                result = r.json()
                if result['success']:
                    print(workflow_name + '-后端负责人-审批同意成功')
                else:
                    raise Exception(workflow_name + '-后端负责人-审批同意失败' + result['data'])
            else:
                raise Exception(workflow_name + '-后端负责人-审批同意失败' + str(r))
            """测试版本更新单前端负责人审批同意"""
            self.ssion.post(CMDB_URL + "/user_login/",
                            data={'username': 'test-前端负责人', 'password': '123123'})
            new_wse = obj.workflows.filter(is_current=1)[0]
            new_wse_id = new_wse.id
            accept_transition = new_wse.state.transition.filter(condition='同意')[0].id
            client_content = [{"cdn_dir": "t1", "version": "Iyougu_21035", "client_type": "ios",
                                          "cdn_root_url": "resjysybt.chuangyunet.com"},
                                         {"cdn_dir": "t1", "version": "Ayougu_21035", "client_type": "android",
                                          "cdn_root_url": "resjysybt.chuangyunet.com"}] if NEW_VERSION_UPDATE else ''
            post_data = {
                "opinion": "同意",
                "transition": accept_transition,
                "wse": new_wse_id,
                "client_version": "test",
                "client_attention": "test",
                "client_content": client_content,
            }
            r = self.ssion.post(CMDB_URL + "/myworkflows/workflow_approve/", json=post_data)
            if r.status_code == 200:
                result = r.json()
                if result['success']:
                    print(workflow_name + '-前端负责人-审批同意成功')
                else:
                    raise Exception(workflow_name + '-前端负责人-审批同意失败' + result['data'])
            else:
                raise Exception(workflow_name + '-前端负责人-审批同意失败' + str(r))
            """测试版本更新单策划负责人审批同意"""
            self.ssion.post(CMDB_URL + "/user_login/",
                            data={'username': 'test-策划', 'password': '123123'})
            new_wse = obj.workflows.filter(is_current=1)[0]
            new_wse_id = new_wse.id
            accept_transition = new_wse.state.transition.filter(condition='同意')[0].id
            post_data = {
                "opinion": "同意",
                "transition": accept_transition,
                "wse": new_wse_id,
            }
            r = self.ssion.post(CMDB_URL + "/myworkflows/workflow_approve/", json=post_data)
            if r.status_code == 200:
                result = r.json()
                if result['success']:
                    print(workflow_name + '-策划负责人-审批同意成功')
                else:
                    raise Exception(workflow_name + '-策划负责人-审批同意失败' + result['data'])
            else:
                raise Exception(workflow_name + '-策划负责人-审批同意失败' + str(r))
            """测试访问更换审批人页面"""
            self.ssion.post(CMDB_URL + "/user_login/", data={'username': 'chenjiefneg', 'password': '123123'})
            new_wse = obj.workflows.filter(is_current=1)[0]
            new_wse_id = new_wse.id
            r = self.ssion.get(CMDB_URL + "/myworkflows/change_approve/?id=" + str(new_wse_id))
            if r.status_code == 200:
                print(workflow_name + '-访问更换审批人页面成功')
            else:
                raise Exception(workflow_name + '-访问更换审批人页面失败' + str(r))
            """测试更换审批人"""
            self.ssion.post(CMDB_URL + "/user_login/", data={'username': 'chenjiefneg', 'password': '123123'})
            new_wse = obj.workflows.filter(is_current=1)[0]
            new_wse_id = new_wse.id
            post_data = {
                "change_approve": "150",
                "wse": new_wse_id,
            }
            r = self.ssion.post(CMDB_URL + "/myworkflows/change_approve/?id=", json=post_data)
            if r.status_code == 200:
                result = r.json()
                if result['success']:
                    print(workflow_name + '-更换审批人成功')
                else:
                    raise Exception(workflow_name + '-更换审批人失败' + result['data'])
            else:
                raise Exception(workflow_name + '-更换审批人失败' + str(r))
            """测试版本更新单测试负责人审批同意"""
            self.ssion.post(CMDB_URL + "/user_login/",
                            data={'username': 'chenzhijian', 'password': '123123'})
            new_wse = obj.workflows.filter(is_current=1)[0]
            new_wse_id = new_wse.id
            accept_transition = new_wse.state.transition.filter(condition='同意')[0].id
            post_data = {
                "opinion": "同意",
                "transition": accept_transition,
                "wse": new_wse_id,
            }
            r = self.ssion.post(CMDB_URL + "/myworkflows/workflow_approve/", json=post_data)
            if r.status_code == 200:
                result = r.json()
                if result['success']:
                    print(workflow_name + '-测试负责人-审批同意成功')
                else:
                    raise Exception(workflow_name + '-测试负责人-审批同意失败' + result['data'])
            else:
                raise Exception(workflow_name + '-测试负责人-审批同意失败' + str(r))
            """测试访问工单详情（我的申请或者工单汇总）"""
            r = self.ssion.get(CMDB_URL + "/myworkflows/myworkflow_history?id=" + str(new_wse_id))
            if r.status_code == 200:
                print(workflow_name + '-访问工单详情成功')
            else:
                raise Exception(workflow_name + '-访问工单详情失败' + str(r))

            self.msg = workflow_name + '测试通过'
        except Exception as e:
            self.success = False
            self.msg = str(e)
        finally:
            return self.success, self.msg


class ClientHotUpdateTest(object):
    """前端热更新测试"""

    def __init__(self):
        self.success = True
        self.msg = 'ok'
        self.ssion = requests.session()
        data = {"username": "chenjiefeng", "password": "123123"}
        self.ssion.post(CMDB_URL + "/user_login/", data=data)

    def test_client_hot_update(self):
        try:
            """测试选择游戏项目页面"""
            workflow = Workflow.objects.get(pk=8)
            workflow_id = workflow.id
            workflow_name = workflow.name
            r = self.ssion.get(CMDB_URL + "/myworkflows/workflow_template/?workflow=" + str(workflow_id))
            if r.status_code == 200:
                print(workflow_name + '-访问选择游戏项目页面成功')
            else:
                raise Exception(workflow_name + '-访问选择游戏项目页面失败' + str(r))
            """测试根据请求用户选择游戏项目下拉框"""
            r = self.ssion.post(CMDB_URL + "/myworkflows/list_game_project_by_group/")
            if r.status_code == 200:
                project_list = r.json()
                if project_list:
                    print('-' + workflow_name + '-访问根据请求用户选择游戏项目下拉框成功')
                else:
                    raise Exception('-' + workflow_name + '-访问根据请求用户选择游戏项目下拉框失败' + '-列表为空')
            else:
                raise Exception('-' + workflow_name + '-访问根据请求用户选择游戏项目下拉框失败' + str(r))
            """测试填单页面"""
            for project in project_list:
                r = self.ssion.get(
                    CMDB_URL + "/myworkflows/start_hotupdate?workflow=" + str(workflow_id) + '&project=' + str(
                        project['id']))
                if r.status_code == 200:
                    print(workflow_name + '-' + project['text'] + '-填单页访问成功')
                else:
                    raise Exception(workflow_name + '-填单页访问出现错误' + str(r))
            """测试根据项目列出地区下拉框"""
            post_data = {
                "project": "23",
                "update_type": "hot_client"
            }
            r = self.ssion.post(
                CMDB_URL + "/myworkflows/list_area_name_by_project/", data=post_data)
            if r.status_code == 200:
                print('-' + workflow_name + '-根据项目列出地区下拉框成功')
            else:
                raise Exception('-' + workflow_name + '-根据项目列出地区下拉框出现错误' + str(r))
            """测试备用主程审批人下拉框"""
            post_data = {
                "project": "23",
                "project_group": "前端组"
            }
            r = self.ssion.post(
                CMDB_URL + "/assets/list_backup_dev/", data=post_data)
            if r.status_code == 200:
                print('-' + workflow_name + '-备用主程审批人下拉框成功')
            else:
                raise Exception('-' + workflow_name + '-备用主程审批人下拉框出现错误' + str(r))
            """测试测试负责人下拉框"""
            r = self.ssion.post(CMDB_URL + "/assets/list_test_user/", headers={'referer': 'http://192.168.90.38:8000/myworkflows/start_hotupdate?workflow=8&project=23'})
            if r.status_code == 200:
                print('-' + workflow_name + '-测试负责人下拉框成功')
            else:
                raise Exception('-' + workflow_name + '-测试负责人下拉框出现错误' + str(r))
            """测试运营负责人下拉框"""
            r = self.ssion.post(
                CMDB_URL + "/assets/list_operation_user/")
            if r.status_code == 200:
                print('-' + workflow_name + '-运营负责人下拉框成功')
            else:
                raise Exception('-' + workflow_name + '-运营负责人下拉框出现错误' + str(r))
            """测试创畅运营负责人下拉框"""
            r = self.ssion.post(
                CMDB_URL + "/assets/list_cc_operation_user/")
            if r.status_code == 200:
                print('-' + workflow_name + '-创畅运营负责人下拉框成功')
            else:
                raise Exception('-' + workflow_name + '-创畅运营负责人下拉框出现错误' + str(r))
            """测试更新版本号下拉框"""
            post_data = {
                "project": "23",
                "area": "大陆"
            }
            r = self.ssion.post(
                CMDB_URL + "/myworkflows/list_game_client_version/", data=post_data)
            if r.status_code == 200:
                print('-' + workflow_name + '-更新版本号下拉框成功')
            else:
                raise Exception('-' + workflow_name + '-更新版本号下拉框出现错误' + str(r))
            """测试cdn版本列表下拉框"""
            post_data = {
                "area_name": "大陆",
                "client_version": "015700000",
                "project": "23",
            }
            r = self.ssion.post(
                CMDB_URL + "/myworkflows/get_cnd_version_list/", json=post_data)
            if r.status_code == 200:
                print('-' + workflow_name + '-cdn版本列表下拉框成功')
            else:
                raise Exception('-' + workflow_name + '-cdn版本列表下拉框出现错误' + str(r))
            """测试根据cdn获取区服列表"""
            post_data = {
                "area_name": "大陆",
                "cdn_dir": "r1",
                "cdn_root_url": "jyjh.cdn.gop.yyclouds.com",
                "client_version": "015700000",
                "id": "552909",
                "project": "23",
            }
            r = self.ssion.post(
                CMDB_URL + "/myworkflows/get_server_list_by_cdn/", json=post_data)
            if r.status_code == 200:
                print('-' + workflow_name + '-根据cdn获取区服列表成功')
            else:
                raise Exception('-' + workflow_name + '-根据cdn获取区服列表出现错误' + str(r))
            """测试获取更新文件列表"""
            test_uuid = str(uuid.uuid1())
            post_data = {
                "area_name": "大陆",
                "area_name_detail": "大陆",
                "content": [
                    {
                        "area_name": "大陆",
                        "cdn_dir": "r1",
                        "cdn_root_url": "jyjh.cdn.gop.yyclouds.com",
                        "client_version": "015700000",
                        "id": 552909,
                        "project": 23,
                    }
                ],
                "project": "23",
                "update_type": "hot_client",
                "uuid": test_uuid,
                "version": "015700000",
            }
            r = self.ssion.post(
                CMDB_URL + "/myworkflows/pull_file_list/", json=post_data)
            if r.status_code == 200:
                print('-' + workflow_name + '-获取更新文件列表成功')
            else:
                raise Exception('-' + workflow_name + '-获取更新文件列表出现错误' + str(r))
            """获取前端热更新手机操作系统类型下拉框"""
            post_data = {
                "area_name": "大陆",
                "project": "29",
            }
            r = self.ssion.post(
                CMDB_URL + "/myworkflows/get_hotupdate_client_type/", data=post_data)
            if r.status_code == 200:
                print('-' + workflow_name + '-手机操作系统类型下拉框成功')
            else:
                raise Exception('-' + workflow_name + '-手机操作系统类型下拉框出现错误-' + str(r))
            """获取cdn根目录下拉框"""
            post_data = {
                "area_name": "大陆",
                "project": "29",
            }
            r = self.ssion.post(
                CMDB_URL + "/myworkflows/get_cdn_root_url/", data=post_data)
            if r.status_code == 200:
                print('-' + workflow_name + '-获取cdn根目录下拉框')
            else:
                raise Exception('-' + workflow_name + '-获取cdn根目录下拉框-' + str(r))
            """获取cdn目录下拉框"""
            post_data = {
                "project": 29,
                "client_type": "cn_ios",
                "cdn_root_url": "res.snsy.chuangyunet.com",
                "area_name": "大陆",
            }
            r = self.ssion.post(
                CMDB_URL + "/myworkflows/get_cdn_dir/", data=post_data)
            if r.status_code == 200:
                print('-' + workflow_name + '-获取cdn目录下拉框')
            else:
                raise Exception('-' + workflow_name + '-获取cdn目录下拉框-' + str(r))
            """获取游戏平台下拉框"""
            post_data = {
                "project": 39,
                "area_name": "大陆",
            }
            r = self.ssion.post(
                CMDB_URL + "/myworkflows/get_csxy_game_server_platform/", data=post_data)
            if r.status_code == 200:
                print('-' + workflow_name + '-获取游戏平台下拉框')
            else:
                raise Exception('-' + workflow_name + '-获取游戏平台下拉框-' + str(r))
            """提交前端热更新申请"""
            backup_dev_id = User.objects.get(username='test-前端负责人').id
            operation_head_id = User.objects.get(username='test-运营').id
            post_data = {
                "workflow": "8",
                "title": "testclienthotupdate" + str(test_uuid),
                "reason": "test",
                "attention": "test",
                "project": "23",
                "area_name_and_en": "大陆",
                "backup_dev": backup_dev_id,
                "test_head": None,
                "operation_head": [operation_head_id],
                "extra": None,
                "client_version": "015700000",
                "content": [{
                    "cdn_dir": "r1",
                    "id": 552909,
                    "project": 23,
                    "area_name": "大陆",
                    "client_version": "015700000",
                    "cdn_root_url": "jyjh.cdn.gop.yyclouds.com"
                }],
                "pair_code": "无",
                "order": "无",
                "list_update_file": [{
                    "file_name": "hello2.td",
                    "file_md5": "d41d8cd98f00b204e9800998ecf8427e",
                    "file_mtime": "2019-03-18 14:45:03",
                    "area_dir": "cn"
                }, {
                    "file_name": "hello1.td",
                    "file_md5": "d41d8cd98f00b204e9800998ecf8427e",
                    "file_mtime": "2019-03-18 14:45:03",
                    "area_dir": "cn"
                }, {
                    "file_name": "hello3.td",
                    "file_md5": "d41d8cd98f00b204e9800998ecf8427e",
                    "file_mtime": "2019-03-18 14:45:03",
                    "area_dir": "cn"
                }],
                "uuid": test_uuid
            }
            r = self.ssion.post(CMDB_URL + "/myworkflows/start_workflow/", json=post_data)
            if r.status_code == 200:
                result = r.json()
                if result['success']:
                    print(workflow_name + '-提交申请成功')
                else:
                    raise Exception(workflow_name + '-提交申请失败' + result['data'])
            else:
                raise Exception(workflow_name + '-提交申请失败' + str(r))
            """测试访问前端热更新申请审批页面"""
            obj = ClientHotUpdate.objects.last()
            wse = obj.workflows.filter(is_current=1)[0]
            wse_id = wse.id
            r = self.ssion.get(CMDB_URL + "/myworkflows/workflow_approve/?id=" + str(wse_id))
            if r.status_code == 200:
                print(workflow_name + '-审批页面访问成功')
            else:
                raise Exception(workflow_name + '-审批页面访问失败' + str(r))
            """测试前端热更新项目组长审批同意"""
            self.ssion.post(CMDB_URL + "/user_login/",
                            data={'username': 'test-前端负责人', 'password': '123123'})
            new_wse = obj.workflows.filter(is_current=1)[0]
            new_wse_id = new_wse.id
            accept_transition = new_wse.state.transition.filter(condition='同意')[0].id
            post_data = {
                "opinion": "同意",
                "transition": accept_transition,
                "wse": new_wse_id,
            }
            r = self.ssion.post(CMDB_URL + "/myworkflows/workflow_approve/", json=post_data)
            if r.status_code == 200:
                result = r.json()
                if result['success']:
                    print(workflow_name + '-项目组长-审批同意成功')
                else:
                    raise Exception(workflow_name + '-项目组长-审批同意失败' + result['data'])
            else:
                raise Exception(workflow_name + '-项目组长-审批同意失败' + str(r))
            """测试前端热更新运营审批同意"""
            self.ssion.post(CMDB_URL + "/user_login/",
                            data={'username': 'test-运营', 'password': '123123'})
            new_wse = obj.workflows.filter(is_current=1)[0]
            new_wse_id = new_wse.id
            accept_transition = new_wse.state.transition.filter(condition='同意')[0].id
            post_data = {
                "opinion": "同意",
                "transition": accept_transition,
                "wse": new_wse_id,
            }
            r = self.ssion.post(CMDB_URL + "/myworkflows/workflow_approve/", json=post_data)
            if r.status_code == 200:
                result = r.json()
                if result['success']:
                    print(workflow_name + '-运营-审批同意成功')
                else:
                    raise Exception(workflow_name + '-运营-审批同意失败' + result['data'])
            else:
                raise Exception(workflow_name + '-运营-审批同意失败' + str(r))
            """测试访问工单详情（我的申请或者工单汇总）"""
            r = self.ssion.get(CMDB_URL + "/myworkflows/myworkflow_history?id=" + str(new_wse_id))
            if r.status_code == 200:
                print(workflow_name + '-访问工单详情成功')
            else:
                raise Exception(workflow_name + '-访问工单详情失败' + str(r))

            self.msg = workflow_name + '测试通过'
        except Exception as e:
            self.success = False
            self.msg = str(e)
        finally:
            return self.success, self.msg


class ServerHotUpdateTest(object):
    """后端热更新测试"""

    def __init__(self):
        self.success = True
        self.msg = 'ok'
        self.ssion = requests.session()
        data = {"username": "chenjiefeng", "password": "123123"}
        self.ssion.post(CMDB_URL + "/user_login/", data=data)

    def test_server_hot_update(self):
        try:
            """测试选择游戏项目页面"""
            workflow = Workflow.objects.get(pk=9)
            workflow_id = workflow.id
            workflow_name = workflow.name
            r = self.ssion.get(CMDB_URL + "/myworkflows/workflow_template/?workflow=" + str(workflow_id))
            if r.status_code == 200:
                print(workflow_name + '-访问选择游戏项目页面成功')
            else:
                raise Exception(workflow_name + '-访问选择游戏项目页面失败' + str(r))
            """测试根据请求用户选择游戏项目下拉框"""
            r = self.ssion.post(CMDB_URL + "/myworkflows/list_game_project_by_group/")
            if r.status_code == 200:
                project_list = r.json()
                if project_list:
                    print('-' + workflow_name + '-访问根据请求用户选择游戏项目下拉框成功')
                else:
                    raise Exception('-' + workflow_name + '-访问根据请求用户选择游戏项目下拉框失败' + '-列表为空')
            else:
                raise Exception('-' + workflow_name + '-访问根据请求用户选择游戏项目下拉框失败' + str(r))
            """测试填单页面"""
            for project in project_list:
                r = self.ssion.get(
                    CMDB_URL + "/myworkflows/start_hotupdate?workflow=" + str(workflow_id) + '&project=' + str(
                        project['id']))
                if r.status_code == 200:
                    print(workflow_name + '-' + project['text'] + '-填单页访问成功')
                else:
                    raise Exception(workflow_name + '-填单页访问出现错误' + str(r))
            """测试根据项目列出地区下拉框"""
            post_data = {
                "project": "23",
                "update_type": "hot_server"
            }
            r = self.ssion.post(
                CMDB_URL + "/myworkflows/list_area_name_by_project/", data=post_data)
            if r.status_code == 200:
                print('-' + workflow_name + '-根据项目列出地区下拉框成功')
            else:
                raise Exception('-' + workflow_name + '-根据项目列出地区下拉框出现错误' + str(r))
            """测试备用主程审批人下拉框"""
            post_data = {
                "project": "23",
                "project_group": "后端组"
            }
            r = self.ssion.post(
                CMDB_URL + "/assets/list_backup_dev/", data=post_data)
            if r.status_code == 200:
                print('-' + workflow_name + '-备用主程审批人下拉框成功')
            else:
                raise Exception('-' + workflow_name + '-备用主程审批人下拉框出现错误' + str(r))
            """提交后端热更新申请"""
            backup_dev_id = User.objects.get(username='test-后端负责人').id
            operation_head_id = User.objects.get(username='test-运营').id
            test_uuid = uuid.uuid1()
            post_data = {
                "workflow": "9",
                "title": "testserverhotupdate" + str(test_uuid),
                "reason": "",
                "attention": "",
                "project": "23",
                "area_name_and_en": "大陆",
                "backup_dev": backup_dev_id,
                "test_head": None,
                "operation_head": [operation_head_id],
                "extra": None,
                "hot_server_type": "0",
                "list_update_file": [{
                    "file_name": "sdlsd3.sdfdasf",
                    "file_md5": "d41d8cd98f00b204e9800998ecf8427e",
                    "file_mtime": "2019-03-18 15:05:18",
                    "area_dir": "cn"
                }, {
                    "file_name": "sdlsd2.sdfdasf",
                    "file_md5": "d41d8cd98f00b204e9800998ecf8427e",
                    "file_mtime": "2019-03-18 15:05:18",
                    "area_dir": "cn"
                }, {
                    "file_name": "sdlsd4.sdfdasf",
                    "file_md5": "d41d8cd98f00b204e9800998ecf8427e",
                    "file_mtime": "2019-03-18 15:05:18",
                    "area_dir": "cn"
                }, {
                    "file_name": "sdlsd1.sdfdasf",
                    "file_md5": "d41d8cd98f00b204e9800998ecf8427e",
                    "file_mtime": "2019-03-18 15:05:18",
                    "area_dir": "cn"
                }],
                "erlang_cmd_list": "",
                "server_version": "015700000",
                "update_server_list": [{
                    "srv_id": "liebao_180",
                    "srv_name": "双线180服",
                    "ip": "10.25.136.77",
                    "gtype": "game",
                    "pf_name": "liebao",
                    "gameserverid": "530437"
                }],
                "replication_server_list": [{
                    "srv_id": "37_1",
                    "srv_name": "双线1服",
                    "ip": "10.25.136.91",
                    "gtype": "game",
                    "pf_name": "37",
                    "gameserverid": "530446"
                }, {
                    "srv_id": "37_26",
                    "srv_name": "双线26服",
                    "ip": "10.25.136.97",
                    "gtype": "game",
                    "pf_name": "37",
                    "gameserverid": "530591"
                }, {
                    "srv_id": "37_67",
                    "srv_name": "双线67服",
                    "ip": "10.25.136.93",
                    "gtype": "game",
                    "pf_name": "37",
                    "gameserverid": "530592"
                }, {
                    "srv_id": "37_163",
                    "srv_name": "双线163服",
                    "ip": "10.25.136.97",
                    "gtype": "game",
                    "pf_name": "37",
                    "gameserverid": "530449"
                }, {
                    "srv_id": "37_217",
                    "srv_name": "双线217服",
                    "ip": "10.25.136.98",
                    "gtype": "game",
                    "pf_name": "37",
                    "gameserverid": "530600"
                }, {
                    "srv_id": "360_1",
                    "srv_name": "双线1服",
                    "ip": "10.25.136.96",
                    "gtype": "game",
                    "pf_name": "360",
                    "gameserverid": "530372"
                }, {
                    "srv_id": "360_77",
                    "srv_name": "双线77服",
                    "ip": "10.25.136.77",
                    "gtype": "game",
                    "pf_name": "360",
                    "gameserverid": "530376"
                }, {
                    "srv_id": "360_328",
                    "srv_name": "双线328服",
                    "ip": "10.25.136.91",
                    "gtype": "game",
                    "pf_name": "360",
                    "gameserverid": "530452"
                }, {
                    "srv_id": "360_647",
                    "srv_name": "双线647服",
                    "ip": "10.25.136.97",
                    "gtype": "game",
                    "pf_name": "360",
                    "gameserverid": "530383"
                }, {
                    "srv_id": "2217_1",
                    "srv_name": "双线1服",
                    "ip": "10.25.136.96",
                    "gtype": "game",
                    "pf_name": "2217",
                    "gameserverid": "530543"
                }, {
                    "srv_id": "2345_1",
                    "srv_name": "双线1服",
                    "ip": "10.25.136.94",
                    "gtype": "game",
                    "pf_name": "2345",
                    "gameserverid": "530451"
                }, {
                    "srv_id": "2345_135",
                    "srv_name": "双线135服",
                    "ip": "10.25.136.91",
                    "gtype": "game",
                    "pf_name": "2345",
                    "gameserverid": "530599"
                }, {
                    "srv_id": "4366_1",
                    "srv_name": "双线1服",
                    "ip": "10.25.136.96",
                    "gtype": "game",
                    "pf_name": "4366",
                    "gameserverid": "530503"
                }, {
                    "srv_id": "afgame_1",
                    "srv_name": "双线1服",
                    "ip": "10.25.136.96",
                    "gtype": "game",
                    "pf_name": "afgame",
                    "gameserverid": "530674"
                }, {
                    "srv_id": "7k7k_1",
                    "srv_name": "双线1服",
                    "ip": "10.25.136.97",
                    "gtype": "game",
                    "pf_name": "7k7k",
                    "gameserverid": "530548"
                }, {
                    "srv_id": "douyu_1",
                    "srv_name": "双线1服",
                    "ip": "10.25.136.93",
                    "gtype": "game",
                    "pf_name": "douyu",
                    "gameserverid": "530737"
                }, {
                    "srv_id": "sogou_1",
                    "srv_name": "双线1服",
                    "ip": "10.25.136.98",
                    "gtype": "game",
                    "pf_name": "sogou",
                    "gameserverid": "530403"
                }, {
                    "srv_id": "yy_9002",
                    "srv_name": "不删档付费测试1服",
                    "ip": "10.25.136.97",
                    "gtype": "game",
                    "pf_name": "yy",
                    "gameserverid": "530353"
                }, {
                    "srv_id": "yy_1",
                    "srv_name": "s1",
                    "ip": "10.25.136.96",
                    "gtype": "game",
                    "pf_name": "yy",
                    "gameserverid": "530325"
                }, {
                    "srv_id": "yy_217",
                    "srv_name": "双线217服",
                    "ip": "10.25.136.77",
                    "gtype": "game",
                    "pf_name": "yy",
                    "gameserverid": "530326"
                }, {
                    "srv_id": "yy_973",
                    "srv_name": "双线973服",
                    "ip": "10.25.136.76",
                    "gtype": "game",
                    "pf_name": "yy",
                    "gameserverid": "530330"
                }, {
                    "srv_id": "yy_1146",
                    "srv_name": "双线1146服",
                    "ip": "10.25.136.96",
                    "gtype": "game",
                    "pf_name": "yy",
                    "gameserverid": "548663"
                }, {
                    "srv_id": "yy_1159",
                    "srv_name": "双线1159服",
                    "ip": "10.25.136.76",
                    "gtype": "game",
                    "pf_name": "yy",
                    "gameserverid": "552255"
                }, {
                    "srv_id": "yy_1161",
                    "srv_name": "双线1161服",
                    "ip": "10.25.136.97",
                    "gtype": "game",
                    "pf_name": "yy",
                    "gameserverid": "552462"
                }, {
                    "srv_id": "yy_1163",
                    "srv_name": "双线1163服",
                    "ip": "10.25.136.91",
                    "gtype": "game",
                    "pf_name": "yy",
                    "gameserverid": "552624"
                }, {
                    "srv_id": "yy_1164",
                    "srv_name": "双线1164服",
                    "ip": "10.25.136.93",
                    "gtype": "game",
                    "pf_name": "yy",
                    "gameserverid": "552780"
                }, {
                    "srv_id": "yy_1165",
                    "srv_name": "双线1165服",
                    "ip": "10.25.136.94",
                    "gtype": "game",
                    "pf_name": "yy",
                    "gameserverid": "552842"
                }, {
                    "srv_id": "yy_1166",
                    "srv_name": "双线1166服",
                    "ip": "10.25.136.76",
                    "gtype": "game",
                    "pf_name": "yy",
                    "gameserverid": "552894"
                }, {
                    "srv_id": "ufojoy_1",
                    "srv_name": "双线1服",
                    "ip": "10.25.136.93",
                    "gtype": "game",
                    "pf_name": "ufojoy",
                    "gameserverid": "530479"
                }, {
                    "srv_id": "ufojoy_794",
                    "srv_name": "双线794服",
                    "ip": "10.25.136.76",
                    "gtype": "game",
                    "pf_name": "ufojoy",
                    "gameserverid": "552442"
                }, {
                    "srv_id": "ufojoy_797",
                    "srv_name": "双线797服",
                    "ip": "10.25.136.96",
                    "gtype": "game",
                    "pf_name": "ufojoy",
                    "gameserverid": "552519"
                }, {
                    "srv_id": "ufojoy_799",
                    "srv_name": "双线799服",
                    "ip": "10.25.136.98",
                    "gtype": "game",
                    "pf_name": "ufojoy",
                    "gameserverid": "552639"
                }, {
                    "srv_id": "ufojoy_801",
                    "srv_name": "双线801服",
                    "ip": "10.25.136.94",
                    "gtype": "game",
                    "pf_name": "ufojoy",
                    "gameserverid": "552719"
                }, {
                    "srv_id": "ufojoy_802",
                    "srv_name": "双线802服",
                    "ip": "10.25.136.76",
                    "gtype": "game",
                    "pf_name": "ufojoy",
                    "gameserverid": "552781"
                }, {
                    "srv_id": "ufojoy_803",
                    "srv_name": "双线803服",
                    "ip": "10.25.136.98",
                    "gtype": "game",
                    "pf_name": "ufojoy",
                    "gameserverid": "552843"
                }, {
                    "srv_id": "ufojoy_804",
                    "srv_name": "双线804服",
                    "ip": "10.25.136.96",
                    "gtype": "game",
                    "pf_name": "ufojoy",
                    "gameserverid": "552893"
                }, {
                    "srv_id": "ufojoy_805",
                    "srv_name": "双线805服",
                    "ip": "10.25.136.98",
                    "gtype": "game",
                    "pf_name": "ufojoy",
                    "gameserverid": "552909"
                }, {
                    "srv_id": "yooxun_1",
                    "srv_name": "双线1服",
                    "ip": "10.25.136.97",
                    "gtype": "game",
                    "pf_name": "yooxun",
                    "gameserverid": "530711"
                }, {
                    "srv_id": "swjoy_1",
                    "srv_name": "双线1服",
                    "ip": "10.25.136.94",
                    "gtype": "game",
                    "pf_name": "swjoy",
                    "gameserverid": "530499"
                }, {
                    "srv_id": "swjoy_332",
                    "srv_name": "双线332服",
                    "ip": "10.25.136.77",
                    "gtype": "game",
                    "pf_name": "swjoy",
                    "gameserverid": "530657"
                }, {
                    "srv_id": "99yx_1",
                    "srv_name": "双线1服",
                    "ip": "10.25.136.93",
                    "gtype": "game",
                    "pf_name": "99yx",
                    "gameserverid": "530546"
                }, {
                    "srv_id": "teeqee_1",
                    "srv_name": "双线1服",
                    "ip": "10.25.136.94",
                    "gtype": "game",
                    "pf_name": "teeqee",
                    "gameserverid": "530630"
                }, {
                    "srv_id": "ywqq_1",
                    "srv_name": "双线1服",
                    "ip": "10.251.60.9",
                    "gtype": "game",
                    "pf_name": "ywqq",
                    "gameserverid": "530275"
                }, {
                    "srv_id": "ywqq_65",
                    "srv_name": "双线65服",
                    "ip": "10.104.67.143",
                    "gtype": "game",
                    "pf_name": "ywqq",
                    "gameserverid": "530278"
                }, {
                    "srv_id": "ywqq_129",
                    "srv_name": "双线129服",
                    "ip": "10.104.94.129",
                    "gtype": "game",
                    "pf_name": "ywqq",
                    "gameserverid": "530274"
                }, {
                    "srv_id": "ywqq_193",
                    "srv_name": "双线193服",
                    "ip": "10.104.59.100",
                    "gtype": "game",
                    "pf_name": "ywqq",
                    "gameserverid": "530276"
                }, {
                    "srv_id": "ywqq_259",
                    "srv_name": "双线259服",
                    "ip": "10.104.35.121",
                    "gtype": "game",
                    "pf_name": "ywqq",
                    "gameserverid": "530283"
                }, {
                    "srv_id": "ywqq_321",
                    "srv_name": "双线321服",
                    "ip": "10.104.26.154",
                    "gtype": "game",
                    "pf_name": "ywqq",
                    "gameserverid": "530286"
                }, {
                    "srv_id": "ywqq_9001",
                    "srv_name": "双线9001服",
                    "ip": "10.104.5.99",
                    "gtype": "game",
                    "pf_name": "ywqq",
                    "gameserverid": "530311"
                }, {
                    "srv_id": "ywqq_385",
                    "srv_name": "双线385服",
                    "ip": "10.104.3.230",
                    "gtype": "game",
                    "pf_name": "ywqq",
                    "gameserverid": "530281"
                }, {
                    "srv_id": "ywqq_449",
                    "srv_name": "双线449服",
                    "ip": "10.104.59.101",
                    "gtype": "game",
                    "pf_name": "ywqq",
                    "gameserverid": "530288"
                }, {
                    "srv_id": "ywqq_513",
                    "srv_name": "双线513服",
                    "ip": "10.104.94.133",
                    "gtype": "game",
                    "pf_name": "ywqq",
                    "gameserverid": "530291"
                }, {
                    "srv_id": "ywqq_577",
                    "srv_name": "双线577服",
                    "ip": "10.104.102.19",
                    "gtype": "game",
                    "pf_name": "ywqq",
                    "gameserverid": "530292"
                }, {
                    "srv_id": "ywqq_641",
                    "srv_name": "双线641服",
                    "ip": "10.104.67.144",
                    "gtype": "game",
                    "pf_name": "ywqq",
                    "gameserverid": "530298"
                }, {
                    "srv_id": "ywqq_705",
                    "srv_name": "双线705服",
                    "ip": "10.104.35.121",
                    "gtype": "game",
                    "pf_name": "ywqq",
                    "gameserverid": "547257"
                }, {
                    "srv_id": "ywqq_713",
                    "srv_name": "双线713服",
                    "ip": "10.104.54.215",
                    "gtype": "game",
                    "pf_name": "ywqq",
                    "gameserverid": "548267"
                }, {
                    "srv_id": "ywqq_717",
                    "srv_name": "双线717服",
                    "ip": "10.104.94.129",
                    "gtype": "game",
                    "pf_name": "ywqq",
                    "gameserverid": "548704"
                }, {
                    "srv_id": "ywqq_721",
                    "srv_name": "双线721服",
                    "ip": "10.104.54.215",
                    "gtype": "game",
                    "pf_name": "ywqq",
                    "gameserverid": "551561"
                }, {
                    "srv_id": "ywqq_723",
                    "srv_name": "双线723服",
                    "ip": "10.104.59.100",
                    "gtype": "game",
                    "pf_name": "ywqq",
                    "gameserverid": "551747"
                }, {
                    "srv_id": "ywqq_725",
                    "srv_name": "双线725服",
                    "ip": "10.104.26.154",
                    "gtype": "game",
                    "pf_name": "ywqq",
                    "gameserverid": "552019"
                }, {
                    "srv_id": "ywqq_727",
                    "srv_name": "双线727服",
                    "ip": "10.251.60.9",
                    "gtype": "game",
                    "pf_name": "ywqq",
                    "gameserverid": "552187"
                }, {
                    "srv_id": "ywqq_728",
                    "srv_name": "双线728服",
                    "ip": "10.104.59.101",
                    "gtype": "game",
                    "pf_name": "ywqq",
                    "gameserverid": "552268"
                }, {
                    "srv_id": "ywqq_729",
                    "srv_name": "双线729服",
                    "ip": "10.251.60.9",
                    "gtype": "game",
                    "pf_name": "ywqq",
                    "gameserverid": "552422"
                }, {
                    "srv_id": "ywqq_730",
                    "srv_name": "双线730服",
                    "ip": "10.104.59.100",
                    "gtype": "game",
                    "pf_name": "ywqq",
                    "gameserverid": "552508"
                }, {
                    "srv_id": "ywqq_731",
                    "srv_name": "双线731服",
                    "ip": "10.104.67.143",
                    "gtype": "game",
                    "pf_name": "ywqq",
                    "gameserverid": "552626"
                }, {
                    "srv_id": "ywqq_732",
                    "srv_name": "双线732服",
                    "ip": "10.104.59.101",
                    "gtype": "game",
                    "pf_name": "ywqq",
                    "gameserverid": "552640"
                }, {
                    "srv_id": "ywqq_733",
                    "srv_name": "双线733服",
                    "ip": "10.104.94.129",
                    "gtype": "game",
                    "pf_name": "ywqq",
                    "gameserverid": "552720"
                }, {
                    "srv_id": "ywqq_734",
                    "srv_name": "双线734服",
                    "ip": "10.104.54.215",
                    "gtype": "game",
                    "pf_name": "ywqq",
                    "gameserverid": "552844"
                }, {
                    "srv_id": "ywqq_735",
                    "srv_name": "双线735服",
                    "ip": "10.104.67.144",
                    "gtype": "game",
                    "pf_name": "ywqq",
                    "gameserverid": "552910"
                }, {
                    "srv_id": "kuwo_1",
                    "srv_name": "双线1服",
                    "ip": "10.25.136.96",
                    "gtype": "game",
                    "pf_name": "kuwo",
                    "gameserverid": "530681"
                }, {
                    "srv_id": "ledu_1",
                    "srv_name": "双线1服",
                    "ip": "10.25.136.77",
                    "gtype": "game",
                    "pf_name": "ledu",
                    "gameserverid": "530524"
                }, {
                    "srv_id": "lmqq_1",
                    "srv_name": "双线1服",
                    "ip": "10.104.67.144",
                    "gtype": "game",
                    "pf_name": "lmqq",
                    "gameserverid": "530314"
                }, {
                    "srv_id": "lmqq_65",
                    "srv_name": "双线65服",
                    "ip": "10.104.35.121",
                    "gtype": "game",
                    "pf_name": "lmqq",
                    "gameserverid": "530315"
                }, {
                    "srv_id": "yilewan_1",
                    "srv_name": "双线1服",
                    "ip": "10.25.136.94",
                    "gtype": "game",
                    "pf_name": "yilewan",
                    "gameserverid": "530665"
                }, {
                    "srv_id": "9377n_1",
                    "srv_name": "双线1服",
                    "ip": "10.25.136.76",
                    "gtype": "game",
                    "pf_name": "9377n",
                    "gameserverid": "530682"
                }, {
                    "srv_id": "kugou_1",
                    "srv_name": "双线1服",
                    "ip": "10.25.136.93",
                    "gtype": "game",
                    "pf_name": "kugou",
                    "gameserverid": "530633"
                }, {
                    "srv_id": "501wan_1",
                    "srv_name": "双线1服",
                    "ip": "10.25.136.97",
                    "gtype": "game",
                    "pf_name": "501wan",
                    "gameserverid": "530534"
                }, {
                    "srv_id": "501wan_158",
                    "srv_name": "双线158服",
                    "ip": "10.25.136.98",
                    "gtype": "game",
                    "pf_name": "501wan",
                    "gameserverid": "551825"
                }, {
                    "srv_id": "501wan_160",
                    "srv_name": "双线160服",
                    "ip": "10.25.136.77",
                    "gtype": "game",
                    "pf_name": "501wan",
                    "gameserverid": "552421"
                }, {
                    "srv_id": "liebao_1",
                    "srv_name": "双线1服",
                    "ip": "10.25.136.91",
                    "gtype": "game",
                    "pf_name": "liebao",
                    "gameserverid": "530576"
                }, {
                    "srv_id": "liebao_180",
                    "srv_name": "双线180服",
                    "ip": "10.25.136.77",
                    "gtype": "game",
                    "pf_name": "liebao",
                    "gameserverid": "530437"
                }, {
                    "srv_id": "liebao_305",
                    "srv_name": "双线305服",
                    "ip": "10.25.136.98",
                    "gtype": "game",
                    "pf_name": "liebao",
                    "gameserverid": "530579"
                }, {
                    "srv_id": "cross_center_37",
                    "srv_name": "cross_center_37",
                    "ip": "10.25.136.102",
                    "gtype": "cross_center",
                    "pf_name": "37",
                    "gameserverid": "530439"
                }, {
                    "srv_id": "cross_center_360",
                    "srv_name": "cross_center_360",
                    "ip": "10.25.136.102",
                    "gtype": "cross_center",
                    "pf_name": "360",
                    "gameserverid": "530371"
                }, {
                    "srv_id": "cross_center_2217",
                    "srv_name": "cross_center_2217",
                    "ip": "10.25.136.102",
                    "gtype": "cross_center",
                    "pf_name": "2217",
                    "gameserverid": "530539"
                }, {
                    "srv_id": "cross_center_2345",
                    "srv_name": "cross_center_2345",
                    "ip": "10.25.136.102",
                    "gtype": "cross_center",
                    "pf_name": "2345",
                    "gameserverid": "530597"
                }, {
                    "srv_id": "cross_center_4366",
                    "srv_name": "cross_center_4366",
                    "ip": "10.25.136.102",
                    "gtype": "cross_center",
                    "pf_name": "4366",
                    "gameserverid": "530661"
                }, {
                    "srv_id": "cross_center_afgame",
                    "srv_name": "cross_center_afgame",
                    "ip": "10.25.136.102",
                    "gtype": "cross_center",
                    "pf_name": "afgame",
                    "gameserverid": "530673"
                }, {
                    "srv_id": "cross_center_7k7k",
                    "srv_name": "cross_center_7k7k",
                    "ip": "10.25.136.102",
                    "gtype": "cross_center",
                    "pf_name": "7k7k",
                    "gameserverid": "530417"
                }, {
                    "srv_id": "cross_center_douyu",
                    "srv_name": "cross_center_douyu",
                    "ip": "10.25.136.102",
                    "gtype": "cross_center",
                    "pf_name": "douyu",
                    "gameserverid": "530549"
                }, {
                    "srv_id": "cross_center_sogou",
                    "srv_name": "cross_center_sogou",
                    "ip": "10.25.136.102",
                    "gtype": "cross_center",
                    "pf_name": "sogou",
                    "gameserverid": "530505"
                }, {
                    "srv_id": "cross_center_ufojoy",
                    "srv_name": "cross_center_ufojoy",
                    "ip": "10.25.136.102",
                    "gtype": "cross_center",
                    "pf_name": "ufojoy",
                    "gameserverid": "530634"
                }, {
                    "srv_id": "cross_center_yooxun",
                    "srv_name": "cross_center_yooxun",
                    "ip": "10.25.136.102",
                    "gtype": "cross_center",
                    "pf_name": "yooxun",
                    "gameserverid": "530708"
                }, {
                    "srv_id": "cross_center_swjoy",
                    "srv_name": "cross_center_swjoy",
                    "ip": "10.25.136.102",
                    "gtype": "cross_center",
                    "pf_name": "swjoy",
                    "gameserverid": "530493"
                }, {
                    "srv_id": "cross_center_99yx",
                    "srv_name": "cross_center_99yx",
                    "ip": "10.25.136.102",
                    "gtype": "cross_center",
                    "pf_name": "99yx",
                    "gameserverid": "530545"
                }, {
                    "srv_id": "cross_center_teeqee",
                    "srv_name": "cross_center_teeqee",
                    "ip": "10.25.136.102",
                    "gtype": "cross_center",
                    "pf_name": "teeqee",
                    "gameserverid": "530628"
                }, {
                    "srv_id": "cross_center_ywqq",
                    "srv_name": "cross_center_ywqq",
                    "ip": "10.104.144.82",
                    "gtype": "cross_center",
                    "pf_name": "ywqq",
                    "gameserverid": "530265"
                }, {
                    "srv_id": "cross_center_ledu",
                    "srv_name": "cross_center_ledu",
                    "ip": "10.25.136.102",
                    "gtype": "cross_center",
                    "pf_name": "ledu",
                    "gameserverid": "530522"
                }, {
                    "srv_id": "cross_center_kuwo",
                    "srv_name": "cross_center_kuwo",
                    "ip": "10.25.136.102",
                    "gtype": "cross_center",
                    "pf_name": "kuwo",
                    "gameserverid": "530506"
                }, {
                    "srv_id": "cross_center_lmqq",
                    "srv_name": "cross_center_lmqq",
                    "ip": "10.104.144.82",
                    "gtype": "cross_center",
                    "pf_name": "lmqq",
                    "gameserverid": "530312"
                }, {
                    "srv_id": "cross_center_yilewan",
                    "srv_name": "cross_center_yilewan",
                    "ip": "10.25.136.102",
                    "gtype": "cross_center",
                    "pf_name": "yilewan",
                    "gameserverid": "530668"
                }, {
                    "srv_id": "cross_center_9377n",
                    "srv_name": "cross_center_9377n",
                    "ip": "10.25.136.102",
                    "gtype": "cross_center",
                    "pf_name": "9377n",
                    "gameserverid": "530679"
                }, {
                    "srv_id": "cross_center_kugou",
                    "srv_name": "cross_center_kugou",
                    "ip": "10.25.136.102",
                    "gtype": "cross_center",
                    "pf_name": "kugou",
                    "gameserverid": "530469"
                }, {
                    "srv_id": "cross_center_501wan",
                    "srv_name": "cross_center_501wan",
                    "ip": "10.25.136.102",
                    "gtype": "cross_center",
                    "pf_name": "501wan",
                    "gameserverid": "530712"
                }, {
                    "srv_id": "cross_center_liebao",
                    "srv_name": "cross_center_liebao",
                    "ip": "10.25.136.102",
                    "gtype": "cross_center",
                    "pf_name": "liebao",
                    "gameserverid": "530574"
                }, {
                    "srv_id": "cross_37_1",
                    "srv_name": "cross_37_1",
                    "ip": "10.25.136.76",
                    "gtype": "cross",
                    "pf_name": "37",
                    "gameserverid": "530444"
                }, {
                    "srv_id": "cross_37_2",
                    "srv_name": "cross_37_2",
                    "ip": "10.25.136.77",
                    "gtype": "cross",
                    "pf_name": "37",
                    "gameserverid": "530440"
                }, {
                    "srv_id": "cross_360_4",
                    "srv_name": "cross_360_4",
                    "ip": "10.25.136.76",
                    "gtype": "cross",
                    "pf_name": "360",
                    "gameserverid": "530364"
                }, {
                    "srv_id": "cross_360_1",
                    "srv_name": "cross_360_1",
                    "ip": "10.25.136.94",
                    "gtype": "cross",
                    "pf_name": "360",
                    "gameserverid": "544235"
                }, {
                    "srv_id": "cross_360_2",
                    "srv_name": "cross_360_2",
                    "ip": "10.25.136.77",
                    "gtype": "cross",
                    "pf_name": "360",
                    "gameserverid": "545467"
                }, {
                    "srv_id": "cross_2217_3",
                    "srv_name": "cross_2217_3",
                    "ip": "10.25.136.94",
                    "gtype": "cross",
                    "pf_name": "2217",
                    "gameserverid": "537295"
                }, {
                    "srv_id": "cross_2345_1",
                    "srv_name": "cross_2345_1",
                    "ip": "10.25.136.102",
                    "gtype": "cross",
                    "pf_name": "2345",
                    "gameserverid": "530448"
                }, {
                    "srv_id": "cross_2345_2",
                    "srv_name": "cross_2345_2",
                    "ip": "10.25.136.97",
                    "gtype": "cross",
                    "pf_name": "2345",
                    "gameserverid": "530598"
                }, {
                    "srv_id": "cross_2345_3",
                    "srv_name": "cross_2345_3",
                    "ip": "10.25.136.98",
                    "gtype": "cross",
                    "pf_name": "2345",
                    "gameserverid": "530596"
                }, {
                    "srv_id": "cross_4366_1",
                    "srv_name": "cross_4366_1",
                    "ip": "10.25.136.96",
                    "gtype": "cross",
                    "pf_name": "4366",
                    "gameserverid": "530500"
                }, {
                    "srv_id": "cross_afgame_1",
                    "srv_name": "cross_afgame_1",
                    "ip": "10.25.136.76",
                    "gtype": "cross",
                    "pf_name": "afgame",
                    "gameserverid": "530672"
                }, {
                    "srv_id": "cross_7k7k_2",
                    "srv_name": "cross_7k7k_2",
                    "ip": "10.25.136.96",
                    "gtype": "cross",
                    "pf_name": "7k7k",
                    "gameserverid": "530547"
                }, {
                    "srv_id": "cross_douyu_2",
                    "srv_name": "cross_douyu_2",
                    "ip": "10.25.136.94",
                    "gtype": "cross",
                    "pf_name": "douyu",
                    "gameserverid": "530734"
                }, {
                    "srv_id": "cross_sogou_2",
                    "srv_name": "cross_sogou_2",
                    "ip": "10.25.136.98",
                    "gtype": "cross",
                    "pf_name": "sogou",
                    "gameserverid": "530399"
                }, {
                    "srv_id": "cross_sogou_1",
                    "srv_name": "cross_sogou_1",
                    "ip": "10.25.136.97",
                    "gtype": "cross",
                    "pf_name": "sogou",
                    "gameserverid": "530404"
                }, {
                    "srv_id": "cross_sogou_3",
                    "srv_name": "cross_sogou_3",
                    "ip": "10.25.136.96",
                    "gtype": "cross",
                    "pf_name": "sogou",
                    "gameserverid": "535958"
                }, {
                    "srv_id": "cross_yy_1",
                    "srv_name": "cross_yy_1",
                    "ip": "10.25.136.98",
                    "gtype": "cross",
                    "pf_name": "yy",
                    "gameserverid": "530323"
                }, {
                    "srv_id": "cross_yy_2",
                    "srv_name": "cross_yy_2",
                    "ip": "10.25.136.97",
                    "gtype": "cross",
                    "pf_name": "yy",
                    "gameserverid": "530327"
                }, {
                    "srv_id": "cross_yy_4",
                    "srv_name": "cross_yy_4",
                    "ip": "10.25.136.102",
                    "gtype": "cross",
                    "pf_name": "yy",
                    "gameserverid": "530320"
                }, {
                    "srv_id": "cross_yy_5",
                    "srv_name": "cross_yy_5",
                    "ip": "10.25.136.76",
                    "gtype": "cross",
                    "pf_name": "yy",
                    "gameserverid": "551912"
                }, {
                    "srv_id": "cross_ufojoy_2",
                    "srv_name": "cross_ufojoy_2",
                    "ip": "10.25.136.77",
                    "gtype": "cross",
                    "pf_name": "ufojoy",
                    "gameserverid": "530473"
                }, {
                    "srv_id": "cross_yooxun_2",
                    "srv_name": "cross_yooxun_2",
                    "ip": "10.25.136.93",
                    "gtype": "cross",
                    "pf_name": "yooxun",
                    "gameserverid": "530710"
                }, {
                    "srv_id": "cross_swjoy_2",
                    "srv_name": "cross_swjoy_2",
                    "ip": "10.25.136.93",
                    "gtype": "cross",
                    "pf_name": "swjoy",
                    "gameserverid": "530497"
                }, {
                    "srv_id": "cross_99yx_2",
                    "srv_name": "cross_99yx_2",
                    "ip": "10.25.136.77",
                    "gtype": "cross",
                    "pf_name": "99yx",
                    "gameserverid": "530728"
                }, {
                    "srv_id": "cross_teeqee_2",
                    "srv_name": "cross_teeqee_2",
                    "ip": "10.25.136.91",
                    "gtype": "cross",
                    "pf_name": "teeqee",
                    "gameserverid": "530472"
                }, {
                    "srv_id": "cross_ywqq_4",
                    "srv_name": "cross_ywqq_4",
                    "ip": "10.104.2.209",
                    "gtype": "cross",
                    "pf_name": "ywqq",
                    "gameserverid": "530269"
                }, {
                    "srv_id": "cross_ywqq_5",
                    "srv_name": "cross_ywqq_5",
                    "ip": "10.104.46.6",
                    "gtype": "cross",
                    "pf_name": "ywqq",
                    "gameserverid": "530267"
                }, {
                    "srv_id": "cross_ywqq_6",
                    "srv_name": "cross_ywqq_6",
                    "ip": "10.104.59.95",
                    "gtype": "cross",
                    "pf_name": "ywqq",
                    "gameserverid": "530268"
                }, {
                    "srv_id": "cross_ywqq_8",
                    "srv_name": "cross_ywqq_8",
                    "ip": "10.104.12.149",
                    "gtype": "cross",
                    "pf_name": "ywqq",
                    "gameserverid": "530270"
                }, {
                    "srv_id": "cross_ywqq_9",
                    "srv_name": "cross_ywqq_9",
                    "ip": "10.104.20.140",
                    "gtype": "cross",
                    "pf_name": "ywqq",
                    "gameserverid": "530271"
                }, {
                    "srv_id": "cross_ywqq_1",
                    "srv_name": "cross_ywqq_1",
                    "ip": "10.251.36.4",
                    "gtype": "cross",
                    "pf_name": "ywqq",
                    "gameserverid": "530266"
                }, {
                    "srv_id": "cross_ywqq_2",
                    "srv_name": "cross_ywqq_2",
                    "ip": "10.104.102.17",
                    "gtype": "cross",
                    "pf_name": "ywqq",
                    "gameserverid": "530264"
                }, {
                    "srv_id": "cross_ywqq_3",
                    "srv_name": "cross_ywqq_3",
                    "ip": "10.104.102.17",
                    "gtype": "cross",
                    "pf_name": "ywqq",
                    "gameserverid": "544236"
                }, {
                    "srv_id": "cross_ledu_3",
                    "srv_name": "cross_ledu_3",
                    "ip": "10.25.136.77",
                    "gtype": "cross",
                    "pf_name": "ledu",
                    "gameserverid": "537298"
                }, {
                    "srv_id": "cross_kuwo_2",
                    "srv_name": "cross_kuwo_2",
                    "ip": "10.25.136.91",
                    "gtype": "cross",
                    "pf_name": "kuwo",
                    "gameserverid": "530402"
                }, {
                    "srv_id": "cross_lmqq_1",
                    "srv_name": "cross_lmqq_1",
                    "ip": "10.104.49.5",
                    "gtype": "cross",
                    "pf_name": "lmqq",
                    "gameserverid": "530310"
                }, {
                    "srv_id": "cross_yilewan_2",
                    "srv_name": "cross_yilewan_2",
                    "ip": "10.25.136.93",
                    "gtype": "cross",
                    "pf_name": "yilewan",
                    "gameserverid": "530667"
                }, {
                    "srv_id": "cross_9377n_1",
                    "srv_name": "cross_9377n_1",
                    "ip": "10.25.136.91",
                    "gtype": "cross",
                    "pf_name": "9377n",
                    "gameserverid": "530678"
                }, {
                    "srv_id": "cross_kugou_1",
                    "srv_name": "cross_kugou_1",
                    "ip": "10.25.136.76",
                    "gtype": "cross",
                    "pf_name": "kugou",
                    "gameserverid": "530471"
                }, {
                    "srv_id": "cross_501wan_1",
                    "srv_name": "cross_501wan_1",
                    "ip": "10.25.136.93",
                    "gtype": "cross",
                    "pf_name": "501wan",
                    "gameserverid": "530713"
                }, {
                    "srv_id": "cross_liebao_1",
                    "srv_name": "cross_liebao_1",
                    "ip": "10.25.136.76",
                    "gtype": "cross",
                    "pf_name": "liebao",
                    "gameserverid": "530432"
                }, {
                    "srv_id": "cross_liebao_2",
                    "srv_name": "cross_liebao_2",
                    "ip": "10.25.136.77",
                    "gtype": "cross",
                    "pf_name": "liebao",
                    "gameserverid": "530570"
                }, {
                    "srv_id": "cross_center_allqqpf",
                    "srv_name": "cross_center_allqqpf",
                    "ip": "10.104.144.82",
                    "gtype": "cross_center_allpf",
                    "pf_name": "allqqpf",
                    "gameserverid": "530317"
                }, {
                    "srv_id": "cross_center_allpf",
                    "srv_name": "cross_center_allpf",
                    "ip": "10.25.136.102",
                    "gtype": "cross_center_allpf",
                    "pf_name": "allpf",
                    "gameserverid": "530741"
                }, {
                    "srv_id": "cross_allqqpf_1",
                    "srv_name": "cross_allqqpf_1",
                    "ip": "10.135.14.236",
                    "gtype": "cross_allpf",
                    "pf_name": "allqqpf",
                    "gameserverid": "530316"
                }, {
                    "srv_id": "cross_allqqpf_2",
                    "srv_name": "cross_allqqpf_2",
                    "ip": "10.251.60.8",
                    "gtype": "cross_allpf",
                    "pf_name": "allqqpf",
                    "gameserverid": "530318"
                }, {
                    "srv_id": "cross_allpf_1",
                    "srv_name": "cross_allpf_1",
                    "ip": "10.25.136.102",
                    "gtype": "cross_allpf",
                    "pf_name": "allpf",
                    "gameserverid": "530567"
                }, {
                    "srv_id": "cross_allpf_2",
                    "srv_name": "cross_allpf_2",
                    "ip": "10.25.136.102",
                    "gtype": "cross_allpf",
                    "pf_name": "allpf",
                    "gameserverid": "530744"
                }, {
                    "srv_id": "cross_allpf_3",
                    "srv_name": "cross_allpf_3",
                    "ip": "10.25.136.102",
                    "gtype": "cross_allpf",
                    "pf_name": "allpf",
                    "gameserverid": "530743"
                }],
                "on_new_server": False,
                "pair_code": "无",
                "order": "无",
                "uuid": str(test_uuid)
            }
            r = self.ssion.post(CMDB_URL + "/myworkflows/start_workflow/", json=post_data)
            if r.status_code == 200:
                result = r.json()
                if result['success']:
                    print(workflow_name + '-提交申请成功')
                else:
                    raise Exception(workflow_name + '-提交申请失败' + result['data'])
            else:
                raise Exception(workflow_name + '-提交申请失败' + str(r))
            """测试访问后端热更新申请审批页面"""
            obj = ServerHotUpdate.objects.last()
            wse = obj.workflows.filter(is_current=1)[0]
            wse_id = wse.id
            r = self.ssion.get(CMDB_URL + "/myworkflows/workflow_approve/?id=" + str(wse_id))
            if r.status_code == 200:
                print(workflow_name + '-审批页面访问成功')
            else:
                raise Exception(workflow_name + '-审批页面访问失败' + str(r))
            """测试后端热更新项目组长审批同意"""
            self.ssion.post(CMDB_URL + "/user_login/",
                            data={'username': 'test-后端负责人', 'password': '123123'})
            new_wse = obj.workflows.filter(is_current=1)[0]
            new_wse_id = new_wse.id
            accept_transition = new_wse.state.transition.filter(condition='同意')[0].id
            post_data = {
                "opinion": "同意",
                "transition": accept_transition,
                "wse": new_wse_id,
            }
            r = self.ssion.post(CMDB_URL + "/myworkflows/workflow_approve/", json=post_data)
            if r.status_code == 200:
                result = r.json()
                if result['success']:
                    print(workflow_name + '-项目组长-审批同意成功')
                else:
                    raise Exception(workflow_name + '-项目组长-审批同意失败' + result['data'])
            else:
                raise Exception(workflow_name + '-项目组长-审批同意失败' + str(r))
            """测试后端热更新运营审批同意"""
            self.ssion.post(CMDB_URL + "/user_login/",
                            data={'username': 'test-运营', 'password': '123123'})
            new_wse = obj.workflows.filter(is_current=1)[0]
            new_wse_id = new_wse.id
            accept_transition = new_wse.state.transition.filter(condition='同意')[0].id
            post_data = {
                "opinion": "同意",
                "transition": accept_transition,
                "wse": new_wse_id,
            }
            r = self.ssion.post(CMDB_URL + "/myworkflows/workflow_approve/", json=post_data)
            if r.status_code == 200:
                result = r.json()
                if result['success']:
                    print(workflow_name + '-运营-审批同意成功')
                else:
                    raise Exception(workflow_name + '-运营-审批同意失败' + result['data'])
            else:
                raise Exception(workflow_name + '-运营-审批同意失败' + str(r))
            """测试访问工单详情（我的申请或者工单汇总）"""
            r = self.ssion.get(CMDB_URL + "/myworkflows/myworkflow_history?id=" + str(new_wse_id))
            if r.status_code == 200:
                print(workflow_name + '-访问工单详情成功')
            else:
                raise Exception(workflow_name + '-访问工单详情失败' + str(r))

            self.msg = workflow_name + '测试通过'
        except Exception as e:
            self.success = False
            self.msg = str(e)
        finally:
            return self.success, self.msg


class VersionUpdateWorkflowV2Test(object):
    """新版版本更新单v2申请测试"""

    def __init__(self):
        self.success = True
        self.msg = 'ok'
        self.ssion = requests.session()
        data = {"username": "chenjiefeng", "password": "123123"}
        self.ssion.post(CMDB_URL + "/user_login/", data=data)

    def test_version_update_workflow(self):
        try:
            """测试填单页面"""
            workflow = Workflow.objects.get(pk=7)
            workflow_id = workflow.id
            workflow_name = workflow.name
            r = self.ssion.get(CMDB_URL + "/myworkflows/workflow_template/?workflow=" + str(workflow_id))
            if r.status_code == 200:
                print(workflow_name + '-填单页访问成功')
            else:
                raise Exception(workflow_name + '-填单页访问出现错误' + str(r))
            """测试根据项目获取地区列表"""
            r = self.ssion.post(CMDB_URL + "/myworkflows/list_area_name_by_project/", data={'project': '78'})
            if r.status_code == 200:
                results = r.json()
                if '大陆' in [r['text'] for r in results]:
                    print('-' + workflow_name + '-提交申请页-根据项目获取地区列表成功')
                else:
                    raise Exception('-' + workflow_name + '-提交申请页-根据项目获取地区列表数据有误')
            else:
                raise Exception('-' + workflow_name + '-提交申请页-根据项目获取地区列表失败' + str(r))
            """测试根据项目获取后端负责人列表"""
            r = self.ssion.post(CMDB_URL + "/myworkflows/list_project_group_user/",
                                data={'project': '23', 'project_group': '服务端技术组'})
            if r.status_code == 200:
                results = r.json()
                if 'test-后端负责人' in [r['text'] for r in results]:
                    print('-' + workflow_name + '-提交申请页-根据项目获取后端负责人列表成功')
                else:
                    raise Exception('-' + workflow_name + '-提交申请页-根据项目获取后端负责人列表数据有误')
            else:
                raise Exception('-' + workflow_name + '-提交申请页-根据项目获取后端负责人列表失败' + str(r))
            """测试根据项目获取前端负责人列表"""
            r = self.ssion.post(CMDB_URL + "/myworkflows/list_project_group_user/",
                                data={'project': '23', 'project_group': '客户端技术组'})
            if r.status_code == 200:
                results = r.json()
                if 'test-前端负责人' in [r['text'] for r in results]:
                    print('-' + workflow_name + '-提交申请页-根据项目获取前端负责人列表成功')
                else:
                    raise Exception('-' + workflow_name + '-提交申请页-根据项目获取前端负责人列表数据有误')
            else:
                raise Exception('-' + workflow_name + '-提交申请页-根据项目获取前端负责人列表失败' + str(r))
            """测试根据项目获取策划负责人列表"""
            r = self.ssion.post(CMDB_URL + "/myworkflows/list_project_group_user/",
                                data={'project': '23', 'project_group': '策划组'})
            if r.status_code == 200:
                results = r.json()
                if 'test-策划' in [r['text'] for r in results]:
                    print('-' + workflow_name + '-提交申请页-根据项目获取策划负责人列表成功')
                else:
                    raise Exception('-' + workflow_name + '-提交申请页-根据项目获取策划负责人列表数据有误')
            else:
                raise Exception('-' + workflow_name + '-提交申请页-根据项目获取策划负责人列表失败' + str(r))
            """测试根据项目获取测试负责人列表"""
            r = self.ssion.post(CMDB_URL + "/myworkflows/list_project_group_user/",
                                data={'project': '23', 'project_group': '测试组'})
            if r.status_code == 200:
                results = r.json()
                if 'test-测试' in [r['text'] for r in results]:
                    print('-' + workflow_name + '-提交申请页-根据项目获取测试负责人列表成功')
                else:
                    raise Exception('-' + workflow_name + '-提交申请页-根据项目获取测试负责人列表数据有误')
            else:
                raise Exception('-' + workflow_name + '-提交申请页-根据项目获取测试负责人列表失败' + str(r))
            """测试提交版本更新单申请"""
            client_charge_id = User.objects.get(username='test-前端负责人').id
            plan_charge_id = User.objects.get(username='test-策划').id
            server_charge_id = User.objects.get(username='test-后端负责人').id
            test_charge_id = User.objects.get(username='test-测试').id
            test_id = uuid.uuid1()
            new_edition = "1" if NEW_VERSION_UPDATE else "0"
            server_list = 'test'
            post_data = {
                "client_charge": client_charge_id,
                "content": "test",
                "end_time": "2019-04-19 12:00",
                "plan_charge": plan_charge_id,
                "project": "78",
                "area": "大陆",
                "server_charge": server_charge_id,
                "server_list": server_list,
                "start_time": "2019-04-19 12:00",
                "test_charge": test_charge_id,
                "title": "testversionupdate" + str(test_id),
                "workflow": "7",
                "new_edition": new_edition,
            }
            r = self.ssion.post(CMDB_URL + "/myworkflows/start_workflow/", json=post_data)
            if r.status_code == 200:
                result = r.json()
                if result['success']:
                    print(workflow_name + '-提交申请成功')
                else:
                    raise Exception(workflow_name + '-提交申请失败' + result['data'])
            else:
                raise Exception(workflow_name + '-提交申请失败' + str(r))
            """测试访问版本更新单申请审批页面"""
            obj = VersionUpdate.objects.last()
            wse = obj.workflows.filter(is_current=1)[0]
            wse_id = wse.id
            r = self.ssion.get(CMDB_URL + "/myworkflows/workflow_approve/?id=" + str(wse_id))
            if r.status_code == 200:
                print(workflow_name + '-审批页面访问成功')
            else:
                raise Exception(workflow_name + '-审批页面访问失败' + str(r))
            """测试版本更新单运维负责人审批同意"""
            self.ssion.post(CMDB_URL + "/user_login/",
                            data={'username': '梁保明', 'password': '123123'})
            accept_transition = wse.state.transition.filter(condition='同意')[0].id
            post_data = {
                "opinion": "同意",
                "transition": accept_transition,
                "wse": wse_id,
                "server_range": "include",
                "server_content": "chuangyu_777",
                "client_content": [
                    {"cdn_dir": "t1", "version": "", "client_type": "ios",
                     "cdn_root_url": "resjysybt.chuangyunet.com"},
                    {"cdn_dir": "t1", "version": "", "client_type": "android",
                     "cdn_root_url": "resjysybt.chuangyunet.com"}
                ],
                "on_new_server": False,
            }
            r = self.ssion.post(CMDB_URL + "/myworkflows/workflow_approve/", json=post_data)
            if r.status_code == 200:
                result = r.json()
                if result['success']:
                    print(workflow_name + '-运维负责人-审批同意成功')
                else:
                    raise Exception(workflow_name + '-运维负责人-审批同意失败' + result['data'])
            else:
                raise Exception(workflow_name + '-运维负责人-审批同意失败' + str(r))
            """测试版本更新单后端负责人审批同意"""
            self.ssion.post(CMDB_URL + "/user_login/",
                            data={'username': 'test-后端负责人', 'password': '123123'})
            new_wse = obj.workflows.filter(is_current=1)[0]
            new_wse_id = new_wse.id
            accept_transition = new_wse.state.transition.filter(condition='同意')[0].id
            post_data = {
                "opinion": "同意",
                "transition": accept_transition,
                "wse": new_wse_id,
                "server_version": "test",
                "server_attention": "test",
                "ask_reset": True,
                "server_erlang": "test",
            }
            r = self.ssion.post(CMDB_URL + "/myworkflows/workflow_approve/", json=post_data)
            if r.status_code == 200:
                result = r.json()
                if result['success']:
                    print(workflow_name + '-后端负责人-审批同意成功')
                else:
                    raise Exception(workflow_name + '-后端负责人-审批同意失败' + result['data'])
            else:
                raise Exception(workflow_name + '-后端负责人-审批同意失败' + str(r))
            """测试版本更新单前端负责人审批同意"""
            self.ssion.post(CMDB_URL + "/user_login/",
                            data={'username': 'test-前端负责人', 'password': '123123'})
            new_wse = obj.workflows.filter(is_current=1)[0]
            new_wse_id = new_wse.id
            accept_transition = new_wse.state.transition.filter(condition='同意')[0].id
            client_content = [{"cdn_dir": "t1", "version": "Iyougu_21035", "client_type": "ios",
                                          "cdn_root_url": "resjysybt.chuangyunet.com"},
                                         {"cdn_dir": "t1", "version": "Ayougu_21035", "client_type": "android",
                                          "cdn_root_url": "resjysybt.chuangyunet.com"}] if NEW_VERSION_UPDATE else ''
            post_data = {
                "opinion": "同意",
                "transition": accept_transition,
                "wse": new_wse_id,
                "client_version": "test",
                "client_attention": "test",
                "client_content": client_content,
            }
            r = self.ssion.post(CMDB_URL + "/myworkflows/workflow_approve/", json=post_data)
            if r.status_code == 200:
                result = r.json()
                if result['success']:
                    print(workflow_name + '-前端负责人-审批同意成功')
                else:
                    raise Exception(workflow_name + '-前端负责人-审批同意失败' + result['data'])
            else:
                raise Exception(workflow_name + '-前端负责人-审批同意失败' + str(r))
            """测试版本更新单策划负责人审批同意"""
            self.ssion.post(CMDB_URL + "/user_login/",
                            data={'username': 'test-策划', 'password': '123123'})
            new_wse = obj.workflows.filter(is_current=1)[0]
            new_wse_id = new_wse.id
            accept_transition = new_wse.state.transition.filter(condition='同意')[0].id
            post_data = {
                "opinion": "同意",
                "transition": accept_transition,
                "wse": new_wse_id,
            }
            r = self.ssion.post(CMDB_URL + "/myworkflows/workflow_approve/", json=post_data)
            if r.status_code == 200:
                result = r.json()
                if result['success']:
                    print(workflow_name + '-策划负责人-审批同意成功')
                else:
                    raise Exception(workflow_name + '-策划负责人-审批同意失败' + result['data'])
            else:
                raise Exception(workflow_name + '-策划负责人-审批同意失败' + str(r))
            """测试访问更换审批人页面"""
            self.ssion.post(CMDB_URL + "/user_login/", data={'username': 'chenjiefneg', 'password': '123123'})
            new_wse = obj.workflows.filter(is_current=1)[0]
            new_wse_id = new_wse.id
            r = self.ssion.get(CMDB_URL + "/myworkflows/change_approve/?id=" + str(new_wse_id))
            if r.status_code == 200:
                print(workflow_name + '-访问更换审批人页面成功')
            else:
                raise Exception(workflow_name + '-访问更换审批人页面失败' + str(r))
            """测试更换审批人"""
            self.ssion.post(CMDB_URL + "/user_login/", data={'username': 'chenjiefneg', 'password': '123123'})
            new_wse = obj.workflows.filter(is_current=1)[0]
            new_wse_id = new_wse.id
            post_data = {
                "change_approve": "150",
                "wse": new_wse_id,
            }
            r = self.ssion.post(CMDB_URL + "/myworkflows/change_approve/?id=", json=post_data)
            if r.status_code == 200:
                result = r.json()
                if result['success']:
                    print(workflow_name + '-更换审批人成功')
                else:
                    raise Exception(workflow_name + '-更换审批人失败' + result['data'])
            else:
                raise Exception(workflow_name + '-更换审批人失败' + str(r))
            """测试版本更新单测试负责人审批同意"""
            self.ssion.post(CMDB_URL + "/user_login/",
                            data={'username': 'chenzhijian', 'password': '123123'})
            new_wse = obj.workflows.filter(is_current=1)[0]
            new_wse_id = new_wse.id
            accept_transition = new_wse.state.transition.filter(condition='同意')[0].id
            post_data = {
                "opinion": "同意",
                "transition": accept_transition,
                "wse": new_wse_id,
            }
            r = self.ssion.post(CMDB_URL + "/myworkflows/workflow_approve/", json=post_data)
            if r.status_code == 200:
                result = r.json()
                if result['success']:
                    print(workflow_name + '-测试负责人-审批同意成功')
                else:
                    raise Exception(workflow_name + '-测试负责人-审批同意失败' + result['data'])
            else:
                raise Exception(workflow_name + '-测试负责人-审批同意失败' + str(r))
            """测试访问工单详情（我的申请或者工单汇总）"""
            r = self.ssion.get(CMDB_URL + "/myworkflows/myworkflow_history?id=" + str(new_wse_id))
            if r.status_code == 200:
                print(workflow_name + '-访问工单详情成功')
            else:
                raise Exception(workflow_name + '-访问工单详情失败' + str(r))

            self.msg = workflow_name + '测试通过'
        except Exception as e:
            self.success = False
            self.msg = str(e)
        finally:
            return self.success, self.msg


if __name__ == '__main__':
    if not PRODUCTION_ENV:
        """工单列表"""
        wlt = WorkflowListTest()
        result, msg = wlt.test_workflow_list()
        print(result, msg)
        for option in TEST_WORKFLOW_OPTION:
            if option == 1:
                """svn申请"""
                svnt = SVNWorkflowTest()
                result, msg = svnt.test_svn_workflow()
                print(result, msg)
            if option == 3:
                """服务器权限申请"""
                spt = ServerPermWorkflowTest()
                result, msg = spt.test_server_perm_workflow()
                print(result, msg)
            if option == 4:
                """电脑故障申报"""
                cft = ComputerFailWorkflowTest()
                result, msg = cft.test_computer_fail_workflow()
                print(result, msg)
            if option == 5:
                """wifi和网络问题申报"""
                wnt = WifiAndNetworkWorkflowTest()
                result, msg = wnt.test_wifi_and_network_workflow()
                print(result, msg)
            if option == 6:
                """电脑配件申请"""
                cpt = ComputerPartsWorkflowTest()
                result, msg = cpt.test_computer_parts_workflow()
                print(result, msg)
            if option == 10:
                """服务器申请测试"""
                mt = MachineWorkflowTest()
                result, msg = mt.test_machine_workflow()
                print(result, msg)
            if option == 13:
                """项目调整申请测试"""
                pat = ProjectAdjustWorkflowTest()
                result, msg = pat.test_project_adjust_workflow()
                print(result, msg)
            if option == 14:
                """数据库申请测试"""
                mt = MySQLWorkflowTest()
                result, msg = mt.test_mysql_workflow()
                print(result, msg)
            if option == 7:
                """版本更新但申请测试"""
                if NEW_VERSION_UPDATE:
                    vwt = VersionUpdateWorkflowV2Test()
                else:
                    vwt = VersionUpdateWorkflowTest()
                result, msg = vwt.test_version_update_workflow()
                print(result, msg)
            if option == 8:
                """前端热更新测试"""
                cwt = ClientHotUpdateTest()
                result, msg = cwt.test_client_hot_update()
                print(result, msg)
            if option == 9:
                """后端热更新测试"""
                swt = ServerHotUpdateTest()
                result, msg = swt.test_server_hot_update()
                print(result, msg)
