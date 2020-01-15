# -*- encoding: utf-8 -*-
"""
主要测试内容：
    模拟调用api接口
使用方法：
    1. 运行脚本 /data/code/cy_devops/bin/python3 /data/www/cmdb/api_mysql/tests.py
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

CMDB_URL = 'http://127.0.0.1:8000/api_mysql/'
TOKEN = 'c6e7724396561cfd9004718330fc8a6dcbaf6409'


class TestMysqlApi(object):
    """测试mysql api类"""

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
            res = requests.post(url, json=post_data, headers=headers, timeout=60, verify=False)
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

    def test_mysql_create(self):
        pdata = {
            "project": 'snsy',
            "area": '大陆',
            "purpose": '测试',
            "host": "192.168.56.101",
            "port": '3307',
            "user": 'mysql',
            "password": 'mypassword',
            "white_list": ['192.168.56.101', '192.168.100.181'],
        }
        url = CMDB_URL + 'Instance.Create/'
        print(self.post_api(url, json.dumps(pdata)))

    def test_mysql_modify(self):
        old_instance = {'host': '192.168.56.101', 'port': 3307}
        new_instance = {
            'user': 'root2', 'area': 'hk', 'password': 'redhat',
        }
        payload = {'old_instance': old_instance, 'new_instance': new_instance}
        url = CMDB_URL + 'Instance.Modify/'
        print(self.post_api(url, json.dumps(payload)))

    def test_mysql_list(self):
        pdata = {
            "host": "192.168.56.101",
        }
        url = CMDB_URL + 'Instance.List/'
        print(self.post_api(url, json.dumps(pdata)))

    def test_mysql_delete(self):
        pdata = {
            "host": "192.168.56.101",
            "port": '3307',
        }
        url = CMDB_URL + 'Instance.Delete/'
        print(self.post_api(url, json.dumps(pdata)))


if __name__ == '__main__':
    if not PRODUCTION_ENV:
        test = TestMysqlApi()
        test.test_mysql_create()
        test.test_mysql_modify()
        test.test_mysql_list()
        test.test_mysql_delete()
