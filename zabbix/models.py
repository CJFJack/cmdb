from django.db import models
from django.contrib.auth.models import User


class ZabbixCookie(models.Model):
    """zabbix登录后cookie"""
    STATUS = (
        (0, '登录失败'),
        (1, '登录成功'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=u'所属用户')
    cookie = models.CharField(max_length=100, null=True, blank=True, verbose_name=u'zabbix登录后的cookie')
    zabbix_ip = models.GenericIPAddressField(null=True, blank=True, verbose_name=u'zabbix IP地址')
    status = models.IntegerField(choices=STATUS, default=1, verbose_name=u'登录是否成功的标识')
    msg = models.CharField(max_length=255, default='', verbose_name=u'登录失败提示信息')

    class Meta:
        verbose_name = u'zabbix登录后cookie'
        verbose_name_plural = verbose_name
        db_table = 'zabbix_cookie'

    def __str__(self):
        return self.cookie


