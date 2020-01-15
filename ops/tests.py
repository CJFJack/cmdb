# -*- encoding: utf-8 -*-
"""
主要测试内容：
    模拟修改开服时间计划/项目下架计划/合服计划等
    web --> cmdb --> 运维管理机 --> cmdb
使用方法：
    1. 修改TEST_OPTION参数
    2. 运行脚本 /data/code/cy_devops/bin/python3 /data/www/cmdb/ops/tests.py
"""
import requests
import os
import django
import uuid
import sys
import json
import time
import random
from cmdb.settings import PRODUCTION_ENV

pathname = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, pathname)
sys.path.insert(0, os.path.abspath(os.path.join(pathname, '..')))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cmdb.settings")
django.setup()

WEB_CMDB_URL = 'http://127.0.0.1:8000/api_web/'
OPS_CMDB_URL = 'http://127.0.0.1:8000/api/'
CMDB_URL = 'http://127.0.0.1:8000/api/'
WEB_CMDB_TOKEN = '431b65c0a00dfa00399a8e36c47f54ad5d3686d5'
OPS_CMDB_TOKEN = 'c6e7724396561cfd9004718330fc8a6dcbaf6409'
"""
1. 修改开服时间计划
2. 项目下架计划
3. 区服管理回调测试
4. 单个区服迁服回调测试
5. web新增cmdb合服计划
6. web新增cmdb开服计划
"""
TEST_OPTION = [2]

from ops.models import ModifyOpenSrvSchedule
from ops.models import GameServerOff


def get_api(url, query_param, token):
    """get请求"""
    msg = 'ok'
    success = True
    try:
        res = requests.get(url + query_param, headers={'Authorization': 'token {}'.format(token)})
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


def post_api(url, token, **kwargs):
    """post请求"""
    msg = 'ok'
    success = True
    try:
        headers = {'Accept': 'application/json', 'Authorization': 'Token ' + token}
        data = kwargs.get('data', None)
        json = kwargs.get('json', None)
        if data:
            res = requests.post(url, data=data, headers=headers, timeout=60, verify=False)
        elif json:
            res = requests.post(url, json=json, headers=headers, timeout=60, verify=False)
        else:
            raise Exception('缺少post参数')
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


def test_modsrv_opentime():
    """测试修改开服时间"""
    success = True
    msg = 'ok'
    try:
        """web调用cmdb接口"""
        url = WEB_CMDB_URL + 'ModifySrvOpenTimeSchedule.Create/'
        token = WEB_CMDB_TOKEN
        post_data = {
            "project": "cyh5s7",
            "area": "cn",
            "srv_id": "1600001",  # web区服id
            "open_time": "1581419600",
        }
        success, msg = post_api(url=url, token=token, data=post_data)
        if not success:
            raise Exception(msg)

        time.sleep(5)

        """运维管理机回调cmdb"""
        url = OPS_CMDB_URL + 'ModSrvOpenTimeCallBack/'
        token = OPS_CMDB_TOKEN
        modify_schedule = ModifyOpenSrvSchedule.objects.last()
        # modify_schedule = ModifyOpenSrvSchedule.objects.get(uuid='455a7512-75fa-11e9-95e4-000c29bedb81')
        for task in modify_schedule.modifyopensrvscheduledetail_set.all():
            post_data = {
                "uuid": modify_schedule.uuid,
                "sid": task.game_server.sid,
                "result": True,
                "msg": "修改开服时间成功",
            }
            success, msg = post_api(url=url, token=token, json=post_data)
    except Exception as e:
        success = False
        msg = str(e)
    finally:
        return success, msg


def test_new_server_callback():
    """测试新区服回调"""
    result = True
    srv_id = str(random.randint(10, 99)) + '_' + str(random.randint(100, 999))
    sid = str(random.randint(10000, 99999))
    api_name = '新区服回调-' + srv_id + '-'
    msg = api_name + '接口调用成功'
    try:
        url = CMDB_URL + 'newSrvCallBack?'
        query_param = 'project_type=1&game=snqxz&game_type=1&pf_name=37&srv_id=' + srv_id + '&srv_name=双线1服&ip=172.16.149.11&client_version=0001311&server_version=1937133&cdn_root_url=res.qxz.zhi-ming.com&cdn_dir=qq_s1&room=QQ云&host=snqxz_boke_210.61.161.63&open_time=1381419600&area_name=大陆&sid=' + sid
        success, reason = get_api(url, query_param, OPS_CMDB_TOKEN)
        if not success:
            raise Exception(reason)
    except Exception as e:
        msg = api_name + '接口调用失败:' + str(e)
        result = False
    finally:
        return result, msg, sid


def test_gameserver_off():
    """测试项目下架计划"""
    success = True
    msg = 'ok'
    try:
        def create_and_send():
            """创建新区服模拟区服下架"""
            print('创建新区服模拟区服下架')
            result, msg, sid = test_new_server_callback()
            srv_list = []
            srv_list.append(int(sid))
            srv_id = str(srv_list)
            """web调用cmdb接口"""
            print('web调用cmdb接口')
            url = WEB_CMDB_URL + 'GameServerOff.Create/'
            token = WEB_CMDB_TOKEN
            post_data = {
                "project": "snqxz",
                "area": "cn",
                "srv_id": srv_id,  # web区服id
                "off_time": "1581419600",
                "web_callback_url": "https://xxxxxx/",
            }
            success, msg = post_api(url=url, token=token, data=post_data)
            if not success:
                raise Exception(msg)

        create_and_send()
        create_and_send()

        time.sleep(3)

        """运维管理机回调cmdb"""
        print('运维管理机回调cmdb')
        url = OPS_CMDB_URL + 'GameServerOffCallBack/'
        token = OPS_CMDB_TOKEN
        game_server_off = GameServerOff.objects.last()
        for task in game_server_off.gameserveroffdetail_set.all():
            post_data = {
                "uuid": game_server_off.uuid,
                "srv_id": task.game_server.sid,
                "result": False,
                "msg": "原因：未知",
            }
            success, msg = post_api(url=url, token=token, json=post_data)

        """删除下架假话"""
        print('删除下架假话')
        url = WEB_CMDB_URL + 'GameServerOff.Delete/'
        token = WEB_CMDB_TOKEN
        game_server_off = GameServerOff.objects.last()
        for task in game_server_off.gameserveroffdetail_set.all():
            post_data = {
                "project": "snqxz",
                "area": "cn",
                "srv_id": json.dumps([task.game_server.sid]),  # web区服id
                "off_time": "1581419600",
                "web_callback_url": "https://xxxxxx/",
            }
            success, msg = post_api(url=url, token=token, data=post_data)
    except Exception as e:
        success = False
        msg = str(e)
    finally:
        return success, msg


def test_game_server_action():
    """测试区服管理回调操作"""
    success = True
    msg = 'ok'
    try:
        url = OPS_CMDB_URL + 'GameServerActionCallback/'
        token = OPS_CMDB_TOKEN
        post_data = {
            "uuid": "54754358-8c2d-11e9-a3cb-000c292acc0b",
            "project": "jyjh",
            "srv_id": "cross_yy_4",
            "action_type": "start",
            "result": 1,
            "msg": "操作成功"
        }
        success, msg = post_api(url=url, token=token, json=post_data)
        if not success:
            raise Exception(msg)
    except Exception as e:
        msg = str(e)
        success = False
    finally:
        return success, msg


def test_migration_callback():
    """测试单个区服迁服回调"""
    success = True
    token = OPS_CMDB_TOKEN
    url = OPS_CMDB_URL + "HostMigrationCallBack/"
    sid = '500000000'
    post_data = {
        'uuid': 'a3dfa844-8cc2-11e9-89d5-000c292acc0b-migrate',
        "sid": sid,
        "result": True,
        "msg": "迁服成功",
    }
    success, msg = post_api(url=url, token=token, json=post_data)
    if not success:
        raise Exception(msg)
    return success, '测试迁服回调'


def test_game_srv_merge_create():
    """测试创建合服计划"""
    success = True
    msg = 'ok'
    try:
        url = WEB_CMDB_URL + 'GameServerMerge.Create/'
        token = WEB_CMDB_TOKEN
        post_data = {
            'data': json.dumps([
                {"main_srv": "2100001", "slave_srv": "300778", "group_id": "130",
                 "merge_time": 1568099875, "project": "snqxz"},
            ]),
        }
        success, msg = post_api(url=url, token=token, data=post_data)
        if not success:
            raise Exception(msg)
    except Exception as e:
        msg = str(e)
        success = False
    finally:
        return success, msg


def test_install_srv_create():
    """测试装服计划"""
    success = True
    msg = 'ok'
    try:
        url = WEB_CMDB_URL + 'InstallGameServer.Create/'
        token = WEB_CMDB_TOKEN
        post_data = [
            {
                "project": "ssss", "area": "大陆", "pf_id": "178",
                "pf_name": "178pop", "srv_num": "256", "srv_name": "双线一服",
                "server_version": "xxxx", "client_version": "xxxx", "client_dir": "xxxx", "open_time": "1531447135",
                "status": "0", "qq_srv_id": "100", "unique_srv_id": "132161841", "srv_type": "1", "srv_farm_id": "0",
                "srv_farm_name": "default"
            },
            {
                "project": "csxy", "area": "大陆", "pf_id": "70",
                "pf_name": "xinghuiorg", "srv_num": "1000", "srv_name": "测试一服",
                "server_version": "xxxx", "client_version": "xxxx", "client_dir": "xxxx", "open_time": "1531447135",
                "status": "0", "qq_srv_id": "100", "unique_srv_id": "984111364", "srv_type": "1", "srv_farm_id": "0",
                "srv_farm_name": "default2"
            }
        ]
        success, msg = post_api(url=url, token=token, json=json.dumps(post_data))
        if not success:
            raise Exception(msg)
    except Exception as e:
        msg = str(e)
        success = False
    finally:
        return success, msg


if __name__ == '__main__':
    if not PRODUCTION_ENV:
        for option in TEST_OPTION:
            if option == 1:
                print(test_modsrv_opentime())
            if option == 2:
                print(test_gameserver_off())
            if option == 3:
                print(test_game_server_action())
            if option == 4:
                print(test_migration_callback())
            if option == 5:
                print(test_game_srv_merge_create())
            if option == 6:
                print(test_install_srv_create())
