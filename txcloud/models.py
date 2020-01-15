from django.db import models

import json


class Region(models.Model):
    """腾讯云地域"""
    code = models.CharField(max_length=30, verbose_name=u'地域英文代码')
    city = models.CharField(max_length=30, verbose_name=u'城市')
    region = models.CharField(max_length=30, verbose_name=u'地区')

    class Meta:
        verbose_name = u'腾讯云地域'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.region


class ServerZoneNumber(models.Model):
    """实例机型可用区数量统计"""
    instance_type = models.CharField(max_length=20, verbose_name=u'实例规格')
    zone_detail = models.TextField(default='', verbose_name=u'可用区')

    class Meta:
        verbose_name = u'实例机型可用区数量统计'
        verbose_name_plural = verbose_name

    def get_zone_number(self):
        return len(list(set(json.loads(self.zone_detail))))

    def __str__(self):
        return self.instance_type + ':' + str(self.get_zone_number())


class MysqlZoneConfig(models.Model):
    """云数据库mysql规格"""
    region = models.CharField(max_length=30, verbose_name=u'地域')
    region_name = models.CharField(max_length=30, verbose_name=u'地域中文名称')
    zone = models.CharField(max_length=30, verbose_name=u'可用区')
    zone_name = models.CharField(max_length=30, verbose_name=u'可用区中文名称')
    protect_mode = models.CharField(max_length=100, null=True, verbose_name=u'数据复制类型')
    config_data = models.TextField(null=True, blank=True, verbose_name=u'json格式配置')

    class Meta:
        verbose_name = u'云数据库mysql规格'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.config_data
