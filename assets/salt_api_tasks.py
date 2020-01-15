# -*- encoding: utf-8 -*-

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import json

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
from cmdb.settings import SALT_MASTER_API
from cmdb.settings import SALT_API_USER
from cmdb.settings import SLAT_API_PASS
from requests.packages.urllib3.util import Retry
from requests.adapters import HTTPAdapter
from requests import Session

salt_api = SALT_MASTER_API


class SaltApi:
    """
    定义salt api接口的类
    初始化获得token
    """

    def __init__(self, url):
        self.url = url
        self.username = SALT_API_USER
        self.password = SLAT_API_PASS
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36",
            "Content-type": "application/json"
        }
        self.login_url = salt_api + "login"
        self.login_params = {'username': self.username, 'password': self.password, 'eauth': 'pam'}
        self.token = self.get_data(self.login_url, self.login_params)['token']
        self.headers['X-Auth-Token'] = self.token

    def get_data(self, url, params):
        send_data = json.dumps(params)
        s = Session()
        s.mount('https://', HTTPAdapter(max_retries=Retry(total=5, status_forcelist=[408])))
        request = s.post(url, data=send_data, headers=self.headers, verify=False)
        if request.status_code == 200:
            response = request.json()
            result = dict(response)
            return result['return'][0]
        else:
            return str(request.status_code)

    # 同步请求
    def salt_command(self, minion, method, arg=None, tgt_type='glob', **kwargs):
        if arg:
            params = {'client': 'local', 'fun': method, 'tgt': minion, 'arg': arg, 'tgt_type': tgt_type}
        else:
            params = {'client': 'local', 'fun': method, 'tgt': minion, 'tgt_type': tgt_type}
        params.update(kwargs)
        result = self.get_data(self.url, params)
        return result

    # 异步请求方法
    def salt_async_command(self, minion, method, arg=None, tgt_type='glob', **kwargs):
        if arg:
            params = {'client': 'local_async', 'fun': method, 'tgt': minion, 'arg': arg, 'tgt_type': tgt_type}
        else:
            params = {'client': 'local_async', 'fun': method, 'tgt': minion, 'tgt_type': tgt_type}
        params.update(kwargs)
        jid = self.get_data(self.url, params)['jid']
        return jid

    # 异步请求之后，需要根据jid得到对应的job的结果
    def look_jid(self, jid):
        params = {'client': 'runner', 'fun': 'jobs.lookup_jid', 'jid': jid}
        result = self.get_data(self.url, params)
        return result


def salt_init():
    salt = SaltApi(salt_api)
    return salt
