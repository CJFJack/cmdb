# -*- encoding: utf-8 -*-
"""
主要测试内容：
    模拟调用api接口
使用方法：
    1. 修改参数 TEST_OPTION 指定测试模块
    2. 运行脚本 /data/code/cy_devops/bin/python3 /data/www/cmdb/api_web/tests.py
"""
import requests
import os
import django
import uuid
import sys
import json
import random
from cmdb.settings import PRODUCTION_ENV

pathname = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, pathname)
sys.path.insert(0, os.path.abspath(os.path.join(pathname, '..')))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cmdb.settings")
django.setup()

CMDB_URL = 'http://127.0.0.1:8000/api_web/'
TOKEN = '431b65c0a00dfa00399a8e36c47f54ad5d3686d5'
"""
1: 区服下线计划
2: 修改开服时间
3. 接收web挂维护信息
"""
TEST_OPTION = (3,)


class TEST_CMDB_API(object):
    """测试cmdb api类"""

    def __init__(self):
        self.token = TOKEN
        self.url = CMDB_URL

    def get_api(self, url, query_param):
        """get请求"""
        msg = 'ok'
        success = True
        try:
            res = requests.get(url + query_param, headers={'Authorization': 'token {}'.format(self.token)})
            if res.status_code == 200:
                r = res.json()
                print(r)
                if r.get('resp', 1) != 1 or not r.get('success', True):
                    raise Exception(r.get('reason', '') + r.get('msg', ''))
            else:
                raise Exception(res.status_code)
        except Exception as e:
            msg = str(e)
            success = False
        finally:
            return success, msg

    def post_api(self, url, post_data, token=TOKEN):
        """post请求"""
        msg = 'ok'
        success = True
        try:
            headers = {'Accept': 'application/json', 'Authorization': 'Token ' + token}
            post_data = post_data
            res = requests.post(url, data=post_data, headers=headers, timeout=60, verify=False)
            if res.status_code == 200:
                r = res.json()
                print(r)
                if r.get('resp', 1) != 1 or not r.get('success', True):
                    raise Exception(r.get('reason', '') + r.get('msg', ''))
            else:
                raise Exception(res.status_code)
        except Exception as e:
            msg = str(e)
            success = False
        finally:
            return success, msg

    def test_gameserveroff_create(self):
        """测试游戏区服下线新增计划"""
        result = True
        api_name = '游戏区服下线新增计划-'
        msg = api_name + '接口调用成功'
        try:
            url = CMDB_URL + 'GameServerOff.Create/'
            post_data = {
                "project": "ssss",
                "area": "cn",
                "srv_id": '["5800001", "2100000023"]',  # web区服id
                "off_time": "1381419601",
                "web_callback_url": "https://xxxxxx/",
            }
            success, reason = self.post_api(url, post_data)
            if not success:
                raise Exception(reason)
        except Exception as e:
            msg = api_name + '接口调用失败:' + str(e)
            result = False
        finally:
            return result, msg

    def test_gameserveroff_delete(self):
        """测试游戏区服下线删除计划"""
        result = True
        api_name = '游戏区服下线删除计划-'
        msg = api_name + '接口调用成功'
        try:
            url = CMDB_URL + 'GameServerOff.Delete/'
            post_data = {
                "project": "ssss",
                "area": "cn",
                "srv_id": '["5800001", "2100000023"]',  # web区服id
                "off_time": "1381419601",
                "web_callback_url": "https://xxxxxx/",
            }
            success, reason = self.post_api(url, post_data)
            if not success:
                raise Exception(reason)
        except Exception as e:
            msg = api_name + '接口调用失败:' + str(e)
            result = False
        finally:
            return result, msg

    def test_modify_srv_opentime_schedule_create(self):
        """测试游戏区服下线新增计划"""
        result = True
        api_name = '修改开服时间新增计划-'
        msg = api_name + '接口调用成功'
        try:
            url = CMDB_URL + 'ModifySrvOpenTimeSchedule.Create/'
            post_data = {
                "project": "cyh5s7",
                "area": "cn",
                "srv_id": "1600001",  # web区服id
                "open_time": "1581419600",
            }
            success, reason = self.post_api(url, post_data)
            if not success:
                raise Exception(reason)
        except Exception as e:
            msg = api_name + '接口调用失败:' + str(e)
            result = False
        finally:
            return result, msg

    def test_version_update_maintenance(self):
        """测试接收版本更新挂维护信息"""
        result = True
        api_name = '接收版本更新挂维护信息-'
        msg = api_name + '接口调用成功'
        try:
            url = CMDB_URL + 'RecvWebMaintenanceInfo/'
            post_data = {
                "project": "cyh5s7",
                "area": "cn",
                "maintenance_type": "3",
            }
            success, reason = self.post_api(url, post_data)
            if not success:
                raise Exception(reason)
        except Exception as e:
            msg = api_name + '接口调用失败:' + str(e)
            result = False
        finally:
            return result, msg


if __name__ == '__main__':
    if not PRODUCTION_ENV:
        test = TEST_CMDB_API()
        for option in TEST_OPTION:
            if option == 1:
                """区服下线计划测试"""
                result, msg = test.test_gameserveroff_create()
                print(result, msg)
                result, msg = test.test_gameserveroff_delete()
                print(result, msg)
            elif option == 2:
                """修改开服时间计划测试"""
                result, msg = test.test_modify_srv_opentime_schedule_create()
                print(result, msg)
            elif option == 3:
                """接收版本更新挂维护信息"""
                result, msg = test.test_version_update_maintenance()
                print(result, msg)
            else:
                print('未知的测试类型')
