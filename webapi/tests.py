# -*- encoding: utf-8 -*-
"""
主要测试内容：
    模拟调用api接口
使用方法：
    运行脚本 /data/code/cy_devops/bin/python3 /data/www/cmdb/webapi/tests.py
"""
import requests
import os
import django
import sys

pathname = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, pathname)
sys.path.insert(0, os.path.abspath(os.path.join(pathname, '..')))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cmdb.settings")
django.setup()
from webapi.models import WebGetCdnListAPI
from webapi.utils import get_cdn_list_from_web


def test_web_get_cdn_dir_api():
    """测试调用web获取cdn目录列表api"""
    result = True
    msg = 'ok'
    try:
        web_api_list = WebGetCdnListAPI.objects.all()
        for api in web_api_list:
            if api.web_url:
                project = api.project
                area = api.area
                root = api.root
                dev_flag = api.dev_flag
                if root:
                    if dev_flag is None:
                        dev_flag = None
                        data = get_cdn_list_from_web(project, area, root, dev_flag)
                        print(area.chinese_name + '-' + project.project_name + '-' + dev_flag + '-' + str(data))
                    else:
                        for x in api.dev_flag.split(','):
                            data = get_cdn_list_from_web(project, area, root, x)
                            print(area.chinese_name + '-' + project.project_name + '-' + x + '-' + str(data))

    except Exception as e:
        msg = str(e)
        result = False
    finally:
        return result, msg


if __name__ == '__main__':
    print(test_web_get_cdn_dir_api())

