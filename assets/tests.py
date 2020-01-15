# -*- encoding: utf-8 -*-
"""
主要测试内容：
1. 前端关键页面访问
2. 前端对后端请求数据接口的异步调用
3. 后端生成主机迁服回收申请单
使用方法：
1. 修改参数 CMDB_URL 指定cmdb测试地址
2. 通过修改 TEST_OPTION 参数指定测试模块
3. 运行脚本 /data/code/cy_devops/bin/python3 /data/www/cmdb/assets/tests.py
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
from myworkflows.models import HostCompressionApply

CMDB_URL = 'http://127.0.0.1:8000'
TOKEN = 'c6e7724396561cfd9004718330fc8a6dcbaf6409'
"""
1: 测试主机迁服回收申请流程
"""
TEST_OPTION = [1]


class HostMigrateRecoverTest(object):
    """测试主机迁服回收申请"""

    def __init__(self):
        self.success = True
        self.ssion = requests.session()
        data = {"username": "chenjiefeng", "password": "123123"}
        self.ssion.post(CMDB_URL + "/user_login/", data=data)
        self.uuid = ''

    def test_host_usage_page(self):
        """测试主机使用率页面"""
        r = self.ssion.get(CMDB_URL + "/assets/host_usage/")
        if r.status_code == 200:
            return self.success, '主机使用率页面-访问成功'
        else:
            self.success = False
            return self.success, '主机使用率页面-访问出现错误' + str(r)

    def test_list_game_project(self):
        """测试列出游戏项目"""
        r = self.ssion.post(CMDB_URL + "/myworkflows/list_game_project/")
        if r.status_code == 200:
            return self.success, '列出游戏项目-成功'
        else:
            self.success = False
            return self.success, '列出游戏项目-出现错误' + str(r)

    def test_list_room_name_by_project(self):
        """测试根据项目列出机房"""
        post_data = {
            'project': "24",
        }
        r = self.ssion.post(CMDB_URL + "/myworkflows/list_room_name_by_project/", data=post_data)
        if r.status_code == 200:
            return self.success, '根据项目列出机房-成功'
        else:
            self.success = False
            return self.success, '根据项目列出机房-出现错误' + str(r)

    def test_data_host_usage(self):
        """测试获取主机使用率数据"""
        post_data = {
            'id_project': 23,
            'id_room': '剑雨页游腾讯云',
        }
        r = self.ssion.post(CMDB_URL + "/assets/data_host_usage/", json=post_data)
        if r.status_code == 200:
            return self.success, '获取主机使用率数据-成功'
        else:
            self.success = False
            return self.success, '获取主机使用率数据-出现错误' + str(r)

    def test_download_host_usage(self):
        """测试导出主机使用率数据"""
        post_data = {
            'id_project': 23,
            'id_room': '剑雨页游腾讯云',
        }
        r = self.ssion.post(CMDB_URL + "/assets/host_usage_downloads/", json=post_data)
        if r.status_code == 200:
            result = r.json()
            if result['success']:
                return self.success, '导出主机使用率数据-成功'
            else:
                raise Exception('导出主机使用率数据-出现错误-' + result['msg'])
        else:
            self.success = False
            return self.success, '导出主机使用率数据-出现错误' + str(r)

    def test_host_recover_migration_apply_page(self):
        """测试主机迁服回收申请页面"""
        r = self.ssion.get(CMDB_URL + "/assets/host_recover_migration_apply/")
        if r.status_code == 200:
            return self.success, '主机迁服回收申请页面-访问成功'
        else:
            self.success = False
            return self.success, '主机迁服回收申请页面-出现错误' + str(r)

    def test_commit_host_compression_apply(self):
        """测试提交迁服回收申请"""
        my_uuid = uuid.uuid1()
        self.uuid = str(my_uuid)
        post_data = {
            "action_deadline": "2019-05-09 12:00",
            "action_time": "2019-05-08 12:00",
            "ip": "118.126.105.125\n118.126.97.249",
            "ops_id": "1155",
            "project": "29",
            "recover_deadline": "2019-05-17 12:00",
            "recover_time": "2019-05-15 12:00",
            "room": "大陆-少年手游腾讯云",
            "title": self.uuid,
            "type": "2",
            "uuid": self.uuid,
        }
        r = self.ssion.post(CMDB_URL + "/myworkflows/host_compression_apply/", json=post_data)
        if r.status_code == 200:
            result = r.json()
            if result['success']:
                return self.success, '提交迁服回收申请-成功'
            else:
                raise Exception('提交迁服回收申请-出现错误-' + result['msg'])
        else:
            self.success = False
            return self.success, '提交迁服回收申请-出现错误' + str(r)

    def test_host_compression_apply_list_page(self):
        """测试主机迁服回收列表页面"""
        r = self.ssion.get(CMDB_URL + "/myworkflows/host_compression_apply_list/")
        if r.status_code == 200:
            return self.success, '主机迁服回收列表页面-访问成功'
        else:
            self.success = False
            return self.success, '主机迁服回收列表页面-出现错误' + str(r)

    def test_host_compression_apply_detail_page(self):
        """测试主机迁服回收详情页面"""
        apply = HostCompressionApply.objects.get(uuid=self.uuid)
        r = self.ssion.get(CMDB_URL + "/myworkflows/host_compression_apply_detail/" + str(apply.id) + "/")
        if r.status_code == 200:
            return self.success, '主机迁服回收详情页面-访问成功'
        else:
            self.success = False
            return self.success, '主机迁服回收详情页面-出现错误' + str(r)

    def test_host_compression_apply_log_page(self):
        """测试主机迁服回收日志页面"""
        apply = HostCompressionApply.objects.get(uuid=self.uuid)
        r = self.ssion.get(CMDB_URL + "/myworkflows/host_compression_cmdb_log/" + str(apply.id) + "/")
        if r.status_code == 200:
            return self.success, '主机迁服回收日志页面-访问成功'
        else:
            self.success = False
            return self.success, '主机迁服回收日志页面-出现错误' + str(r)

    def test_edit_host_compression_apply(self):
        """测试修改迁服回收申请"""
        apply = HostCompressionApply.objects.get(uuid=self.uuid)
        post_data = {
            "action_deadline": "2019-05-10 12:00",
            "action_status": "3",
            "action_time": "2019-05-09 12:00",
            "apply_id": apply.id,
            "ops": "1155",
            "recover_deadline": "2019-05-31 12:00",
            "recover_status": "3",
            "recover_time": "2019-05-16 12:00",
        }
        r = self.ssion.post(CMDB_URL + "/myworkflows/edit_host_compression_apply/", json=post_data)
        if r.status_code == 200:
            result = r.json()
            if result['success']:
                return self.success, '修改迁服回收申请-成功'
            else:
                raise Exception('修改迁服回收申请-出现错误-' + result['msg'])
        else:
            self.success = False
            return self.success, '提交迁服回收申请-出现错误' + str(r)

    def test_migration_callback(self):
        """测试迁服回调"""
        headers = {'Accept': 'application/json', 'Authorization': 'Token ' + TOKEN}
        apply = HostCompressionApply.objects.get(uuid=self.uuid)
        # apply = HostCompressionApply.objects.get(uuid='39e586ca-80f1-11e9-9b0b-000c29bedb81')
        for detail in apply.hostcompressiondetail_set.all():
            for x in detail.hostmigratesrvdetail_set.all():
                sid = x.sid
                post_data = {
                    'uuid': apply.uuid,
                    "sid": sid,
                    "result": True,
                    "msg": "迁服成功",
                }
                r = self.ssion.post(CMDB_URL + "/api/HostMigrationCallBack/", json=post_data, headers=headers, timeout=60, verify=False)
                if r.status_code == 200:
                    print(self.success, '测试迁服回调-区服sid: {}迁服成功'.format(sid))
                else:
                    self.success = False
                    print(self.success, '测试迁服回调-区服sid: {}迁服失败'.format(sid) + str(r))
        return self.success, '测试迁服回调'

    def test_recover_callback(self):
        """测试回收回调"""
        headers = {'Accept': 'application/json', 'Authorization': 'Token ' + TOKEN}
        apply = HostCompressionApply.objects.get(uuid=self.uuid)
        # apply = HostCompressionApply.objects.get(uuid='39e586ca-80f1-11e9-9b0b-000c29bedb81')
        for detail in apply.hostcompressiondetail_set.all():
            ip = detail.ip
            post_data = {
                'uuid': apply.uuid,
                "ip": ip,
                "result": True,
                "msg": "回收失败",
            }
            r = self.ssion.post(CMDB_URL + "/api/HostRecoverCallBack/", json=post_data, headers=headers, timeout=60, verify=False)
            if r.status_code == 200:
                print(self.success, '测试回收回调-主机: {}回收成功'.format(ip))
            else:
                self.success = False
                print(self.success, '测试回收回调-主机: {}回收失败'.format(ip) + str(r))

        return self.success, '测试迁服回调'


if __name__ == '__main__':
    if not PRODUCTION_ENV:
        """主机迁服回收申请"""
        hmr = HostMigrateRecoverTest()
        for option in TEST_OPTION:
            if option == 1:
                result, msg = hmr.test_host_usage_page()
                print(result, msg)
                result, msg = hmr.test_list_game_project()
                print(result, msg)
                result, msg = hmr.test_list_room_name_by_project()
                print(result, msg)
                result, msg = hmr.test_data_host_usage()
                print(result, msg)
                result, msg = hmr.test_download_host_usage()
                print(result, msg)
                result, msg = hmr.test_host_recover_migration_apply_page()
                print(result, msg)
                result, msg = hmr.test_commit_host_compression_apply()
                print(result, msg)
                result, msg = hmr.test_host_compression_apply_detail_page()
                print(result, msg)
                result, msg = hmr.test_host_compression_apply_log_page()
                print(result, msg)
                # result, msg = hmr.test_edit_host_compression_apply()
                # print(result, msg)
                result, msg = hmr.test_migration_callback()
                print(result, msg)
                result, msg = hmr.test_recover_callback()
                print(result, msg)
