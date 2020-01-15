# -*- encoding: utf-8 -*-

"""外部的脚本，通过读取redis中
的cmdb:log的key记录，来更新日志文件到
前端页面中
"""

import time
import json
import logging
import traceback
from concurrent import futures

import redis

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cmdb.settings")


import django
django.setup()

from cmdb.settings import REDIS_HOST
from cmdb.settings import REDIS_PORT
from cmdb.settings import REDIS_PASSWORD

# from cmdb import asgi

from channels import Channel

redis_client = redis.Redis(
    host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, db=2, charset="utf-8", decode_responses=True)


# cl = asgi.get_channel_layer()

# 默认的过期时间是十分钟
DEFAULT_INTERVAL = 60 * 5

MAX_WORKER = 15

# 默认读取的log文件最后20行
NUMBER_LINES = 20


class LoopLog(object):
    """记录工单流程的log"""

    def __init__(self):
        # create logger
        self.logger = logging.getLogger('looplog')
        self.logger.setLevel(logging.DEBUG)

        if not self.logger.handlers:

            # create file handler and set level to debug
            fh = logging.FileHandler('/var/log/looplog.log', 'a', encoding='UTF-8')
            fh.setLevel(logging.DEBUG)

            # create formatter
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

            # add formatter
            fh.setFormatter(formatter)

            # add fh to logger
            self.logger.addHandler(fh)


looplog = LoopLog()


def tail_file(filename, nlines):
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


def yield_cmdb_log(reply_channel_name, uuid, row, heartbeat):
    """使用生成器获取从row
    开始的log的内容
    """
    filename = '/var/log/nginx/access.log'

    # position = tail_file(filename, NUMBER_LINES)

    with open(filename) as fp:
        fp.seek(row)
        for line in iter(fp.readline, ''):
            Channel(reply_channel_name).send({'text': line}, immediately=True)
        else:
            row = fp.tell()

    # 更新reply_channel_name记录的行数
    reply_channel_name_dic = {'uuid': uuid, 'row': row, 'heartbeat': heartbeat}
    name = 'cmdb:log'
    redis_client.hset(name, reply_channel_name, json.dumps(reply_channel_name_dic))

    # print('thread: %s end process' % (reply_channel_name))
    looplog.logger.info('thread: %s end process' % (reply_channel_name))

    return None


def main():
    name = 'cmdb:log'
    # all_cmdb_log_reply_channels = [x for x in redis_client.hgetall(name)]

    while True:
        duplicate_reply_channels_name = []
        to_do_map = {}
        with futures.ThreadPoolExecutor(max_workers=MAX_WORKER) as executor:
            looplog.logger.info('*** starting a new round thread ***')
            for reply_channel_name, reply_channel_info in redis_client.hgetall(name).items():
                reply_channel_info = json.loads(reply_channel_info)
                uuid = reply_channel_info.get('uuid')
                row = reply_channel_info.get('row')
                heartbeat = reply_channel_info.get('heartbeat')
                current_time = int(time.time())
                if current_time - heartbeat > DEFAULT_INTERVAL:
                    duplicate_reply_channels_name.append(reply_channel_name)
                else:
                    looplog.logger.info('Scheduled thread %s' % (reply_channel_name))
                    future = executor.submit(yield_cmdb_log, reply_channel_name, uuid, row, heartbeat)
                    to_do_map[future] = reply_channel_name

            looplog.logger.info('Current to_do_map list is %s' % (to_do_map))

            done_iter = futures.as_completed(to_do_map)

            for future in done_iter:
                try:
                    future.result()
                except Exception as exc:
                    print('------ find Exception -------', to_do_map[future])
                    traceback.print_exc()

            # 删除过期的
            for rc in duplicate_reply_channels_name:
                # 主动断开ws连接，这样，正常的连接会通过
                # 浏览器重新自动连接
                # 如果是异常断开的无效的reply_channel
                # 还是需要从redis中删除
                # 调用send({"close": True})会调用disconnect
                # 也就会删除redis里面的reply_channel
                Channel(rc).send({"close": True})
                redis_client.hdel(name, rc)

        # 休眠一秒钟
        time.sleep(1)


if __name__ == "__main__":
    main()
