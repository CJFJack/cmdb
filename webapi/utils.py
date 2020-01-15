"""从web中获取cdn的信息
"""

import requests
import time
import json
import hashlib

from webapi.models import WebGetCdnListAPI
from assets.models import GameProject


def get_cdn_list_from_web(project, area, root=None, dev_flag=None):
    """从web调用接口获取某个项目某个域名下的cdn目录"""
    msg = 'ok'
    try:
        api = WebGetCdnListAPI.objects.get(project=project, area=area)
        url = api.get_full_url(root, dev_flag)
        r = requests.get(url)
        result = r.json()
        if result.get('resp', 0) == 1:
            return result.get('data')
        else:
            raise Exception('获取cdn目录失败')
    except WebGetCdnListAPI.DoesNotExist:
        msg = '没有配置项目%s，地区%s的api信息' % (project, area)
        raise Exception(msg)
    except Exception as e:
        msg = str(e)
        raise Exception(msg)


class GetCDNDirFromWeb(object):
    """
    cmdb向web获取cdn目录新接口 2.0
    初始化参数：
    project_id： cmdb项目id
    data： '{"root_url": "res.fg.cn"}'
    """

    def __init__(self, project_id, root_url, area):
        self.project_id = project_id
        self.area = area
        self._time = int(time.time())
        self._key = 'cytZEG>?v"9D~Wi(]Z<`%p(!1UzjLOe4gq'

        def assert_msg(condition, msg):
            if not condition:
                raise Exception(msg)

        assert_msg(GameProject.objects.filter(pk=self.project_id), '游戏项目不存在')
        assert_msg(GameProject.objects.get(pk=self.project_id).web_game_id, '游戏项目未设置web game id')
        assert_msg(WebGetCdnListAPI.objects.filter(project_id=self.project_id, area=self.area), 'WebGetCdnListAPI没有配置该项目')
        assert_msg(WebGetCdnListAPI.objects.get(project_id=self.project_id).web_url, 'WebGetCdnListAPI没有配置api地址')

        self._g = int(GameProject.objects.get(pk=self.project_id).web_game_id)
        self._url = WebGetCdnListAPI.objects.get(project_id=self.project_id).web_url
        self._data = json.dumps({'root_url': root_url})
        self._sign = self.sign()

    def sign(self):
        """sha256(md5(data内串行json数据(未进行urlencode前) + time + key ))"""
        sign_data = self._data + str(self._time) + self._key
        md5 = hashlib.md5()
        md5.update(sign_data.encode('utf-8'))
        md5_sign = md5.hexdigest()
        _hash = hashlib.sha256()
        _hash.update(md5_sign.encode('utf-8'))
        sign = _hash.hexdigest()
        return sign

    def post_api(self):
        post_data = {
            'g': self._g,
            'time': self._time,
            'data': self._data,
            'sign': self._sign,
        }
        response = requests.post(self._url, data=post_data)
        if response.status_code == 200:
            res = response.json()
            if res['status'] == 1:
                return res['data']
        return []
