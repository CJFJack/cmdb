# -*- encoding: utf-8 -*-
"""
主要测试内容：
    模拟调用api接口
使用方法：
    1. 修改参数 TEST_OPTION 指定测试模块
    2. 运行脚本 /data/code/cy_devops/bin/python3 /data/www/cmdb/api/tests.py
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

from assets.models import Host

CMDB_URL = 'http://127.0.0.1:8000/api/'
TOKEN = 'c6e7724396561cfd9004718330fc8a6dcbaf6409'
"""
1: 主机回调接口
2: 区服回调接口
3. 版本更新计划接口
"""
TEST_OPTION = [2]


class TEST_CMDB_API(object):
    """测试cmdb api类"""

    def __init__(self):
        self.token = TOKEN
        self.url = CMDB_URL
        self.ip_random = ''
        self.srv_id = ''

    def get_api(self, url, query_param):
        """get请求"""
        msg = 'ok'
        success = True
        try:
            res = requests.get(url + query_param, headers={'Authorization': 'token {}'.format(self.token)})
            if res.status_code == 200:
                r = res.json()
                print(r.get('success', True))
                if r.get('resp', r.get('success')) not in (1, True):
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
                if r.get('resp', r.get('success')) not in (1, True):
                    raise Exception(r.get('reason', '') + r.get('msg', ''))
            else:
                raise Exception(res.status_code)
        except Exception as e:
            msg = str(e)
            success = False
        finally:
            return success, msg

    def test_host_list(self):
        """测试获取主机记录"""
        result = True
        api_name = '获取主机记录-'
        msg = api_name + '接口调用成功'
        try:
            url = CMDB_URL + 'Host.List/'
            host = Host.objects.first()
            post_data = {
                'keywords': {
                    "telecom_ip": host.telecom_ip
                }
            }
            success, reason = self.post_api(url, post_data)
            if not success:
                raise Exception(reason)
        except Exception as e:
            msg = api_name + '接口调用失败:' + str(e)
            result = False
        finally:
            return result, msg

    def test_host_create(self):
        """测试添加主机"""
        self.ip_random = '.'.join(
            [str(random.randint(0, 254)), str(random.randint(0, 254)), str(random.randint(0, 254)),
             str(random.randint(0, 254))])
        result = True
        api_name = '添加主机-' + self.ip_random + '-'
        msg = api_name + '接口调用成功'
        try:
            url = CMDB_URL + 'Host.Create/'
            my_uuid = uuid.uuid1()
            host_info = {
                'status': 0,
                'host_class': 0,
                'belongs_to_game_project': 'ssss',
                'belongs_to_room': '三生QQ云',
                'machine_type': 0,
                'belongs_to_business': 'game',
                'platform': 'ruike',
                'telecom_ip': self.ip_random,
                'internal_ip': self.ip_random,
                'system': 0,
                'is_internet': 0,
                'sshuser': 'root',
                'sshport': '22',
                'machine_model': 'pc',
                'cpu_num': 4,
                'cpu': 'xen',
                'ram': '16G',
                'disk': '200G',
                'host_comment': 'test',
                'host_identifier': str(my_uuid),
                'opsmanager': 'ssss-三生QQ云',
                'password': '123456',
                'area': '大陆',
            }
            success, reason = self.post_api(url, host_info)
            if not success:
                raise Exception(reason)
        except Exception as e:
            msg = api_name + '接口调用失败:' + str(e)
            result = False
        finally:
            return result, msg

    def test_host_modify(self):
        """测试修改主机"""
        result = True
        api_name = '修改主机-' + self.ip_random + '-'
        msg = api_name + '接口调用成功'
        try:
            url = CMDB_URL + 'Host.Modify/'
            old_host_info = {
                'telecom_ip': self.ip_random,
                # 'belongs_to_room': '三生QQ云',
                # 'belongs_to_game_project': 'ssss',
                # 'internal_ip': self.ip_random,
                # 'area': '大陆'
            }
            new_host_info = {
                'password': '654321',
                'opsmanager': '剑雨江湖-台湾中华电信',
                'area': '台湾'
            }
            payload = {'old_host_info': old_host_info, 'new_host_info': new_host_info}
            success, reason = self.post_api(url, payload)
            if not success:
                raise Exception(reason)
        except Exception as e:
            msg = api_name + '接口调用失败:' + str(e)
            result = False
        finally:
            return result, msg

    def test_lock_opsmanager(self):
        """测试运维管理机上锁"""
        result = True
        api_name = '运维管理机上锁-'
        msg = api_name + '接口调用成功'
        try:
            url = CMDB_URL + 'lockOpsManager?'
            query_param = 'project=ssss&area=大陆&status=1'
            success, reason = self.get_api(url, query_param)
            if not success:
                raise Exception(reason)
        except Exception as e:
            msg = api_name + '接口调用失败:' + str(e)
            result = False
        finally:
            return result, msg

    def test_unlock_opsmanager(self):
        """测试运维管理机上锁"""
        result = True
        api_name = '运维管理机解锁-'
        msg = api_name + '接口调用成功'
        try:
            url = CMDB_URL + 'unlockOpsManager?'
            query_param = 'project=ssss&area=大陆&status=1'
            success, reason = self.get_api(url, query_param)
            if not success:
                raise Exception(reason)
        except Exception as e:
            msg = api_name + '接口调用失败:' + str(e)
            result = False
        finally:
            return result, msg

    def test_add_user_host(self):
        """测试添加服务器权限"""
        result = True
        api_name = '添加服务器权限-'
        msg = api_name + '接口调用成功'
        try:
            url = CMDB_URL + 'addUserHost?'
            query_param = 'username=chenjiefeng&host=snqxz_boke_210.61.161.63&temporary=0&is_root=0'
            success, reason = self.get_api(url, query_param)
            if not success:
                raise Exception(reason)
        except Exception as e:
            msg = api_name + '接口调用失败:' + str(e)
            result = False
        finally:
            return result, msg

    def test_delete_user_host(self):
        """测试删除服务器权限"""
        result = True
        api_name = '删除服务器权限-'
        msg = api_name + '接口调用成功'
        try:
            url = CMDB_URL + 'delUserHost?'
            query_param = 'username=chenjiefeng&host=snqxz_boke_210.61.161.63'
            success, reason = self.get_api(url, query_param)
            if not success:
                raise Exception(reason)
        except Exception as e:
            msg = api_name + '接口调用失败:' + str(e)
            result = False
        finally:
            return result, msg

    def test_host_initialize_callback(self):
        """测试主机初始化结果"""
        result = True
        api_name = '主机初始化结果回调-'
        msg = api_name + '接口调用成功'
        try:
            url = CMDB_URL + 'HostInitializeCallback/'
            post_data = {
                'minion_ip': '11.22.33.44',
                'type': 1,      # 1: 安装salt-minion结果回调，   2: 主机初始化结果回调
                'result': True,
                'msg': '安装成功',
            }
            success, reason = self.post_api(url, json.dumps(post_data))
            if not success:
                raise Exception(reason)
        except Exception as e:
            msg = api_name + '接口调用失败:' + str(e)
            result = False
        finally:
            return result, msg

    def test_list_game_servers(self):
        """测试获取区服列表"""
        result = True
        api_name = '获取区服列表-'
        msg = api_name + '接口调用成功'
        try:
            url = CMDB_URL + 'gameservers?'
            query_param = 'project=jyjh&area_name=大陆'
            success, reason = self.get_api(url, query_param)
            if not success:
                raise Exception(reason)
        except Exception as e:
            msg = api_name + '接口调用失败:' + str(e)
            result = False
        finally:
            return result, msg

    def test_new_server_callback(self):
        """测试新区服回调"""
        result = True
        self.srv_id = str(random.randint(10, 99)) + '_' + str(random.randint(100, 999))
        api_name = '新区服回调-' + self.srv_id + '-'
        msg = api_name + '接口调用成功'
        try:
            url = CMDB_URL + 'newSrvCallBack?'
            query_param = 'project_type=1&game=snqxz&game_type=1&pf_name=37&srv_id=' + self.srv_id + '&srv_name=双线1服&ip=172.16.149.11&client_version=0001311&server_version=1937133&cdn_root_url=res.qxz.zhi-ming.com&cdn_dir=qq_s1&room=QQ云&host=snqxz_boke_210.61.161.63&open_time=1381419600&area_name=大陆&sid=391001'
            success, reason = self.get_api(url, query_param)
            if not success:
                raise Exception(reason)
        except Exception as e:
            msg = api_name + '接口调用失败:' + str(e)
            result = False
        finally:
            return result, msg

    def test_update_gameserver_client_param(self):
        """测试更新区服前端版本号"""
        result = True
        api_name = '更新区服前端版本号-'
        msg = api_name + '接口调用成功'
        try:
            url = CMDB_URL + 'updateClientPara?'
            query_param = 'game=jyjh&client_ver=a_new_version34&cdn_root_url=jyjh.cdn.gop.yyclouds.com&cdn_dir=s1&area_name=大陆'
            success, reason = self.get_api(url, query_param)
            if not success:
                raise Exception(reason)
        except Exception as e:
            msg = api_name + '接口调用失败:' + str(e)
            result = False
        finally:
            return result, msg

    def test_update_gameserver_server_param(self):
        """测试更新区服后端版本号"""
        result = True
        api_name = '更新区服后端版本号-'
        msg = api_name + '接口调用成功'
        try:
            url = CMDB_URL + 'updateSrvPara?'
            query_param = 'game=jyjh&pf_select_type=include&pf_list=lmqq&server_ver=002server&area_name=大陆'
            success, reason = self.get_api(url, query_param)
            if not success:
                raise Exception(reason)
        except Exception as e:
            msg = api_name + '接口调用失败:' + str(e)
            result = False
        finally:
            return result, msg

    def test_del_gameserver(self):
        """测试删除区服"""
        result = True
        api_name = '删除区服-' + self.srv_id + '-'
        msg = api_name + '接口调用成功'
        try:
            url = CMDB_URL + 'delSrvRelateInfo?'
            query_param = 'game=snqxz&srv_id=' + self.srv_id + '&area_name=大陆'
            success, reason = self.get_api(url, query_param)
            if not success:
                raise Exception(reason)
        except Exception as e:
            msg = api_name + '接口调用失败:' + str(e)
            result = False
        finally:
            return result, msg

    def test_modify_gameserver(self):
        """测试修改区服"""
        result = True
        api_name = '修改区服-' + self.srv_id + '-'
        msg = api_name + '接口调用成功'
        try:
            url = CMDB_URL + 'modifySrvRelateInfo?'
            query_param = 'game=snqxz&pf_name=lmqq1&srv_id=' + self.srv_id + '&area_name=大陆&cdn_root_url=cdn.jyjh.yaowan.com&cdn_dir=qq_r2&&client_version=0001client'
            success, reason = self.get_api(url, query_param)
            if not success:
                raise Exception(reason)
        except Exception as e:
            msg = api_name + '接口调用失败:' + str(e)
            result = False
        finally:
            return result, msg

    def test_batch_modify_gameserver_cdn(self):
        """测试批量修改区服cdn目录"""
        result = True
        api_name = '批量修改区服cdn目录-' + self.srv_id + '-'
        msg = api_name + '接口调用成功'
        try:
            url = CMDB_URL + 'batchModifyCdn?'
            query_param = 'game=snqxz&area_name=大陆&srv_list=' + self.srv_id + '&new_cdn_root_url=cdn7.jyjh.yaowan.com&new_cdn_dir=qq_r1&client_version=new_client_version'
            success, reason = self.get_api(url, query_param)
            if not success:
                raise Exception(reason)
        except Exception as e:
            msg = api_name + '接口调用失败:' + str(e)
            result = False
        finally:
            return result, msg

    def test_merge_callback(self):
        """测试合服回调"""
        result = True
        api_name = '合服回调-' + self.srv_id + '-'
        msg = api_name + '接口调用成功'
        try:
            url = CMDB_URL + 'mergeSrvCallBack?'
            query_param = 'game=snqxz&merge_id=44_142&merge_time=1502790997&srv_id=' + self.srv_id + '&area_name=大陆'
            success, reason = self.get_api(url, query_param)
            if not success:
                raise Exception(reason)
        except Exception as e:
            msg = api_name + '接口调用失败:' + str(e)
            result = False
        finally:
            return result, msg

    def test_batch_modify_gameserver_status(self):
        """测试批量修改区服状态"""
        result = True
        api_name = '批量修改区服状态-'
        msg = api_name + '接口调用成功'
        try:
            url = CMDB_URL + 'BatchModifyGameServerStatus/'
            post_data = {'area_name': '大陆',
                         'project': 'snqxz',
                         'status_dict': {'44_142': 1, '64_238': 5},
                         }
            success, reason = self.post_api(url, post_data)
            if not success:
                raise Exception(reason)
        except Exception as e:
            msg = api_name + '接口调用失败:' + str(e)
            result = False
        finally:
            return result, msg

    def test_version_update_plan(self):
        """测试版本更新计划接口"""
        result = True
        api_name = '版本更新计划-'
        msg = api_name + '接口调用成功'
        try:
            url = CMDB_URL + 'VersionUpdatePlan/'
            post_data = {'update_date': '2019-10-23'}
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
                """主机测试"""
                result, msg = test.test_host_list()
                print(result, msg)
                result, msg = test.test_host_create()
                print(result, msg)
                result, msg = test.test_host_modify()
                print(result, msg)
                result, msg = test.test_lock_opsmanager()
                print(result, msg)
                result, msg = test.test_unlock_opsmanager()
                print(result, msg)
                result, msg = test.test_add_user_host()
                print(result, msg)
                result, msg = test.test_delete_user_host()
                print(result, msg)
                result, msg = test.test_host_initialize_callback()
                print(result, msg)
            if option == 2:
                """区服测试"""
                result, msg = test.test_list_game_servers()
                print(result, msg)
                result, msg = test.test_new_server_callback()
                print(result, msg)
                result, msg = test.test_update_gameserver_client_param()
                print(result, msg)
                result, msg = test.test_update_gameserver_server_param()
                print(result, msg)
                result, msg = test.test_modify_gameserver()
                print(result, msg)
                result, msg = test.test_batch_modify_gameserver_cdn()
                print(result, msg)
                result, msg = test.test_merge_callback()
                print(result, msg)
                result, msg = test.test_new_server_callback()
                print(result, msg)
                result, msg = test.test_batch_modify_gameserver_status()
                print(result, msg)
                result, msg = test.test_del_gameserver()
                print(result, msg)
            if option == 3:
                """版本更新计划"""
                result, msg = test.test_version_update_plan()
                print(result, msg)
