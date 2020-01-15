"""从web中获取cdn的信息
"""

import requests
import time
import json
import hashlib

from webapi.models import WebGetCdnListAPI
from assets.models import GameProject


# def get_snsy_cdn_dir(pre_url, client_type, cdn_root_url):
#     """根据client_type和cdn_root_url
#     从web中获取相应的cdn目录
#     """
#
#     # 特殊处理一个cdn_root_url
#     if cdn_root_url in ('kvm.vcdn.vn/real'):
#         cdn_root_url = 'kvm.vcdn.vn%2Freal'
#         cdn_root_url = urllib.parse.quote_plus(cdn_root_url)
#
#     timestamp = str(int(time.time()))
#     key = 'cytZEG>?v"9D~Wi(]Z<`%p(!1UzjLOe4gq'
#
#     signkey = timestamp + key
#
#     md5 = hashlib.md5()
#     md5.update(signkey.encode('utf-8'))
#
#     keymd5 = md5.hexdigest()
#     _hash = hashlib.sha256()
#
#     _hash.update(keymd5.encode('utf-8'))
#     signkey = _hash.hexdigest()
#
#     # sign = "data=" + data + "&sign=" + signkey + "&time=" + timestamp
#
#     # pre_url = 'http://web.manager.chuangyunet.com/admin.php?s=ApiServer/getCdnList/game_id/5/'
#     url = pre_url + 'root/' + cdn_root_url + '/dev_flag/' + client_type + '/time/' + timestamp + '/sign/' + signkey
#
#     r = requests.get(url)
#
#     result = r.json()
#
#     if result.get('resp', 0) == 1:
#         return result.get('data')
#     else:
#         raise Exception('获取cdn目录失败')


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

        assert_msg(isinstance(self.project_id, int), 'project_id必须是数字整形')
        assert_msg(GameProject.objects.filter(pk=self.project_id), '游戏项目不存在')
        assert_msg(GameProject.objects.get(pk=self.project_id).web_game_id, '游戏项目未设置web game id')
        assert_msg(WebGetCdnListAPI.objects.filter(project_id=self.project_id, area__short_name=self.area), 'WebGetCdnListAPI没有配置该项目')
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
        print(post_data)
        response = requests.post(self._url, data=post_data)
        if response.status_code == 200:
            print(response.json())
        else:
            print(str(response))
