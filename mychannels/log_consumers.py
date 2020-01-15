# -*- encoding: utf-8 -*-
"""实时log的ws
"""

import json
import time
import os

import redis

from cmdb.settings import REDIS_HOST
from cmdb.settings import REDIS_PORT
from cmdb.settings import REDIS_PASSWORD

redis_client = redis.Redis(
    host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, db=2, charset="utf-8", decode_responses=True)


def log_connect(message):
    # Work out room name from path (ignore slashes)
    # Accept the connection request
    message.reply_channel.send({"accept": True})


def log_receive(message):
    # ASGI WebSocket packet-received and send-packet message types
    # both have a "text" key for their textual data.
    """将初始的行数，reply_channel_name, uuid存放在redis的name
    为'cmdb:log'的key中，以便daemon脚本能遍历
    {
        "cmdb:log": {
            'reply_channel_name1': "{'uuid': 'uuid1', 'row': 0}",    # 后面为json
            'reply_channel_name2': "{'uuid': 'uuid2', 'row': 0}",
            'reply_channel_name3': "{'uuid': 'uuid3', 'row': 0}",
        }
    }
    """

    reply_channel_name = message.reply_channel

    name = 'cmdb:log'
    row = 0    # 初始化的读取文件的行数
    uuid = 'xxx'
    heartbeat = int(time.time())  # 心跳时间戳，过期的可以删除

    reply_channel_name_dic = {'uuid': uuid, 'row': row, 'heartbeat': heartbeat}

    redis_client.hset(name, reply_channel_name, json.dumps(reply_channel_name_dic))
    message.reply_channel.send({"text": '成功建立连接\n'})


def log_disconnect(message):
    name = 'cmdb:log'
    redis_client.hdel(name, message.reply_channel)
    message.reply_channel.send({"close": True})


def hotupdate_cmdb_log_connect(message, uuid):
    # Work out room name from path (ignore slashes)
    # Accept the connection request
    message.reply_channel.send({"accept": True})


def tail_file(filename, nlines=20):
    with open(filename, encoding="ISO-8859-1") as qfile:
        qfile.seek(0, os.SEEK_END)
        endf = position = qfile.tell()
        linecnt = 0
        while position >= 1:
            qfile.seek(position)
            next_char = qfile.read(1)
            if next_char == "\n" and position != endf - 1:
                linecnt += 1

            if linecnt == nlines:
                break
            position -= 1

    return position


def hotupdate_cmdb_log_receive(message, uuid):
    # ASGI WebSocket packet-received and send-packet message types
    # both have a "text" key for their textual data.
    """将初始的行数，reply_channel_name, uuid存放在redis的name
    为'cmdb:log'的key中，以便daemon脚本能遍历
    {
        "cmdb:log": {
            'reply_channel_name1': "{'uuid': 'uuid1', 'row': 0}",    # 后面为json
            'reply_channel_name2': "{'uuid': 'uuid2', 'row': 0}",
            'reply_channel_name3': "{'uuid': 'uuid3', 'row': 0}",
        }
    }
    """

    reply_channel_name = message.reply_channel

    name = 'hotupdate:cmdb:log'
    filename = os.path.join('/var/log/cmdb_hotupdate/', uuid)
    row = tail_file(filename, nlines=20)
    # row = 0    # 初始化的读取文件的行数
    heartbeat = int(time.time())  # 心跳时间戳，过期的可以删除

    reply_channel_name_dic = {'uuid': uuid, 'row': row, 'heartbeat': heartbeat}

    redis_client.hset(name, reply_channel_name, json.dumps(reply_channel_name_dic))
    message.reply_channel.send({"text": '成功建立连接\n'})


def hotupdate_cmdb_log_disconnect(message, uuid):
    name = 'hotupdate:cmdb:log'
    redis_client.hdel(name, message.reply_channel)
    message.reply_channel.send({"close": True})
