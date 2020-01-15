from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation

from assets.models import GameProject
from assets.models import Room
from assets.models import Host
from assets.models import ProjectGroup
from assets.models import GroupSection
from assets.models import OpsManager
from assets.models import Area

from users.models import OrganizationMptt

import time
import json


def containenglish(str0):
    import re
    return bool(re.search('[a-z]', str0))


class Workflow(models.Model):
    """流程表

    关联到相应的流程状态
    """

    name = models.CharField(max_length=100, unique=True, help_text='流程名')
    describtion = models.CharField(max_length=100, default='', help_text='工单的描述')
    init_state = models.ForeignKey("State", on_delete=models.SET_NULL, related_name='workflow_initstate', blank=True,
                                   null=True, help_text='初始化状态')
    allow_users = models.ManyToManyField(User, help_text='用户申请的权限')
    workflow_type = models.ForeignKey(ContentType, on_delete=models.PROTECT)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'workflow'

    def show_all(self):
        return {
            'id': self.id,
            'name': self.name,
            'describtion': self.describtion,
        }

    def show_id_and_name(self):
        return {
            'id': self.id,
            'name': self.name,
        }


class State(models.Model):
    """状态表

    关联到对应的流程

    常见的状态:
    CEO审核，各个组长审核，运维审核，完成

    specified_users: 某些state下有特定的用户来处理
    而不是通过关联出来的，比如不同流程的CEO审核state的
    用户总是CEO个人，运维审核的用户总是运维那些人
    """

    name = models.CharField(max_length=100, help_text='状态名')
    workflow = models.ForeignKey("Workflow", help_text='对应的流程名')
    transition = models.ManyToManyField("Transition", help_text='状态转化')
    specified_users = models.ManyToManyField(User, help_text='指定的用户')

    def get_pre_state(self):
        try:
            return self.transition.get(condition='拒绝').destination
        except:
            return None

    def get_latter_state(self):
        try:
            return self.transition.get(condition='同意').destination
        except:
            return None

    def __str__(self):
        return self.workflow.name + ':' + self.name

    def show_specified_user(self):
        return {
            'id': self.id,
            'workflow': self.workflow.name,
            'state': self.name,
            'specified_user': ','.join(
                [x.username for x in self.specified_users.all()]) if self.specified_users.all() else None,
        }

    def edit_data(self):
        return {
            'workflow_id': self.workflow.id,
            'workflow': self.workflow.name,
            'state_id': self.id,
            'state': self.name,
            'specified_user': [{'id': x.id, 'username': x.username} for x in self.specified_users.all()],
        }

    class Meta:
        db_table = 'state'
        unique_together = ('name', 'workflow')


class Transition(models.Model):
    """流程转化,从一个流程转化到另一个流程

    **Attributes:**

    name
        在流程内一个唯一的转化名称

    workflow
        转化归属的流程，必须是一个流程实例

    destination
        当转化发生后的目标指向状态

    condition
        发生转化的条件
    """

    name = models.CharField(max_length=100, help_text='转化名称')
    workflow = models.ForeignKey("Workflow", help_text='所属的流程')
    destination = models.ForeignKey("State", related_name='transition_destination', help_text='目标状态指向')
    condition = models.CharField(max_length=100, help_text='发生转化的条件')

    def __str__(self):
        return self.workflow.name + ':' + self.name

    class Meta:
        db_table = 'transition'
        unique_together = ('workflow', 'name')


class WorkflowObjectRelation(models.Model):
    """流程和object的对应关系

    关于通用外健
    see https://docs.djangoproject.com/en/1.10/ref/contrib/contenttypes/
    """

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    workflow = models.ForeignKey("Workflow")

    def __str__(self):
        return "%s:%s" % (self.content_type.name, self.workflow.name)

    class Meta:
        db_table = 'workflow_object_relation'
        unique_together = ("content_type", "object_id")


class StateObjectUserRelation(models.Model):
    """obj和状态和的用户关系
    """
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    state = models.ForeignKey("State")
    users = models.ManyToManyField(User)

    def __str__(self):
        return "%s:%s:%s" % (self.content_type.name, self.object_id, self.state.name)

    class Meta:
        unique_together = ("content_type", "object_id", "state")
        db_table = 'state_object_user'


class WorkflowStateEvent(models.Model):
    """流程转化的日志

    记录了每个流程转化到相应的state时的结果

    增加了额外的create_time， creator， title这三个属性
    这三个属性本来是任意申请的必须字段，他们的值都是相同的
    在创建wse的时候，把obj的这三个属性值赋值过来

    这样做的目的是为了在"我的待审批"和"我的审批记录"中可以通过
    关键字查找
    """

    MAIL_STATUS = (
        (0, '未发送'),
        (1, '已发送'),
    )
    IS_VALID = (
        (0, '无效'),
        (1, '有效'),
    )

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    state = models.ForeignKey("State", blank=True, null=True)
    create_time = models.DateTimeField()
    approve_time = models.DateTimeField(blank=True, null=True)
    creator = models.ForeignKey(User, help_text='工单发起人', on_delete=models.PROTECT)
    title = models.CharField(max_length=500, help_text='标题')
    is_current = models.BooleanField(default=False, help_text='是否为当前状态')
    approve_user = models.ForeignKey(User, related_name='approve_user_user', blank=True, null=True,
                                     help_text='审批的用户', on_delete=models.PROTECT)
    state_value = models.CharField(max_length=10, blank=True, null=True, help_text='state的审批值')
    send_mail = models.IntegerField(choices=MAIL_STATUS, default=0, help_text='是否已经发送过邮件通知')
    opinion = models.CharField(max_length=100, blank=True, null=True, help_text='审批意见')
    users = models.ManyToManyField(User, related_name='wse_approve_users', help_text='指定的审批用户,每次审批后从sor中copy')
    is_cancel = models.IntegerField(choices=((0, '未取消'), (1, '已取消')), default=0, verbose_name=u'工单流程是否取消')
    is_valid = models.IntegerField(choices=IS_VALID, default=1, verbose_name=u'工单是否有效')

    def __str__(self):
        return '%s-%s-%s' % (self.content_object.title, self.state, self.state_value)

    def show_all(self, show_creator=False):
        '展示当前接点状态的记录'
        if self.state_value:
            state_value = self.state_value
        else:
            if self.state.name == '完成':
                if isinstance(self.content_object, SVNWorkflow):
                    if self.content_object.status == 0:
                        state_value = '完成' + '-' + self.content_object.get_status_display()
                    else:
                        state_value = '完成' + '-' + self.content_object.get_status_display()
                elif isinstance(self.content_object, ServerPermissionWorkflow):
                    state_value = '完成' + '-' + self.content_object.get_status_display()
                elif isinstance(self.content_object, FailureDeclareWorkflow):
                    state_value = '完成' + '-' + self.content_object.get_status_display()
                elif isinstance(self.content_object, Wifi):
                    state_value = '完成' + '-' + self.content_object.get_status_display()
                elif isinstance(self.content_object, ComputerParts):
                    state_value = '完成' + '-' + self.content_object.get_status_display()
                elif isinstance(self.content_object, ClientHotUpdate):
                    state_value = '完成' + '-' + self.content_object.get_status_display()
                elif isinstance(self.content_object, ServerHotUpdate):
                    state_value = '完成' + '-' + self.content_object.get_status_display()
                elif isinstance(self.content_object, ProjectAdjust):
                    state_value = '完成' + '-' + self.content_object.get_status_display()
                elif isinstance(self.content_object, Machine):
                    state_value = '完成' + '-' + self.content_object.get_status_display()
                else:
                    state_value = '完成'
            else:
                state_value = '审核中'
        if self.is_cancel == 1:
            state_value = '取消'
        if show_creator:
            return {
                'id': self.id,
                'create_time': self.create_time.strftime('%Y-%m-%d %H:%M'),
                'workflow': self.state.workflow.name,
                'creator': self.creator.username,
                'applicant': self.content_object.applicant.username,
                'title': self.title,
                'current_state': self.state.name,
                'state_value': state_value,
                'send_mail': self.get_send_mail_display(),
                'can_cancel': '1' if self.is_cancel == 0 and state_value == '审核中' else '0'
            }
        else:
            return {
                'id': self.id,
                'create_time': self.create_time.strftime('%Y-%m-%d %H:%M'),
                'workflow': self.state.workflow.name,
                'title': self.title,
                'current_state': self.state.name,
                'state_value': state_value,
                'send_mail': self.get_send_mail_display(),
                'can_cancel': '1' if self.is_cancel == 0 and state_value == '审核中' else '0'
            }

    def show_workflow_history_all(self):
        '工单汇总展示的数据'
        if self.state_value:
            state_value = self.state_value
        else:
            if self.state.name == '完成':
                state_value = '完成'
            else:
                state_value = '审核中'
        if self.is_cancel == 1:
            state_value = '取消'
        title = self.title

        if isinstance(self.content_object, VersionUpdate) and not self.content_object.new_edition:
            status = ''
        else:
            if hasattr(self.content_object, 'get_status_display'):
                status = self.content_object.get_status_display()
                if self.is_cancel == 1 or state_value == '拒绝':
                    status = ''
            else:
                status = ''

        return {
            'id': self.id,
            'create_time': self.create_time.strftime('%Y-%m-%d %H:%M'),
            'workflow': self.state.workflow.name,
            'creator': self.creator.username,
            'applicant': self.content_object.applicant.username,
            'title': title,
            'current_state': self.state.name,
            'state_value': state_value,
            'status': status,
            'is_valid': self.get_is_valid_display(),
        }

    def get_current_state(self):
        '根据某个wse获取当前content_object的当前state'

        if self.is_current:
            return self.state.name
        else:
            ctype = ContentType.objects.get_for_model(self.content_object)
            return WorkflowStateEvent.objects.get(
                content_type=ctype, object_id=self.content_object.id, is_current=True).state.name

    def show_approve(self):
        '展示审批'
        if self.state_value:
            state_value = self.state_value
        else:
            state_value = '待审批'
        if self.is_cancel == 1:
            state_value = '取消'
        title = self.title
        if isinstance(self.content_object, Wifi):
            title += ' （' + self.content_object.mac + '）'
        return {
            'id': self.id,
            'create_time': self.create_time.strftime('%Y-%m-%d %H:%M'),
            'approve_time': self.approve_time.strftime('%Y-%m-%d %H:%M') if self.approve_time else '',
            'creator': self.creator.username,
            'workflow': self.state.workflow.name,
            'title': title,
            'current_state': self.get_current_state(),
            'state_value': state_value,
        }

    def show_version_update_summarize(self):
        """展示版本更新汇总数据
        """
        # content_object = self.content_object
        if self.state_value:
            state_value = self.state_value
        else:
            if self.state.name == '完成':
                state_value = '完成'
            else:
                state_value = '审核中'
        return {
            'id': self.id,
            'project': self.content_object.project.project_name,
            'create_time': self.create_time.strftime('%Y-%m-%d %H:%M'),
            'creator': self.creator.username,
            'applicant': self.content_object.applicant.username,
            'title': self.title,
            'current_state': self.state.name,
            'state_value': state_value,
            'is_valid': self.get_is_valid_display(),
            'handle_status': self.content_object.get_status_display() if self.content_object.new_edition else '',
        }

    def get_state_value(self):
        """获取当前流程的结果，若is_cancel为True，则返回取消，否则返回state_value内容"""
        if not self.state_value:
            return '审核中'
        if self.is_cancel:
            return '取消'
        else:
            return self.state_value

    def get_ctype_id(self):
        """获取ctype_id"""
        ctype = ContentType.objects.get_for_model(self.content_object)
        return ctype.id

    class Meta:
        db_table = 'workflow_state_event'
        unique_together = ("content_type", "object_id", "state")


class SVNRepo(models.Model):
    """SVN仓库表"""
    name = models.CharField(max_length=20, unique=True, help_text='SVN仓库名称')

    def show_all(self):
        return {
            'id': self.id,
            'name': self.name
        }

    def edit_data(self):
        return {
            'id': self.id,
            'name': self.name
        }

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'svn_repo'


class SVNScheme(models.Model):
    """SVN权限方案名"""
    name = models.CharField(max_length=50, unique=True, help_text='方案名')
    project = models.ForeignKey(GameProject, help_text='所属的项目', on_delete=models.PROTECT)

    def __str__(self):
        return self.name + ':' + self.project.project_name

    class Meta:
        db_table = 'svn_scheme'

    def show_all(self):
        return {
            'id': self.id,
            'name': self.name,
            'project': self.project.project_name,
        }

    def edit_data(self):
        return {
            'id': self.id,
            'name': self.name,
            'project_id': self.project.id,
            'project': self.project.project_name,
        }


class SVNSchemeDetail(models.Model):
    """SVN方案明细"""
    PERM = (
        (0, '读'),
        (1, '写'),
        (2, '读写'),
    )
    svn_scheme = models.ForeignKey(SVNScheme, help_text='所属的方案', on_delete=models.PROTECT)
    svn_repo = models.ForeignKey(SVNRepo, help_text='所属的仓库', on_delete=models.PROTECT)
    svn_path = models.CharField(max_length=100, blank=True, null=True, help_text='仓库子目录')
    svn_perm = models.IntegerField(choices=PERM, default=1, help_text='权限')

    def __str__(self):
        return self.svn_scheme.project.project_name_en + ':' + self.svn_repo.name + ':' + self.svn_path

    class Meta:
        unique_together = ('svn_scheme', 'svn_repo', 'svn_path')
        db_table = 'svn_scheme_detail'

    def show_all(self):
        return {
            'id': self.id,
            'svn_scheme': self.svn_scheme.name,
            'svn_repo': self.svn_repo.name,
            'svn_path': self.svn_path,
            'svn_perm': self.get_svn_perm_display(),
        }

    def show_all_data(self):
        return {
            'project': self.svn_scheme.project.project_name,
            'svn_repo': self.svn_repo.name,
            'svn_path': self.svn_path,
            'svn_perm': self.get_svn_perm_display(),
        }

    def edit_data(self):
        return {
            'id': self.id,
            'svn_scheme_id': self.svn_scheme.id,
            'svn_scheme': self.svn_scheme.name,
            'svn_repo_id': self.svn_repo.id,
            'svn_repo': self.svn_repo.name,
            'svn_path': self.svn_path,
            'svn_perm': self.svn_perm,
        }


class SVNWorkflow(models.Model):
    """SVN申请流程

    content的内容是json的形式:
    [
        {'project_id': 'id1', 'project': project1, 'repo_id': id1, 'repo': 'repo1',  'path': 'path1', 'perm': 'perm1'},
        {'project_id': 'id2', 'project': project2, 'repo_id': id2, 'repo': 'repo2',  'path': 'path2', 'perm': 'perm2'},
    ]
    dir是目录, perm是权限，有读，写， 读写三种情况
    """

    PROCESS_STATUS = (
        (0, '查看企业邮件通知'),
        (1, '未处理'),
        (2, '故障中'),
    )

    create_time = models.DateTimeField()
    creator = models.ForeignKey(User, help_text='发起人', on_delete=models.PROTECT)
    title = models.CharField(max_length=100, help_text='标题')
    content = models.TextField(help_text='内容')
    project = models.ForeignKey(GameProject, help_text='项目')
    applicant = models.ForeignKey(User, related_name='applicant_user', help_text='申请人', on_delete=models.PROTECT)
    reason = models.CharField(max_length=200, blank=True, null=True, help_text='申请原因')
    status = models.IntegerField(choices=PROCESS_STATUS, default=0, help_text='处理状态')
    svn_scheme = models.ForeignKey(SVNScheme, blank=True, null=True, default=None,
                                   help_text='svn方案套餐', on_delete=models.SET_NULL)
    workflows = GenericRelation(WorkflowStateEvent, related_query_name='svn_workflow')

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'svn_workflow'

    def get_current_state(self):
        '获取流程的当前状态'
        pass

    @classmethod
    def status_dict(cls):
        return dict(cls.PROCESS_STATUS)


class UpdateWorkflow(models.Model):
    """更新流程，这里是测试用的
    """

    create_time = models.DateTimeField(auto_now=True)
    creator = models.ForeignKey(User, help_text='发起人')
    title = models.CharField(max_length=100, help_text='标题')
    server_ip = models.TextField(help_text='更新的内容')


class ServerPermissionWorkflow(models.Model):
    """内网外服务器权限申请流程

    ips 是json格式, format:
    [
        {id: id, ip: ip1-room_name},
        {id: id, ip: ip2-room_name},
    ]
    """

    PROCESS_STATUS = (
        (0, '已处理'),
        (1, '故障中'),
        (2, '未处理'),
    )

    create_time = models.DateTimeField()
    creator = models.ForeignKey(User, help_text='发起人', on_delete=models.PROTECT)
    applicant = models.ForeignKey(User, related_name='server_perm_user', help_text='申请人', on_delete=models.PROTECT)
    title = models.CharField(max_length=100, help_text='标题')
    reason = models.CharField(max_length=100, help_text='原因')
    project = models.ForeignKey(GameProject, help_text='项目')
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, blank=True, null=True, help_text='目标机房')
    ips = models.TextField(help_text='目标ip', blank=True, null=True)
    all_ip = models.NullBooleanField(blank=True, null=True, default=None, help_text='是否目标机房下的全部ip')
    key = models.TextField(help_text='key的内容')
    is_root = models.BooleanField(help_text='是否root')
    start_time = models.DateTimeField(blank=True, null=True, help_text='起始时间')
    end_time = models.DateTimeField(blank=True, null=True, help_text='结束时间')
    temporary = models.BooleanField(default=True, help_text='是否是临时')
    group = models.CharField(max_length=20, blank=True, null=True, help_text='分组')
    status = models.IntegerField(choices=PROCESS_STATUS, default=2)
    workflows = GenericRelation(WorkflowStateEvent, related_query_name='ser_per_workflow')

    def __str__(self):
        return self.title

    @classmethod
    def status_dict(cls):
        return dict(cls.PROCESS_STATUS)

    class Meta:
        db_table = 'server_permission_workflow'


class FailureDeclareWorkflow(models.Model):
    """故障申报流程
    """
    PROCESS_STATUS = (
        (0, '已处理'),
        (1, '未处理'),
    )

    CLASSIFICATION = (
        (1, '电脑硬件故障'),
        (2, 'windows系统故障'),
        (3, '软件使用问题'),
        # (4, '企业QQ、邮箱和wifi账号密码问题'),
        # (6, '资产采购事项'),
    )
    create_time = models.DateTimeField()
    creator = models.ForeignKey(User, help_text='发起人', on_delete=models.PROTECT)
    applicant = models.ForeignKey(User, related_name='failure_declare_user', help_text='申请人', on_delete=models.PROTECT)
    title = models.CharField(max_length=100, help_text='标题')
    classification = models.IntegerField(choices=CLASSIFICATION, default=1, help_text='问题分类')
    content = models.CharField(max_length=500, help_text='问题描述')
    status = models.IntegerField(choices=PROCESS_STATUS, default=1)
    workflows = GenericRelation(WorkflowStateEvent, related_query_name='failure_declare_workflow')
    state_object = GenericRelation(StateObjectUserRelation, related_query_name='failure_declare_sor')

    def __str__(self):
        return self.title

    @classmethod
    def status_dict(cls):
        return dict(cls.PROCESS_STATUS)

    @classmethod
    def class_dict(cls):
        return dict(cls.CLASSIFICATION)

    class Meta:
        db_table = 'failure_declare_workflow'


class HotUpdate(models.Model):
    """热更新流程
    """
    UPDATE_TYPE = (
        (0, '前端'),
        (1, '后端'),
    )

    create_time = models.DateTimeField()
    creator = models.ForeignKey(User, help_text='发起人', on_delete=models.PROTECT)
    applicant = models.ForeignKey(User, related_name='hot_update_user', help_text='申请人', on_delete=models.PROTECT)
    title = models.CharField(max_length=200, help_text='标题')
    reason = models.CharField(max_length=100, help_text='更新原因')
    attention = models.CharField(max_length=200, blank=True, null=True, help_text='注意事项')
    project = models.CharField(max_length=20, help_text='热更的项目')
    update_type = models.IntegerField(choices=UPDATE_TYPE, help_text='更新类型')
    update_version = models.CharField(max_length=20, help_text='更新版本号')
    update_time = models.DateTimeField(help_text='更新时间')
    file_list = models.CharField(max_length=100, blank=True, null=True, help_text='热更新文件列表, json list 格式,可选')
    erlang_cmd = models.CharField(max_length=100, blank=True, null=True, help_text='执行的erlang命令，json list格式，可选')
    choose_server_type = models.CharField(max_length=10, help_text='选区服的方式')
    content = models.TextField(help_text='热更新的数据')

    class Meta:
        db_table = 'hotupdate_workflow'

    def __str__(self):
        return self.title


class ClientHotUpdate(models.Model):
    """前端热更新
    """
    STATUS = (
        ('0', '未处理'),
        ('1', '更新中'),
        ('2', '更新失败'),
        ('3', '更新成功'),
        ('4', '待更新'),
    )
    PRIORITY = (
        ('0', '低'),
        ('1', '普通'),
        ('2', '高'),
        ('3', '暂停'),
    )

    CTYPE = (
        ('0', '安卓'),
        ('1', 'iOS'),
    )

    create_time = models.DateTimeField()
    creator = models.ForeignKey(User, help_text='发起人', on_delete=models.PROTECT)
    applicant = models.ForeignKey(User, related_name='client_hot_update_user', help_text='申请人',
                                  on_delete=models.PROTECT)
    title = models.CharField(max_length=255, unique=True, help_text='标题')
    reason = models.TextField(help_text='更新原因')
    attention = models.CharField(max_length=200, blank=True, null=True, help_text='注意事项')
    project = models.ForeignKey(GameProject, help_text='热更的项目')
    area_name = models.CharField(max_length=20, help_text='地区')
    rsync_area_name = models.CharField(max_length=20, help_text='版本接收机上地区的代号, 大陆->cn')
    client_version = models.CharField(max_length=50, help_text='热更新的前端版本号')
    update_file_list = models.TextField(help_text='前端热更新的文件和MD5列表')
    uuid = models.CharField(max_length=255, unique=True, help_text='更新的唯一id')
    content = models.TextField(help_text='热更新前端的数据')
    status = models.CharField(max_length=10, choices=STATUS, default='0')
    priority = models.CharField(max_length=10, choices=PRIORITY, default='1')
    client_type = models.CharField(max_length=10, blank=True, null=True, default=None, help_text='客户端类型')
    workflows = GenericRelation(WorkflowStateEvent, related_query_name='hot_client_workflow')
    pair_code = models.CharField(max_length=255, blank=True, null=True, default=None, help_text='成对的执行码')
    order = models.CharField(max_length=10, blank=True, null=True, default=None, help_text='先后顺序')
    extra = models.ManyToManyField(User, related_name='hot_client_extra_user', help_text='申请人')
    notifier = models.SmallIntegerField(default=1, help_text='提醒次数')
    no_auto_execute_reason = models.CharField(max_length=255, blank=True, null=True, help_text='没有自动执行原因')

    class Meta:
        db_table = 'client_hotupdate_workflow'

    def __str__(self):
        return self.title

    @classmethod
    def status_dict(cls):
        return dict(cls.STATUS)

    def reversed_time(self):
        ts = self.create_time.timestamp()
        return -ts

    def get_ops_manager(self):
        """获取该流程的锁定的运维管理机
        """
        area = json.loads(self.content)[0]['area_name']
        project = self.project

        return (project, area)

    def get_cdn_dir_and_type(self):
        """根据项目组的要求
        在excel中展示校花的
        例如: content的内容是
        [
            {
                'version': 'Achuangyu_00000', 'cdn_root_url': 'res.snsy.chuangyunet.com',
                'client_type': 'cn_android', 'data': '前端热更新成功', 'status': True, 'cdn_dir': 'chuangyu_t2'
            }
        ]
        转化为
        chuangyu_t2  cn_android
        chuangyu_r1  cn_ios
        """
        if self.project.project_name_en in ('snsy',):
            json_content = json.loads(self.content)
            list_cdn_dir = [x['cdn_dir'] for x in json_content]
            list_client_type = [x['client_type'] for x in json_content]
            return ('\n'.join(list_cdn_dir), '\n'.join(list_client_type))
        else:
            return ''

    def get_area_name(self):
        if containenglish(self.area_name[0]):
            area_name = Area.objects.filter(short_name=self.area_name)
            if area_name:
                return area_name[0].chinese_name
            else:
                return self.area_name
        else:
            return self.area_name

    def show_task(self):
        """展示任务的相关数据
        """

        return {
            'id': self.id,
            'create_time': self.create_time.strftime('%Y-%m-%d %H:%M'),
            'project': self.project.project_name,
            'update_type': '前端',
            'uuid': self.uuid,
            'pair_code': self.pair_code if self.pair_code else '',
            'order': self.order if self.order else '',
            'area_name': self.get_area_name(),
            'title': self.title,
            'priority': self.get_priority_display(),
            'status': self.get_status_display(),
            'priority_code': self.priority,
            'status_code': self.status,
            'no_auto_execute_reason': self.no_auto_execute_reason,
        }

    def get_client_version(self):
        """
        获取前端版本号
        若client_version字段内容为 xxxxxxx，则便利conetent取出version信息
        若不是，则直接返回client_version
        """
        if self.client_version == 'xxxxxxx':
            return ','.join(list(set([x.get('version', x.get('input_version', '')) for x in json.loads(self.content)])))
        else:
            return self.client_version


class ServerHotUpdate(models.Model):
    """热更新后端
    """
    STATUS = (
        ('0', '未处理'),
        ('1', '更新中'),
        ('2', '更新失败'),
        ('3', '更新成功'),
        ('4', '待更新'),
    )
    PRIORITY = (
        ('0', '低'),
        ('1', '普通'),
        ('2', '高'),
        ('3', '暂停'),
    )

    HOT_SERVER_TYPE = (
        ('0', '只热更'),
        ('1', '先热更,再执行erl命令'),
        ('2', '只执行erl命令'),
        ('3', '先执行erl命令,再热更'),
    )

    create_time = models.DateTimeField()
    creator = models.ForeignKey(User, help_text='发起人', on_delete=models.PROTECT)
    applicant = models.ForeignKey(User, related_name='server_hot_update_user', help_text='申请人',
                                  on_delete=models.PROTECT)
    title = models.CharField(max_length=255, unique=True, help_text='标题')
    reason = models.TextField(help_text='更新原因')
    attention = models.CharField(max_length=200, blank=True, null=True, help_text='注意事项')
    project = models.ForeignKey(GameProject, help_text='热更的项目')
    area_name = models.CharField(max_length=20, help_text='地区')
    rsync_area_name = models.CharField(max_length=20, help_text='版本接收机上地区的代号, 大陆->cn')
    server_version = models.CharField(max_length=50, help_text='热更新的后端版本号')
    hot_server_type = models.CharField(max_length=10, choices=HOT_SERVER_TYPE, default='0', help_text='后端热更方式')
    status = models.CharField(max_length=10, choices=STATUS, default='0')
    priority = models.CharField(max_length=10, choices=PRIORITY, default='1')
    erlang_cmd_list = models.CharField(max_length=255, blank=True, null=True, default=None, help_text='执行的erlang命令')
    update_file_list = models.TextField(blank=True, null=True, default=None, help_text='后端热更新的文件和MD5列表')
    # erlang_server_list = models.TextField(blank=True, null=True, default=None, help_text='erlang命令的区服列表')
    update_server_list = models.TextField(blank=True, null=True, default=None, help_text='原始热更新的区服列表,不做修改')
    uuid = models.CharField(max_length=255, unique=True, help_text='更新的唯一id')
    final_result = models.NullBooleanField(blank=True, null=True, default=None, help_text='最终的结果')
    final_data = models.CharField(max_length=255, blank=True, null=True, default=None, help_text='最终的数据')
    result_update_file_list = models.TextField(max_length=255, null=True, default=None, help_text='区服列表更新结果')
    workflows = GenericRelation(WorkflowStateEvent, related_query_name='hot_server_workflow')
    pair_code = models.CharField(max_length=255, blank=True, null=True, default=None, help_text='成对的执行码')
    order = models.CharField(max_length=10, blank=True, null=True, default=None, help_text='先后顺序')
    extra = models.ManyToManyField(User, related_name='hot_server_extra_user', help_text='申请人')
    notifier = models.SmallIntegerField(default=1, help_text='提醒次数')
    no_auto_execute_reason = models.CharField(max_length=255, blank=True, null=True, help_text='没有自动执行原因')

    class Meta:
        db_table = 'server_hotupdate_workflow'

    def __str__(self):
        return self.title

    @classmethod
    def status_dict(cls):
        return dict(cls.STATUS)

    def reversed_time(self):
        ts = self.create_time.timestamp()
        return -ts

    def get_area_name(self):
        if containenglish(self.area_name[0]):
            area_name = Area.objects.filter(short_name=self.area_name)
            if area_name:
                return area_name[0].chinese_name
            else:
                return self.area_name
        else:
            return self.area_name

    def show_task(self):
        """展示任务的相关数据
        """

        return {
            'id': self.id,
            'create_time': self.create_time.strftime('%Y-%m-%d %H:%M'),
            'project': self.project.project_name,
            'update_type': '后端',
            'area_name': self.get_area_name(),
            'title': self.title,
            'uuid': self.uuid,
            'pair_code': self.pair_code if self.pair_code else '',
            'order': self.order if self.order else '',
            'priority': self.get_priority_display(),
            'status': self.get_status_display(),
            'priority_code': self.priority,
            'status_code': self.status,
            'no_auto_execute_reason': self.no_auto_execute_reason,
        }

    def show_detail(self):
        '展示全部的区服更新情况'
        update_server_list = json.loads(self.update_server_list)

        # 遍历整个list，如果没有相应的字段，增加
        for server in update_server_list:
            update_data = server.get('update_data', None)
            erl_data = server.get('erl_data', None)

            if self.hot_server_type == '0':
                # 只热更新
                if update_data is None:
                    server['update_data_data'] = ''
                    server['update_data_status'] = '待更新'
                else:
                    update_data_data = update_data.get('data', '')
                    server['update_data_data'] = update_data_data

                    update_data_status = update_data.get('status', False)
                    if update_data_status:
                        update_data_status = '成功'
                    else:
                        update_data_status = '失败'
                    server['update_data_status'] = update_data_status

                server['erl_data_data'] = ''
                server['erl_data_status'] = ''
            elif self.hot_server_type in ['1', '3']:
                # 热更新和erl都执行
                if update_data is None:
                    server['update_data_data'] = ''
                    server['update_data_status'] = '待更新'
                else:
                    update_data_data = update_data.get('data', '')
                    server['update_data_data'] = update_data_data

                    update_data_status = update_data.get('status', False)
                    if update_data_status:
                        update_data_status = '成功'
                    else:
                        update_data_status = '失败'
                    server['update_data_status'] = update_data_status

                if erl_data is None:
                    server['erl_data_data'] = ''
                    server['erl_data_status'] = '待更新'
                else:
                    erl_data_data = erl_data.get('data', '')
                    server['erl_data_data'] = erl_data_data

                    erl_data_status = erl_data.get('status', False)
                    if erl_data_status:
                        erl_data_status = '成功'
                    else:
                        erl_data_status = '失败'
                    server['erl_data_status'] = erl_data_status
            elif self.hot_server_type == '2':
                # 只执行erl命令
                if erl_data is None:
                    server['erl_data_data'] = ''
                    server['erl_data_status'] = '待更新'
                else:
                    erl_data_data = erl_data.get('data', '')
                    server['erl_data_data'] = erl_data_data

                    erl_data_status = erl_data.get('status', False)
                    if erl_data_status:
                        erl_data_status = '成功'
                    else:
                        erl_data_status = '失败'
                    server['erl_data_status'] = erl_data_status
                server['update_data_data'] = ''
                server['update_data_status'] = ''

        return update_server_list

    def is_all_good(self):
        """判断是否有更新出错
        """
        hot_server_type = self.hot_server_type
        result_update_file_list = json.loads(self.result_update_file_list)

        if hot_server_type == '0':
            # 只热更新
            for x in result_update_file_list:
                update_data_status = x.get('update_data_status', False)
                if not update_data_status:
                    return False
            return True
        elif hot_server_type in ['1', '3']:
            # 热更和erl命令都执行
            for x in result_update_file_list:
                update_data_status = x.get('update_data_status', False)
                erl_data_status = x.get('erl_data_status', False)
                if not update_data_status:
                    return False
                if not erl_data_status:
                    return False
            return True
        elif hot_server_type == '2':
            for x in result_update_file_list:
                erl_data_status = x.get('erl_data_status', False)
                if not erl_data_status:
                    return False
            return True

    def get_detail_data(self):
        """获取更新完成后
        本次更新的总数，成功的总数，失败的总数,是否全部成功
        """

        hot_server_type = self.hot_server_type
        result_update_file_list = json.loads(self.result_update_file_list)

        succeed_count = 0
        failed_count = 0

        is_all_good = True

        if hot_server_type == '0':
            # 只热更新
            for x in result_update_file_list:
                update_data_status = x.get('update_data_status', '失败')
                if update_data_status == '失败':
                    failed_count += 1
                    is_all_good = False
                else:
                    succeed_count += 1
        elif hot_server_type in ['1', '3']:
            # 热更和erl命令都执行
            for x in result_update_file_list:
                update_data_status = x.get('update_data_status', '失败')
                erl_data_status = x.get('erl_data_status', '失败')
                if update_data_status == '失败' or erl_data_status == '失败':
                    failed_count += 1
                    is_all_good = False
                else:
                    succeed_count += 1
        elif hot_server_type == '2':
            for x in result_update_file_list:
                erl_data_status = x.get('erl_data_status', '失败')
                if erl_data_status == '失败':
                    failed_count += 1
                    is_all_good = False
                else:
                    succeed_count += 1

        result = {}
        result['total'] = len(result_update_file_list)
        result['finished'] = len(result_update_file_list)
        result['succeed'] = succeed_count
        result['failed'] = failed_count
        result['is_all_good'] = is_all_good
        result['status'] = self.status

        return result


class ClientHotUpdateRsyncTask(models.Model):
    """前端热更新rsync子任务表"""
    RSYNC_STATUS = (
        (0, u'推送失败'),
        (1, u'推送成功'),
    )
    client_hot_update = models.ForeignKey(ClientHotUpdate, help_text=u'所属前端热更新任务')
    ops = models.ForeignKey(OpsManager, help_text=u'所属运维管理机')
    rsync_result = models.IntegerField(RSYNC_STATUS, null=True, blank=True, help_text=u'rsync推送结果')
    update_file_list = models.TextField(null=True, blank=True, help_text='前端热更新的文件和MD5列表')
    content = models.TextField(null=True, blank=True, help_text='前端热更新的数据')

    class Meta:
        verbose_name = u'前端热更新rsync子任务表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.client_hot_update.title


class ServerHotUpdateRsyncTask(models.Model):
    """后端热更新rsync子任务表"""
    RSYNC_STATUS = (
        (0, u'推送失败'),
        (1, u'推送成功'),
    )
    server_hot_update = models.ForeignKey(ServerHotUpdate, help_text=u'所属后端热更新任务')
    ops = models.ForeignKey(OpsManager, help_text=u'所属运维管理机')
    rsync_result = models.IntegerField(RSYNC_STATUS, null=True, blank=True, help_text=u'rsync推送结果')
    update_file_list = models.TextField(null=True, blank=True, help_text='后端热更新的文件和MD5列表')
    update_server_list = models.TextField(null=True, blank=True, help_text='后端热更新的区服数据')

    class Meta:
        verbose_name = u'后端热更新rsync子任务表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.server_hot_update.title


class ServerHotUpdateReplication(models.Model):
    """后端热更新的副本表
    通常用来记录每次热更新的时候的
    原来的全部的区服列表
    如果校验区服数据有问题，记录在这里
    """
    replication = models.OneToOneField(ServerHotUpdate, on_delete=models.CASCADE, help_text='所关联的后端热更新')
    raw_server_list = models.TextField(blank=True, null=True, default=None, help_text='原来选择的区服列表')
    replication_server_list = models.TextField(blank=True, null=True, default=None, help_text='本次热更新全部的区服数据')
    on_new_server = models.BooleanField(default=False, help_text='是否同步热更新服')
    change_log = models.TextField(blank=True, null=True, default=None, help_text='区服变更日志')

    class Meta:
        db_table = 'server_hotupdate_replication'

    def __str__(self):
        return self.replication.title


class VersionUpdate(models.Model):
    """版本更新单流程
    """
    ASK_RESET = (
        (0, 'no'),
        (1, 'yes')
    )
    PROCESS_STATUS = (
        (0, '已处理'),
        (1, '故障中'),
        (2, '未处理'),
    )
    SERVER_RANGE = (
        ('all', '全服'),
        ('include', '部分区服'),
        ('exclude', '排除区服'),
    )
    create_time = models.DateTimeField()
    creator = models.ForeignKey(User, help_text='发起人', on_delete=models.PROTECT)
    applicant = models.ForeignKey(User, related_name='version_update_user', help_text='申请人', on_delete=models.PROTECT)
    title = models.CharField(max_length=100, help_text='标题')
    content = models.TextField(help_text='版本更新内容')
    project = models.ForeignKey(GameProject, help_text='更新游戏项目')
    start_time = models.DateTimeField(help_text='启始时间')
    end_time = models.DateTimeField(help_text='结束时间')
    server_list = models.TextField(help_text='更新区服')
    server_content = models.TextField(null=True, blank=True, help_text='后端更新内容')
    server_exclude_content = models.TextField(null=True, blank=True, help_text='后端需要排除的更新内容')
    client_version = models.CharField(max_length=255, blank=True, null=True, default=None, help_text='前端版本号')
    server_version = models.CharField(max_length=255, blank=True, null=True, default=None, help_text='后端版本号')
    client_attention = models.TextField(blank=True, null=True, default=None, help_text='前端注意事项')
    server_attention = models.TextField(blank=True, null=True, default=None, help_text='后端注意事项')
    workflows = GenericRelation(WorkflowStateEvent, related_query_name='version_update_workflow')
    client_content = models.TextField(null=True, blank=True, help_text='前端更新内容')
    new_edition = models.BooleanField(default=False, help_text='是否使用新版本更新流程')
    area = models.ForeignKey(Area, null=True, blank=True, on_delete=models.SET_NULL, help_text='更新地区')
    ask_reset = models.IntegerField(choices=ASK_RESET, default=0, help_text='是否重排')
    uuid = models.CharField(max_length=255, null=True, blank=True, help_text='任务唯一标识')
    status = models.IntegerField(choices=PROCESS_STATUS, default=2, help_text='处理状态')
    on_new_server = models.BooleanField(default=False, help_text='是否同步热更新服')
    server_range = models.CharField(max_length=20, choices=SERVER_RANGE, null=True, blank=True, help_text='更新区服范围')
    server_erlang = models.TextField(default='', help_text='需要执行的erlang命令')
    is_maintenance = models.BooleanField(default=False, help_text='是否已挂维护')

    class Meta:
        db_table = 'myworkflows_version_update'

    def format_server_list(self):
        from myworkflows.utils import hot_server_update_server_list_to_tree
        if self.new_edition:
            server_list = hot_server_update_server_list_to_tree(json.loads(self.server_list))
        else:
            server_list = self.server_list
        return self.new_edition, server_list

    def get_srv_id_list(self):
        """
        1. 如果不需要同步新服，或者只更新部分区服，则直接返回server_content
        2. 其余情况则需要重新获取全服，再减去排除区服
        """
        if not self.on_new_server or self.server_range == 'include':
            return [x for x in map(lambda x: x.strip(), self.server_content.split('\n')) if x is not None and x != '']
        else:
            project = self.project
            area = self.area
            all_game_server_list = GameServer.objects.select_related('host').filter(srv_status=0, project=project,
                                                                                    host__belongs_to_room__area=area)
            all_srv_id_list = [game_server.srv_id for game_server in all_game_server_list]
            exclude_srv_id_list = []
            if self.server_exclude_content and self.server_range == 'exclude':
                exclude_srv_id_list = [x for x in map(lambda x: x.strip(), self.server_exclude_content.split('\n')) if
                                       x is not None and x != '']
            return list(set(all_srv_id_list) - set(exclude_srv_id_list))

    def __str__(self):
        return self.title

    @classmethod
    def status_dict(cls):
        return {}


class Wifi(models.Model):
    """wifi流程申请
    """

    PROCESS_STATUS = (
        (0, '已处理'),
        (1, '未处理'),
    )

    create_time = models.DateTimeField()
    creator = models.ForeignKey(User, help_text='发起人', on_delete=models.PROTECT)
    applicant = models.ForeignKey(User, related_name='wifi_user', help_text='申请人', on_delete=models.PROTECT)
    title = models.CharField(max_length=100, help_text='标题')
    reason = models.CharField(max_length=100, help_text='申请原因')
    name = models.CharField(max_length=20, help_text='申请的wifi')
    mac = models.CharField(max_length=100, default='', help_text='mac地址')
    status = models.IntegerField(choices=PROCESS_STATUS, default=1, help_text='处理状态')
    state_object = GenericRelation(StateObjectUserRelation, related_query_name='wifi_sor')
    workflows = GenericRelation(WorkflowStateEvent, related_query_name='wifi_workflow')
    wifi_add_result = models.CharField(max_length=100, null=True, blank=True, verbose_name=u'wifi开通结果')

    class Meta:
        db_table = 'wifi_workflow'

    def __str__(self):
        return self.title

    @classmethod
    def status_dict(cls):
        return dict(cls.PROCESS_STATUS)


class Machine(models.Model):
    """服务器申请工单
    """
    IP_TYPE = (
        ('0', '内网'),
        ('1', '外网'),
    )
    PROCESS_STATUS = (
        (0, '已处理'),
        (1, '未处理'),
    )
    create_time = models.DateTimeField()
    creator = models.ForeignKey(User, help_text='发起人', on_delete=models.PROTECT)
    applicant = models.ForeignKey(User, related_name='machine_user', help_text='申请人', on_delete=models.PROTECT)
    title = models.CharField(max_length=100, help_text='标题')
    project = models.ForeignKey(GameProject, help_text='所在项目')
    purpose = models.TextField(help_text='用途')
    config = models.TextField(help_text='机器配置')
    number = models.IntegerField(default=1, help_text='数量')
    ip_type = models.CharField(max_length=10, choices=IP_TYPE, default='1', help_text='内外网')
    requirements = models.TextField(blank=True, null=True, default=None, help_text='其他需求')
    status = models.IntegerField(choices=PROCESS_STATUS, default=1, help_text='处理状态')
    workflows = GenericRelation(WorkflowStateEvent, related_query_name='machine_workflow')

    class Meta:
        db_table = 'machine_workflow'

    def __str__(self):
        return self.title

    @classmethod
    def status_dict(cls):
        return dict(cls.PROCESS_STATUS)


class ProjectAdjust(models.Model):
    """项目调整工单
    """
    PROCESS_STATUS = (
        (0, '已处理'),
        (1, '故障中'),
        (2, '未处理'),
    )
    create_time = models.DateTimeField()
    creator = models.ForeignKey(User, help_text='发起人', on_delete=models.PROTECT)
    applicant = models.ForeignKey(User, related_name='adjust_user', help_text='申请人', on_delete=models.PROTECT)
    title = models.CharField(max_length=100, help_text='标题')
    raw_project_group = models.ForeignKey(
        ProjectGroup, blank=True, null=True, default=None, related_name='raw_project_group', help_text='原来的项目分组')
    delete_svn = models.BooleanField(default=False, help_text='默认不删除svn权限')
    svn_projects = models.CharField(max_length=255, blank=True, null=True, default=None,
                                    help_text='svn项目')  # json [1, 2]
    delete_svn_info = models.CharField(max_length=255, blank=True, null=True, default=None, help_text='清除svn的情况')
    delete_serper = models.BooleanField(default=False, help_text='默认不删除服务器权限')
    serper_projects = models.CharField(
        max_length=255, blank=True, null=True, default=None, help_text='服务器项目')  # json [1, 2]
    delete_serper_info = models.CharField(max_length=255, blank=True, null=True, default=None, help_text='清除服务器权限的情况')
    new_project_group = models.ForeignKey(
        ProjectGroup, related_name='new_project_group', blank=True, null=True, default=None, help_text='调入的项目分组')
    new_group_section = models.ForeignKey(GroupSection, blank=True, null=True, default=None, help_text='调入的部门分组-废弃')
    new_department_group = models.ForeignKey(OrganizationMptt, blank=True, null=True, default=None,
                                             help_text='调入的部门分组-新')
    status = models.IntegerField(choices=PROCESS_STATUS, default=2, help_text='处理状态')
    workflows = GenericRelation(WorkflowStateEvent, related_query_name='project_adjust_workflow')

    class Meta:
        db_table = 'project_adjust_workflow'

    def __str__(self):
        return self.title

    @classmethod
    def status_dict(cls):
        return dict(cls.PROCESS_STATUS)


class MysqlWorkflow(models.Model):
    """数据库申请
    """
    PROCESS_STATUS = (
        (0, '查看企业邮件通知'),
        (1, '故障中'),
        (2, '未处理'),
    )
    create_time = models.DateTimeField()
    creator = models.ForeignKey(User, help_text='发起人', on_delete=models.PROTECT)
    applicant = models.ForeignKey(User, related_name='mysqlworkflow_user', help_text='申请人', on_delete=models.PROTECT)
    title = models.CharField(max_length=100, help_text='标题')
    reason = models.CharField(max_length=255, help_text='申请原因')
    content = models.TextField(help_text='申请的实例内容')
    status = models.IntegerField(choices=PROCESS_STATUS, default=2, help_text='处理状态')
    workflows = GenericRelation(WorkflowStateEvent, related_query_name='mysql_workflow')

    class Meta:
        db_table = 'mysql_workflow'

    def __str__(self):
        return self.title

    @classmethod
    def status_dict(cls):
        return dict(cls.PROCESS_STATUS)


class ComputerParts(models.Model):
    """办公电脑和配件申请流程
    """

    PROCESS_STATUS = (
        (0, '已处理'),
        (1, '未处理'),
    )

    create_time = models.DateTimeField()
    creator = models.ForeignKey(User, help_text='发起人', on_delete=models.PROTECT)
    applicant = models.ForeignKey(User, related_name='computer_parts_user', help_text='申请人', on_delete=models.PROTECT)
    title = models.CharField(max_length=100, help_text='标题')
    reason = models.CharField(max_length=200, help_text='申请原因')
    status = models.IntegerField(choices=PROCESS_STATUS, default=1, help_text='处理状态')
    state_object = GenericRelation(StateObjectUserRelation, related_query_name='computer_parts_sor')
    workflows = GenericRelation(WorkflowStateEvent, related_query_name='computer_parts_workflow')

    class Meta:
        db_table = 'computer_parts_workflow'

    def __str__(self):
        return self.title

    @classmethod
    def status_dict(cls):
        return dict(cls.PROCESS_STATUS)


class GameServerType(models.Model):
    """区服的类型，各个项目的区服类型都不同
    """

    project = models.ForeignKey(GameProject, help_text='关联的游戏项目')
    game_type_code = models.CharField(max_length=20, help_text='类型代号')
    game_type_text = models.CharField(max_length=50, help_text='类型代号对应的值')

    class Meta:
        db_table = 'myworkflows_game_server_type'
        unique_together = (('project', 'game_type_code'), ('project', 'game_type_text'))

    def __str__(self):
        return self.game_type_code + ':' + self.game_type_text

    def show_all(self):
        return {
            'id': self.id,
            'project_name': self.project.project_name,
            'project_name_en': self.project.project_name_en,
            'game_type_code': self.game_type_code,
            'game_type_text': self.game_type_text,
        }

    def edit_data(self):
        return {
            'id': self.id,
            'project_id': self.project.id,
            'project_name': self.project.project_name,
            'game_type_code': self.game_type_code,
            'game_type_text': self.game_type_text,
        }


class GameServer(models.Model):
    """热更新和版本更新所需的区服列表
    """
    PTYPE = (
        (0, '手游'),
        (1, '页游'),
    )

    STATUS = (
        (0, '正常'),
        (1, '注销'),
        (4, '关闭平台'),
        (5, '正在合服'),
        (6, '正在重启'),
        (7, '正在清档'),
        (8, '正在开服'),
        (9, '正在关服'),
        (10, '正在迁服'),
    )

    project_type = models.IntegerField(choices=PTYPE, default=1, help_text='项目类型, 手游or页游')
    project = models.ForeignKey(GameProject, help_text='关联cmdb的项目')
    srv_status = models.IntegerField(choices=STATUS, default=0, help_text='状态')
    room = models.ForeignKey(Room, on_delete=models.PROTECT, help_text='关联cmdb的机房')
    host = models.ForeignKey(Host, on_delete=models.PROTECT, help_text='所属的主机')
    game_type = models.ForeignKey(GameServerType, help_text='关联的游戏区服类型外键')
    pf_name = models.CharField(max_length=20, help_text='平台名, 37, qq')
    srv_id = models.CharField(max_length=50, help_text='区服id, liebao_10003')
    srv_name = models.CharField(max_length=15, blank=True, null=True, help_text='抢鲜12服')
    ip = models.GenericIPAddressField(help_text='ip')
    merge_id = models.CharField(max_length=50, blank=True, null=True, default=None, help_text='合服相对id,和project一起确定主服')
    merge_time = models.DateTimeField(blank=True, null=True, default=None, help_text='合服时间')
    client_version = models.CharField(max_length=50, help_text='前端版本号')
    server_version = models.CharField(max_length=50, help_text='后端版本号')
    cdn_root_url = models.CharField(max_length=100, help_text='cdn根url')
    cdn_dir = models.CharField(max_length=50, blank=True, null=True, help_text='cdn目录')
    open_time = models.CharField(max_length=200, help_text='开服时间，时间戳')
    area_name = models.CharField(max_length=10, help_text='游戏区域')
    sid = models.BigIntegerField(null=True, blank=True, help_text='web的区服id')

    class Meta:
        db_table = 'myworkflows_game_server'
        unique_together = ('project', 'srv_id', 'area_name')

    def __str__(self):
        return self.srv_name + '-' + self.srv_id

    def get_ip_info(self):
        """获取游戏服的IP信息
        """
        ip_list = []

        internal_ip = '内网IP:' + self.ip
        ip_list.append(internal_ip)

        if self.host.telecom_ip:
            telecom_ip = '电信IP:' + str(self.host.telecom_ip)
            ip_list.append(telecom_ip)

        if self.host.unicom_ip:
            unicom_ip = '联通IP:' + str(self.host.unicom_ip)
            ip_list.append(unicom_ip)

        return ','.join(ip_list)

    def show_all(self):
        return {
            'id': self.id,
            'project_type': self.get_project_type_display(),
            'project': self.project.project_name,
            'srv_status': self.get_srv_status_display(),
            'game_type': self.game_type.game_type_text,
            'pf_name': self.pf_name,
            'srv_id': self.srv_id,
            'srv_name': self.srv_name,
            'room': self.room.area.chinese_name + '-' + self.room.room_name,
            'ip': self.get_ip_info(),
            'merge_id': self.merge_id if self.merge_id else '',
            'merge_time': self.merge_time.strftime('%Y-%m-%d %H:%M') if self.merge_time else '',
            "client_version": self.client_version,
            'server_version': self.server_version,
            'cdn_root_url': self.cdn_root_url,
            'cdn_dir': self.cdn_dir,
            'open_time': time.strftime('%Y-%m-%d %H:%M', time.localtime(float(self.open_time))),
            'area_name': self.host.belongs_to_room.area.chinese_name,
            'sid': self.sid,
        }

    def show_cdn_client_version(self):
        '展示cdn和客户端版本号以及机房的信息'
        return {
            'id': self.id,
            'cdn_root_url': self.cdn_root_url,
            'cdn_dir': self.cdn_dir,
            'client_version': self.client_version,
            'room': self.room.id,
        }

    def show_server_list_info(self):
        "展示热更新需要的字段"
        return {
            'srv_name': self.srv_name if self.srv_name else self.srv_id,
            'srv_id': self.srv_id,
            'ip': self.ip,
            'gameserverid': str(self.id),
        }

    def get_ops_manager(self):
        if not self.host:
            return None
        ops = self.host.opsmanager
        if not ops:
            return None
        return ops

    @staticmethod
    def get_srv_status_tuple_remark(srv_status):
        for status_tuple in GameServer.STATUS:
            if str(status_tuple[0]) == str(srv_status):
                return status_tuple[1]
        return '未知'


class WXAccessToken(models.Model):
    """微信token记录表"""
    access_token = models.TextField(verbose_name=u'access_token')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name=u'token生成时间')
    expires_time = models.DateTimeField(verbose_name=u'token过期时间')
    valid = models.IntegerField(choices=((0, u'失效'), (1, u'有效')), default=1, verbose_name=u'token可用状态')

    class Meta:
        verbose_name = u'微信token记录表'
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return self.access_token


class GameServerActionRecord(models.Model):
    """区服管理操作记录表"""
    ACTION_TYPE = (
        ('start', u'开服'),
        ('stop', u'关服'),
        ('restart', u'重启'),
        ('clean', u'清档'),
        ('merge', u'合服'),
        ('install', u'装服'),
        ('migrate', u'迁服'),
        ('add', u'新增'),
        ('update', u'修改'),
        ('delete', u'删除'),
    )
    ACTION_RESULT = (
        (0, u'执行失败'),
        (1, u'执行成功'),
        (2, u'执行中')
    )
    game_server = models.ForeignKey(GameServer, null=True, blank=True, on_delete=models.SET_NULL, verbose_name=u'关联区服')
    operation_type = models.CharField(max_length=20, choices=ACTION_TYPE, verbose_name=u'操作类型')
    operation_user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, verbose_name=u'操作人')
    operation_time = models.DateTimeField(auto_now_add=True, verbose_name=u'操作时间')
    result = models.IntegerField(choices=ACTION_RESULT, default=2, verbose_name=u'操作结果')
    remark = models.TextField(default='', verbose_name=u'失败原因备注')
    uuid = models.CharField(max_length=100, verbose_name='uuid')
    old_status = models.IntegerField(verbose_name=u'区服操作前的状态')
    source_ip = models.CharField(max_length=20, default='', verbose_name=u'操作来源IP')

    class Meta:
        verbose_name = u'区服管理操作记录表'
        verbose_name_plural = verbose_name

    def get_operation_type_chinese_word(self):
        return [x[1] for x in GameServerActionRecord.ACTION_TYPE if self.operation_type == x[0]][0]

    def show_all(self):
        return {
            'id': self.id,
            'project': self.game_server.project.project_name if self.game_server else '',
            'srv_id': self.game_server.srv_id if self.game_server else '',
            'area': self.game_server.host.belongs_to_room.area.chinese_name if self.game_server else '',
            'operation_type': self.get_operation_type_chinese_word(),
            'operation_user': self.operation_user.username if self.operation_user else '',
            'operation_time': str(self.operation_time)[:19],
            'result': self.get_result_display(),
            'remark': self.remark,
            'uuid': self.uuid,
            'source_ip': self.source_ip,
        }

    def get_relate_role_user(self):
        return self.game_server.project.get_relate_role_user()

    def __str__(self):
        return self.game_server.srv_id + self.get_operation_type_display()


class CeleryWorkerStatus(models.Model):
    """celery worker状态表"""
    STATUS = (
        (1, u'在线'),
        (0, u'离线'),
    )

    celery_hostname = models.CharField(max_length=50, verbose_name=u'celery worker的hostname')
    status = models.IntegerField(choices=STATUS, default=1, verbose_name=u'worker状态')
    total = models.IntegerField(default=0, verbose_name=u'启动后执行任务次数')
    off_count = models.IntegerField(default=0, verbose_name=u'告警发生次数，恢复后清零')

    class Meta:
        verbose_name = u'celery worker状态表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.celery_hostname


class CeleryReceiveNoticeUser(models.Model):
    """celery告警信息通知接收人表"""
    receive_user = models.ForeignKey(User, verbose_name=u'接收通知人')

    class Meta:
        verbose_name = u'celery告警信息通知接收人表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.receive_user.username


class HostCompressionApply(models.Model):
    """主机回收申请表"""
    TYPE = (
        (1, u'空闲回收'),
        (2, u'迁服回收'),
        (3, u'关服回收'),
    )
    ACTION_STATUS = (
        (1, u'未迁服'),
        (2, u'迁服中'),
        (3, u'迁服成功'),
        (4, u'迁服失败'),
        (5, u'取消'),
    )
    RECOVER_STATUS = (
        (1, u'未回收'),
        (2, u'回收中'),
        (3, u'回收成功'),
        (4, u'回收失败'),
        (5, u'取消'),
    )
    title = models.CharField(max_length=60, verbose_name=u'工单标题')
    ops = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, verbose_name=u'工单当前处理人')
    type = models.IntegerField(choices=TYPE, verbose_name=u'操作类型')
    action_time = models.DateTimeField(null=True, blank=True, verbose_name=u'迁服时间')
    action_deadline = models.DateTimeField(null=True, blank=True, verbose_name=u'迁服截止时间')
    recover_time = models.DateTimeField(null=True, blank=True, verbose_name=u'回收时间')
    recover_deadline = models.DateTimeField(null=True, blank=True, verbose_name=u'回收截止时间')
    action_status = models.IntegerField(choices=ACTION_STATUS, default=1, verbose_name=u'执行状态')
    recover_status = models.IntegerField(choices=RECOVER_STATUS, default=1, verbose_name=u'执行状态')
    uuid = models.CharField(max_length=255, unique=True, verbose_name=u'更新的唯一id')
    apply_user = models.CharField(max_length=10, verbose_name=u'申请人')
    apply_time = models.DateTimeField(auto_now_add=True, verbose_name=u'申请时间')
    project = models.ForeignKey(GameProject, null=True, blank=True, on_delete=models.SET_NULL, verbose_name=u'所属项目')
    room = models.ForeignKey(Room, null=True, blank=True, on_delete=models.SET_NULL, verbose_name=u'所属机房')

    class Meta:
        verbose_name = u'主机回收申请表'
        verbose_name_plural = verbose_name

    def show_all(self):
        return {
            'id': self.id,
            'title': self.title,
            'project': self.project.project_name,
            'room': self.room.area.chinese_name + '-' + self.room.room_name if self.room else self.hostcompressiondetail_set.first().get_host_obj().belongs_to_room.area.chinese_name + '-' + self.hostcompressiondetail_set.first().get_host_obj().belongs_to_room.room_name,
            'uuid': self.uuid,
            'ops': self.ops.username if self.ops else '',
            'type': self.get_type_display(),
            'hosts': ','.join([x.ip for x in self.hostcompressiondetail_set.order_by('id')]),
            'action_time': str(self.action_time)[:16] if self.action_time else '',
            'action_status': self.get_action_status_display(),
            'action_status_detail': ','.join([x.get_migration_status_display() + '-' + x.migration_remark for x in
                                              self.hostcompressiondetail_set.order_by('id')]),
            'recover_time': str(self.recover_time)[:16] if self.recover_time else '',
            'recover_status': self.get_recover_status_display(),
            'recover_status_detail': ','.join([x.get_recover_status_display() + '-' + x.recover_remark for x in
                                               self.hostcompressiondetail_set.order_by('id')]),
            'apply_user': self.apply_user,
            'apply_time': str(self.apply_time)[:16],
            'action_deadline': str(self.action_deadline)[:16],
            'recover_deadline': str(self.recover_deadline)[:16],
        }

    def detail_data(self):
        detail_list = []
        for x in self.hostcompressiondetail_set.all():
            detail_dict = {}
            detail_dict['ip'] = x.ip
            host = Host.objects.filter(telecom_ip=x.ip)
            if host:
                host = host[0]
                detail_dict['project'] = host.belongs_to_game_project.project_name
                detail_dict['room'] = host.belongs_to_room.room_name
                detail_dict['business'] = host.belongs_to_business.business_name
            else:
                detail_dict['project'] = ''
                detail_dict['room'] = ''
                detail_dict['business'] = ''
            detail_dict['type'] = self.get_type_display()
            detail_dict['recover_status'] = x.get_recover_status_display()
            detail_dict['recover_remark'] = x.recover_remark
            if self.type == 2:
                detail_dict['migration_status'] = x.get_migration_status_display()
            detail_dict['migration_remark'] = x.migration_remark
            detail_list.append(detail_dict)
        return detail_list

    def edit_data(self):
        return {
            'id': self.id,
            'title': self.title,
            'ops_id': self.ops.id if self.ops else -1,
            'ops_text': self.ops.username if self.ops else '',
            'type_id': self.type,
            'type_text': self.get_type_display(),
            'action_time': str(self.action_time)[:16],
            'action_deadline': str(self.action_deadline)[:16],
            'action_status_id': self.action_status,
            'action_status_text': self.get_action_status_display(),
            'recover_time': str(self.recover_time)[:16] if self.recover_time else '',
            'recover_deadline': str(self.recover_deadline)[:16] if self.recover_deadline else '',
            'recover_status_id': self.recover_status,
            'recover_status_text': self.get_recover_status_display(),
        }

    def get_related_user(self):
        related_user_list = []
        for task in self.hostcompressiondetail_set.all():
            for related_user in task.get_related_user():
                if related_user not in related_user_list:
                    related_user_list.append(related_user)
        return related_user_list

    def get_relate_role_user(self):
        relate_role_user_list = set()
        for task in self.hostcompressiondetail_set.all():
            for relate_role_user in task.get_relate_role_user():
                relate_role_user_list.add(relate_role_user)
        return list(relate_role_user_list)

    def __str__(self):
        return self.title


class HostCompressionDetail(models.Model):
    """主机回收申请明细表"""
    M_STATUS = (
        (0, u'迁服失败'),
        (1, u'迁服成功'),
        (2, u'未迁服'),
    )
    R_STATUS = (
        (0, u'回收失败'),
        (1, u'回收成功'),
        (2, u'未回收'),
    )
    apply = models.ForeignKey(HostCompressionApply, on_delete=models.CASCADE, verbose_name=u'所属申请单')
    ip = models.CharField(max_length=50, verbose_name=u'IP地址')
    migration_status = models.IntegerField(choices=M_STATUS, default=2, verbose_name=u'迁服状态')
    migration_remark = models.TextField(default='无', verbose_name=u'迁移结果备注')
    recover_status = models.IntegerField(choices=R_STATUS, default=2, verbose_name=u'回收状态')
    recover_remark = models.TextField(default=u'无', verbose_name=u'回收结果备注')

    class Meta:
        verbose_name = u'主机回收申请明细表'

    def get_host_obj(self):
        obj = Host.objects.filter(telecom_ip=self.ip)
        if obj:
            return obj[0]
        else:
            return None

    def get_related_user(self):
        return self.get_host_obj().belongs_to_game_project.related_user.all()

    def get_relate_role_user(self):
        return self.get_host_obj().belongs_to_game_project.get_relate_role_user()

    def get_srv_mgiration_status_list(self):
        return [x.status for x in self.hostmigratesrvdetail_set.all()]

    def check_srv_statue(self):
        for srvdetail in self.hostmigratesrvdetail_set.all():
            if srvdetail.status == 0:
                return 0
        if 2 in self.get_srv_mgiration_status_list():
            return 2
        if len(list(set(self.get_srv_mgiration_status_list()))) == 1 and 1 in self.get_srv_mgiration_status_list():
            return 1

    def get_failure_srv(self):
        failure_srv_list = []
        for srvdetail in self.hostmigratesrvdetail_set.all():
            if srvdetail.status == 0:
                failure_srv_list.append(str(srvdetail.sid))
        return ','.join(failure_srv_list)

    def __str__(self):
        return self.ip


class HostCompressionLog(models.Model):
    """主机回收任务日志"""
    host_compression = models.OneToOneField(HostCompressionApply, verbose_name=u'所属主机回收申请')
    log = models.TextField(default='', verbose_name=u'任务执行日志内容')

    class Meta:
        verbose_name = u'主机回收任务日志'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.host_compression.title


class HostMigrateSrvDetail(models.Model):
    """主机迁服区服明细表"""
    STATUE = (
        (0, u'迁服失败'),
        (1, u'迁服成功'),
        (2, u'未执行'),
    )
    migrate_host = models.ForeignKey(HostCompressionDetail, on_delete=models.CASCADE, verbose_name=u'所属迁服主机')
    sid = models.IntegerField(verbose_name=u'区服id')
    status = models.IntegerField(choices=STATUE, default=2, verbose_name=u'迁服状态')
    remark = models.TextField(default='', verbose_name=u'迁服结果备注')

    class Meta:
        verbose_name = u'主机迁服区服明细表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.sid


class ProjectCeleryQueueMap(models.Model):
    """项目英文名到celery任务队列的对应关系"""
    USE = (
        (1, '拉取'),
        (2, '推送'),
    )
    project = models.ForeignKey(GameProject, on_delete=models.CASCADE, verbose_name=u'所属项目')
    celery_queue = models.CharField(max_length=50, verbose_name=u'celery任务队列名')
    use = models.IntegerField(choices=USE, verbose_name=u'用途')
    worker = models.ForeignKey(CeleryWorkerStatus, null=True, blank=True, on_delete=models.SET_NULL,
                               verbose_name=u'所属celery worker')

    class Meta:
        verbose_name = u'项目英文名到celery任务队列的对应关系表'
        verbose_name_plural = verbose_name
        unique_together = ('project', 'celery_queue')

    def show_all(self):
        return {
            'id': self.id,
            'project_name': self.project.project_name,
            'project_name_en': self.project.project_name_en,
            'celery_queue': self.celery_queue,
            'use': self.get_use_display(),
            'worker': self.worker.celery_hostname if self.worker else '',
        }

    def edit_data(self):
        return {
            'id': self.id,
            'project_id': self.project.id,
            'project': self.project.project_name,
            'celery_queue': self.celery_queue,
            'use_id': self.use,
            'use': self.get_use_display(),
            'worker_id': self.worker.id if self.worker else '',
            'worker': self.worker.celery_hostname if self.worker else '',
        }

    def __str__(self):
        return self.celery_queue + '-' + self.project.project_name_en + '-' + self.get_use_display()


class SpecialUserParamConfig(models.Model):
    """工单流程中涉及的特殊人员参数配置"""
    user = models.ManyToManyField(User, verbose_name=u'关联用户表对象')
    param = models.CharField(max_length=50, unique=True, verbose_name=u'参数名称')
    remark = models.CharField(max_length=100, null=True, blank=True, verbose_name=u'备注')

    class Meta:
        verbose_name = u'特殊人员配置表'
        verbose_name_plural = verbose_name

    def edit_data(self):
        return {
            'id': self.id,
            'param': self.param,
            'remark': self.remark,
            'special_user': [{'id': x.id, 'username': x.username} for x in self.user.all()],
        }

    def get_user_obj_list(self):
        return [x for x in self.user.all() if x.is_active]

    def get_user_list(self):
        return [x.username for x in self.user.all() if x.is_active]

    def get_user_first_name_list(self):
        return [x.first_name for x in self.user.all() if x.is_active]

    def get_user_email_list(self):
        return [x.email for x in self.user.all() if x.is_active]

    def __str__(self):
        return self.param


class WechatAccountTransfer(models.Model):
    """cmdb帐号与企业微信帐号的转换表"""
    cmdb_account = models.ForeignKey(User, verbose_name=u'所属cmdb帐号')
    wechat_account = models.CharField(max_length=30, verbose_name=u'企业微信帐号')

    class Meta:
        verbose_name = u'cmdb帐号与企业微信帐号的转换表'
        verbose_name_plural = verbose_name

    def edit_data(self):
        return {
            'cmdb_account_id': self.cmdb_account.id,
            'cmdb_account': self.cmdb_account.username + '(' + self.cmdb_account.first_name + ')',
            'wechat_account': self.wechat_account,
        }

    def __str__(self):
        return self.wechat_account


class HotUpdateTemplate(models.Model):
    """热更新工单模板"""
    TYPE = (
        (1, '前端'),
        (2, '后端'),
    )
    name = models.CharField(max_length=20, verbose_name=u'模板名称')
    tag = models.CharField(max_length=10, null=True, blank=True, verbose_name=u'模板标签')
    type = models.IntegerField(choices=TYPE, default=1, verbose_name=u'模板类型')
    remark = models.TextField(default='', verbose_name='模板信息备注')

    class Meta:
        verbose_name = u'热更新工单模板'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class HotUpdateTemplateItems(models.Model):
    """热更新工单模板子项"""
    template = models.ForeignKey(HotUpdateTemplate, on_delete=models.CASCADE, verbose_name=u'所属模板')
    image = models.ImageField(null=True, blank=True, upload_to='cmdb/static/img/hotupdate_templates',
                              verbose_name=u'图片')

    class Meta:
        verbose_name = u'热更新工单模板子项'
        verbose_name_plural = verbose_name

    def get_image_url(self):
        if self.image:
            return self.image.url[4:]
        return ''

    def __str__(self):
        return ' '
