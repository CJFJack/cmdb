# -*- encoding: utf-8 -*-

"""使用redis
"""

import redis

import json

from cmdb.logs import HotUpdateLog

from cmdb.settings import REDIS_HOST
from cmdb.settings import REDIS_PORT
from cmdb.settings import REDIS_PASSWORD

# hot_update_log = HotUpdateLog()


r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, db=1, charset="utf-8", decode_responses=True)


def load_to_redis(hot_server):
    """将后端热更新的区服列表
    加载到redis中
    数据格式: 将uuid#ip#srv_id作为唯一的组合key
    后面接上如下hset value:
    {'pf_name': 'yy', 'srv_name': 'S36', 'gtype': 'game'}
    {}
    """

    uuid = hot_server.uuid
    update_server_list = json.loads(hot_server.update_server_list)

    for server in update_server_list:
        uuid_ip_srv_id_key = uuid + '#' + server['ip'] + '#' + server['srv_id']
        gtype = server['gtype']
        pf_name = server['pf_name']
        srv_name = server['srv_name']
        ip = server['ip']
        srv_id = server['srv_id']
        r.hset(uuid_ip_srv_id_key, 'gtype', gtype)
        r.hset(uuid_ip_srv_id_key, 'pf_name', pf_name)
        r.hset(uuid_ip_srv_id_key, 'srv_name', srv_name)
        r.hset(uuid_ip_srv_id_key, 'ip', ip)
        r.hset(uuid_ip_srv_id_key, 'srv_id', srv_id)

        # 初始化的时候将更新结果数据全部为空
        r.hset(uuid_ip_srv_id_key, 'erl_data_data', "")
        r.hset(uuid_ip_srv_id_key, 'erl_data_status', "")
        r.hset(uuid_ip_srv_id_key, 'update_data_status', "")
        r.hset(uuid_ip_srv_id_key, 'update_data_data', "")

    # 记录总的更新条数和已经执行的
    # 已经执行的初始状态为0
    total = len(update_server_list)
    r.hset(uuid, 'total', total)
    r.hset(uuid, 'finished', 0)

    # 刚开始总是设置为没有出错的更新
    r.hset(uuid, 'is_all_good', True)


def update_server(uuid, ip, hot_server_type, update_data=None, erl_data=None):
    """更新redis里面的区服数据
    主要是更新update_data和erl_data

    管理机post过来的update_data格式:
    "update_data": {
        "qq_1": {"data": "更新失败,不执行erl命令", "status": False},
        "qq_2": {"data": "更新失败,不执行erl命令", "status": False},
    },

    erl_data的格式
    "erl_data": {
        "qq_1": {"data": "更新失败,不执行erl命令", "status": False},
        "qq_2": {"data": "更新失败,不执行erl命令", "status": False},
    },

    """

    hot_update_log = HotUpdateLog(uuid)

    if update_data:
        raw_finished = int(r.hgetall(uuid).get('finished'))
        hot_update_log.logger.info('hot_server: 原来的完成数目是%s' % (raw_finished))
        now_finished = raw_finished + len(update_data)
        r.hset(uuid, 'finished', now_finished)
        hot_update_log.logger.info('hot_server: 更新新的完成数目%s' % (now_finished))
        for srv_id, data_status in update_data.items():
            seaching_redis_key = uuid + '#' + ip + '#' + srv_id
            redis_value = r.hgetall(seaching_redis_key)
            if redis_value:
                if hot_server_type == '2':
                    # 只执行erl命令
                    pass
                else:
                    update_data_data = data_status.get("data", "")
                    update_data_status = data_status.get("status", False)
                    if update_data_status:
                        update_data_status = "成功"
                    else:
                        update_data_status = "失败"
                r.hset(seaching_redis_key, 'update_data_data', update_data_data)
                r.hset(seaching_redis_key, 'update_data_status', update_data_status)
                hot_update_log.logger.info('更新redis key %s update_data成功' % (seaching_redis_key))
            else:
                hot_update_log.logger.error('没有在redis中找到%s#%s#%s的key' % (uuid, ip, srv_id))

    if erl_data:
        raw_finished = int(r.hgetall(uuid).get('finished'))
        hot_update_log.logger.info('hot_server: 原来的完成数目是%s' % (raw_finished))
        now_finished = raw_finished + len(erl_data)
        r.hset(uuid, 'finished', now_finished)
        hot_update_log.logger.info('hot_server: 更新新的完成数目%s' % (now_finished))
        for srv_id, data_status in erl_data.items():
            seaching_redis_key = uuid + '#' + ip + '#' + srv_id
            redis_value = r.hgetall(seaching_redis_key)
            if redis_value:
                if hot_server_type == '0':
                    # 只热更
                    pass
                else:
                    erl_data_data = data_status.get("data", "")
                    erl_data_status = data_status.get("status", False)
                    if erl_data_status:
                        erl_data_status = "成功"
                    else:
                        erl_data_status = "失败"
                r.hset(seaching_redis_key, 'erl_data_data', erl_data_data)
                r.hset(seaching_redis_key, 'erl_data_status', erl_data_status)
                hot_update_log.logger.info('更新redis key %s update_data成功' % (seaching_redis_key))
            else:
                hot_update_log.logger.error('没有在redis中找到%s#%s#%s的key' % (uuid, ip, srv_id))


def get_uuid_related_value(uuid):
    """根据uuid来匹配redis中的key
    并且赋值后返回
    """

    related_key = uuid + '#*'

    update_server_list = []

    for key in r.scan_iter(related_key):
        update_server_list.append(r.hgetall(key))

    return update_server_list


def delete_uuid_related_value(uuid):
    """热更新完成以后，删除掉redis中的相关
    uuid的数据
    """

    related_key = uuid + '*'

    for key in r.scan_iter(related_key):
        r.delete(key)


def get_hot_server_process_from_redis(uuid):
    """从redis中获取更新进度
    """

    result = r.hgetall(uuid)

    return result
