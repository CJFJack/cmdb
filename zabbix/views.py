from django.shortcuts import redirect
from zabbix.models import ZabbixCookie
from cmdb.settings import ZABBIX_URL
from cmdb.settings import ZABBIX_HOST

import json


def zabbix(request):
    """跳转到zabbix，并设置cookie"""
    ip_or_domain = request.get_host().split(':')[0]
    redirect_url = 'http://' + ip_or_domain + ':' + ZABBIX_URL.split(':')[-1]
    response = redirect(redirect_url)
    cookie_obj, created = ZabbixCookie.objects.get_or_create(user=request.user, zabbix_ip=ZABBIX_HOST)
    if not created:
        cookie_dict = json.loads(cookie_obj.cookie)
        for key, value in cookie_dict.items():
            response.set_cookie(key=key, value=value)
    return response
