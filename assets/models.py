from django.db import models
from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

import json


class GroupSection(models.Model):
    """部门下面的分组
    """
    group = models.ForeignKey(Group)
    name = models.CharField(max_length=20)
    leader = models.ForeignKey(User, help_text='管理分组负责人')

    class Meta:
        db_table = 'group_section'
        unique_together = (('group', 'name'),)

    def __str__(self):
        return self.group.name + ':' + self.name

    def group_section_to_root(self):
        """部门分组到部门root节点的路径
        返回格式:
        {'leaf': '管理分组1', 'leaf_to_root': '管理分组1/前端技术部/产品开发部/广州创娱'}
        """

        group = self.group
        leaf_to_root_path = []
        leaf_to_root_path.append(group.name)
        while group.groupprofile.parent_group:
            group = group.groupprofile.parent_group
            leaf_to_root_path.append(group.name)
        leaf_to_root_path.append(group.groupprofile.company.name)
        leaf_to_root_path.reverse()

        # link_group_section = '<a href="#">{}</a>'.format(self.name)
        return {'leaf': self.name, 'leaf_to_root': '/'.join(leaf_to_root_path), 'linkurl': self.group.id}

    def get_allocation_select2(self):
        """查看这个部门分组所指派到的项目组
        数据展示用于select2多选
        """
        data = []

        for progro in ProjectGroup.objects.filter(group_section=self):
            data.append({'id': progro.id, 'name': progro.project.project_name + '-' + progro.name})

        return data

    def get_users(self):
        """查看这个部门分组的用户
        每行展示四个
        """
        username_str = ''
        nrow = 4
        for index, u in enumerate(User.objects.filter(profile__group_section=self, is_active=1), 1):
            linked_user = '<a href="/users/user_list/?username={username}">{username}</a>'.format(username=u.username)
            if index % nrow == 0:
                username_str += linked_user + ','
            else:
                username_str += linked_user + ' '

        return username_str

    def get_allocation(self):
        """查看部门分组所分配到的项目组
        """
        return ','.join(
            [x.project.project_name + '-' + x.name for x in ProjectGroup.objects.filter(group_section=self)])

    def show_all(self):
        return {
            'id': self.id,
            'group': self.group.name,
            'leader': self.leader.username,
            'name': self.name,
            'users': self.get_users(),
            'allocation': self.get_allocation(),
        }

    def edit_data(self):
        return {
            'id': self.id,
            'group': self.group.name,
            'leader_id': self.leader.id,
            'leader_name': self.leader.username,
            'name': self.name,
            'allocation': self.get_allocation_select2(),
        }


class Area(models.Model):
    """地区表"""
    chinese_name = models.CharField(max_length=20, unique=True, verbose_name=u'中文名')
    short_name = models.CharField(max_length=20, null=True, blank=True, unique=True, verbose_name=u'简称')

    class Meta:
        verbose_name = u'地区表'
        verbose_name_plural = verbose_name

    def edit_data(self):
        return {
            'id': self.id,
            'chinese_name': self.chinese_name,
            'short_name': self.short_name,
        }

    def __str__(self):
        return self.short_name


class GameProject(models.Model):
    """游戏项目表"""

    STATUS = (
        (0, '停用'),
        (1, '可用'),
    )
    PTYPE = (
        (0, '手游'),
        (1, '页游'),
    )

    project_name = models.CharField(max_length=50, blank=True, null=True, unique=True, help_text='游戏项目名')
    project_name_en = models.CharField(max_length=50, unique=True, help_text='游戏项目英文名')
    status = models.IntegerField(choices=STATUS, default=0, help_text='项目状态')
    svn_repo = models.CharField(max_length=20, blank=True, null=True, help_text='项目svn仓库名')
    related_user = models.ManyToManyField(User, help_text='项目对接的人员')
    leader = models.ForeignKey(User, blank=True, null=True, default=None, related_name='leader',
                               help_text='项目负责人', on_delete=models.SET_NULL)
    group = models.ForeignKey(Group, blank=True, null=True, default=None, help_text='关联的部门(已废弃)', on_delete=models.SET_NULL)
    is_game_project = models.BooleanField(default=True, help_text='是否为游戏项目')
    web_game_id = models.CharField(max_length=10, null=True, blank=True, unique=True, help_text='与web系统的项目id一一对应')
    project_type = models.IntegerField(choices=PTYPE, default=1, help_text='项目类型, 手游or页游')
    content_type = models.ForeignKey(ContentType, null=True, blank=True, on_delete=models.SET_NULL)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    cloud_account = GenericForeignKey('content_type', 'object_id')
    web_ip = models.CharField(max_length=100, null=True, blank=True, help_text='web ip地址字符串，以空格分割')
    manager_wan_ip = models.GenericIPAddressField(null=True, blank=True, help_text='管理机外网IP')
    zabbix_proxy_ip = models.GenericIPAddressField(null=True, blank=True, help_text='zabbix代理IP')
    manager_lan_ip = models.GenericIPAddressField(null=True, blank=True, help_text='管理机内网IP')
    area = models.ForeignKey(Area, null=True, blank=True, on_delete=models.SET_NULL, help_text='所属地区')
    softlist = models.CharField(max_length=255, null=True, blank=True, help_text='软件版本列表，json字符串形式保存')
    hotupdate_template = models.ManyToManyField('myworkflows.HotUpdateTemplate', help_text='关联热更新页面模板')
    auto_version_update = models.BooleanField(default=False, help_text='是否启用自动版本更新')
    wx_robot = models.CharField(max_length=300, blank=True, null=True, verbose_name=u'微信机器人接口地址')

    class Meta:
        db_table = 'cmdb_game_project'
        permissions = (
            ('view_project', 'View project'),
        )

    def __str__(self):
        return self.project_name_en

    def format_related_user_link(self, rnum=2):
        """给项目负责运维格式化展示
        每行展示三个
        u1 u2 u3, u4 u5 u6, u7 u8 u9, u10 u11
        """
        related_users = self.related_user.all()
        related_users = [x for x in related_users if x.is_active]

        link_user = ''

        for index, u in enumerate(related_users, 1):
            # linked_user = '<a href="/users/user_list/?username={username}">{username}</a>'.format(username=u.username)
            linked_user = '{username}'.format(username=u.username)
            if index % rnum == 0:
                link_user += linked_user + ','
            else:
                link_user += linked_user + ' '

        return link_user

    def __format_soft_list(self):
        if self.softlist:
            return ','.join([str(k) + ': ' + str(v) for k, v in json.loads(self.softlist).items()])
        return ''

    def __get_manager_wan_ip(self):
        return str(self.manager_wan_ip) if self.manager_wan_ip else ''

    def __get_manager_lan_ip(self):
        return str(self.manager_lan_ip) if self.manager_lan_ip else ''

    def get_client_hotupdate_template(self, id=False, tag=False):
        template = self.hotupdate_template.filter(type=1)
        if id:
            return template[0].id if template else 991
        if tag:
            return template[0].tag if template else ''
        return template[0] if template else '无'

    def get_server_hotupdate_template(self, id=False, tag=False):
        template = self.hotupdate_template.filter(type=2)
        if tag:
            return template[0].tag if template else ''
        if id:
            return template[0].id if template else 992
        return template[0] if template else '无'

    def show_all(self):
        return {
            'id': self.id,
            'project_name': self.project_name,
            'project_name_en': self.project_name_en,
            'svn_repo': self.svn_repo if self.svn_repo else '',
            'status': self.get_status_display(),
            'leader': self.leader.username if self.leader else '',
            'group': self.group.name if self.group else '',
            'related_user': self.format_related_user_link(),
            'relate_role': ','.join([x.name for x in self.role_set.all()]),
            'is_game_project': '是' if self.is_game_project else '否',
            'related_organization': ','.join([org.get_ancestors_name() for org in self.organizationmptt_set.all()]),
            'web_game_id': self.web_game_id,
            'game_project_type': self.get_project_type_display() if self.is_game_project == 1 else '',
            'cloud_account': self.cloud_account.cloud.name + '-' + self.cloud_account.remark if self.cloud_account else '',
            'web_ip': self.web_ip,
            'manager_ip': '外网：' + self.__get_manager_wan_ip() + ',' + '内网：' + self.__get_manager_lan_ip(),
            'zabbix_proxy_ip': self.zabbix_proxy_ip,
            'area': self.area.chinese_name if self.area else '',
            'softlist': self.__format_soft_list(),
            'hotupdate_template': '前端: {},后端: {}'.format(self.get_client_hotupdate_template(),
                                                         self.get_server_hotupdate_template()),
            'auto_version_update': '自动' if self.auto_version_update else '手动',
            'wx_robot': self.wx_robot if self.wx_robot else '',
        }

    def edit_data(self):
        return {
            'id': self.id,
            'project_name': self.project_name,
            'project_name_en': self.project_name_en,
            'svn_repo': self.svn_repo,
            'leader_id': self.leader.id if self.leader else '0',
            'leader': self.leader.username if self.leader else '选择负责人',
            'group_id': self.group.id if self.group else '0',
            'group': self.group.name if self.group else '选择部门',
            'related_user': [{'id': x.id, 'username': x.username} for x in self.related_user.all()],
            'relate_role': [{'id': x.id, 'name': x.name} for x in self.role_set.all()],
            'is_game_project': self.is_game_project,
            'status': self.status,
            'related_organization': [{'id': x.id, 'name': x.get_ancestors_name()} for x in self.organizationmptt_set.all()],
            'web_game_id': self.web_game_id,
            'game_project_type': self.project_type,
            'cloud_account_id': str(self.content_type_id) + '-' + str(self.object_id) if self.cloud_account else '',
            'web_ip': self.web_ip,
            'manager_wan_ip': self.manager_wan_ip,
            'zabbix_proxy_ip': self.zabbix_proxy_ip,
            'manager_lan_ip': self.manager_lan_ip,
            'area': self.area.id if self.area else 0,
            'softlist': json.loads(self.softlist) if self.softlist else {},
            'auto_version_update': 1 if self.auto_version_update else 0,
            'wx_robot': self.wx_robot if self.wx_robot else '',
        }

    def show_related_user(self):
        return {
            'id': self.id,
            'project': self.project_name,
            'related_user': ','.join(x.username for x in self.related_user.all())
        }

    def get_related_user(self):
        """
        [
            {'id': user_id, 'username': username},
            {'id': user_id, 'username': username},
            {'id': user_id, 'username': username},
        ]
        """
        return {
            'id': self.id,
            'project_name': self.project_name,
            'related_user': [{'id': x.id, 'username': x.username} for x in self.related_user.all()]
        }

    def get_new_organization(self):
        if self.organizationmptt_set.first():
            return self.organizationmptt_set.first().name
        return ''

    def get_related_organization(self):
        if self.organizationmptt_set.first():
            return {
                'id': self.organizationmptt_set.first().id,
                'name': self.organizationmptt_set.first().get_ancestors_name()
            }
        else:
            return {
                'id': '',
                'name': ''
            }

    def get_relate_role_user(self):
        """获取管理角色分组的中的用户"""
        s = set()
        for r in self.role_set.all():
            for u in r.user.all():
                s.add(u)
        return list(s)

    def get_relate_role_user_email_list(self):
        return list(set([u.email for u in self.get_relate_role_user()]))

    def get_relate_role_user_wechat_list(self):
        return '|'.join(list(set([u.first_name for u in self.get_relate_role_user()])))


class ProjectGroup(models.Model):
    name = models.CharField(max_length=50, help_text='项目分组名称')
    project = models.ForeignKey(GameProject, help_text='所属项目')
    project_group_leader = models.ForeignKey(User, blank=True, null=True, related_name='aproject_group_leader',
                                             help_text='项目分组的组长', on_delete=models.PROTECT)
    group_section = models.ForeignKey(
        GroupSection, blank=True, null=True, default=None, help_text='关联的部门分组', on_delete=models.PROTECT)

    def __str__(self):
        return self.name

    def show_all(self):
        return {
            'id': self.id,
            'name': self.name,
            'project_name': self.project.project_name,
            'project_group_leader': self.project_group_leader.username if self.project_group_leader else '',
            'group_section': self.group_section.name if self.group_section else '',
        }

    def edit_data(self):
        return {
            'id': self.id,
            'name': self.name,
            'project_group_leader_id': self.project_group_leader.id if self.project_group_leader else '0',
            'project_group_leader': self.project_group_leader.username if self.project_group_leader else '选择组长',
            'group_section_id': self.group_section.id if self.group_section else '0',
            'group_section': self.group_section.name if self.group_section else '部门分组',
        }


class Room(models.Model):
    """机房表"""
    room_name = models.CharField(max_length=20, help_text='机房名')
    room_name_en = models.CharField(max_length=20, null=True, blank=True, help_text='机房英文简称')
    area = models.ForeignKey(Area, null=True, blank=True, on_delete=models.SET_NULL, help_text='所属地区')

    class Meta:
        db_table = 'assets_room'
        unique_together = (('area', 'room_name'), ('area', 'room_name_en'))

    def __str__(self):
        return self.area.chinese_name + '-' + self.room_name

    def show_all(self):
        return {
            'id': self.id,
            'room_name': self.room_name + ('(' + self.room_name_en + ')' if self.room_name_en else ''),
            'area': self.area.chinese_name + '(' + self.area.short_name + ')' if self.area else '',
        }

    def edit_data(self):
        return {
            'id': self.id,
            'room_name': self.room_name,
            'room_name_en': self.room_name_en,
            'area_id': self.area.id if self.area else '',
            'area_text': self.area.chinese_name if self.area else '',
        }


class DutySchedule(models.Model):
    """值班安排表"""

    belongs_to_game_project = models.ForeignKey(GameProject, help_text='所属游戏项目', on_delete=models.PROTECT)
    start_date = models.DateField(help_text='开始值班时间')
    end_date = models.DateField(help_text='结束值班时间')
    weekdays_person = models.ManyToManyField(User, related_name='weekdays_person', help_text='周一到周五晚上跟进值班人')
    weekend_person = models.ManyToManyField(User, related_name='weekend_person', help_text='周六日值班值班人')

    class Meta:
        db_table = 'cmdb_duty_schedule'
        unique_together = (('belongs_to_game_project', 'start_date', 'end_date'),)
        ordering = ['-start_date', '-end_date']

    def get_weekdays_person(self):
        return ','.join(
            [x.username + ":" + (x.profile.telphone if x.profile.telphone else '') for x in self.weekdays_person.all()])

    def get_weekend_person(self):
        return ','.join(
            [x.username + ":" + (x.profile.telphone if x.profile.telphone else '') for x in self.weekend_person.all()])

    def show_all(self):
        return {
            'id': self.id,
            'game_project': self.belongs_to_game_project.project_name,
            'schedul_date': self.start_date.strftime('%Y-%m-%d') + '到' + self.end_date.strftime('%Y-%m-%d'),
            'weekdays_person': self.get_weekdays_person(),
            'weekend_person': self.get_weekend_person(),
        }

    def edit_data(self):
        return {
            'id': self.id,
            'game_project_id': self.belongs_to_game_project.id,
            'game_project': self.belongs_to_game_project.project_name,
            'start_date': self.start_date.strftime('%Y-%m-%d'),
            'end_date': self.end_date.strftime('%Y-%m-%d'),
            'weekdays_person': [{'id': x.id, 'username': x.username} for x in self.weekdays_person.all()],
            'weekend_person': [{'id': x.id, 'username': x.username} for x in self.weekend_person.all()],
        }


class Business(models.Model):
    """业务类型表"""
    business_name = models.CharField(max_length=50, unique=True, help_text='业务类型名称')

    class Meta:
        db_table = 'assets_business'

    def __str__(self):
        return self.business_name

    def show_all(self):
        return {
            'id': self.id,
            'business_name': self.business_name
        }

    def edit_data(self):
        return {
            'id': self.id,
            'business_name': self.business_name
        }


class OpsManager(models.Model):
    """运维管理机列表

    通过项目和机房来确定唯一的运维管理机url
    """
    STATUS = (
        ('0', '空闲'),
        ('1', '装服'),
        ('2', 'CMDB热更新'),
        ('3', '运维管理机热更新'),
        ('4', '合服'),
        ('5', '迁移'),
        ('6', '版本更新'),
        ('7', '关平台'),
        ('8', 'CMDB区服下线'),
        ('9', 'CMDB主机迁服回收'),
        ('10', 'CMDB修改开服时间'),
        ('11', '开服'),
        ('12', '关服'),
        ('13', '重启'),
        ('14', '清档'),
        ('15', '迁服'),
    )

    CMDB_CAN_CHANGE_STATUS = ('2',)

    OPS_MANAGER_CAN_CHANGE_STATUS = ('1', '3', '4', '5', '6', '7')

    project = models.ForeignKey(GameProject, help_text='项目')
    area = models.CharField(max_length=20, null=True, blank=True, help_text='区域')
    room = models.ForeignKey(Room, on_delete=models.PROTECT, help_text='机房')
    url = models.CharField(max_length=50, help_text='管理机的url')
    token = models.CharField(max_length=50, help_text='token')
    status = models.CharField(max_length=10, choices=STATUS, default='0', help_text='状态')
    end_time = models.CharField(max_length=200, blank=True, null=True, default=None, help_text='结束时间，时间戳')
    rsync_module = models.CharField(max_length=50, null=True, blank=True, help_text='rsync推送模块名')
    rsync_user = models.CharField(max_length=20, null=True, blank=True, help_text='rsync推送用户')
    rsync_pass_file = models.CharField(max_length=100, null=True, blank=True, help_text='rsync推送密码存放路径')
    rsync_port = models.CharField(max_length=10, null=True, blank=True, help_text='rsync推送端口')
    rsync_area_dir = models.CharField(max_length=10, null=True, blank=True, verbose_name='rsync路径中的反映的地区信息的目录名称')
    rsync_ip = models.CharField(max_length=30, null=True, blank=True, help_text='rsync推送IP')
    is_proxy = models.BooleanField(default=False, help_text='是否启用代理')
    proxy_url = models.CharField(max_length=50, null=True, blank=True, help_text='运维管理机的代理url')
    enable = models.BooleanField(default=True, help_text='是否启用')

    class Meta:
        db_table = 'assets_ops_manager'
        unique_together = ('project', 'room')

    def __str__(self):
        return self.url

    def show_all(self):
        return {
            'id': self.id,
            'project': self.project.project_name,
            'area': self.room.area.chinese_name,
            'room': self.room.area.chinese_name + '-' + self.room.room_name,
            'url': self.url,
            'token': self.token,
            'status': self.get_status_display(),
            'end_time': self.end_time if self.end_time else '',
            'rsync_module': self.rsync_module,
            'rsync_user': self.rsync_user,
            'rsync_pass_file': self.rsync_pass_file,
            'rsync_port': self.rsync_port,
            'rsync_area_dir': self.rsync_area_dir,
            'rsync_ip': self.rsync_ip,
            'is_proxy': '是' if self.is_proxy else '否',
            'proxy_url': self.proxy_url,
            'enable': self.enable,
        }

    def show_lock(self):
        return {
            'id': self.id,
            'project': self.project.project_name,
            'area': self.room.area.chinese_name,
            'status': self.get_status_display(),
            'status_id': int(self.status),
            'status_code': self.status,
            'url': self.url,
        }

    def edit_data(self):
        return {
            'id': self.id,
            'project_id': self.project.id,
            'project_name': self.project.project_name,
            'area': self.area,
            'room_id': self.room.id,
            'room_name': self.room.area.chinese_name + '-' + self.room.room_name,
            'url': self.url,
            'token': self.token,
            'rsync_module': self.rsync_module,
            'rsync_user': self.rsync_user,
            'rsync_pass_file': self.rsync_pass_file,
            'rsync_port': self.rsync_port,
            'rsync_area_dir': self.rsync_area_dir,
            'rsync_ip': self.rsync_ip,
            'is_proxy': self.is_proxy,
            'proxy_url': self.proxy_url,
            'enable': self.enable,
        }

    def get_manager_host_status(self):
        """判断对应的主机状态是否为可用，可用则返回True，否则返回False"""
        if self.host_set.filter(belongs_to_business__business_name='manager', status=1):
            return True
        else:
            return False

    def get_ops_ip(self):
        """根据url截取IP地址"""
        url = self.url
        ip = url.split('/')[2]
        return ip

    def get_url(self):
        """若启用代理，即is_proxy为True，则返回proxy_url，否则返回url"""
        if self.is_proxy and self.proxy_url is not None and self.proxy_url != '':
            return self.proxy_url
        else:
            return self.url

    def get_status_display(self):
        for x in OpsManager.STATUS:
            if self.status == x[0]:
                return x[1]


class Host(models.Model):
    """主机表"""
    STATUS = (
        (0, '未初始化'),
        (1, '可用'),
        (2, '停用'),
        (3, '新机器'),
        (4, '已归还'),
    )

    CLASSES = (
        (0, '公司内网'),
        (1, '公司自有外网机器'),
        (2, '游戏合作商提供'),
    )

    TYPE = (
        (0, '云主机'),
        (1, '物理机'),
    )

    SYSTEM = (
        (0, 'linux'),
        (1, 'windows'),
    )

    INTERNET = (
        (0, '完全内网机器'),
        (1, '公网访问不了但可上外网'),
        (2, '公网可访问'),
        (3, '映射外部受限访问'),
    )

    status = models.IntegerField(choices=STATUS, help_text='状态标识')
    host_class = models.IntegerField(choices=CLASSES, help_text='机器归属')
    belongs_to_game_project = models.ForeignKey(GameProject, on_delete=models.PROTECT, help_text='所在项目')
    belongs_to_room = models.ForeignKey(Room, on_delete=models.PROTECT, help_text='所在机房')
    machine_type = models.IntegerField(choices=TYPE, help_text='机器类型')
    belongs_to_business = models.ForeignKey(Business, on_delete=models.PROTECT, help_text='业务类型')
    platform = models.CharField(max_length=50, help_text='平台或者提供商标识')
    internal_ip = models.GenericIPAddressField(blank=True, null=True, help_text='局域网IP')
    telecom_ip = models.GenericIPAddressField(unique=True, blank=True, null=True, help_text='电信ip')
    unicom_ip = models.GenericIPAddressField(unique=True, blank=True, null=True, help_text='联通ip')
    system = models.IntegerField(choices=SYSTEM, help_text='操作系统')
    is_internet = models.IntegerField(choices=INTERNET, help_text='是否公网访问状态标识')
    sshuser = models.CharField(max_length=20, default='root', help_text='服务器SSH用户')
    sshport = models.IntegerField(default=9022, help_text='服务器SSH端口')
    machine_model = models.CharField(max_length=20, help_text='机器型号')
    cpu_num = models.IntegerField(help_text='cpu核心数')
    cpu = models.CharField(max_length=100, help_text='CPU')
    ram = models.CharField(max_length=20, help_text='内存')
    disk = models.CharField(max_length=100, help_text='硬盘')
    host_comment = models.CharField(max_length=20, help_text='用途')
    belongs_to_host = models.CharField(max_length=20, blank=True, null=True, help_text='所属的宿主机')
    host_identifier = models.CharField(max_length=100, unique=True, help_text='主机的唯一标识符')
    opsmanager = models.ForeignKey(OpsManager, null=True, blank=True, on_delete=models.SET_NULL, help_text=u'所属运维管理机')
    password = models.CharField(max_length=100, null=True, blank=True, help_text='主机root密码')

    class Meta:
        db_table = 'assets_host'
        unique_together = ('belongs_to_game_project', 'belongs_to_room', 'internal_ip')

    def __str__(self):
        return self.belongs_to_room.room_name + ':' + self.belongs_to_business.business_name + ':' + self.internal_ip

    def show_all(self, project_name=True):
        return {
            'id': self.id,
            'status': self.get_status_display(),
            'host_class': self.get_host_class_display(),
            'belongs_to_game_project':
                self.belongs_to_game_project.project_name
                if project_name else self.belongs_to_game_project.project_name_en,
            'belongs_to_room': self.belongs_to_room.area.chinese_name + '-' + self.belongs_to_room.room_name,
            'machine_type': self.get_machine_type_display(),
            'belongs_to_business': self.belongs_to_business.business_name,
            'platform': self.platform,
            'internal_ip': self.internal_ip,
            'telecom_ip': self.telecom_ip,
            'unicom_ip': self.unicom_ip,
            'system': self.get_system_display(),
            'is_internet': self.get_is_internet_display(),
            'sshuser': self.sshuser,
            'sshport': self.sshport,
            'machine_model': self.machine_model,
            'cpu_num': self.cpu_num,
            'cpu': self.cpu,
            'ram': self.ram,
            'disk': self.disk,
            'host_comment': self.host_comment,
            'belongs_to_host': self.belongs_to_host,
            'host_identifier': self.host_identifier,
            'opsmanager': self.opsmanager.project.project_name + '-' + self.opsmanager.room.room_name + '-' + self.opsmanager.url
            if self.opsmanager else '',
            'password': self.password if self.password else '',
            'area': self.belongs_to_room.area.chinese_name if self.belongs_to_room else '',
        }

    def edit_data(self):
        return {
            'id': self.id,
            'status': self.status,
            'host_class': self.host_class,
            'belongs_to_game_project': {'id': self.belongs_to_game_project.id,
                                        'text': self.belongs_to_game_project.project_name},
            'belongs_to_room': {'id': self.belongs_to_room.id,
                                'text': self.belongs_to_room.area.chinese_name + '-' + self.belongs_to_room.room_name},
            'machine_type': self.machine_type,
            'belongs_to_business': {'id': self.belongs_to_business.id,
                                    'text': self.belongs_to_business.business_name},
            'platform': self.platform,
            'internal_ip': self.internal_ip,
            'telecom_ip': self.telecom_ip,
            'unicom_ip': self.unicom_ip,
            'system': self.system,
            'is_internet': self.is_internet,
            'sshuser': self.sshuser,
            'sshport': self.sshport,
            'machine_model': self.machine_model,
            'cpu_num': self.cpu_num,
            'cpu': self.cpu,
            'ram': self.ram,
            'disk': self.disk,
            'host_comment': self.host_comment,
            'belongs_to_host': self.belongs_to_host,
            'host_identifier': self.host_identifier,
            'opsmanager': {
                'id': self.opsmanager_id if self.opsmanager else 0,
                'text': self.opsmanager.project.project_name + '-' + self.opsmanager.room.room_name + '-' + self.opsmanager.url
                if self.opsmanager else '无'
            },
            'password': self.password if self.password else '',
        }

    def show_usage(self):
        return {
            'id': self.id,
            'project': self.belongs_to_game_project.project_name if self.belongs_to_game_project else '',
            'room': self.belongs_to_room.area.chinese_name + '-' + self.belongs_to_room.room_name if self.belongs_to_room else '',
            'business': self.belongs_to_business.business_name if self.belongs_to_business else '',
            'extranet_ip': self.telecom_ip if self.telecom_ip else '',
            'cpu_num': self.cpu_num,
            'ram': self.ram,
            'disk': self.disk,
            'game_server': ','.join([x.srv_id for x in self.gameserver_set.all() if
                                     x.srv_status == 0]) if self.gameserver_set.all() else '',
            'game_server_count': len(
                [x for x in self.gameserver_set.all() if x.srv_status == 0]) if self.gameserver_set.all() else 0,
            'usage': self.usage(),
        }

    def usage(self):
        srv_count = len([x for x in self.gameserver_set.all() if x.srv_status == 0])
        if self.belongs_to_business.business_name == 'backup' and not self.gameserver_set.all():
            return 100
        elif len([x.game_type for x in self.gameserver_set.all()]) > 1:
            return 100
        else:
            if self.belongs_to_business.business_name == 'cross':
                if self.cpu_num > 8:
                    return round((float(srv_count) * 5 / (float(24))) * 100, 2)
                else:
                    return round((float(srv_count) * 4 / self.cpu_num) * 100, 2)
            if self.belongs_to_business.business_name == 'game':
                if self.cpu_num <= 8:
                    SrvMax = self.cpu_num - 3
                elif 12 <= self.cpu_num <= 16:
                    SrvMax = self.cpu_num - 6
                elif self.cpu_num >= 24:
                    SrvMax = 24 - 10
                else:
                    SrvMax = self.cpu_num - 6
                return round(float(srv_count) / float(SrvMax) * 100, 2)
            else:
                return 100

    def get_opsmanager_obj(self):
        return self.opsmanager if self.opsmanager else None

    def get_sid_list(self):
        return [x.sid for x in self.gameserver_set.filter(srv_status=0, merge_id=None) if x.sid]

    def saltstack_show_all(self, project_name=True):
        return {
            'id': self.id,
            'status': self.get_status_display(),
            'belongs_to_game_project':
                self.belongs_to_game_project.project_name
                if project_name else self.belongs_to_game_project.project_name_en,
            'belongs_to_room': self.belongs_to_room.area.chinese_name + '-' + self.belongs_to_room.room_name,
            'belongs_to_business': self.belongs_to_business.business_name,
            'platform': self.platform,
            'internal_ip': self.internal_ip,
            'telecom_ip': self.telecom_ip,
            'unicom_ip': self.unicom_ip,
            'host_comment': self.host_comment,
            'area': self.belongs_to_room.area.chinese_name if self.belongs_to_room else '',
        }

    def get_host_ip(self):
        if self.telecom_ip:
            return '电信IP：' + str(self.telecom_ip or '')
        elif self.internal_ip:
            return '内网IP：' + str(self.internal_ip or '')
        elif self.unicom_ip:
            return '联通IP：' + str(self.unicom_ip or '')
        else:
            return ''


class HostHistoryRecord(models.Model):
    TYPE = (
        (1, u'新增'),
        (2, u'修改'),
        (3, u'删除')
    )
    host = models.ForeignKey(Host, null=True, blank=True, on_delete=models.SET_NULL, verbose_name=u'所属主机',
                             help_text=u'所属主机')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间', help_text=u'创建时间')
    operation_user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, verbose_name=u'操作人',
                                       help_text=u'操作人')
    type = models.IntegerField(choices=TYPE, verbose_name=u'变更类型', help_text=u'变更类型')
    alter_field = models.CharField(max_length=50, verbose_name=u'变更字段', help_text=u'变更字段')
    old_content = models.CharField(max_length=120, null=True, blank=True, verbose_name=u'变更前内容', help_text=u'变更前内容')
    new_content = models.CharField(max_length=120, null=True, blank=True, verbose_name=u'变更后内容', help_text=u'变更后内容')
    remark = models.TextField(null=True, blank=True, verbose_name=u'备注', help_text=u'备注')
    source_ip = models.CharField(null=True, blank=True, max_length=30, verbose_name=u'来源IP')

    class Meta:
        verbose_name = u'主机信息变更记录表'
        verbose_name_plural = verbose_name

    def show_all(self):
        return {
            'id': self.id,
            'host': self.host.belongs_to_room.room_name + ':' + self.host.belongs_to_business.business_name + ':' +
                    str(self.host.internal_ip or '') if self.host else self.remark,
            'telecom_ip': self.host.get_host_ip() if self.host else self.remark,
            'project': self.host.belongs_to_game_project.project_name if self.host else '',
            'room': self.host.belongs_to_room.room_name if self.host else '',
            'business': self.host.belongs_to_business.business_name if self.host else '',
            'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            'operation_user': self.operation_user.username if self.operation_user else 'cmdb',
            'type': self.get_type_display(),
            'alter_field': self.alter_field,
            'old_content': self.old_content,
            'new_content': self.new_content,
            'remark': self.remark,
            'source_ip': self.source_ip,
        }

    def show_record(self):
        if self.type == 2:
            return {
                'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S'),
                'operation_user': self.operation_user.username if self.operation_user else 'cmdb',
                'type': self.get_type_display(),
                'alter_detail': [str(self.alter_field or '') + '：' + str(self.old_content or '') + ' --> ' + str(
                    self.new_content or '')],
                'source_ip': self.source_ip if self.source_ip else '',
            }
        else:
            return {
                'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S'),
                'operation_user': self.operation_user.username if self.operation_user else 'cmdb',
                'type': self.get_type_display(),
                'source_ip': self.source_ip if self.source_ip else '',
            }

    def __unicode__(self):
        return self.alter_field + ':' + str(self.old_content or '') + '-->' + str(self.new_content or '')


class FullCalendar(models.Model):
    """FullCalendar Event 表"""
    title = models.CharField(max_length=30, help_text='事件标题')
    allDay = models.NullBooleanField(blank=True, null=True, help_text='全天')
    color = models.CharField(max_length=20, blank=True, null=True, help_text='颜色')

    class Meta:
        db_table = 'cmdb_fullcalendar'

    def __str__(self):
        return self.title

    def show_all(self):
        return {
            'id': self.id,
            'title': self.title,
            'allDay': self.allDay,
            'start': self.start,
            'end': self.end,
            'color': self.color
        }

    def edit_data(self):
        # 根据title获取所属项目和用户
        title = self.title

        related_user_obj = User.objects.get(username=title.split('#')[1])
        project_name_obj = GameProject.objects.get(project_name=title.split('#')[0])

        return {
            'id': self.id,
            'game_project_id': project_name_obj.id,
            'game_project': project_name_obj.project_name,
            'related_user_id': related_user_obj.id,
            'related_user': related_user_obj.username,
            'start': self.start.strftime('%Y-%m-%d'),
            'end': self.end.strftime('%Y-%m-%d')
        }


class SaltTask(models.Model):
    name = models.CharField(max_length=50, verbose_name=u'任务名称')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name=u'最新同步时间')
    status = models.IntegerField(choices=((0, u'禁用'), (1, u'启用')), default=1, verbose_name=u'推送状态')

    class Meta:
        verbose_name = u'saltstack任务表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class SaltTaskExecuteHistory(models.Model):
    salt_task = models.ForeignKey(SaltTask, on_delete=models.CASCADE, verbose_name=u'所属salt任务')
    run_targets = models.TextField(null=True, blank=True, verbose_name=u'执行对象，主机IP列表')
    execute_time = models.DateTimeField(auto_now_add=True, verbose_name=u'执行时间')
    execute_user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, verbose_name=u'执行人')
    execute_result = models.TextField(null=True, blank=True, verbose_name=u'执行结果')

    class Meta:
        verbose_name = u'salt任务执行历史记录'
        verbose_name_plural = verbose_name

    def format_run_target(self):
        """格式化执行主机对象，如果执行主机数大于5，这只显示前5台，其他用省略号代替"""
        targets_list = self.run_targets.replace("'", "").strip("[]").strip().split(',')
        if len(list(targets_list)) > 5:
            targets_list = targets_list[:5]
            targets_char = ''
            for x in targets_list:
                targets_char += x + ', '
            targets_char += '......'
        else:
            targets_char = ''
            for x in targets_list:
                targets_char += x + ', '
        return targets_char

    def get_execute_result(self):
        """汇总主机执行任务结果，若所有主机失败，则返回全部失败，若部分成功部分失败，则返回部分失败，若全部成功，则返回全部成功"""
        status_list = list(set([x.status for x in self.saltexecutehistorydetail_set.all()]))
        if len(status_list) > 1:
            return '部分失败'
        if len(status_list) == 1:
            if status_list[0] == 0:
                return '全部失败'
            else:
                return '全部成功'

    def __str__(self):
        return self.salt_task.name + '-' + str(self.execute_time) + '-' + self.execute_user.username


class SaltExecuteHistoryDetail(models.Model):
    STATUS = (
        (0, '执行失败'),
        (1, '执行成功'),
    )
    execute_history = models.ForeignKey(SaltTaskExecuteHistory, on_delete=models.CASCADE, verbose_name=u'所属执行历史记录')
    host = models.ForeignKey(Host, on_delete=models.CASCADE, verbose_name=u'执行主机')
    status = models.IntegerField(choices=STATUS, default=1, verbose_name=u'执行状态')
    result = models.TextField(null=True, blank=True, verbose_name=u'执行结果')

    class Meta:
        verbose_name = u'saltstack任务执行历史记录明细'
        verbose_name_plural = verbose_name

    def show_all(self):
        return {
            'id': self.id,
            'area': self.host.belongs_to_room.area.chinese_name,
            'belongs_to_game_project': self.host.belongs_to_game_project.project_name,
            'belongs_to_room': self.host.belongs_to_room.area.chinese_name + '-' + self.host.belongs_to_room.room_name,
            'belongs_to_business': self.host.belongs_to_business.business_name,
            'platform': self.host.platform,
            'internal_ip': self.host.internal_ip,
            'telecom_ip': self.host.telecom_ip,
            'unicom_ip': self.host.unicom_ip,
            'host_comment': self.host.host_comment,
            'execute_status': self.get_status_display(),
        }

    def __str__(self):
        return self.host.telecom_ip


class SaltConfig(models.Model):
    salt_task = models.ForeignKey(SaltTask, on_delete=models.CASCADE, verbose_name=u'所属saltstack任务')
    filename = models.CharField(max_length=30, verbose_name=u'配置文件名')
    content = models.TextField(null=True, blank=True, verbose_name=u'配置内容')
    push_path = models.CharField(max_length=80, null=True, blank=True, verbose_name=u'推送远程路径')
    modified_user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, verbose_name=u'修改人')
    modified_time = models.DateTimeField(auto_now=True, null=True, blank=True, verbose_name=u'修改时间')

    class Meta:
        verbose_name = u'saltstack任务配置表'
        verbose_name_plural = verbose_name

    def get_last_execute_user(self):
        """获取最后一次执行任务的用户"""
        if self.salt_task.salttaskexecutehistory_set.all():
            return self.salt_task.salttaskexecutehistory_set.order_by('-id')[0].execute_user.username
        else:
            return ''

    def get_last_execute_time(self):
        """获取最后一次执行时间"""
        if self.salt_task.salttaskexecutehistory_set.all():
            return self.salt_task.salttaskexecutehistory_set.order_by('-id')[0].execute_time
        else:
            return ''

    def get_last_execute_result(self):
        """获取最后一次执行执行结果"""
        if self.salt_task.salttaskexecutehistory_set.all():
            return self.salt_task.salttaskexecutehistory_set.order_by('-id')[0].get_execute_result()
        else:
            return ''

    def if_exist_unreleased_status(self):
        """若存在推送状态为未推送，则返回True，否则返回False"""
        if list(set([release.status for release in self.release_set.all()])) == [1]:
            return False
        else:
            return True

    def __str__(self):
        return self.salt_task.name + '-' + self.filename


class SaltConfigHistory(models.Model):
    salt_config = models.ForeignKey(SaltConfig, on_delete=models.CASCADE, verbose_name=u'所属salt配置文件')
    modified_time = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')
    type = models.IntegerField(choices=((1, u'新增'), (2, u'修改'), (3, u'删除'), (4, u'回滚')), verbose_name=u'类型')
    content = models.TextField(null=True, blank=True, verbose_name=u'修改后内容')
    modified_user = models.ForeignKey(User, verbose_name=u'修改人')
    remark = models.TextField(null=True, blank=True, verbose_name=u'修改原因备注')

    class Meta:
        verbose_name = u'salt配置历史记录表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.salt_config.salt_task.name + '-' + self.salt_config.filename + '-' + self.get_type_display()


class Release(models.Model):
    salt_config = models.ForeignKey(SaltConfig, on_delete=models.CASCADE, verbose_name=u'所属salt配置文件')
    status = models.IntegerField(choices=((1, u'已推送'), (2, u'未推送')), default=2, verbose_name=u'推送状态')
    release_user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, verbose_name=u'下发人')
    release_time = models.DateTimeField(null=True, blank=True, verbose_name=u'下发时间')

    class Meta:
        verbose_name = u'配置推送状态表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.salt_config.salt_task.name + '-' + self.salt_config.filename + '-' + self.get_status_display()


class SaltCommandHistory(models.Model):
    """salt命令执行记录"""
    execute_time = models.DateTimeField(auto_now_add=True, verbose_name=u'执行时间')
    execute_user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=u'执行人')
    command = models.CharField(max_length=200, verbose_name=u'执行的命令')
    result = models.TextField(default='', verbose_name=u'执行结果')

    class Meta:
        verbose_name = u'salt命令执行记录'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.command


class CDN(models.Model):
    name = models.CharField(max_length=30, verbose_name=u'CDN供应商')

    class Meta:
        verbose_name = u'cdn供应商表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class CDNAPI(models.Model):
    cdn = models.ForeignKey(CDN, on_delete=models.CASCADE, verbose_name=u'所属CDN供应商')
    auth = models.IntegerField(choices=((1, 'token'), (2, 'secretId+secretKey')), verbose_name=u'接口认证方式')
    token = models.CharField(max_length=100, null=True, blank=True, verbose_name=u'接口token')
    secret_id = models.CharField(max_length=100, null=True, blank=True, verbose_name=u'接口secretId')
    secret_key = models.CharField(max_length=100, null=True, blank=True, verbose_name=u'接口secretKey')
    remark = models.TextField(null=True, blank=True, verbose_name=u'备注')
    game_project = models.ManyToManyField(GameProject, verbose_name=u'与游戏项目的关系')
    area = models.CharField(max_length=30, null=True, blank=True, verbose_name=u'适用地区')

    class Meta:
        verbose_name = u'CDN供应商接口信息表'
        verbose_name_plural = verbose_name
        unique_together = ('cdn', 'token', 'secret_id', 'secret_key')

    def edit_data(self):
        return {
            'cdn_supplier_id': self.cdn.id,
            'cdn_supplier': self.cdn.name,
            'auth': self.auth,
            'token': self.token,
            'secret_id': self.secret_id,
            'secret_key': self.secret_key,
            'remark': self.remark,
            'game_project': [{'id': x.id, 'name': x.project_name} for x in
                             self.game_project.all()] if self.game_project.all() else '',
            'area': self.area,
        }

    def __str__(self):
        if self.auth == 2:
            return self.cdn.name + '-' + self.secret_id + '-' + self.secret_key
        if self.auth == 1:
            return self.cdn.name + '-' + self.token


class CDNRefreshRecord(models.Model):
    commit_time = models.DateTimeField(auto_now_add=True, verbose_name=u'提交刷新时间')
    commit_user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, verbose_name=u'提交人')
    cdn_api = models.ForeignKey(CDNAPI, null=True, blank=True, on_delete=models.SET_NULL, verbose_name=u'所使用的cdn接口')
    refresh_obj = models.TextField(max_length=200, verbose_name=u'提交刷新对象url或dir')
    task_id = models.CharField(max_length=30, null=True, blank=True, verbose_name=u'刷新任务编号')
    result = models.IntegerField(choices=((-1, u'刷新失败'), (0, u'刷新中'), (1, u'刷新成功'), (2, u'待处理')), null=True, blank=True,
                                 verbose_name=u'刷新结果')
    remark = models.CharField(max_length=50, null=True, blank=True, verbose_name=u'记录刷新失败原因')
    auto_refresh = models.IntegerField(default=0, verbose_name=u'自动查询结果次数')
    finish_time = models.DateTimeField(null=True, blank=True, verbose_name=u'刷新完成时间')

    class Meta:
        verbose_name = u'cdn刷新记录表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.task_id + '-' + self.get_result_display() if self.result else ''


class HostInitialize(models.Model):
    """主机初始化"""
    INSTALL_STATUS = (
        (0, '未安装'),
        (1, '安装中'),
        (2, '安装成功'),
        (3, '安装失败'),
    )
    INITIALIZE_STATUS = (
        (0, '未初始化'),
        (1, '初始化中'),
        (2, '初始化成功'),
        (3, '初始化失败'),
    )
    REBOOT_STATUS = (
        (0, '未重启'),
        (1, '重启中'),
        (2, '重启成功'),
        (3, '重启失败'),
    )
    IMPORT_STATUS = (
        (0, '未入库'),
        (1, '入库中'),
        (2, '入库成功'),
        (3, '入库失败'),
    )
    INSTANCE_STATE = (
        ('PENDING', '创建中'),
        ('LAUNCH_FAILED', '创建失败'),
        ('RUNNING', '运行中'),
        ('STOPPED', '关机'),
        ('STARTING', '开机中'),
        ('STOPPING', '关机中'),
        ('REBOOTING', '重启中'),
        ('SHUTDOWN', '停止待销毁'),
        ('TERMINATING', '销毁中'),
    )
    telecom_ip = models.GenericIPAddressField(unique=True, blank=True, null=True, verbose_name=u'外网ip')
    sshuser = models.CharField(max_length=20, default='root', verbose_name=u'ssh用户')
    sshport = models.IntegerField(default=22, verbose_name=u'ssh端口')
    password = models.CharField(max_length=100, null=True, blank=True, verbose_name=u'ssh密码')
    project = models.ForeignKey(GameProject, null=True, blank=True, on_delete=models.SET_NULL, verbose_name=u'所属项目')
    room = models.ForeignKey(Room, null=True, blank=True, on_delete=models.SET_NULL, verbose_name=u'所属机房')
    syndic_ip = models.GenericIPAddressField(blank=True, null=True, verbose_name=u'salt-syndic的IP')
    business = models.ForeignKey(Business, null=True, blank=True, on_delete=models.SET_NULL, help_text='业务类型')
    add_time = models.DateTimeField(auto_now=True, verbose_name=u'添加时间')
    add_user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, verbose_name=u'添加人')
    install_status = models.IntegerField(choices=INSTALL_STATUS, default=0, verbose_name=u'saltstack客户端安装状态')
    install_remark = models.TextField(default='', verbose_name=u'saltstack客户端安装情况')
    initialize_status = models.IntegerField(choices=INITIALIZE_STATUS, default=0, verbose_name=u'初始化状态')
    initialize_remark = models.TextField(default='', verbose_name=u'初始化情况')
    reboot_status = models.IntegerField(choices=REBOOT_STATUS, default=0, verbose_name=u'主机重启状态')
    instance_id = models.CharField(max_length=30, null=True, blank=True, verbose_name=u'云实例ID')
    instance_state = models.CharField(max_length=20, choices=INSTANCE_STATE, default='RUNNING', verbose_name=u'实例状态')
    import_status = models.IntegerField(choices=IMPORT_STATUS, default=0, verbose_name=u'入库状态')

    class Meta:
        verbose_name = u'主机初始化'
        verbose_name_plural = verbose_name

    def get_whole_status(self):
        if self.install_status == 2 and self.initialize_status == 2 and self.reboot_status == 2 and self.import_status == 2:
            return '初始化成功'
        elif self.install_status == 3 or self.initialize_status == 3 or self.reboot_status == 3 or self.import_status == 3:
            return '初始化失败'
        elif self.install_status == 1 or self.initialize_status == 1 or self.reboot_status == 1 or self.import_status == 1:
            return '初始化中'
        else:
            return '待处理'

    def show_all(self):
        return {
            'id': self.id,
            'add_user': self.add_user.username,
            'add_time': str(self.add_time)[:19],
            'telecom_ip': self.telecom_ip,
            'sshuser': self.sshuser,
            'sshport': self.sshport,
            'syndic_ip': self.syndic_ip,
            'business': self.business.business_name if self.business else '',
            'project': self.project.project_name,
            'room': self.room.area.chinese_name + '-' + self.room.room_name if self.room else '',
            'install_status': self.get_install_status_display(),
            'initialize_status': self.get_initialize_status_display(),
            'reboot_status': self.get_reboot_status_display(),
            'instance_state': self.get_instance_state_display(),
            'import_status': self.get_import_status_display(),
        }

    def edit_data(self):
        return {
            'telecom_ip': self.telecom_ip,
            'sshuser': self.sshuser,
            'sshport': self.sshport,
            'password': self.password,
            'syndic_ip': self.syndic_ip,
            'project_id': self.project.id,
            'project': self.project.project_name,
            'room_id': self.room.id if self.room else 0,
            'room': self.room.area.chinese_name + '-' + self.room.room_name if self.room else '',
            'business_id': self.business.id if self.business else 0,
            'business': self.business.business_name if self.business else '',
            'install_status': self.install_status,
            'initialize_status': self.initialize_status,
            'reboot_status': self.reboot_status,
            'instance_state': self.instance_state,
            'import_status': self.import_status,
        }

    def __str__(self):
        return self.telecom_ip if self.telecom_ip else ''


class HostInitializeLog(models.Model):
    """主机初始化日志"""
    host_initialize = models.OneToOneField(HostInitialize, verbose_name=u'所属主机初始化记录')
    content = models.TextField(default='', verbose_name=u'日日志内容')

    class Meta:
        verbose_name = u'主机初始化日志'
        verbose_name_plural = verbose_name


class Cloud(models.Model):
    """云供应商"""
    name = models.CharField(max_length=30, default='', unique=True, verbose_name=u'云供应商名称')

    class Meta:
        verbose_name = u'云供应商表'
        verbose_name_plural = verbose_name

    def show_all(self):
        if self.name == '腾讯云':
            href = '/assets/tecent_cloud_account/'
        else:
            href = ''
        return {
            'id': self.id,
            'name': self.name,
            'href': href
        }

    def __str__(self):
        return self.name


class TecentCloudAccount(models.Model):
    """腾讯云帐号信息"""
    cloud = models.ForeignKey(Cloud, null=True, blank=True, on_delete=models.SET_NULL, verbose_name=u'关联云帐号信息')
    secret_id = models.CharField(max_length=100, null=True, blank=True, verbose_name=u'接口secretId')
    secret_key = models.CharField(max_length=100, null=True, blank=True, verbose_name=u'接口secretKey')
    remark = models.CharField(max_length=50, unique=True, verbose_name=u'备注')

    class Meta:
        verbose_name = '腾讯云帐号信息表'
        verbose_name_plural = verbose_name

    def show_all(self):
        return {
            'id': self.id,
            'cloud': self.cloud.name,
            'secret_id': self.secret_id,
            'secret_key': self.secret_key,
            'remark': self.remark
        }

    def edit_data(self):
        return {
            'id': self.id,
            'secret_id': self.secret_id,
            'secret_key': self.secret_key,
            'remark': self.remark
        }

    def __str__(self):
        return self.cloud.name + '-' + self.remark
