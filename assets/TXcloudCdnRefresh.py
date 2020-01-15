import requests
import sys
import json
import hashlib
import time
import base64
import hmac
import random


class Qcloud(object):
    """腾讯云CDN接口认证类"""
    def __init__(self, config, Id, key):
        self.config = config
        self.url = 'https://cdn.api.qcloud.com/v2/index.php'
        self.id = Id
        self.Key = key

    def Auth(self):
        data = {}
        Singna = []
        Random = range(100000)
        number = random.choice(Random)
        data['SecretId'] = self.id
        data['Nonce'] = number
        data['Timestamp'] = int(time.time())
        data = dict(data, **self.config)
        base = sorted(data.items(), key=lambda data: data[0])
        for i in base:
            Singna.append(str(i[0]) + '=' + str(i[1]) + '&')  # end='')
            result = 'POSTcdn.api.qcloud.com/v2/index.php?' + ''.join(Singna).rstrip('&')
        self.Key = self.Key.encode(encoding='utf-8')
        result = result.encode(encoding='utf-8')
        uri = hmac.new(self.Key, result, digestmod=hashlib.sha1).digest()
        key = base64.b64encode(uri)
        data['Signature'] = key
        return data


def QcloudCdnRefresh(type, obj, secret_id, secret_key):
    """腾讯云CDN刷新"""
    try:
        config = {'detail': '1'}
        if type == 'url':
            action = 'RefreshCdnUrl'
            for x in range(len(obj)):
                key = 'urls.' + str(x)
                config[key] = obj[x]
        elif type == 'dir':
            action = 'RefreshCdnDir'
            for x in range(len(obj)):
                key = 'dirs.' + str(x)
                config[key] = obj[x]
        else:
            raise Exception("刷新类型只能是 url 或 dir")
        config['Action'] = action
        qcloud = Qcloud(config, secret_id, secret_key)
        data = qcloud.Auth()
        res = requests.post(qcloud.url, data=data)
        if res.status_code == 200:
            r = res.json()
            if r['code'] == 0:
                task_id = r['data']['task_id']
                return {'success': True, 'task_id': task_id}
            else:
                raise Exception(r['message'])
        else:
            raise Exception(str(res))

    except Exception as e:
        return {'success': False, 'msg': str(e)}


def QcloudRefreshResultQuery(task_id, secret_id, secret_key):
    """查询腾讯云CDN刷新结果"""
    try:
        config = {'Action': 'GetCdnRefreshLog', 'detail': '1', 'taskId': task_id}
        qcloud = Qcloud(config, secret_id, secret_key)
        data = qcloud.Auth()
        res = requests.post(qcloud.url, data=data, timeout=60, verify=False)
        if res.status_code == 200:
            r = res.json()
            if r['code'] == 0:
                status = r['data']['logs'][0]['status']
                if status == 1:
                    msg = '刷新成功'
                    return {'success': True, 'msg': msg}
                else:
                    raise Exception('刷新中')
            else:
                raise Exception(r['message'])
        else:
            raise Exception(str(res))

    except Exception as e:
        return {'success': False, 'msg': str(e)}


def QcloudRefreshResultQueryByTime(startDate, endDate, secret_id, secret_key):
    """根据时间范围查询腾讯云CDN刷新结果"""
    try:
        config = {'Action': 'GetCdnRefreshLog', 'detail': '1', 'startDate': startDate, 'endDate': endDate}
        qcloud = Qcloud(config, secret_id, secret_key)
        data = qcloud.Auth()
        res = requests.post(qcloud.url, data=data, timeout=60, verify=False)
        if res.status_code == 200:
            r = res.json()
            # print(r)
            if r['code'] == 0:
                logs = r['data']['logs']
                return {'success': True, 'msg': logs}
            else:
                raise Exception(r['message'])
        else:
            raise Exception(str(res))

    except Exception as e:
        return {'success': False, 'msg': str(e)}


if __name__ == '__main__':
    secret_id = 'HKSDFdasfgahawxASHgfoNSdlfnlsfsdf'
    secret_key = 'asdfaewghwhw3arhawgswdfexx'
    startDate = '2019-01-29'
    endDate = '2019-01-29'
    # res = QcloudCdnRefresh('url', 'http://res.snsy.chuangyunet.com/c1/1.txt', secret_id, secret_key)
    # if res['success']:
    #     task_id = res['task_id']
    #     print(task_id)
    #     print(QcloudRefreshResultQuery(task_id, secret_id, secret_key))
    # else:
    #     print(res['msg'])

    # print(QcloudRefreshResultQuery("1547708229653589981", secret_id, secret_key))
    print(QcloudRefreshResultQueryByTime(startDate, endDate, secret_id, secret_key))
