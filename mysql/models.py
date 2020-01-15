from django.db import models

from assets.models import GameProject
from assets.models import Area
from django.contrib.auth.models import User
from mysql.utils import is_ip
from txcloud.models import Region

import json

# Create your models here.


class MysqlInstance(models.Model):
    """mysql实例
    """
    STATUS = (
        (0, '创建中'),
        (1, '运行中'),
        (2, '正在初始化'),
        (3, '外网访问开通中'),
        (4, '正在进行隔离操作'),
        (5, '隔离中(可在回收站恢复开机)')
    )
    WAN = (
        (1, '已开通'),
        (0, '未开通')
    )

    project = models.ForeignKey(GameProject, help_text='归属项目')
    area = models.CharField(max_length=10, help_text='地区')
    purpose = models.CharField(max_length=20, help_text='用途')
    host = models.CharField(max_length=50, null=True, blank=True, help_text='主机地址')
    port = models.CharField(max_length=5, null=True, blank=True, help_text='端口')
    user = models.CharField(max_length=10, null=True, blank=True, help_text='用户')
    password = models.CharField(max_length=100, null=True, blank=True, help_text='密码')
    white_list = models.CharField(max_length=255, blank=True, null=True, default=None, help_text='白名单')
    cmdb_area = models.ForeignKey(Area, null=True, blank=True, on_delete=models.SET_NULL, help_text='关联地区')
    instance_id = models.CharField(max_length=50, null=True, blank=True, help_text='实例ID')
    status = models.IntegerField(choices=STATUS, default=1, help_text='实例状态')
    open_wan = models.IntegerField(choices=WAN, default=1, help_text='是否已开通外网访问')
    tx_region = models.ForeignKey(Region, null=True, blank=True, on_delete=models.SET_NULL, help_text='腾讯云所属地域')

    class Meta:
        db_table = 'mysqlinstance'
        unique_together = (('host', 'port'),)

    def __str__(self):
        return self.host

    def show_all(self, password_visible=True):
        password = self.password if password_visible else '******'
        return {
            'id': self.id,
            'project': self.project.project_name,
            'area': self.area,
            'purpose': self.purpose,
            'host': self.host,
            'port': self.port,
            'account': self.user + ',' + password,
            'white_list': ','.join(json.loads(self.white_list)) if self.white_list else '',
            'cmdb_area': self.cmdb_area.chinese_name if self.cmdb_area else '',
            'status': self.get_status_display(),
            'instance_id': self.instance_id,
            'open_wan': self.open_wan,
        }

    def show_api(self):
        return {
            'id': self.id,
            'project': self.project.project_name_en,
            'area': self.cmdb_area.chinese_name if self.cmdb_area else self.area,
            'purpose': self.purpose,
            'host': self.host,
            'port': self.port,
            'user': self.user,
            'password': self.password,
            'white_list': self.white_list if self.white_list else ''
        }

    def edit_data(self):
        return {
            'id': self.id,
            'project': self.project.id,
            'area': self.area,
            'purpose': self.purpose,
            'host': self.host,
            'port': self.port,
            'user': self.user,
            'password': self.password,
            'white_list': ','.join(json.loads(self.white_list)) if self.white_list else '',
            'cmdb_area': self.cmdb_area.id if self.cmdb_area else '0',
        }

    def get_tx_region_code(self):
        if self.tx_region:
            return self.tx_region.code
        return 'ap-guangzhou'


class MyqlHistoryRecord(models.Model):
    """Mysql变更记录表"""
    TYPE = (
        (1, u'新增'),
        (2, u'修改'),
        (3, u'删除'),
    )
    mysql = models.ForeignKey(MysqlInstance, null=True, blank=True, on_delete=models.SET_NULL, verbose_name=u'所属mysql实例')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name=u'变更时间')
    create_user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, verbose_name=u'操作人')
    type = models.IntegerField(choices=TYPE, default=1, verbose_name=u'变更类型')
    alter_field = models.CharField(max_length=20, default='', verbose_name=u'修改的字段')
    old_content = models.CharField(max_length=255, default='', verbose_name=u'变更前内容')
    new_content = models.CharField(max_length=255, default='', verbose_name=u'变更后内容')
    remark = models.CharField(max_length=255, default='', verbose_name=u'备注')
    source_ip = models.GenericIPAddressField(null=True, blank=True, verbose_name=u'源IP')

    class Meta:
        verbose_name = 'Mysql变更记录表'
        verbose_name_plural = verbose_name
        db_table = 'mysql_historyrecord'

    def show_all(self):
        return {
            'id': self.id,
            'project': self.mysql.project.project_name if self.mysql and self.mysql.project else '',
            'cmdb_area': self.mysql.cmdb_area.chinese_name if self.mysql and self.mysql.cmdb_area else '',
            'instance': self.mysql.host + ':' + self.mysql.port if self.mysql else '',
            'create_time': str(self.create_time)[:19],
            'create_user': self.create_user.username,
            'type': self.get_type_display(),
            'alter_field': self.alter_field,
            'old_content': self.old_content,
            'new_content': self.new_content,
            'remark': self.remark,
            'source_ip': self.source_ip,
        }

    def __str__(self):
        return self.mysql.host + ':' + self.mysql.port
