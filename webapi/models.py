from django.db import models
from assets.models import GameProject, Area

import time
import hashlib
import urllib
import json


class WebGetCdnListAPI(models.Model):
    """web获取cdn目录API配置表"""
    VERSION = (
        (1, 'v1.0'),
        (2, 'v2.0'),
    )
    project = models.ForeignKey(GameProject, on_delete=models.CASCADE, verbose_name=u'所属项目')
    area = models.ForeignKey(Area, on_delete=models.CASCADE, verbose_name=u'所属地区')
    web_url = models.CharField(null=True, blank=True, max_length=255, verbose_name=u'webAPI地址')
    root = models.CharField(null=True, blank=True, max_length=100, verbose_name=u'cdn根域名')
    dev_flag = models.CharField(max_length=50, null=True, blank=True, verbose_name=u'客户端类型')
    version = models.IntegerField(choices=VERSION, default=1, verbose_name=u'接口版本')

    class Meta:
        verbose_name = u'web获取cdn目录API配置表'
        verbose_name_plural = verbose_name
        unique_together = ('project', 'area')

    def show_all(self):
        return {
            'id': self.id,
            'project': self.project.project_name,
            'area': self.area.short_name,
            'web_url': self.web_url,
            'root': self.root,
            'dev_flag': self.dev_flag,
            'version': self.get_version_display(),
        }

    def edit_data(self):
        return {
            'id': self.id,
            'project_id': self.project.id,
            'project': self.project.project_name,
            'area_id': self.area.id,
            'area': self.area.chinese_name,
            'web_url': self.web_url,
            'root': self.root,
            'dev_flag': self.dev_flag,
            'version_id': self.version,
            'version': self.get_version_display(),
        }

    def get_time(self):
        """获取当前时间戳"""
        timestamp = str(int(time.time()))
        return timestamp

    def get_sign(self):
        """获取web签名（旧接口）"""
        key = 'cytZEG>?v"9D~Wi(]Z<`%p(!1UzjLOe4gq'
        signkey = self.get_time() + key
        md5 = hashlib.md5()
        md5.update(signkey.encode('utf-8'))
        keymd5 = md5.hexdigest()
        _hash = hashlib.sha256()
        _hash.update(keymd5.encode('utf-8'))
        signkey = _hash.hexdigest()
        return signkey

    def quote_plus_root(self, root):
        """将cdn根目录做url特殊转化，如kvm.vcdn.vn/real，转化为kvm.vcdn.vn%2Freal"""
        return urllib.parse.quote_plus(urllib.parse.quote_plus(root))

    def get_full_url(self, root, dev_flag):
        """获取完整url地址"""
        if self.dev_flag:
            return self.web_url + '/game_id/' + str(
                self.project.web_game_id) + '/root/' + self.quote_plus_root(
                root) + '/dev_flag/' + dev_flag + '/time/' + self.get_time() + '/sign/' + self.get_sign()
        else:
            return self.web_url + '/game_id/' + str(
                self.project.web_game_id) + '/root/' + self.quote_plus_root(
                root) + '/time/' + self.get_time() + '/sign/' + self.get_sign()

    def get_data_param_new(self, root, dev_flag):
        """获取新版接口data参数（未urlencode）"""
        data = {}
        data['game_id'] = str(self.project.web_game_id)
        data['root'] = urllib.parse.quote_plus(root)
        if dev_flag:
            data['dev_flag'] = dev_flag
        return data

    def get_sign_new(self, root, dev_flag):
        """获取新版web签名"""
        key = 'cytZEG>?v"9D~Wi(]Z<`%p(!1UzjLOe4gq'
        sign_data = json.dumps(self.get_data_param_new(root, dev_flag), sort_keys=True) + str(self.get_time()) + key
        md5 = hashlib.md5()
        md5.update(sign_data.encode('utf-8'))
        sign_md5 = md5.hexdigest()
        _hash = hashlib.sha256()
        _hash.update(sign_md5.encode('utf-8'))
        sign = _hash.hexdigest()
        return sign

    def get_full_url_new(self, root, dev_flag):
        """获取新版完整url地址"""
        return self.web_url + '?data=' + urllib.parse.urlencode(
            self.get_data_param_new(root, dev_flag)) + '&time=' + str(
            self.get_time()) + '&sign=' + self.get_sign_new(root, dev_flag) + '&g=' + str(
            self.project.web_game_id)

    def get_dev_flag_list(self):
        return self.dev_flag.split(',')

    def get_root(self):
        return self.root.split(',')
