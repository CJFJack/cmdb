# -*- encoding: utf-8 -*-

from django.db import models

from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from assets.models import GameProject
from assets.models import ProjectGroup
from assets.models import Host
from assets.models import GroupSection
from assets.models import OpsManager
from it_assets.models import CompanyCode
from mysql.models import MysqlInstance

from mptt.models import MPTTModel, TreeForeignKey

import json

# from collections import namedtuple

"""
create an auxiliary model with no database table
That model can bring to your project any permission you need
There is no need to deal with ContentType or create Permission objects explicit
"""


# Create your models here.


class Profile(models.Model):
    """用户模型的扩展

    采用的办法是该模型和用户模型一对一的关联

    增加人员状态字段
    最后修改时间字段

    以后有额外的用户模型的字段扩充，都可以
    通过这个模型增加字段

    """

    STATUS = (
        (0, '在职'),
        (1, '离职'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, help_text='所属的用户')
    status = models.IntegerField(choices=STATUS, default=1, help_text='员工状态')
    last_modified = models.DateField(blank=True, null=True, help_text='最后修改时间')
    project_group = models.ForeignKey(
        ProjectGroup, blank=True, null=True, default=None, on_delete=models.SET_NULL, help_text='项目分组')
    user_key = models.CharField(max_length=1000, blank=True, null=True, default=None, help_text='用户key')
    with_host = models.ManyToManyField(Host, through='UserProfileHost')
    one_group = models.ForeignKey(Group, blank=True, null=True, default=None, on_delete=models.PROTECT)  # 唯一的部门
    group_section = models.ForeignKey(GroupSection, blank=True, null=True, default=None, on_delete=models.PROTECT)
    hot_update_email_approve = models.BooleanField(default=True, help_text='是否开启热更新邮件审批')
    telphone = models.CharField(max_length=100, blank=True, null=True, default=None, help_text='电话')

    class Meta:
        db_table = 'users_profile'

    def __str__(self):
        return self.user.username


class UserClearStatus(models.Model):
    """用户扩展清理情况
    server_permission, svn, samba都是json格式
    """

    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, help_text='用户扩展')
    server_permission = models.TextField(blank=True, null=True, default=None, help_text='清除服务器权限的情况')
    svn = models.TextField(blank=True, null=True, default=None, help_text='清除svn的情况')
    svn2 = models.CharField(max_length=255, blank=True, null=True, default=None, help_text='清除svn2的情况')
    samba = models.CharField(max_length=255, blank=True, null=True, default=None, help_text='清除samba的情况')
    mysql_permission = models.TextField(blank=True, null=True, default=None, help_text='清除数据库权限的情况')
    ldap = models.CharField(max_length=255, blank=True, null=True, default=None, help_text='清除ldap账号情况')
    ent_qq = models.CharField(max_length=500, blank=True, null=True, default=None, help_text='清除企业QQ账号情况')
    ent_email = models.CharField(max_length=500, blank=True, null=True, default=None, help_text='清除企业邮箱账号情况')
    wifi = models.CharField(max_length=255, blank=True, null=True, default=None, help_text='清除wifi账号情况')
    openvpn = models.CharField(max_length=255, blank=True, null=True, default=None, help_text='清除openvpn账号情况')

    class Meta:
        db_table = 'users_clear_status'

    def get_server_permission_info(self, server_permission):
        """获取清除服务器权限的字符串
        """

        if server_permission:
            ops_ip = server_permission.get('ops_ip')
            info = "服务器权限:<br>"
            fail_info = ""
            success_info = ""
            ing_info = ""
            for ip in ops_ip:
                url = 'https://' + ip + '/api/'
                ops_obj = OpsManager.objects.filter(url=url).first()
                if ops_obj:
                    if server_permission.get(ip, None):
                        if server_permission[ip].get('success', False):
                            msg = "项目：%s，地区：%s，机房：%s，运维管理机@%s: 清除完成<br>" % (
                                ops_obj.project.project_name, ops_obj.room.area.chinese_name, ops_obj.room.room_name,
                                ip)
                            success_info += msg
                        else:
                            msg = "<span class=\"text-danger\">项目：%s，地区：%s，机房：%s，运维管理机@%s: 清除失败 %s</span><br>" % (
                                ops_obj.project.project_name, ops_obj.room.area.chinese_name, ops_obj.room.room_name,
                                ip,
                                server_permission[ip].get('result', ''))
                            fail_info += msg
                    else:
                        msg = "<span class=\"text-warning\">项目：%s，地区：%s，机房：%s，运维管理机@%s: 清除中...</span><br>" % (
                            ops_obj.project.project_name, ops_obj.room.area.chinese_name, ops_obj.room.room_name, ip)
                        ing_info += msg

            info = info + fail_info + ing_info + success_info
        else:
            info = ''
        return info

    def get_mysql_permission_info(self, mysql_permission):
        """获取清除mysql权限的字符串
        {
            '203.74.37.187:3306': {'result': '清理用户完毕', 'success': True},
            '61.28.245.6:3306': {'result': '清理用户完毕', 'success': True},
            'mysql_instance': ['203.74.37.187:3306', '61.28.245.6:3306']
        }
        """

        if mysql_permission:
            info = "mysql账号:<br>"
            fail_info = ""
            success_info = ""
            ing_info = ""
            mysql_instance = mysql_permission.get('mysql_instance')
            for instance in mysql_instance:
                if mysql_permission.get(instance, None):
                    mysql_obj = MysqlInstance.objects.filter(host=instance.split(':')[0]).first()
                    if mysql_obj:
                        if mysql_permission[instance].get('success', False):
                            msg = '项目：%s，用途：%s，mysql@%s: 清除账号完成<br>' % (
                                mysql_obj.project.project_name, mysql_obj.purpose, instance)
                            success_info += msg
                        else:
                            msg = '<span class=\"text-danger\">项目：%s，用途：%s，mysql@%s: 清除账号失败 %s</span><br>' % (
                                mysql_obj.project.project_name, mysql_obj.purpose, instance,
                                mysql_permission[instance].get('result', ''))
                            fail_info += msg
                else:
                    msg = '<span class=\"text-warning\">mysql@%s: 清除中...</span><br>' % (instance)
                    ing_info += msg

            info += fail_info + ing_info + success_info
        else:
            info = ''
        return info

    def get_svn_info(self, svn):
        """获取清除svn信息
        """

        if svn:
            if 'success' in svn:
                if svn.get('success', False):
                    info = "SVN: 所有项目清除完成<br>"
                else:
                    info = "<span class=\"text-danger\">SVN: 清除失败 %s</span><br>" % (svn.get('result', ''),)
            else:
                info = 'SVN权限<br>'
                for k, v in svn.items():
                    project_obj = GameProject.objects.filter(project_name_en=k)
                    if not project_obj:
                        continue
                    if v.get('success', False):
                        info += "项目：{}: 清除完成<br>".format(project_obj[0].project_name)
                    else:
                        info += "<span class=\"text-danger\">项目：{}：清除失败 {}</span><br>".format(project_obj[0].project_name,
                                                                                              v.get('result', ''))
        else:
            info = ''
        return info

    def get_svn2_info(self, svn2):
        """获取清除svn信息
        """

        if svn2:
            if svn2.get('success', False):
                info = "SVN2: 清除完成<br>"
            else:
                info = "<span class=\"text-danger\">SVN2: 清除失败 %s</span><br>" % (svn2.get('result', ''))
        else:
            info = ''
        return info

    def get_samba_info(self, samba):
        """获取清除samba信息
        """

        if samba:
            if samba.get('success', False):
                info = "samba: 清除完成<br>"
            else:
                info = "<span class=\"text-danger\">samba: 清除失败 %s</span><br>" % (samba.get('result', ''))
        else:
            info = ''
        return info

    def get_ldap_info(self, ldap):
        """获取清除svn信息
        """

        if ldap:
            if ldap.get('success', False):
                info = "ldap: 清除完成<br>"
            else:
                info = "<span class=\"text-danger\">ldap: 清除失败 %s</span><br>" % (ldap.get('result', ''))
        else:
            info = ''
        return info

    def get_ent_qq_info(self, ent_qq):
        """获取清除企业QQ信息
        """

        if ent_qq:
            if ent_qq.get('ret', True):
                info = "企业QQ: 清除完成<br>"
            else:
                info = "<span class=\"text-danger\">企业QQ: 清除失败 %s</span><br>" % (ent_qq.get('msg', ''))
        else:
            info = ''
        return info

    def get_ent_email_info(self, ent_email):
        """获取清除企业邮箱信息
        """
        info = ''
        if ent_email:
            try:
                for x in ent_email.keys():
                    if ent_email[x]['ret']:
                        info = info + "企业邮箱" + x + ": 清除完成<br>"
                    else:
                        info = info + "<span class=\"text-danger\">企业邮箱" + x + ": 清除失败 %s</span><br>" % (
                        ent_email[x]['msg'])
            except:
                if ent_email.get('ret', True):
                    info = "企业邮箱: 清除完成<br>"
                else:
                    info = "<span class=\"text-danger\">企业邮箱: 清除失败 %s</span><br>" % (ent_email.get('msg', ''))
        else:
            info = ''
        return info

    def get_wifi_info(self, wifi):
        """获取清除wifi信息
        """

        if wifi:
            if wifi.get('ret', True):
                info = "wifi: 清除完成<br>"
            else:
                info = "<span class=\"text-danger\">wifi: 清除失败 %s</span><br>" % (wifi.get('msg', ''))
        else:
            info = ''
        return info

    def get_openvpn_info(self, openvpn):
        """获取清除openvpn信息
        """

        if openvpn:
            if openvpn.get('ret', True):
                info = "OpenVPN: 清除完成<br>"
            else:
                info = "<span class=\"text-danger\">OpenVPN: 清除失败 %s</span><br>" % (openvpn.get('msg', ''))
        else:
            info = ''
        return info

    def show_process_info(self):
        """展示清除的结果
        """
        server_permission = json.loads(self.server_permission) if self.server_permission else ''
        server_permission_info = self.get_server_permission_info(server_permission)

        mysql_permission = json.loads(self.mysql_permission) if self.mysql_permission else ''
        mysql_permission_info = self.get_mysql_permission_info(mysql_permission)

        svn = json.loads(self.svn) if self.svn else ''
        svn_info = self.get_svn_info(svn)

        svn2 = json.loads(self.svn2) if self.svn2 else ''
        svn2_info = self.get_svn2_info(svn2)

        samba = json.loads(self.samba) if self.samba else ''
        samba_info = self.get_samba_info(samba)

        ldap = json.loads(self.ldap) if self.ldap else ''
        # print(self.ldap, type(self.ldap))
        # ldap = ''
        ldap_info = self.get_ldap_info(ldap)

        ent_qq = json.loads(self.ent_qq) if self.ent_qq else ''
        ent_qq_info = self.get_ent_qq_info(ent_qq)

        ent_email = json.loads(self.ent_email) if self.ent_email else ''
        ent_email_info = self.get_ent_email_info(ent_email)

        wifi = json.loads(self.wifi) if self.wifi else ''
        wifi_info = self.get_wifi_info(wifi)

        openvpn = json.loads(self.openvpn) if self.openvpn else ''
        openvpn_info = self.get_openvpn_info(openvpn)

        return server_permission_info + svn_info + svn2_info + samba_info + mysql_permission_info + ldap_info + ent_qq_info + ent_email_info + wifi_info + openvpn_info


class OrganizationMptt(MPTTModel):
    """新组织结构表，包括用户及部门节点两种角色"""
    name = models.CharField(max_length=50, unique=False, verbose_name='组织架构节点名称')
    is_public = models.BooleanField(default=False, verbose_name='是否为公共部门')
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children',
                            verbose_name='父级节点')
    leader = models.IntegerField(default=0, null=True, blank=True, verbose_name='负责人')
    with_host = models.ManyToManyField(Host, verbose_name='用户与服务器关联表')
    hot_update_email_approve = models.BooleanField(default=True, verbose_name='是否开启热更新邮件审批')
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='关联django系统用户User表')
    type = models.IntegerField(default=2, choices=((1, '部门'), (2, '用户')), verbose_name='数据类型，部门或者用户')
    is_active = models.BooleanField(default=True, verbose_name='是否在职')
    project = models.ManyToManyField(GameProject, verbose_name='部门与项目之间关系', help_text='部门与项目之间关系')
    is_department_group = models.BooleanField(default=False, verbose_name='是否部门下分组', help_text='是否部门下分组')
    permission = models.ManyToManyField(Permission, verbose_name='组织节点与权限关系',
                                        help_text='组织节点与权限关系')
    sex = models.IntegerField(choices=((1, '男'), (2, '女')), default=2, verbose_name='性别', help_text='性别')
    title = models.CharField(max_length=20, null=True, blank=True, verbose_name='员工职位', help_text='员工职位')
    ent_qq = models.CharField(max_length=50, null=True, blank=True, verbose_name='企业QQ开通结果', help_text='企业QQ开通结果')
    ent_email = models.CharField(max_length=254, null=True, blank=True, verbose_name='企业邮箱开通结果', help_text='企业邮箱开通结果')
    openvpn = models.IntegerField(choices=((0, u'未开通'), (1, u'已开通')), default=0, verbose_name='是否已经开通openvpn帐号',
                                  help_text='是否已经开通openvpn帐号')
    is_register = models.BooleanField(default=True, verbose_name='是否确认入职')
    wechat_approve = models.BooleanField(default=True, verbose_name=u'是否开启工单微信审批')

    class MPTTMeta:
        order_insertion_by = ['name']

    def get_leader_username(self):
        """获取负责人姓名"""
        if self.leader != 0:
            user = User.objects.filter(pk=self.leader)
            if user:
                return user[0].username
        return ''

    def get_leader_firstname(self):
        """获取负责人名字拼音"""
        if self.leader != 0:
            user = User.objects.filter(pk=self.leader)
            if user:
                return user[0].first_name
        return ''

    def get_leader_org_obj(self):
        """获取负责人的self对象"""
        if self.leader != 0:
            user = User.objects.get(pk=self.leader)
            return OrganizationMptt.objects.get(user=user)
        else:
            return ''

    def get_ancestors_name(self):
        """获取所有父级节点，包括本身，如: 原力互娱-运维部-运维开发组-xxx """
        if self.parent is not None:
            return '-'.join(a.name for a in self.get_ancestors()) + '-' + self.name
        else:
            return self.name

    def get_ancestors_except_self(self):
        """获取所属父级节点，如: 原力互娱-运维部-运维开发组 """
        if self.parent is not None:
            return '-'.join(a.name for a in self.get_ancestors())
        else:
            return self.name

    def get_parent_leader_obj(self):
        """获取父级节点的负责人的user对象"""
        if self.parent:
            if self.parent.leader != 0:
                return User.objects.get(pk=self.parent.leader)
        else:
            return ''

    def get_parent_parent_leader_obj(self):
        """获取父级的父级的负责人的user对象"""
        if self.parent.parent:
            if self.parent.parent.leader != 0:
                return User.objects.get(pk=self.parent.parent.leader)
        else:
            return ''

    def get_all_parent_leader_list(self, is_game_project=False):
        """
        找到self所有上级节点的负责人名字list，并去除最高领导人及self本身
            -->若list为空:
                -->若为游戏项目:
                    -->list加上最高领导人
                -->若非游戏项目:
                    -->返回空list
            -->若list不为空，则不管是否游戏项目，代表已经找到部门负责人，则正常返回list

        """
        if self.type == 2:
            parent_leader_list = []
            if self.user_id == OrganizationMptt.objects.get(pk=1).leader:
                return parent_leader_list
            else:
                for x in self.get_ancestors():
                    if x.get_leader_username() and x.is_active == 1 and x.is_register == 1:
                        parent_leader_list.append(x.get_leader_username())
                if len(parent_leader_list) == 1 and OrganizationMptt.objects.get(
                        pk=1).get_leader_username() in parent_leader_list:
                    if is_game_project and self.user_id != OrganizationMptt.objects.get(pk=1).leader:
                        pass
                    else:
                        parent_leader_list.remove(OrganizationMptt.objects.get(pk=1).get_leader_username())
                else:
                    parent_leader_list.remove(OrganizationMptt.objects.get(pk=1).get_leader_username())
                return parent_leader_list

    def get_department_obj(self):
        """获取部门的self对象"""
        if self.type == 2:
            ancestors_list = self.get_ancestors()
            ancestors_list = ancestors_list.reverse()
            for a in ancestors_list:
                if not a.is_department_group:
                    return a
            else:
                return None

    def get_department_group_obj(self):
        """获取部门下分组的self对象"""
        if self.type == 2:
            if self.parent:
                if self.parent.is_department_group:
                    return self.parent
                else:
                    return None

    def get_user_charge_project(self):
        """获取用户所属部门所属负责的项目"""
        if self.type == 2:
            project_list = []
            for parent in self.get_ancestors():
                if parent.project.all():
                    for project in parent.project.all():
                        project_list.append(project)
            return project_list

    def get_all_children_section_obj_list(self):
        """获取所有组织子节点"""
        return [x for x in OrganizationMptt.objects.filter(type=1, is_active=1, is_register=1) if
                self in x.get_ancestors()]

    def get_all_children_obj_list(self):
        """获取所有子节点（部门/及在职人员）"""
        return [x for x in OrganizationMptt.objects.filter(is_active=1, is_register=1).select_related('parent') if
                self in x.get_ancestors()]

    def get_all_children_user_obj_list(self):
        """获取所有人员子节点"""
        return [x.user for x in self.get_leafnodes() if x.is_active == 1 and x.is_register == 1 and x.type == 2]

    def get_ancestors_except_self_by_slash(self):
        """获取所有父级节点，以斜杠/分割"""
        if self.parent is not None:
            return '/'.join(a.name for a in self.get_ancestors())
        else:
            return ''

    def get_ancestors_by_slash(self):
        """获取所有父级节点，包括自身，以斜杠/分割"""
        if self.parent is not None:
            return '/'.join(a.name for a in self.get_ancestors()) + '/' + self.name
        else:
            return ''

    def get_title(self):
        """获取职位"""
        return self.title if self.title else ''

    def __str__(self):
        return self.name


class OuterAccountTemp(models.Model):
    """开通外部帐号临时表，记录是否需要开通企业qq/企业邮箱/ldap，开通外部帐号后或者删除cmdb用户后删除该记录"""
    IS_EMAIL = (
        (0, '否'),
        (1, '开通forcegames.cn'),
        (2, '开通chuangyuenet.com'),
        (3, '同时开通forcegames.cn和chuangyunet.com'),
    )
    IS_QQ = (
        (0, '否'),
        (1, '是'),
    )
    IS_LDAP = (
        (0, '否'),
        (1, '是'),
    )
    org = models.OneToOneField(OrganizationMptt, on_delete=models.CASCADE, verbose_name=u'所属组织架构表对象')
    is_email = models.IntegerField(choices=IS_EMAIL, default=0, verbose_name=u'是否开通企业邮箱')
    is_qq = models.IntegerField(choices=IS_QQ, default=0, verbose_name=u'是否开通企业QQ')
    is_ldap = models.IntegerField(choices=IS_LDAP, default=0, verbose_name=u'是否开通ldap帐号')

    class Meta:
        verbose_name = u'开通外部帐号临时表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.org.name


class UserProfileHost(models.Model):
    """用户扩展和主机权限的中间表
    """
    T_STATUS = (
        (0, '永久'),
        (1, '临时'),
    )

    R_STATUS = (
        (0, '普通用户'),
        (1, 'root用户'),
    )

    V_STATUS = (
        (0, '过期'),
        (1, '有效'),
    )
    user_profile = models.ForeignKey(Profile, help_text='用户扩展')
    host = models.ForeignKey(Host, help_text='主机')
    start_time = models.DateTimeField(blank=True, null=True, help_text='启始时间')
    end_time = models.DateTimeField(blank=True, null=True, help_text='结束时间')
    temporary = models.IntegerField(choices=T_STATUS, default=1, help_text='是否是临时')
    is_root = models.IntegerField(choices=R_STATUS, default=0, help_text='是否root')
    is_valid = models.IntegerField(choices=V_STATUS, default=1, help_text='是否有效')
    organization = models.ForeignKey(OrganizationMptt, null=True, blank=True, on_delete=models.SET_NULL,
                                     verbose_name='关联新组织架构', help_text='关联新组织架构')

    class Meta:
        db_table = 'userprofile_host'

    def __str__(self):
        return self.user_profile.user.username + ':' + self.host.host_identifier

    def ip_info(self):
        """获取ip的信息
        电信: ip1
        联通: ip2
        内网: ip3
        """
        host = self.host

        telecom_ip_info = '电信: ' + host.telecom_ip if host.telecom_ip else '电信:'

        unicom_ip_info = '联通: ' + host.unicom_ip if host.unicom_ip else '联通:'

        internal_ip_info = '内网: ' + host.internal_ip if host.internal_ip else '内网:'

        return telecom_ip_info + ',' + unicom_ip_info + ',' + internal_ip_info

    def show_all(self):
        return {
            'id': self.id,
            'user': self.user_profile.user.username,
            'host': self.host.host_identifier,
            'host_status': self.host.get_status_display(),
            'ip_info': self.ip_info(),
            'start_time': self.start_time.strftime('%Y-%m-%d %H:%M') if self.start_time else '',
            'end_time': self.end_time.strftime('%Y-%m-%d %H:%M') if self.start_time else '',
            'temporary': self.get_temporary_display(),
            'is_root': self.get_is_root_display(),
            'is_valid': self.get_is_valid_display()
        }


class GroupProfile(models.Model):
    """用户组的模型扩展

    剑雨江湖下面有后台组，美术组，前端组...

    """

    group = models.OneToOneField(Group, on_delete=models.CASCADE, help_text='关联的分组')
    company = models.ForeignKey(CompanyCode, blank=True, null=True, default=None, on_delete=models.PROTECT)
    parent_group = models.ForeignKey(
        Group, on_delete=models.PROTECT, related_name='pgroup', blank=True, null=True, default=None, help_text='父部门')
    project = models.ForeignKey(GameProject, blank=True, null=True, help_text='所属项目')
    is_public = models.BooleanField(default=False, help_text='是否为公共部门')
    project_group_leader = models.ForeignKey(
        User, blank=True, null=True, related_name='project_group_leader', help_text='项目分组的组长')
    group_leader = models.ForeignKey(
        User, blank=True, null=True, related_name='group_leader', help_text='部门负责人')

    class Meta:
        db_table = 'group_profile'

    def __str__(self):
        return self.group.name

    def get_children(self):
        """获取该节点的子节点
        """
        children_nodes = GroupProfile.objects.select_related(
            'parent_group__groupprofile').filter(parent_group__groupprofile=self)
        return children_nodes

    def to_root(self):
        """从一个节点到根节点"""
        node = self
        while node.parent_group:
            node = node.parent_group.groupprofile

        return node

    @classmethod
    def get_root_nodes(cls):
        root_nodes = cls.objects.filter(parent_group=None)
        return root_nodes

    @classmethod
    def get_leaf_nodes(cls):
        leaf_nodes = []
        for gp in cls.objects.all():
            if not gp.get_children():
                leaf_nodes.append(gp)
            elif gp.group.groupsection_set.all():
                leaf_nodes.append(gp)
        return leaf_nodes

    @classmethod
    def get_group_org(cls):
        """组织架构图
        返回格式:
        [
            {'leaf1': 'leaf_to_path'},
            {'leaf2': 'leaf_to_path2'}
        ]
        """
        leaf_nodes = cls.get_leaf_nodes()
        group_org = []

        for leaf in leaf_nodes:
            if leaf.group.groupsection_set.all():
                for gs in leaf.group.groupsection_set.all():
                    group_org.append(gs.group_section_to_root())
            else:
                group_org.append(leaf.leaf_to_root())

        return group_org

    def leaf_to_root(self):
        """从叶子节点到根节点的路径
        比如C是叶子节点，到根节点是C->B->A
        返回一个namedtuple(leaf, leaf_to_root)
        """

        node = self
        leaf_to_root_path = []
        while node.parent_group:
            leaf_to_root_path.append(node.parent_group.name)
            node = node.parent_group.groupprofile
        leaf_to_root_path.append(node.company.name)
        leaf_to_root_path.reverse()
        return {'leaf': self.group.name, 'leaf_to_root': '/'.join(leaf_to_root_path)}


class PermGropu(models.Model):
    '''权限组'''

    class Meta:
        managed = False

        permissions = (
            ('view_room_obj', 'can view room obj'),  # 机房增删改查
            ('edit_room_obj', 'can edit room obj'),
            ('add_room_obj', 'can add room obj'),
            ('del_room_obj', 'can del resource obj'),
            ('view_host_obj', 'can view host obj'),  # host的增删改查
            ('edit_host_obj', 'can edit host obj'),
            ('add_host_obj', 'can add host obj'),
            ('del_host_obj', 'can del host obj'),
            ('view_business_obj', 'can view business obj'),  # 业务类型的增删改查
            ('edit_business_obj', 'can edit business obj'),
            ('add_business_obj', 'can add business obj'),
            ('del_business_obj', 'can del business obj'),
            ('view_game_project_obj', 'can view game_project obj'),  # 游戏项目的增删改查
            ('edit_game_project_obj', 'can edit game_project obj'),
            ('add_game_project_obj', 'can add game_project obj'),
            ('del_game_project_obj', 'can del game_project obj'),
            ('view_duty_schedule_obj', 'can view duty_schedule obj'),  # 值班表的增删改查
            ('edit_duty_schedule_obj', 'can edit duty_schedule obj'),
            ('add_duty_schedule_obj', 'can add duty_schedule obj'),
            ('del_duty_schedule_obj', 'can del duty_schedule obj'),
        )


class PermissionChangeRecord(models.Model):
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='操作时间', help_text='操作时间')
    operation_user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='操作人', help_text='操作人')
    object = models.IntegerField(choices=((1, '部门'), (2, '用户')), default=0, verbose_name='操作对象', help_text='操作对象')
    change_department = models.ForeignKey(OrganizationMptt, null=True, blank=True, on_delete=models.SET_NULL,
                                          verbose_name='权限变更', help_text='权限变更')
    change_user = models.CharField(max_length=10, null=True, blank=True, verbose_name='权限变更人', help_text='权限变更人')
    change_content = models.CharField(max_length=200, null=True, blank=True, verbose_name='修改明细', help_text='修改明细')

    class Meta:
        verbose_name = '修改权限操作记录'
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return self.get_object_display() + '权限修改'


class UserChangeRecord(models.Model):
    TYPE = (
        (1, u'新增'),
        (2, u'修改'),
        (3, u'删除'),
        (4, u'清除权限'),
        (5, u'确认入职'),
    )
    create_time = models.DateTimeField(auto_now_add=True, verbose_name=u'操作时间')
    create_user = models.ForeignKey(User, verbose_name=u'操作人')
    change_obj = models.CharField(max_length=20, default='', verbose_name=u'操作对象')
    type = models.IntegerField(choices=TYPE, verbose_name=u'操作类型')
    remark = models.CharField(max_length=1000, default='', verbose_name=u'操作备注')

    class Meta:
        verbose_name = u'用户变更记录表'
        verbose_name_plural = verbose_name

    def show_all(self):
        return {
            'id': self.id,
            'create_user': self.create_user.username,
            'create_time': str(self.create_time)[:19],
            'change_obj': self.change_obj,
            'type': self.get_type_display(),
            'remark': self.remark,
        }

    def __str__(self):
        return self.change_obj + self.get_type_display()


class Role(models.Model):
    """角色分组"""
    user = models.ManyToManyField(User, verbose_name=u'角色分组内用户')
    name = models.CharField(max_length=30, verbose_name=u'分组名字')
    project = models.ManyToManyField(GameProject, verbose_name=u'关联项目')

    class Meta:
        verbose_name = u'角色分组表'
        verbose_name_plural = verbose_name

    def show_all(self):
        return {
            'id': self.id,
            'name': self.name,
            'relate_user': ','.join([x.username for x in self.user.all()])
        }

    def edit_data(self):
        return {
            'id': self.id,
            'name': self.name,
            'relate_user': [{'id': x.id, 'username': x.username} for x in self.user.all()],
        }

    def get_relate_user_list(self):
        return [u for u in self.user.all()]

    def __str__(self):
        return self.name
