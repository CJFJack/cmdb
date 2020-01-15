import urllib.request
import http.cookiejar
import urllib.parse
from pyquery import PyQuery as py
from cmdb.settings import ZABBIX_URL


def get_zabbix_cookie_v2(username, password):
    """获取zabbix登录后cookie"""
    cookie_dict = dict()
    success = True
    msg = 'ok'
    try:
        hosturl = ZABBIX_URL
        posturl = ZABBIX_URL + '/index.php'
        cj = http.cookiejar.LWPCookieJar()
        cookie_support = urllib.request.HTTPCookieProcessor(cj)
        opener = urllib.request.build_opener(cookie_support, urllib.request.HTTPHandler)
        urllib.request.install_opener(opener)
        urllib.request.urlopen(hosturl)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0',
            'Referer': 'http://monitor.chuangyunet.com/index.php'
        }
        postData = {
            "name": username,
            "password": password,
            "autologin": 1,
            "enter": "Sign in"
        }
        postData = urllib.parse.urlencode(postData).encode('utf-8')
        request = urllib.request.Request(posturl, postData, headers)
        res = urllib.request.urlopen(request)
        doc = py(res.read().decode())
        login_failed = doc('.red')
        if login_failed:
            raise Exception(login_failed.text())
        for item in cj:
            cookie_dict[item.name] = item.value
    except Exception as e:
        success = False
        msg = str(e)
    finally:
        return success, cookie_dict, msg
