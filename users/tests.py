from django.test import TestCase

# Create your tests here.

from requests.packages.urllib3.util import Retry
from requests.adapters import HTTPAdapter
from requests import Session


def create_user_for_openvpn(username, email):
    url = 'https://192.168.40.11/api/addvpnuser/'
    token = 'd11205fc792d2d2def44ca55e5252dcbdcea6961'
    authorized_token = "Token " + token
    headers = {
        'Accept': 'application/json',
        'Authorization': authorized_token,
        'Connection': 'keep-alive',
    }
    data = {
        'username': username,
        'email': email
    }
    try:
        s = Session()
        s.mount('https://', HTTPAdapter(max_retries=Retry(total=3, status_forcelist=[408])))
        r = s.post(url, headers=headers, json=data, verify=False, timeout=30)
        if r.status_code == 200:
            result = r.json()
            return result
        else:
            raise Exception('发送到40.11失败' + str(r))
    except Exception as e:
        return {'msg': str(e), 'result': False}


def delete_user_for_openvpn(username):
    url = 'https://192.168.40.11/api/delvpnuser/'
    token = 'd11205fc792d2d2def44ca55e5252dcbdcea6961'
    authorized_token = "Token " + token
    headers = {
        'Accept': 'application/json',
        'Authorization': authorized_token,
        'Connection': 'keep-alive',
    }
    data = {
        'username': username,
    }
    try:
        s = Session()
        s.mount('https://', HTTPAdapter(max_retries=Retry(total=3, status_forcelist=[408])))
        r = s.post(url, headers=headers, json=data, verify=False, timeout=30)
        if r.status_code == 200:
            result = r.json()
            return result
        else:
            raise Exception('发送到40.11失败' + str(r))
    except Exception as e:
        return {'msg': str(e), 'result': False}


def modify_password_for_openvpn(username, passwd):
    url = 'https://192.168.40.11/api/modvpnuser/'
    token = 'd11205fc792d2d2def44ca55e5252dcbdcea6961'
    authorized_token = "Token " + token
    headers = {
        'Accept': 'application/json',
        'Authorization': authorized_token,
        'Connection': 'keep-alive',
    }
    data = {
        'username': username,
        'passwd': passwd
    }
    try:
        s = Session()
        s.mount('https://', HTTPAdapter(max_retries=Retry(total=3, status_forcelist=[408])))
        r = s.post(url, headers=headers, json=data, verify=False, timeout=30)
        if r.status_code == 200:
            result = r.json()
            return result
        else:
            raise Exception('发送到40.11失败' + str(r))
    except Exception as e:
        return {'msg': str(e), 'result': False}


if __name__ == '__main__':
    # print(create_user_for_openvpn('chenjiefeng', ['chenjiefeng@forcegames.cn', '398741302@qq.com']))
    print(delete_user_for_openvpn('chenjiefeng'))
    # print(modify_password_for_openvpn('chenjiefeng', '123456'))
    pass
