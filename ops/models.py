from django.db import models

from assets.models import GameProject
from myworkflows.models import GameServer
from django.contrib.auth.models import User
from assets.models import GameProject
from assets.models import Area
from assets.models import Room

import time
import json


# Create your models here.


class InstallGameServer(models.Model):
    """装服计划
    """

    STATUS = (
        (0, '未处理'),
        (1, '安装中'),
        (2, '安装成功'),
        (3, '安装失败'),
        (4, '卸载中'),
        (5, '卸载成功'),
        (6, '卸载失败'),
    )

    project = models.ForeignKey(GameProject, help_text='归属项目')
    area = models.CharField(max_length=10, help_text='地区')
    pf_id = models.IntegerField(help_text='平台id')
    pf_name = models.CharField(max_length=50, help_text='平台名称')
    srv_num = models.IntegerField(help_text='web区服id')
    srv_name = models.CharField(max_length=50, help_text='区服名称')
    server_version = models.CharField(null=True, blank=True, max_length=50, help_text='后端版本号')
    client_version = models.CharField(null=True, blank=True, max_length=50, help_text='前端版本号')
    client_dir = models.CharField(null=True, blank=True, max_length=100, help_text='前端目录')
    open_time = models.IntegerField(help_text='正式开服时间，时间戳')
    status = models.IntegerField(choices=STATUS, default=0, help_text='状态')
    qq_srv_id = models.IntegerField(default=0, help_text='开平台区服ID')
    unique_srv_id = models.IntegerField(help_text='唯一区服ID')
    srv_type = models.IntegerField(default=1, help_text='服务器组')
    srv_farm_id = models.IntegerField(default=0, help_text='服务器群组ID')
    srv_farm_name = models.CharField(max_length=50, default='default', help_text='服务器群组英文名')
    install_remark = models.TextField(default='', help_text='安装失败的备注')
    uninstall_remark = models.TextField(default='', help_text='卸载失败的备注')

    class Meta:
        db_table = 'install_gameserver'
        unique_together = (('project', 'area', 'pf_id', 'srv_num'), ('project', 'area', 'pf_name', 'srv_num'),)

    def __str__(self):
        return self.project.project_name + '-' + self.srv_name

    def show_all(self, project_name_en=False, timestamp=False):
        if project_name_en:
            project_name = self.project.project_name_en
        else:
            project_name = self.project.project_name
        if timestamp:
            open_time = int(self.open_time)
        else:
            open_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.open_time))
        return {
            'id': self.id,
            'open_time': open_time,
            'project': project_name,
            'area': self.area,
            'pf_id': self.pf_id,
            'pf_name': self.pf_name,
            'srv_num': self.srv_num,
            'srv_name': self.srv_name,
            'server_version': self.server_version,
            'client_version': self.client_version if self.client_version else '',
            'client_dir': self.client_dir if self.client_dir else '',
            'status': self.get_status_display(),
            'qq_srv_id': self.qq_srv_id,
            'unique_srv_id': self.unique_srv_id,
            'srv_type': self.srv_type,
            'srv_farm_id': self.srv_farm_id,
            'srv_farm_name': self.srv_farm_name,
            'install_remark': self.install_remark,
            'uninstall_remark': self.uninstall_remark,
        }


class InstallGameServerRecord(models.Model):
    """装服计划操作记录"""
    TYPES = (
        (0, '执行装服'),
        (1, '添加装服'),
        (2, '修改装服'),
        (3, '添加卸服'),
        (4, '执行卸服'),
    )
    RESULTS = (
        (1, '成功'),
        (0, '失败'),
    )
    OperationTime = models.DateTimeField(auto_now_add=True, verbose_name='操作时间', help_text='操作时间')
    OperationUser = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='操作人', help_text='操作人')
    OperationType = models.IntegerField(choices=TYPES, default=0, verbose_name='操作类型', help_text='操作类型')
    OperationResult = models.IntegerField(choices=RESULTS, default=1, verbose_name='操作结果', help_text='操作结果')
    InstallGameServer = models.ForeignKey(InstallGameServer, null=True, blank=True, on_delete=models.SET_NULL,
                                          verbose_name='关联开服计划', help_text='关联开服计划')
    remark = models.CharField(max_length=100, null=True, blank=True, verbose_name='备注', help_text='备注')

    class Meta:
        verbose_name = '开副计划操作记录表'
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return str(self.OperationTime) + self.OperationUser.username + self.get_OperationType_display()


class GameServerOff(models.Model):
    """区服下线计划"""
    STATUS = (
        (1, u'未执行'),
        (2, u'正在执行'),
        (3, u'下线成功'),
        (4, u'下线失败'),
        (5, u'取消'),
    )
    off_time = models.DateTimeField(verbose_name=u'下线时间')
    web_callback_url = models.CharField(max_length=100, verbose_name=u'web回调地址')
    status = models.IntegerField(choices=STATUS, default=1, verbose_name=u'计划执行状态')
    uuid = models.CharField(max_length=100, verbose_name=u'任务唯一标识')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')

    class Meta:
        verbose_name = u'游戏区服下线计划'
        verbose_name_plural = verbose_name

    def get_sid_list(self):
        sid_list = [str(x.game_server.sid) for x in self.gameserveroffdetail_set.all()]
        sid_list.sort()
        return sid_list

    def get_srv_id_list(self):
        srv_id_list = [str(x.game_server.srv_id) for x in self.gameserveroffdetail_set.all()]
        srv_id_list.sort()
        return srv_id_list

    def show_all(self):
        return {
            'id': self.id,
            'off_time': str(self.off_time)[:16],
            'web_callback_url': self.web_callback_url,
            'status_id': self.status,
            'status_text': self.get_status_display(),
            'uuid': self.uuid,
            'create_time': str(self.create_time)[:16],
            'log': '',
            'off_srv': ','.join(
                [x.game_server.project.project_name + '-' + x.game_server.room.room_name + '-' + x.game_server.srv_id
                 for x in self.gameserveroffdetail_set.order_by('id') if
                 self.gameserveroffdetail_set.all() and x.game_server]),
            'off_srv_detail': ','.join([x.get_status_display() + '-' + x.get_remark() for x in
                                        self.gameserveroffdetail_set.order_by('id') if
                                        self.gameserveroffdetail_set.all()]),
        }

    def edit_data(self):
        return {
            'id': self.id,
            'off_time': str(self.off_time)[:16],
            'status_id': self.status,
            'status_text': self.get_status_display(),
            'uuid': self.uuid,
        }

    def get_related_user(self):
        user_list = []
        for detail in self.gameserveroffdetail_set.all():
            user_list += detail.get_related_user()
        return list(set(user_list))

    def get_related_project_name_en(self):
        return self.gameserveroffdetail_set.all()[0].game_server.project.project_name_en

    def get_relate_role_user(self):
        """获取关联据色分组中的用户"""
        user_list = []
        for detail in self.gameserveroffdetail_set.all():
            user_list += detail.get_relate_role_user()
        return list(set(user_list))

    def __str__(self):
        return self.uuid


class GameServerOffDetail(models.Model):
    """区服下线计划明细"""
    STATUS = (
        (0, u'下线失败'),
        (1, u'下线成功'),
        (2, u'未执行'),
    )
    game_server_off = models.ForeignKey(GameServerOff, on_delete=models.CASCADE, verbose_name=u'所属游戏项目下线计划')
    game_server = models.ForeignKey(GameServer, null=True, blank=True, on_delete=models.SET_NULL,
                                    verbose_name=u'需要下线的区服')
    status = models.IntegerField(choices=STATUS, default=2, verbose_name=u'下线状态')
    remark = models.TextField(null=True, blank=True, verbose_name=u'区服下线结果信息')

    class Meta:
        verbose_name = u'区服下线明细表'
        verbose_name_plural = verbose_name

    def get_related_user(self):
        return [x for x in self.game_server.host.belongs_to_game_project.related_user.all()]

    def get_relate_role_user(self):
        return [x for x in self.game_server.host.belongs_to_game_project.get_relate_role_user()]

    def get_remark(self):
        return str(self.remark) if self.remark else ''

    def __str__(self):
        return self.game_server.srv_id


class GameServerOffLog(models.Model):
    """区服下线任务日志表"""
    game_server_off = models.OneToOneField(GameServerOff, verbose_name=u'所属区服下线任务')
    log = models.TextField(default='', verbose_name=u'任务日志')

    class Meta:
        verbose_name = u'区服下线任务日志表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.game_server_off.uuid


class ModifyOpenSrvSchedule(models.Model):
    """修改开服时间计划"""
    STATUS = (
        (1, u'未执行'),
        (2, u'正在执行'),
        (3, u'修改成功'),
        (4, u'修改失败'),
        (5, u'取消'),
    )
    open_time = models.DateTimeField(verbose_name=u'开服时间')
    status = models.IntegerField(choices=STATUS, default=1, verbose_name=u'计划执行状态')
    uuid = models.CharField(max_length=100, verbose_name=u'任务唯一标识')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')

    class Meta:
        verbose_name = u'修改开服时间计划'
        verbose_name_plural = verbose_name

    def get_sid_list(self):
        sid_list = [str(x.game_server.sid) for x in self.modifyopensrvscheduledetail_set.all()]
        sid_list.sort()
        return sid_list

    def get_srv_id_list(self):
        srv_id_list = [str(x.game_server.srv_id) for x in self.modifyopensrvscheduledetail_set.all()]
        srv_id_list.sort()
        return srv_id_list

    def show_all(self):
        return {
            'id': self.id,
            'open_time': str(self.open_time)[:16],
            'status_id': self.status,
            'status_text': self.get_status_display(),
            'uuid': self.uuid,
            'create_time': str(self.create_time)[:16],
            'log': '',
            'modify_srv': ','.join(
                [x.game_server.project.project_name + '-' + x.game_server.room.room_name + '-' + str(x.game_server.sid)
                 for x in self.modifyopensrvscheduledetail_set.all()]),
        }

    def edit_data(self):
        return {
            'id': self.id,
            'open_time': str(self.open_time)[:16],
            'status_id': self.status,
            'status_text': self.get_status_display(),
            'uuid': self.uuid,
        }

    def get_related_user(self):
        user_list = []
        for detail in self.modifyopensrvscheduledetail_set.all():
            user_list += detail.get_related_user()
        return user_list

    def get_relate_role_user(self):
        user_list = []
        for detail in self.modifyopensrvscheduledetail_set.all():
            user_list += detail.get_relate_role_user()
        return user_list

    def get_related_project_name_en(self):
        return self.modifyopensrvscheduledetail_set.all()[0].game_server.project.project_name_en

    def __str__(self):
        return self.uuid


class ModifyOpenSrvScheduleDetail(models.Model):
    """修改开服时间计划明细"""
    STATUS = (
        (0, u'修改失败'),
        (1, u'修改成功'),
        (2, u'未执行'),
    )
    modify_schedule = models.ForeignKey(ModifyOpenSrvSchedule, on_delete=models.CASCADE, verbose_name=u'所属修改开服时间计划')
    game_server = models.ForeignKey(GameServer, null=True, blank=True, on_delete=models.SET_NULL,
                                    verbose_name=u'需要修改开服时间的区服')
    status = models.IntegerField(choices=STATUS, default=2, verbose_name=u'执行状态')
    remark = models.TextField(default='', verbose_name=u'修改开服时间结果信息')

    class Meta:
        verbose_name = u'修改开服时间计划明细'
        verbose_name_plural = verbose_name

    def get_related_user(self):
        return [x for x in self.game_server.host.belongs_to_game_project.related_user.all()]

    def get_relate_role_user(self):
        return [x for x in self.game_server.host.belongs_to_game_project.get_relate_role_user()]

    def __str__(self):
        return self.game_server.srv_id


class ModifyOpenSrvScheduleLog(models.Model):
    """修改开服时间计划日志表"""
    modify_schedule = models.OneToOneField(ModifyOpenSrvSchedule, verbose_name=u'所属修改开服时间计划')
    log = models.TextField(default='', verbose_name=u'任务日志')

    class Meta:
        verbose_name = u'修改开服时间计划日志表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.modify_schedule.uuid


class GameServerMergeSchedule(models.Model):
    """创建合服计划"""
    STATUS = (
        (0, '未发送'),
        (1, '合服-发送成功'),
        (2, '合服-发送失败'),
        (3, '回滚-发送成功'),
        (4, '回滚-发送失败'),
    )
    uuid = models.CharField(max_length=100, verbose_name=u'计划唯一标识')
    project = models.ForeignKey(GameProject, null=True, blank=True, on_delete=models.SET_NULL, verbose_name=u'所属项目')
    room = models.ForeignKey(Room, null=True, blank=True, on_delete=models.SET_NULL, verbose_name=u'所属机房')
    main_srv = models.CharField(max_length=20, null=True, blank=True, verbose_name=u'主服')
    slave_srv = models.CharField(max_length=255, null=True, blank=True, verbose_name=u'从服字符串')
    group_id = models.CharField(max_length=10, null=True, blank=True, verbose_name=u'组id')
    merge_time = models.DateTimeField(verbose_name=u'合服时间')
    status = models.IntegerField(choices=STATUS, default=0, verbose_name=u'是否已发送到运维管理机')
    remark = models.TextField(default='', verbose_name=u'发送失败备注')

    def show_all(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'project': self.project.project_name if self.project else '',
            'room': str(self.room.area.chinese_name or '') + '-' + self.room.room_name if self.room else '',
            'main_srv': self.main_srv,
            'slave_srv': self.slave_srv,
            'group_id': self.group_id,
            'merge_time': str(self.merge_time)[:19],
            'status': self.get_status_display(),
            'remark': self.remark,
        }

    def edit_data(self):
        return {
            'status_id': self.status,
            'status': self.get_status_display(),
        }

    def send_data(self):
        """
        :returns
        '[
            {"main_srv": "1", "slave_srv": "3,4,5", "group_id": 1, "merge_time": "1234567890", "project": "ssss"},
        ]'
        """
        data_dict = {"main_srv": self.main_srv, "slave_srv": self.slave_srv, "group_id": self.group_id,
                     "merge_time": int(time.mktime(self.merge_time.timetuple())), 'project': self.project.project_name_en}
        return json.dumps([data_dict])

    def __str__(self):
        return self.uuid
