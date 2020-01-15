# -*- encoding: utf-8 -*-
"""
主要测试内容：
    模拟调用api接口
使用方法：
    1. 修改参数 TEST_OPTION
    2. 运行脚本 /data/code/cy_devops/bin/python3 /data/www/cmdb/api_user/tests.py
"""
import requests
import os
import django
import sys
from cmdb.settings import PRODUCTION_ENV

pathname = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, pathname)
sys.path.insert(0, os.path.abspath(os.path.join(pathname, '..')))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cmdb.settings")
django.setup()

CMDB_URL = 'http://127.0.0.1:8000/api_user/'
TOKEN = '431b65c0a00dfa00399a8e36c47f54ad5d3686d5'
"""
1. 测试:生成帐号-->确认入职  
2. 测试:生成帐号-->删除帐号
3. 测试获取角色分组信息
"""
TEST_OPTION = 1


class TEST_CMDB_API(object):
    """测试cmdb api类"""

    def __init__(self):
        self.token = TOKEN
        self.url = CMDB_URL

    def get_api(self, url, query_param='', token=TOKEN):
        """get请求"""
        res = requests.get(url + query_param, headers={'Authorization': 'token {}'.format(token)})
        return res

    def post_api(self, url, post_data, token=TOKEN):
        """post请求"""
        headers = {'Accept': 'application/json', 'Authorization': 'Token ' + token}
        post_data = post_data
        res = requests.post(url, data=post_data, headers=headers, timeout=60, verify=False)
        return res

    def test_user_add(self):
        """测试新增cmdb用户"""
        result = True
        api_name = '新增cmdb用户API-'
        msg = api_name + '接口调用成功'
        try:
            url = CMDB_URL + 'user_add/'
            post_data = {
                'username': 'test-运维',
                'first_name': 'test-yunwei',
                'position': 'test-运维',
                'department': '原力互娱/运维部/运维开发组',
                'gender': 1,
                'is_qq': 0,
                'is_email': 0,
                'is_wifi': 0,
            }
            res = self.post_api(url, post_data)
            if res.status_code == 200:
                r = res.json()
                if not r['success']:
                    msg = r['msg']
            else:
                raise Exception(res.status_code)
        except Exception as e:
            msg = api_name + '接口调用失败:' + str(e)
            result = False
        finally:
            return result, msg

    def test_user_confirm(self):
        """测试确认cmdb用户报到入职"""
        result = True
        api_name = '确认cmdb用户报到入职API-'
        msg = api_name + '接口调用成功'
        try:
            url = CMDB_URL + 'user_confirm/'
            post_data = {
                'first_name': 'test-yunwei',
            }
            res = self.post_api(url, post_data)
            if res.status_code == 200:
                r = res.json()
                if not r['success']:
                    msg = r['msg']
            else:
                raise Exception(res.status_code)
        except Exception as e:
            msg = api_name + '接口调用失败:' + str(e)
            result = False
        finally:
            return result, msg

    def test_user_delete(self):
        """测试删除cmdb用户"""
        result = True
        api_name = '删除cmdb用户API-'
        msg = api_name + '接口调用成功'
        try:
            url = CMDB_URL + 'user_delete/'
            post_data = {
                'first_name': 'test-yunwei',
            }
            res = self.post_api(url, post_data)
            if res.status_code == 200:
                r = res.json()
                if not r['success']:
                    msg = r['msg']
            else:
                raise Exception(res.status_code)
        except Exception as e:
            msg = api_name + '接口调用失败:' + str(e)
            result = False
        finally:
            return result, msg

    def test_get_role_info(self):
        """测试获取角色分组信息"""
        url = CMDB_URL + 'role_info'
        res = self.get_api(url=url, query_param='', token='c6e7724396561cfd9004718330fc8a6dcbaf6409')
        print(res)
        print(res.json())


if __name__ == '__main__':
    if not PRODUCTION_ENV:
        test = TEST_CMDB_API()
        if TEST_OPTION == 1:
            result, msg = test.test_user_add()
            print(result, msg)
            result, msg = test.test_user_confirm()
            print(result, msg)
            result, msg = test.test_user_delete()
            print(result, msg)
        if TEST_OPTION == 2:
            result, msg = test.test_user_add()
            print(result, msg)
            result, msg = test.test_user_delete()
            print(result, msg)
        if TEST_OPTION == 3:
            test.test_get_role_info()
