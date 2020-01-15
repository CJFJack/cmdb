# -*- encoding: utf-8 -*-
# django imports
from django.contrib.contenttypes.models import ContentType
from django.db import IntegrityError
from django.db.models import Q
from django.db.models import Count
from django.db.models import Sum
from django.core.exceptions import MultipleObjectsReturned

from myworkflows.models import *
from myworkflows.exceptions import *
from myworkflows.myredis import *
from myworkflows.workflow_approve_user_by_chain import get_approve_user_chain

from assets.models import OpsManager
from assets.models import Host
from assets.models import GroupSection
from users.models import UserProfileHost
from users.models import GroupProfile
from users.models import OrganizationMptt, Profile

from cmdb.logs import SerPerLog, SVNLog
from cmdb.logs import HotUpdateLog, WorkflowApproveLog, SendWxTaskCardLog
from cmdb.settings import REDIS_URL
from cmdb.settings import PRODUCTION_ENV

# from tasks import do_hot_client

from myworkflows.config import *
# from myworkflows.rsync_conf import CMDB_PROJECT_MAP

from django.contrib.auth.models import Group
from django.db import transaction

from itertools import chain
from datetime import datetime, timedelta
from channels import Channel

import json
import hashlib
import requests
import os
import celery

from collections import defaultdict
from django.http import JsonResponse
from django.forms.models import model_to_dict
from requests.packages.urllib3.util import Retry
from requests.adapters import HTTPAdapter
from requests import Session

# hot_update_log = HotUpdateLog()


# svn执行人
SVN_EXCUTORS = [
    '梁保明',
    '梁太生',
]


def is_state_user(wse, user):
    """判断当前的user是否在state下的users中

    有两种情况
    1 state下的users
    2 根据wse的content_object 和state获取sor下面的users

    返回True or False
    """

    state = wse.state

    if user in state.specified_users.all():
        return True

    # 从StateObjectUserRelation表中获取users
    sor = get_sor(wse.state, wse.content_object)

    if sor:
        if user in sor.users.all():
            return True

    return False


def get_sor(state, obj):
    """根据state和obj从StateObjectUserRelation中获取一条记录"""

    ctype = ContentType.objects.get_for_model(obj)

    try:
        sor = StateObjectUserRelation.objects.get(content_type=ctype, object_id=obj.id, state=state)
    except StateObjectUserRelation.DoesNotExist:
        return None

    return sor


def get_wse(state, obj):
    """根据state和object从WorkflowStateEvent获取唯一的记录"""

    ctype = ContentType.objects.get_for_model(obj)

    try:
        wse = WorkflowStateEvent.objects.get(content_type=ctype, object_id=obj.id, state=state)
    except WorkflowStateEvent.DoesNotExist:
        return None

    return wse


def can_delete_workflow(list_content_object):
    """对于已经发起的申请，能够删除的条件

    条件1 被拒绝
    条件2 任何审批节点都未执行

    返回True 或者引发异常
    """

    list_content_type_object_id = []

    q_objects = Q()

    for x in list_content_object:
        content_type_object_id = {}
        content_type_object_id['content_type'] = ContentType.objects.get_for_model(x)
        content_type_object_id['object_id'] = x.id
        list_content_type_object_id.append(content_type_object_id)

    for x in list_content_type_object_id:
        q_objects.add(Q(**x), Q.OR)

    wse_query_set = WorkflowStateEvent.objects.filter(q_objects)

    for wse in wse_query_set:
        if wse.state_value == '拒绝':
            return True

    for wse in wse_query_set:
        # 如果存在审批意见
        if wse.state_value:
            raise WorkflowError('不能删除已经审批的流程!')

    return True


def get_state_user(state, obj=None, list_format=False):
    """根据obj和state获取用户"""

    if not obj:
        return state.specified_users.all()
    else:
        sor = get_sor(state, obj)
        if sor:
            if list_format:
                list_user = []
                list_specified_users = list(state.specified_users.all())
                list_sor_users = list(sor.users.all())
                list_user.extend(list_specified_users)
                list_user.extend(list_sor_users)
                return list_user
            else:
                user_list = [x for x in list(sor.users.all())]
                return user_list
        else:
            return state.specified_users.all()


def get_approved_users_from_wse_by_obj(content_obj):
    """根据content_obj获取sor中所有的用户
    """

    ctype = ContentType.objects.get_for_model(content_obj)
    list_wse = WorkflowStateEvent.objects.filter(content_type=ctype, object_id=content_obj.id).exclude(state__name='完成')
    list_user = []

    for wse in list_wse:
        list_user.append(wse.approve_user)

    return list_user


def get_hot_update_all_related_user(content_obj, project_ops_user=False):
    """获取某个热更新中所有需要通知的相关用户
    1 工单发起人
    2 工单各个节点审批人
    3 需要额外通知的人
    """

    # 全部的通知人员
    all_users = []

    # 工单发起人
    applicant = content_obj.applicant

    # 工单审批人
    list_approve_user = get_approved_users_from_wse_by_obj(content_obj)

    # 额外需要通知的人
    extra = list(content_obj.extra.all())

    # 是否需要通知项目上的运维
    if project_ops_user:
        list_project_ops_user = content_obj.project.related_user.all()
    else:
        list_project_ops_user = []

    # 全部组合在一起
    all_users.append(applicant)
    all_users.extend(list_approve_user)
    all_users.extend(extra)
    all_users.extend(list_project_ops_user)
    all_users = list(set(all_users))

    # 排除离职的用户
    all_users = [x for x in all_users if x is not None and x.is_active]

    return all_users


def get_workflow_user(workflow, obj):
    """获取某个workflow的所有需要审批的用户

    从state的specified_users中和sor中获取

    返回user list

    """

    pass


def is_group_or_project_leader(user):
    """判断用户是否为部门或者项目负责人
    """

    list_group_leader = [x.groupprofile.group_leader for x in Group.objects.all()]

    list_project_leader = [x.leader for x in GameProject.objects.all()]

    if (user in list_group_leader or user in list_project_leader):
        return True
    else:
        return False


def is_group_leader(user, show_group=False):
    """判断用户是否为部门负责人
    包括一二级部门
    如果使用了show_group的参数，则同时返回所属部门
    """

    """
    过时的方法，效率不高
    list_group_leader = [x.groupprofile.group_leader for x in Group.objects.select_related('groupprofile').all()]

    if user in list_group_leader:
        return True
    else:
        return False
    """

    for group_profile in GroupProfile.objects.select_related('group_leader').all():
        if user == group_profile.group_leader:
            if show_group:
                return (True, group_profile.group)
            else:
                return True
    else:
        return False


def is_organization_leader(user):
    """
    判断用户是否为所有组织节点的负责人之一
    """
    result = False
    for org in OrganizationMptt.objects.filter(type=1):
        if user.id == org.user_id:
            result = True
    return result


def is_group_section_leader(user, show_group_section=False):
    """
    判断用户是否为部门分组负责人
    这里可以理解为三级部门负责人
    如果使用了show_group的参数，则同时返回所属部门分组
    """

    for group_section in GroupSection.objects.select_related('leader').all():
        if user == group_section.leader:
            if show_group_section:
                return (True, group_section)
            else:
                return True
    else:
        return False


def is_orgnization_group_leader(user):
    """
    判断用户是否为部门分组负责人，若部门为项目组，则判断是否项目下分组负责人
    默认判断用户上一级，即传入用户的org对象的parent.leader是否为传入用户的user_id相同
    """

    org_obj = OrganizationMptt.objects.get(user_id=user.id)
    parent_obj = org_obj.parent
    if parent_obj.user_id == user.id:
        return True
    else:
        return False


def has_approved_user(wse, user):
    """获取workflow state event下相同的obj

    根据相同的obj获取state下的用户
    如果该记录有state_value的值，说明已经审批过

    返回True or False
    """

    content_obj = wse.content_object

    ctype = ContentType.objects.get_for_model(content_obj)

    listWorkflowStateEvent = WorkflowStateEvent.objects.filter(content_type=ctype, object_id=content_obj.id)

    if listWorkflowStateEvent:
        for w in listWorkflowStateEvent:
            if user in get_state_user(w.state, w.content_object):
                return True
        return False
    else:
        return False


def get_approved_user(workflow, obj, next_state_user):
    """根据workflow和申请的obj

    从state或者sor中获取所有的需要审批的用户，如果之前的用户已经审批过，返回用户
    不然，返回None
    """

    ctype = ContentType.objects.get_for_model(obj)

    list_wse = WorkflowStateEvent.objects.filter(content_type=ctype, object_id=obj.id)

    for wse in list_wse:
        if wse.approve_user in next_state_user:
            return wse.approve_user

    return None


def do_transition(wse, transition, user, opinion=None):
    """发生转化的条件

    1 wse的is_current 为True
    2 transition在当前的wse的state中
    3 user在当前的wse的state中, 对应applicant
    4 当前的state_value为空
    """
    wse_log = WorkflowApproveLog()

    transitions = wse.state.transition.all()
    approve_user_list = get_state_user(wse.state, wse.content_object)

    if not wse.is_current:
        msg = '不是当前状态，不能审批'
        success = False
        return (msg, success, wse)

    if transition not in transitions:
        msg = '要转化的transition不在当前状态transition列表中'
        success = False
        return (msg, success, wse)

    if user not in approve_user_list and user != wse.creator:
        msg = '你没有审批的权限'
        success = False
        return (msg, success, wse)

    if wse.state_value:
        msg = '你已经审批过'
        success = False
        return (msg, success, wse)

    wse_log.logger.info(
        '第2节点： 审批人：{}，审批意见：{}，工单标题：{}，wse_id：{}，is_current：{}'.format(user.username, transition.condition,
                                                                      wse.title, wse.id, wse.is_current))
    new_wse = set_state(wse, transition, user, opinion=opinion)
    wse_log.logger.info(
        '第7节点： 审批人：{}，审批意见：{}，工单标题：{}，wse_id：{}，is_current：{}'.format(user.username, transition.condition,
                                                                      wse.title, wse.id, wse.is_current))

    msg = ''
    success = True

    return (msg, success, new_wse)


def set_state(wse, transition, user, opinion=None):
    """根据当前的wse新增一条

    如果是在多次审批的情况下，直接get出来
    user对应applicant
    """
    wse_log = WorkflowApproveLog()

    try:
        with transaction.atomic():
            # 创建下一个节点的wse
            new_wse = WorkflowStateEvent.objects.create(
                content_object=wse.content_object, state=transition.destination,
                create_time=wse.create_time, creator=wse.creator, title=wse.title, is_current=True, opinion=opinion)

            # 当前的wse设置为已经审批过
            wse.is_current = False
            wse.state_value = transition.condition
            wse.approve_user = user
            wse.approve_time = datetime.now()
            wse.opinion = opinion
            wse.save()
            wse_log.logger.info(
                '第3节点： 审批人：{}，审批意见：{}，工单标题：{}，wse_id：{}，is_current：{}'.format(user.username, transition.condition,
                                                                              wse.title, wse.id, wse.is_current))

            # 如果是不是部门负责人或者项目负责人，CEO节点自动审批通过
            # group_or_project_leader = is_group_or_project_leader(new_wse.content_object.applicant)

            """去掉CEO审批的环节
            if not group_or_project_leader and new_wse.state.name == 'CEO':
                user = new_wse.state.specified_users.all()[0]
                transition = new_wse.state.transition.get(condition='同意')
                return set_state(new_wse, transition, user)
            """

            # 如果下一个审批节点的审批用户还是自己
            # 或者是下一个节点审批人是工单发起人自身
            # 或者是下一个节点的审批用户已经审批过之前的节点
            next_state_user = get_state_user(new_wse.state, obj=new_wse.content_object, list_format=True)

            if user in next_state_user:
                transition = new_wse.state.transition.get(condition='同意')
                return set_state(new_wse, transition, user)
            elif new_wse.creator in next_state_user:
                transition = new_wse.state.transition.get(condition='同意')
                return set_state(new_wse, transition, new_wse.creator)
            else:
                approved_user = get_approved_user(new_wse.state.workflow, new_wse.content_object, next_state_user)
                if approved_user:
                    transition = new_wse.state.transition.get(condition='同意')
                    return set_state(new_wse, transition, approved_user)
                else:
                    wse_log.logger.info('第4节点： 审批人：{}，审批意见：{}，工单标题：{}，wse_id：{}，is_current：{}'.format(user.username,
                                                                                                      transition.condition,
                                                                                                      wse.title, wse.id,
                                                                                                      wse.is_current))
                    return new_wse

    except IntegrityError:
        # 如果是拒绝的
        wse.approve_user = user
        wse.state_value = transition.condition
        wse.opinion = opinion
        """
        若重复请求，创建new_wse时会由于主键冲突而导致IntegrityError
        防止因为重复请求导致is_current值不正确的问题
        """
        if transition.condition == '同意':
            wse.is_current = False
        wse.approve_time = datetime.now()
        wse.save()
        wse_log.logger.error(
            '第5节点： 审批人：{}，审批意见：{}，工单标题：{}，wse_id：{}，is_current：{}'.format(user.username, transition.condition,
                                                                          wse.title, wse.id, wse.is_current))
        return wse

    except Exception as e:
        wse_log.logger.error('第6节点： 审批人：{}，审批意见：{}，工单标题：{}，wse_id：{}，is_current：{}，exception：{}'.format(user.username,
                                                                                                        transition.condition,
                                                                                                        wse.title,
                                                                                                        wse.id,
                                                                                                        wse.is_current,
                                                                                                        str(e)))
        return wse


def reset_init_state(wse):
    """将当前的流程state重置到初始化状态

    这个函数由state选择了拒绝后触发

    重置条件
    1 wse的state为当前状态
    2 wse的state_vlaue 为拒绝

    """

    if wse.is_current and wse.state_value == '拒绝':
        # 清除掉除了初始state的所有state
        content_obj = wse.content_object
        ctype = ContentType.objects.get_for_model(content_obj)
        init_state = wse.state.workflow.init_state

        WorkflowStateEvent.objects.filter(content_type=ctype, object_id=content_obj.id).exclude(
            state=init_state).delete()

        # 将初始state设置为当前状态，并且state_value为None
        init_wse = WorkflowStateEvent.objects.get(content_type=ctype, object_id=content_obj.id, state=init_state)

        init_wse.is_current = True
        init_wse.state_value = None
        init_wse.send_mail = 0
        init_wse.save()
        return init_wse
    else:
        raise CurrentStateError('当前状态不能重新提交')


def set_state_obj_user(obj, workflow_obj, user, project):
    """设置state obj 下的审批用户

    user是申请人, applicant
    """
    if workflow_obj.name == 'SVN申请':
        """审批节点选择
        1 如果选择的项目是游戏项目:
            如果是部门负责人，那么部门负责人审批
            的人是该部门负责人的上一级部门负责人 张文辉->郑甲伟。

            如果不是部门负责人，部门负责人审批节点为申请人所在部门负责人.
        2 如果选择的是非游戏项目，部门负责人审批人为申请人说在部门负责人

        3 项目负责人审批人为申请项目的负责人
        """

        """
        2018.12修改，获取审批链，关联新组织架构
        """
        org = OrganizationMptt.objects.get(user_id=user.id)
        if obj.project.is_game_project:
            approve_list = org.get_all_parent_leader_list(True)
            approve_list.reverse()
            if len(approve_list) == 1:
                approve_list.insert(0, user.username)
            if len(approve_list) == 0:
                approve_list.insert(0, user.username)
                approve_list.insert(0, user.username)
        else:
            approve_list = org.get_all_parent_leader_list(False)
            approve_list.reverse()
            if len(approve_list) == 1:
                approve_list.insert(0, user.username)
            if len(approve_list) == 0:
                approve_list.insert(0, user.username)
                approve_list.insert(0, user.username)

        # 第一步
        # 部门分组负责人
        project_group_leader_name = approve_list[0]
        project_group_leader = User.objects.get(username=project_group_leader_name)
        # 小组长审批的state,这里对应的是svnworkflow流程的init_state
        project_group_leader_state = workflow_obj.init_state
        if not project_group_leader_state:
            raise WorkflowError('当前流程没有设置初始状态')
        # 创建obj, state 和user的关联
        sor = StateObjectUserRelation.objects.create(content_object=obj, state=project_group_leader_state)
        # 添加用户
        sor.users.add(project_group_leader)

        # 第二步
        # 部门的负责人
        group_leader_name = approve_list[1]
        group_leader = User.objects.get(username=group_leader_name)
        # 部门负责人审批的state，对应的是小组长审批的condition状态是同意的destination的state
        group_leader_state = project_group_leader_state.transition.get(condition='同意').destination
        # 创建三者之前的关系
        sor = StateObjectUserRelation.objects.create(content_object=obj, state=group_leader_state)
        sor.users.add(group_leader)
        if group_leader_name == '苏锡宝':
            sor.users.add(User.objects.get(username='孙珑'))

        # 第三步
        # 项目负责人
        project_leader = project.leader
        if not project_leader:
            raise WorkflowStateUserRelationError('项目负责人不存在')

        # 项目负责人审批的state,这里对应的是部门负责人审批的condition状态是同意的destination的state
        project_leader_state = group_leader_state.transition.get(condition='同意').destination

        # 创建三者之前的关系
        sor = StateObjectUserRelation.objects.create(content_object=obj, state=project_leader_state)
        sor.users.add(project_leader)

    if workflow_obj.name == '服务器权限申请':
        # 第一步
        # 小组长
        # 如果有小组长，是部门管理分组的组长
        # 如果没有小组长，则需要申请人自己审批
        """
        if obj.applicant.profile.group_section:
            project_group_leader = obj.applicant.profile.group_section.leader
        else:
            project_group_leader = user
        """

        """
        2018.12修改，获取审批链，关联新组织架构
        """
        org = OrganizationMptt.objects.get(user_id=user.id)
        approve_list = org.get_all_parent_leader_list(True)
        approve_list.reverse()
        if len(approve_list) == 1:
            approve_list.insert(0, user.username)
        if len(approve_list) == 0:
            approve_list.insert(0, user.username)
            approve_list.insert(0, user.username)

        # 第一步
        # 部门分组负责人
        project_group_leader_name = approve_list[0]
        project_group_leader = User.objects.get(username=project_group_leader_name)
        # 小组长审批的state,这里对应的是serverpermissionflow流程的init_state
        project_group_leader_state = workflow_obj.init_state
        if not project_group_leader_state:
            raise WorkflowError('当前流程没有设置初始状态')
        # 创建obj, state 和user的关联
        sor = StateObjectUserRelation.objects.create(content_object=obj, state=project_group_leader_state)
        # 添加用户
        sor.users.add(project_group_leader)

        # 第二步
        # 部门的负责人
        group_leader_name = approve_list[1]
        group_leader = User.objects.get(username=group_leader_name)
        # 部门负责人审批的state，对应的是小组长审批的condition状态是同意的destination的state
        group_leader_state = project_group_leader_state.transition.get(condition='同意').destination
        # 创建三者之前的关系
        sor = StateObjectUserRelation.objects.create(content_object=obj, state=group_leader_state)
        sor.users.add(group_leader)
        if group_leader_name == '苏锡宝':
            sor.users.add(User.objects.get(username='孙珑'))

        """
        # 第三步，运维负责人
        # 根据项目关联运维，找出相应的运维负责人
        # 如果没有，则指定全部的运维部的人,然后排除掉运维网络管理员组的人
        ops_manager = project.related_user.all()

        # 需要排除的账号
        exclude_users = User.objects.filter(username__in=['严文驰', '张文辉', '运维公共账户'])

        if not ops_manager:
            ops_manager = list(
                set(Group.objects.get(name='运维部').user_set.all()) - set(Group.objects.get(name='运维网络管理员组').user_set.all())
            )

            ops_manager = list(set(ops_manager) - set(exclude_users))

            # 去除掉离职的用户
            ops_manager = [x for x in ops_manager if x.is_active]

        # 运维负责人审批的state， 这里对应部门负责人state的condition为
        # 同意的destination的state
        ops_state = group_leader_state.transition.get(condition='同意').destination

        # 创建三者之间的关系
        sor = StateObjectUserRelation.objects.create(content_object=obj, state=ops_state)
        sor.users.add(*ops_manager)
        """

    if workflow_obj.name == 'wifi申请和网络问题申报':
        """
        2018.12修改，获取审批链，关联新组织架构，第一步部门负责人，第二步，网络管理员
        """
        """第一步，部门负责人"""
        org = OrganizationMptt.objects.filter(user=user)
        if not org:
            raise Exception('用户没有在新组织架构中')
        else:
            org = OrganizationMptt.objects.get(user=user)
            if not org.parent:
                raise UserNotInGroup('用户没有在部门里面')
            else:
                if org.parent.leader == 0 and org.parent.parent.leader == 0:
                    raise GroupExtentionError("申请人所在的部门没有设置负责人")
        if org.parent.is_department_group == 0:
            department_leader_id = org.parent.leader
        else:
            if org.parent.parent.is_department_group == 0:
                department_leader_id = org.parent.parent.leader
            else:
                if org.parent.parent.parent.is_department_group == 0:
                    department_leader_id = org.parent.parent.parent.leader
        group_leader = User.objects.get(pk=department_leader_id)

        # 部门负责人审批的state
        group_leader_state = workflow_obj.init_state
        if not group_leader_state:
            raise WorkflowError('当前流程没有设置初始状态')

        # 创建三者之前的关系
        sor = StateObjectUserRelation.objects.create(content_object=obj, state=group_leader_state)
        sor.users.add(group_leader)

        """第二步，网路管理员"""
        administrator_state = group_leader_state.transition.get(condition='同意').destination
        administrator = get_administrator(assigned_to='', administrator_state=administrator_state, classification=8)
        # 创建三者之前的关系
        sor = StateObjectUserRelation.objects.create(content_object=obj, state=administrator_state)
        sor.users.add(administrator)

    if workflow_obj.name == '办公电脑和配件申请':
        """
        2018.12修改，获取审批链，关联新组织架构 begin
        """
        org = OrganizationMptt.objects.get(user_id=user.id)
        approve_list = org.get_all_parent_leader_list(False)
        approve_list.reverse()
        if len(approve_list) == 1:
            approve_list.insert(0, user.username)
        if len(approve_list) == 0:
            approve_list.insert(0, user.username)
            approve_list.insert(0, user.username)

        # 第一步
        # 部门分组负责人
        project_group_leader_name = approve_list[0]
        project_group_leader = User.objects.get(username=project_group_leader_name)
        # 小组长审批的state,这里对应的是流程的init_state
        project_group_leader_state = workflow_obj.init_state
        if not project_group_leader_state:
            raise WorkflowError('当前流程没有设置初始状态')
        # 创建obj, state 和user的关联
        sor = StateObjectUserRelation.objects.create(content_object=obj, state=project_group_leader_state)
        # 添加用户
        sor.users.add(project_group_leader)

        # 第二步
        # 部门的负责人
        group_leader_name = approve_list[1]
        group_leader = User.objects.get(username=group_leader_name)
        # 部门负责人审批的state，对应的是小组长审批的condition状态是同意的destination的state
        group_leader_state = project_group_leader_state.transition.get(condition='同意').destination
        # 创建三者之前的关系
        sor = StateObjectUserRelation.objects.create(content_object=obj, state=group_leader_state)
        sor.users.add(group_leader)
        """
        2018.12修改，获取审批链，关联新组织架构 end
        """

        # 第三部，运维
        # 运维负责人审批的state， 这里对应部门负责人state的condition为
        # 同意的destination的state
        ops_state = group_leader_state.transition.get(condition='同意').destination

        # 网络管理员
        # admins = [x for x in Group.objects.get(name='运维网络管理员组').user_set.all() if x.is_active]
        admins = User.objects.filter(username__in=NETWORK_ADMINISTRATOR, is_active=1)

        # 创建三者之前的关系
        sor = StateObjectUserRelation.objects.create(content_object=obj, state=ops_state)
        sor.users.add(*admins)

    if workflow_obj.name == '数据库权限申请':
        """
        2018.12修改，获取审批链，关联新组织架构 begin
        """
        org = OrganizationMptt.objects.get(user_id=user.id)
        approve_list = org.get_all_parent_leader_list(False)
        approve_list.reverse()
        if len(approve_list) == 1:
            approve_list.insert(0, user.username)
        if len(approve_list) == 0:
            approve_list.insert(0, user.username)
            approve_list.insert(0, user.username)

        # 第一步
        # 部门分组负责人
        project_group_leader_name = approve_list[0]
        project_group_leader = User.objects.get(username=project_group_leader_name)
        # 小组长审批的state,这里对应的是流程的init_state
        project_group_leader_state = workflow_obj.init_state
        if not project_group_leader_state:
            raise WorkflowError('当前流程没有设置初始状态')
        # 创建obj, state 和user的关联
        sor = StateObjectUserRelation.objects.create(content_object=obj, state=project_group_leader_state)
        # 添加用户
        sor.users.add(project_group_leader)

        # 第二步
        # 部门的负责人
        group_leader_name = approve_list[1]
        group_leader = User.objects.get(username=group_leader_name)
        # 部门负责人审批的state，对应的是小组长审批的condition状态是同意的destination的state
        group_leader_state = project_group_leader_state.transition.get(condition='同意').destination
        # 创建三者之前的关系
        sor = StateObjectUserRelation.objects.create(content_object=obj, state=group_leader_state)
        sor.users.add(group_leader)
        """
        2018.12修改，获取审批链，关联新组织架构 end
        """


def get_specified_user_related_state(user):
    """查找出用户在state的直接关联用户下的所有state"""

    states = []

    for x in State.objects.all():
        if user in x.specified_users.all():
            states.append(x)

    return list(set(states))


def get_user_related_states(user):
    """查找出某个用户的所有的states"""
    states = []

    specified_states = get_specified_user_related_state(user)

    for x in StateObjectUserRelation.objects.all():
        if user in x.users.all():
            states.append(x.state)

    states.extend(specified_states)

    return states


def get_content_obj_and_state(user):
    """从StateObjectUserRelation的表中，
    根据user来获取匹配到的content_obj和state

    返回格式:
    [
        {'content_type': ctype, 'object_id': object_id, 'state': state},
        {'content_type': ctype, 'object_id': object_id, 'state': state},
        {'content_type': ctype, 'object_id': object_id, 'state': state}
    ]
    """

    list_content_object_state = []

    for x in StateObjectUserRelation.objects.prefetch_related('users').all():
        if user in x.users.all():
            ctype = ContentType.objects.get_for_model(x.content_object)
            object_id = x.content_object.id
            state = x.state
            list_content_object_state.append({'content_type': ctype, 'object_id': object_id, 'state': state})

    return list_content_object_state


def get_content_object_by_user_from_sor(user):
    """从StateObjectUserRelation的表中，
    根据user来获取到所有的content_object_list
    """

    list_content_object = []

    ctype = ContentType.objects.get(model='FailureDeclareWorkflow')

    for x in StateObjectUserRelation.objects.prefetch_related('users').filter(content_type=ctype):
        if user in x.users.all():
            list_content_object.append(x.content_object)

    return list_content_object


def get_workflow_state_order(workflow):
    """获取workflow state的链表

    从workflow的init_state出发，找到transition为同意的destination
    """

    init_state = workflow.init_state
    if init_state is None:
        order_state = []
    else:
        list_state = []
        list_state.append(init_state)
        order_state = get_next_state(init_state, list_state)

    return order_state


def get_next_state(state, list_state):
    """从当前的state到下一个state
    transition的condition状态为同意的
    """

    try:
        state = state.transition.get(condition='同意').destination
        list_state.append(state)
        return get_next_state(state, list_state)
    except Transition.DoesNotExist:
        return list_state


def get_next_one_state(state):
    """从当前的state到下一个state

    transition的condition状态为同意的
    只返回下一个state
    """

    try:
        next_state = state.transition.get(condition='同意').destination
        return next_state
    except Transition.DoesNotExist:
        return None


def get_state_process(wse):
    """ 根据wse获取当前的obj的审批进度

        排除掉state_value为空并且state不是完成的wse
    """

    content_obj = wse.content_object
    ctype = ContentType.objects.get_for_model(content_obj)

    process = WorkflowStateEvent.objects.filter(content_type=ctype, object_id=content_obj.id).exclude(
        state_value=None).exclude(state__name='完成').order_by('id')

    process_info = []

    for x in process:
        if x.state.name == '完成':
            info = '完成'
        else:
            info = x.state.name + ':' + x.approve_user.username + ':' + x.state_value
        process_info.append(info)

    return process_info


def get_workflow_state_approve_process(wse, send_mail=False):
    """ 获取流程的审批进度
        返回各个节点的step
        [
            {'title': '项目组长审核', 'content': 用户A/同意},
            {'title': '项目负责人审核', 'content': 用户B/审核中},
            {'title': '中心负责人审核', 'content': 用户C/审核中},
            {'title': 'CEO审核', 'content': 用户D/审核中},
            {'title': '运维审核', 'content': 用户E/审核中},
        ]
    """

    workflow = wse.state.workflow
    raw_wse = wse
    content_object = wse.content_object

    order_state = get_workflow_state_order(workflow)

    step = []
    current_index = 0

    for s in order_state:
        step_info = {}
        state_users = get_state_user(s, content_object)
        step_info['title'] = s.name
        wse = get_wse(s, content_object)

        # 如果state是完成，也就是最后一个状态，通常这个状态是没人审批的
        if s.name == '完成':
            if wse and wse.is_current:
                current_index = order_state.index(wse.state)
            if isinstance(raw_wse.content_object, SVNWorkflow):
                step_info['content'] = '查看企业邮件通知'
            else:
                step_info['content'] = ''
        else:
            # 如果wse存在，说明流程经历过该state节点
            if wse:
                # 如果审批过，展示审批用户
                if wse.state_value:
                    state_value = wse.state_value
                    if wse.is_cancel == 1:
                        state_value = '取消'
                    step_info['content'] = wse.approve_user.username + \
                                           '/' + state_value + '/' + wse.approve_time.strftime('%Y-%m-%d %H:%M')
                # 如果没有审批过，展示可以审批的用户
                else:
                    step_info['content'] = ','.join([x.username for x in state_users]) + '/审批中'

                # 从order_state中找出current_state的index
                if wse.is_current:
                    current_index = order_state.index(wse.state)
            # 如果没有，说明没有经历过
            else:
                step_info['content'] = ','.join([x.username for x in state_users])

        step.append(step_info)

    if send_mail:
        step = [x.get('content') for x in step[0:current_index + 1]]
        return '==>'.join(step)
    else:
        return (step, current_index)


def format_svn_scheme(svn_scheme_obj):
    """将svn权限方案转化为字符串
    ===============>

    <li>项目:剑雨江湖 仓库:plan 仓库内子路径: path 权限: 读</li>
    <li>项目:三生三世 仓库:test 仓库内子路径: www 权限: 读写</li>
    """

    path_perm_str = ''

    if svn_scheme_obj:
        for x in svn_scheme_obj.svnschemedetail_set.all():
            path_perm_str += '<li>项目:%s 仓库:%s 仓库内子路径:%s 权限:%s</li>' % \
                             (svn_scheme_obj.project.project_name, x.svn_repo.name,
                              x.svn_path, x.get_svn_perm_display())

    return path_perm_str


def format_svn_content(path_perm):
    """ 将svn的目录和权限的json转化为字符串

       [
        {'project_id': 'id1', 'project': project1, 'repo_id': id1, 'repo': 'repo1',  'path': 'path1', 'perm': 'perm1'},
        {'project_id': 'id2', 'project': project2, 'repo_id': id2, 'repo': 'repo2',  'path': 'path2', 'perm': 'perm2'},
      ]
        =================>
        <li>项目:剑雨江湖 仓库:plan 仓库内子路径: path 权限: 读</li>
        <li>项目:三生三世 仓库:test 仓库内子路径: www 权限: 读写</li>
    """

    path_perm_str = ''

    for x in path_perm:
        path_perm_str += '<li>项目:%s 仓库:%s 仓库内子路径:%s 权限:%s</li>' % (x['project'], x['repo'], x['path'], x['perm'])

    return path_perm_str


def format_ser_perm_ips(ip_list):
    """将ip的列表转化为字符串形式

    ['ip1', 'ip2', 'ip3']
    ======================>
    <li>ip1</li>
    <li>ip2</li>
    <li>ip3</li>
    """

    ip_str = ''

    for ip in ip_list:
        ip_str += '<li>%s</li>' % (ip['ip'])

    return ip_str


def make_content(obj, process, approve_url):
    """根据obj来构造邮件的内容"""

    if isinstance(obj, SVNWorkflow):
        template = "<html>" + \
                   "<head>" + \
                   "<meta charset='utf-8'>" + \
                   "</head>" + \
                   "<body>" + \
                   "<h3>你有一个新的svn审批，内容如下:</h3>" + \
                   "<p><b>工单创建人:</b>%s</p>" + \
                   "<p><b>申请人:</b>%s</p>" + \
                   "<p><b>申请人部门:</b>%s</p>" + \
                   "<p><b>项目:</b>%s</p>" + \
                   "<p><b>标题:</b>%s</p>" + \
                   "<p><b>原因:</b>%s</p>" + \
                   "<p><b>自定义权限:</b></p>" + \
                   "<ul>" + \
                   "%s" + \
                   "</ul>" + \
                   "<p><b>svn方案套餐:</b></p>" + \
                   "<ul>" + \
                   "%s" + \
                   "</ul>" + \
                   "<p><b>审批流程进度:</b></p>" + \
                   "%s" + \
                   "<p><b>如果你在公司，我们强烈建议你点击下面的链接进入到审批页面去审批</b></p>" + \
                   "%s" + \
                   "<p><b>如果你不在公司，直接回复本邮件'yes(表示同意)', 或者'no(表示拒绝)'来处理</b></p>" + \
                   "</body>" + \
                   "</html>"
        svn_scheme_obj = obj.svn_scheme

        # 申请人部门
        if obj.applicant.organizationmptt_set.all():
            group = obj.applicant.organizationmptt_set.all()[0].get_ancestors_except_self()
        else:
            group = ''

        content_ = template % (obj.creator.username, obj.applicant.username, group, obj.project.project_name,
                               obj.title, obj.reason, format_svn_content(json.loads(obj.content)),
                               format_svn_scheme(svn_scheme_obj), process, approve_url)

    if isinstance(obj, ServerPermissionWorkflow):
        template = "<html>" + \
                   "<head>" + \
                   "<meta charset='utf-8'>" + \
                   "</head>" + \
                   "<body>" + \
                   "<h3>你有一个新的服务器权限审批，内容如下:</h3>" + \
                   "<p><b>工单创建人:</b>%s</p>" + \
                   "<p><b>申请人:</b>%s</p>" + \
                   "<p><b>申请人部门:</b>%s</p>" + \
                   "<p><b>项目:</b>%s</p>" + \
                   "<p><b>标题:</b>%s</p>" + \
                   "<p><b>原因:</b>%s</p>" + \
                   "<p><b>key:</b>%s</p>" + \
                   "<p><b>key类型:</b>%s</p>" + \
                   "<p><b>目标IP:</b></p>" + \
                   "<ul>" + \
                   "%s" + \
                   "</ul>" + \
                   "<p><b>审批流程进度:</b></p>" + \
                   "%s" + \
                   "<p><b>如果你在公司，我们强烈建议你点击下面的链接进入到审批页面去审批</b></p>" + \
                   "%s" + \
                   "<p><b>如果你不在公司，直接回复本邮件'yes(表示同意)', 或者'no(表示拒绝)'来处理</b></p>" + \
                   "</body>" + \
                   "</html>"
        # 申请人部门
        if obj.applicant.organizationmptt_set.all():
            group = obj.applicant.organizationmptt_set.all()[0].get_ancestors_except_self()
        else:
            group = ''

        """
        if obj.all_ip:
            all_ip = '是'
        else:
            all_ip = '否'
        """

        content_ = template % (obj.creator.username, obj.applicant.username, group, obj.project.project_name,
                               obj.title, obj.reason, obj.key, 'root用户' if obj.is_root else '普通用户',
                               format_ser_perm_ips(json.loads(obj.ips)), process, approve_url)

    if isinstance(obj, ClientHotUpdate):
        template = "<html>" + \
                   "<head>" + \
                   "<meta charset='utf-8'>" + \
                   "</head>" + \
                   "<body>" + \
                   "<h3>你有一个热更新需要审批，内容如下:</h3>" + \
                   "<p><b>申请人:</b>%s</p>" + \
                   "<p><b>热更新类型:</b>前端热更新</p>" + \
                   "<p><b>标题:</b>%s</p>" + \
                   "<p><b>项目:</b>%s</p>" + \
                   "<p><b>地区:</b>%s</p>" + \
                   "<p><b>版本号:</b>%s</p>" + \
                   "<p><b>审批流程进度:</b></p>" + \
                   "%s" + \
                   "<p><b>如果你在公司，我们强烈建议你点击下面的链接进入到审批页面去审批</b></p>" + \
                   "%s" + \
                   "<p><b>如果你不在公司，直接回复本邮件'yes(表示同意)', 或者'no(表示拒绝)'来处理</b></p>" + \
                   "</body>" + \
                   "</html>"

        content_ = template % (obj.applicant.username, obj.title, obj.project.project_name,
                               obj.area_name, obj.client_version, process, approve_url)

    if isinstance(obj, ServerHotUpdate):
        template = "<html>" + \
                   "<head>" + \
                   "<meta charset='utf-8'>" + \
                   "</head>" + \
                   "<body>" + \
                   "<h3>你有一个热更新需要审批，内容如下:</h3>" + \
                   "<p><b>申请人:</b>%s</p>" + \
                   "<p><b>热更新类型:</b>后端热更新</p>" + \
                   "<p><b>标题:</b>%s</p>" + \
                   "<p><b>项目:</b>%s</p>" + \
                   "<p><b>地区:</b>%s</p>" + \
                   "<p><b>版本号:</b>%s</p>" + \
                   "<p><b>审批流程进度:</b></p>" + \
                   "%s" + \
                   "<p><b>如果你在公司，我们强烈建议你点击下面的链接进入到审批页面去审批</b></p>" + \
                   "%s" + \
                   "<p><b>如果你不在公司，直接回复本邮件'yes(表示同意)', 或者'no(表示拒绝)'来处理</b></p>" + \
                   "</body>" + \
                   "</html>"

        content_ = template % (obj.applicant.username, obj.title, obj.project.project_name,
                               obj.area_name, obj.server_version, process, approve_url)

    if isinstance(obj, ComputerParts):
        template = "<html>" + \
                   "<head>" + \
                   "<meta charset='utf-8'>" + \
                   "</head>" + \
                   "<body>" + \
                   "<h3>你有一个新的办公电脑和配件申请审批，内容如下:</h3>" + \
                   "<p><b>工单创建人:</b>%s</p>" + \
                   "<p><b>申请人:</b>%s</p>" + \
                   "<p><b>申请人部门:</b>%s</p>" + \
                   "<p><b>标题:</b>%s</p>" + \
                   "<p><b>申请理由:</b>%s</p>" + \
                   "<p><b>审批流程进度:</b></p>" + \
                   "%s" + \
                   "<p><b>如果你在公司，我们强烈建议你点击下面的链接进入到审批页面去审批</b></p>" + \
                   "%s" + \
                   "<p><b>如果你不在公司，直接回复本邮件'yes(表示同意)', 或者'no(表示拒绝)'来处理</b></p>" + \
                   "</body>" + \
                   "</html>"
        # 申请人部门
        if obj.applicant.organizationmptt_set.all():
            group = obj.applicant.organizationmptt_set.all()[0].get_ancestors_except_self()
        else:
            group = ''

        content_ = template % (obj.creator.username, obj.applicant.username, group,
                               obj.title, obj.reason, process, approve_url)

    else:
        template = "<html>" + \
                   "<head>" + \
                   "<meta charset='utf-8'>" + \
                   "</head>" + \
                   "<body>" + \
                   "<h3>你有一个新的cmdb审批，内容如下:</h3>" + \
                   "<p><b>工单创建人:</b>%s</p>" + \
                   "<p><b>申请人:</b>%s</p>" + \
                   "<p><b>申请人部门:</b>%s</p>" + \
                   "<p><b>标题:</b>%s</p>" + \
                   "<p><b>审批流程进度:</b></p>" + \
                   "%s" + \
                   "<p><b>如果你在公司，我们强烈建议你点击下面的链接进入到审批页面去审批</b></p>" + \
                   "%s" + \
                   "<p><b>如果你不在公司，直接回复本邮件'yes(表示同意)', 或者'no(表示拒绝)'来处理</b></p>" + \
                   "</body>" + \
                   "</html>"
        # 申请人部门
        if obj.applicant.organizationmptt_set.all():
            group = obj.applicant.organizationmptt_set.all()[0].get_ancestors_except_self()
        else:
            group = ''

        content_ = template % (obj.creator.username, obj.applicant.username, group,
                               obj.title, process, approve_url)

    return content_


def make_content_notify(success):
    """通知邮件的内容"""

    if success:
        url = 'http://192.168.100.66/myworkflows/approve_list/'
        title = '你有一个新的审批'
        text = '我的待审批'
    else:
        url = 'http://192.168.100.66/myworkflows/apply_history/'
        title = '你的申请被拒绝'
        text = '我的申请'

    template = "<html>" + \
               "<head>" + \
               "<meta charset='utf-8'>" + \
               "</head>" + \
               "<body>" + \
               "<h3>%s</h3>" + \
               "<p><b>点击<a href=%s>%s</a> 查看</b></p>" + \
               "<h3>该邮件仅仅是一封通知的邮件，你不能通过回复邮件来审批</h3>" + \
               "</body>" + \
               "</html>"

    content = template % (title, url, text)

    return content


def user_add_nofity(username, password):
    """添加用户完成后发送邮件通知
    告诉cmdb的账号密码和wifi的账号密码
    """

    template = "<html>" + \
               "<head>" + \
               "<meta charset='utf-8'>" + \
               "</head>" + \
               "<body>" + \
               "<h3>欢迎, %s</h3>" + \
               "<div>你的<a href=http://192.168.100.66/>CMDB</a>(只能使用谷歌或者火狐浏览器)账号%s，密码:<b>redhat</b></div>" + \
               "<div>你的公司wifi(选择Cy-Public)账号%s，密码:%s</div>" + \
               "<h3>该邮件仅仅是一封通知的邮件，你不用回复</h3>" + \
               "</body>" + \
               "</html>"

    content = template % (username, username, username, password)

    return content


def make_email(wse):
    """构建邮件的subject和content"""
    # subject
    subject = '#工单流程#%s#wse=%d' % (wse.content_object.title, wse.id)

    # process
    process = get_workflow_state_approve_process(wse, send_mail=True)

    # approve_url
    approve_url = 'http://192.168.100.66/myworkflows/approve_list/'

    # content
    content = make_content(wse.content_object, process, approve_url)

    return (subject, content)


def make_email_notify(success):
    """发送通知邮件

    如果审批通过，发送邮件到下一个节点审批人
    如果拒绝，发送邮件给工单创建人
    """

    # subject
    if success:
        subject = '你有一个新的审批'
    else:
        subject = '你的申请被拒绝'

    content = make_content_notify(success)

    return (subject, content)


def get_qq_notify():
    """发送qq弹框提醒
    返回一些常用的信息
    """

    data = {
        "window_title": "你有一个新的审批",
        "tips_title": "你有一个新的审批",
        "tips_content": "链接:请登录CMDB处理(只能使用谷歌或者火狐浏览器)",
        "tips_url": "http://192.168.100.66/myworkflows/approve_list/",
    }

    return data


def get_wx_notify():
    """发送wx弹框提醒
    返回一些常用的信息
    """

    data = "你有一个新的审批    链接:请登录<a href=\"http://192.168.100.66/myworkflows/approve_list/\">CMDB</a>处理(只能使用谷歌或者火狐浏览器)   http://192.168.100.66/myworkflows/approve_list/"

    return data


def get_version_update_notify(title=''):
    """发送qq弹框提醒
    返回版本更新需要的信息
    """

    data = {
        "window_title": "你有一个版本更新单需要执行",
        "tips_title": "你有一个版本更新单需要执行，标题: {}".format(title),
        "tips_content": "链接:请登录CMDB处理(只能使用谷歌或者火狐浏览器)",
        "tips_url": "http://192.168.100.66/myworkflows/apply_history_all/",
    }

    return data


def make_email_svn_execute():
    """发送邮件通知
    需要执行svn
    """

    subject = '你有一个SVN需要执行'

    content = "<html>" + \
              "<head>" + \
              "<meta charset='utf-8'>" + \
              "</head>" + \
              "<body>" + \
              "<h3>你有一个SVN需要执行</h3>" + \
              "<p><b>进入到申请工单汇总，找到完成-未处理点击进入执行页面</b></p>" + \
              "<h3>该邮件仅仅是一封通知的邮件，你不能通过回复邮件来审批</h3>" + \
              "</body>" + \
              "</html>"

    return (subject, content)


def format_svn(svn_workflow_obj):
    """将一个svn申请的权限转化为对接接口需要的数据

    需要从两个地方转化
    1 svn_workflow_obj 的content
    2 svn_workflow_obj 的svn_scheme

    content的格式:
    [
        {'project_id': 'id1', 'project': project1, 'project_name_cn': '剑雨江湖', 'repo_id': id1, 'repo': 'repo1',  'path': 'path1', 'perm': 'perm1'},
        {'project_id': 'id2', 'project': project2, 'project_name_cn': '剑雨江湖', 'repo_id': id2, 'repo': 'repo2',  'path': 'path2', 'perm': 'perm2'},
    ]
    """
    svn_log = SVNLog()
    content = json.loads(svn_workflow_obj.content)
    svn_scheme = svn_workflow_obj.svn_scheme

    svn_info = []

    data = {}

    for x in content:
        info = {}
        project = GameProject.objects.get(id=x['project_id']).svn_repo
        info['project'] = project
        info['project_name_cn'] = GameProject.objects.get(id=x['project_id']).project_name
        info['svnlibrary'] = x['repo']
        info['svnpath'] = x['path']

        perm = x['perm']
        if perm == '读':
            info['privilege'] = 'r'
        elif perm == '写':
            info['privilege'] = 'w'
        elif perm == '读写':
            info['privilege'] = 'rw'

        svn_info.append(info)

    if svn_scheme:
        svn_scheme_detail = SVNSchemeDetail.objects.filter(svn_scheme=svn_scheme)
        for x in svn_scheme_detail:
            info = {}
            info['project'] = x.svn_scheme.project.svn_repo
            info['project_name_cn'] = x.svn_scheme.project.project_name
            info['svnlibrary'] = x.svn_repo.name
            info['svnpath'] = x.svn_path

            perm = x.svn_perm
            if perm == 0:
                info['privilege'] = 'r'
            elif perm == 1:
                info['privilege'] = 'w'
            elif perm == 2:
                info['privilege'] = 'rw'

            """2019.1修改，若svn_scheme存在与自定义相同的仓库和子路径，以自定义的权限为准，则不再添加进svn_info"""
            if [x for x in svn_info if
                info['project'] == x['project'] and info['svnlibrary'] == x['svnlibrary'] and x['svnpath'] == info[
                    'svnpath']]:
                pass
            else:
                svn_info.append(info)
        svn_log.logger.info('%s' % (svn_info,))

    data['username'] = svn_workflow_obj.applicant.first_name
    data['action'] = 'addPrivilege'
    data['email'] = svn_workflow_obj.applicant.email

    svn_info = json.dumps(svn_info)

    data['svn_info'] = svn_info

    ticket_str = data['action'] + data['username'] + "ZkG3HHQv%n3VMoIvn"
    m = hashlib.md5()
    m.update(ticket_str.encode('utf-8'))
    ticket = m.hexdigest()

    data['ticket'] = ticket

    return data


def format_server_permission(server_permission_workflow_obj):
    """将一个服务器权限的数据添加到对接接口

    参数格式:
    [
        {
            'ip_list': ['10.1.1.1', '10.1.1.2', '10.1.1.3'],
            'username': 'yanwenchi',
            'groupname': 'phper',
            'add_time': 'ts1',
            'del_time': 'ts2'
            'authorized_key': 'key',
            'om': opsmanager_obj,
        },
        {
            'ip_list': ['192.168.1.1'],
            'username': 'yanwenchi',
            'groupname': 'phper',
            'add_time': 'ts1',
            'del_time': 'ts2'
            'authorized_key': 'key',
            'room': opsmanager_obj2,
        },
    ]

    """

    # def get_index(room, ip_info_list):
    #     for index, ip_info in enumerate(ip_info_list):
    #         if room == ip_info['room']:
    #             return index
    #     return None

    def get_om_index(om, ip_info_list):
        for index, ip_info in enumerate(ip_info_list):
            if om == ip_info['om']:
                return index
        return None

    ip_info_list = []

    # ips format: ['192.168.1.1-room1', '192.168.1.2-room2', '192.168.1.3-room2', '1.1.1.1-room34']
    # ips = [x['ip'] for x in json.loads(server_permission_workflow_obj.ips)]
    ips = [{'id': x['id'].split('_')[0], 'ip': x['ip']} for x in json.loads(server_permission_workflow_obj.ips)]

    # 通用的数据
    username = server_permission_workflow_obj.applicant.first_name
    groupname = server_permission_workflow_obj.group

    # 如果是临时的权限，时间和申请的一样
    # 如果是永久的权限，开始时间是当前的时间戳，结束时间一般设置三年后
    if server_permission_workflow_obj.temporary:
        add_time = int(server_permission_workflow_obj.start_time.timestamp())
        del_time = int(server_permission_workflow_obj.end_time.timestamp())
    else:
        add_time = int(datetime(1990, 10, 10).timestamp())
        del_time = int(datetime(2027, 10, 10).timestamp())

    temporary = server_permission_workflow_obj.temporary
    authorized_key = server_permission_workflow_obj.key

    for x in ips:
        ip = x['ip'].split('-')[0].split(':')[0]
        ip_info = {}
        host_id = x['id']
        om = Host.objects.get(pk=host_id).get_opsmanager_obj()
        if ip_info_list:
            index = get_om_index(om, ip_info_list)
            if index is not None:
                ip_info_list[index]['ip_list'].extend([ip])
            else:
                ip_info['ip_list'] = [ip]
                ip_info['username'] = username
                ip_info['groupname'] = groupname
                ip_info['add_time'] = add_time
                ip_info['del_time'] = del_time
                ip_info['temporary'] = temporary
                ip_info['authorized_key'] = authorized_key
                ip_info['om'] = om
                ip_info_list.append(ip_info)
        else:
            ip_info['ip_list'] = [ip]
            ip_info['username'] = username
            ip_info['groupname'] = groupname
            ip_info['add_time'] = add_time
            ip_info['del_time'] = del_time
            ip_info['temporary'] = temporary
            ip_info['authorized_key'] = authorized_key
            ip_info['om'] = om
            ip_info_list.append(ip_info)

        # room = x.split('-')[1]
        # ip = x.split('-')[0].split(':')[0]
        # ip_info = {}
        #
        # if ip_info_list:
        #     index = get_index(room, ip_info_list)
        #     if index is not None:
        #         ip_info_list[index]['ip_list'].extend([ip])
        #     else:
        #         ip_info['ip_list'] = [ip]
        #         ip_info['username'] = username
        #         ip_info['groupname'] = groupname
        #         ip_info['add_time'] = add_time
        #         ip_info['del_time'] = del_time
        #         ip_info['temporary'] = temporary
        #         ip_info['authorized_key'] = authorized_key
        #         ip_info['room'] = room
        #         ip_info_list.append(ip_info)
        # else:
        #     ip_info['ip_list'] = [ip]
        #     ip_info['username'] = username
        #     ip_info['groupname'] = groupname
        #     ip_info['add_time'] = add_time
        #     ip_info['del_time'] = del_time
        #     ip_info['temporary'] = temporary
        #     ip_info['authorized_key'] = authorized_key
        #     ip_info['room'] = room
        #     ip_info_list.append(ip_info)

    # 将room转化为room对象
    # for x in ip_info_list:
    #     x['room'] = Room.objects.get(room_name=x['room'])

    # 将ip_list转为化json
    for x in ip_info_list:
        x['ip_list'] = json.dumps(x['ip_list'])

    return ip_info_list


def get_ops_manager_url(project, om):
    """根据项目和机房获取运维管理机的url
    """
    DETAULT_URL = 'https://192.168.40.8/api/'
    DETAULT_TOKEN = 'e621314337f895d2b7d06cca5b4a269ab32cc943'
    # try:
    #     om = OpsManager.objects.get(project=project, room=room)
    #     return (om.url, om.token)
    # except OpsManager.DoesNotExist:
    #     return (DETAULT_URL, DETAULT_TOKEN)
    if om:
        return (om.get_url(), om.token)
    else:
        return (DETAULT_URL, DETAULT_TOKEN)


def update_serperworkflow_ips(serper_workflow_instance, data):
    """根据接口返回的数据更新服务器权限流程的ip数据

    data的数据格式:
    {
        'ip1': True,
        'ip2': False,
    }

    data有可能有None

    ips 是json格式, format:
    [
        {id: id, ip: ip1-room_name},
        {id: id, ip: ip2-room_name},
    ]
    """
    if data is not None:
        ips = json.loads(serper_workflow_instance.ips)

        for ip_info in ips:
            ip = ip_info['ip'].split('-')[0].split(':')[0]
            for data_ip, value in data.items():
                if ip == data_ip:
                    ip_info['result'] = value

        serper_workflow_instance.ips = json.dumps(ips)

        serper_workflow_instance.save()


def add_user_host_list(serper_workflow_instance):
    """添加权限到权限汇总表中
    """
    applicant = serper_workflow_instance.applicant
    user_profile = applicant.profile
    organization = OrganizationMptt.objects.get(user=applicant)
    if not user_profile:
        user_profile = Profile.objects.create(user=applicant)

    ips = json.loads(serper_workflow_instance.ips)

    # hosts = list(set([x['id'].split('_', 1)[0] for x in ips]))

    # hosts = Host.objects.filter(id__in=hosts)

    if serper_workflow_instance.is_root:
        is_root = 1
    else:
        is_root = 0

    if serper_workflow_instance.temporary:
        temporary = 1
    else:
        temporary = 0

    start_time = serper_workflow_instance.start_time
    end_time = serper_workflow_instance.end_time

    for ip_info in ips:
        host = Host.objects.get(id=ip_info['id'].split('_', 1)[0])
        if ip_info.get('result', False):
            # 如果记录存在，保存
            if not UserProfileHost.objects.filter(
                    user_profile=user_profile, host=host, start_time=start_time,
                    end_time=end_time, temporary=temporary, is_root=is_root, organization=organization
            ):
                UserProfileHost.objects.create(
                    user_profile=user_profile, host=host, start_time=start_time,
                    end_time=end_time, temporary=temporary, is_root=is_root, organization=organization)


def api_add_server_permission(wse):
    """调用管理机的api添加服务器权限
    """

    content_object = wse.content_object

    serper_log = SerPerLog()

    try:
        if isinstance(content_object, ServerPermissionWorkflow):
            ip_info_list = format_server_permission(content_object)
            status_list = []

            for ip_info in ip_info_list:
                url_prefix, token = get_ops_manager_url(content_object.project, ip_info['om'])
                ip_info.pop('om')
                if url_prefix is None or token is None:
                    # content_object.status = 1
                    # content_object.save()
                    status_list.append(1)
                    serper_log.logger.info('no pos manager found')
                    # success = True
                    # data = '添加失败'
                    continue
                url = url_prefix + USERADD
                authorized_token = "Token " + token
                headers = {
                    'Accept': 'application/json',
                    'Authorization': authorized_token,
                    'Connection': 'keep-alive',
                }

                try:
                    r = requests.post(url, headers=headers, data=ip_info, verify=False, timeout=60)
                    """返回的数据格式如下：
                    {
                        'status': 0 or 1,
                        'data': {'ip1': True, 'ip2': False}
                    }
                    """
                    serper_log.logger.info('%s: %s: %s: %s' % (content_object.title, r.text, url, ip_info))
                    result = r.json()
                    print(result)
                    # content_object.status = result['status']
                    status_list.append(result['status'])
                    update_serperworkflow_ips(content_object, result['data'])
                    # content_object.save()
                except requests.exceptions.ConnectionError:
                    # content_object.status = 1
                    status_list.append(1)
                    # content_object.save()
                    serper_log.logger.info('timeout')
                    # success = False
                    # data = '连接超时'
                    continue

            # 修改流程状态
            if 1 in status_list:
                content_object.status = 1
                data = '添加失败'
                success = False
            else:
                content_object.status = 0
                data = '添加成功'
                success = True

            content_object.save()

            add_user_host_list(content_object)

    except requests.exceptions.ConnectionError:
        content_object.status = 1
        content_object.save()
        serper_log.logger.info('timeout')
        success = False
        data = '连接超时'
    except OpsManager.DoesNotExist:
        content_object.status = 1
        content_object.save()
        serper_log.logger.info('no pos manager found')
        success = False
        data = '添加失败'
    except Room.DoesNotExist:
        content_object.status = 1
        content_object.save()
        serper_log.logger.info('no room found')
        success = False
        data = '机房名找不到'
    except Exception as e:
        content_object.status = 1
        content_object.save()
        serper_log.logger.info('%s' % (str(e)))
        success = False
        data = '添加失败'

    return (success, data)


def get_db_info(project_name, area=None):
    "从配置文件中根据项目名获取到db的连接信息"
    list_db_info = []

    if area:
        for index, db_info in enumerate(OPSMANAGER_DB):
            if project_name == db_info['project'] and area == db_info['area']:
                list_db_info.append(OPSMANAGER_DB[index])
    else:
        for index, db_info in enumerate(OPSMANAGER_DB):
            if project_name == db_info['project']:
                list_db_info.append(OPSMANAGER_DB[index])

    return list_db_info


def get_administrator(assigned_to, administrator_state, classification):
    """获取网络管理员
    如果是指定的，则就是他自身
    如果是系统指派，通过算法计算出当前任务最少的人员
    """
    if assigned_to:
        return assigned_to
    else:
        # 构造出一个初始化的用户的任务数量的字典
        user_task = {}
        for u in [User.objects.get(username=x)
                  for x in FAILURE_DECLARE_WITH_ADMIN.get(int(classification))
                  if User.objects.get(username=x).is_active]:
            user_task[u] = 0

        # ctype = ContentType.objects.get(model='FailureDeclareWorkflow')

        """获取当前正在进行的没有完成的流程
        state是运维，并且是当前状态，或者object的状态是未处理的
        """
        if administrator_state.workflow.name == 'wifi申请和网络问题申报':
            running_wse = WorkflowStateEvent.objects.filter(
                Q(state=administrator_state, is_current=True) |
                Q(wifi_workflow__status=1))
        else:
            running_wse = WorkflowStateEvent.objects.filter(
                Q(state=administrator_state, is_current=True) |
                Q(failure_declare_workflow__status=1))

        list_content_object = []

        for wse in running_wse:
            if wse.content_object not in list_content_object:
                list_content_object.append(wse.content_object)

        if administrator_state.workflow.name == 'wifi申请和网络问题申报':
            all_sor = StateObjectUserRelation.objects.filter(
                wifi_sor__in=list_content_object)
        else:
            all_sor = StateObjectUserRelation.objects.filter(
                failure_declare_sor__in=list_content_object)

        for sor in all_sor:
            users = sor.users.all()
            for u in users:
                if u in user_task:
                    user_task[u] += 1

        # 根据task数量最少的人来指派人
        return sorted(user_task, key=user_task.get)[0]


def _get_pair_hotupdate(content_object):
    """根据一个工单，获取到和他绑定的另一个工单
    然后根据先后顺序和是否已经更新成功来返回

    如果顺序为先的没有更新成功，仍然返回顺序为先的
    如果顺序为先的更新成功，返回顺序为后的

    如果是顺序为后的，总是返回顺序为先的

    如果出错，返回None
    """
    msg = ''
    another_pair_hotupdate = None

    if content_object.pair_code is None:
        if content_object.status == '4':
            msg = '不是绑定的热更新, 状态是待更新，返回自己'
            return (msg, content_object)
        else:
            msg = '工单：' + content_object.title + '，状态不是待更新，请检查是否已审批完成，若已完成审批并更新成功，请手动执行本热更新工单！'
            return (msg, None)

    pair_code = content_object.pair_code

    current_order = content_object.order
    if current_order == '先':
        opposite_order = '后'
    elif current_order == '后':
        opposite_order = '先'
    else:
        msg = '未知的顺序'
        return (msg, another_pair_hotupdate)

    if isinstance(content_object, ClientHotUpdate):
        obj = ServerHotUpdate
    elif isinstance(content_object, ServerHotUpdate):
        obj = ClientHotUpdate
    else:
        msg = '未知的content_object'
        another_pair_hotupdate = None
        return (msg, another_pair_hotupdate)

    try:
        another_pair_hotupdate = obj.objects.get(pair_code=pair_code, order=opposite_order)
        if current_order == '先':
            # 如果顺序为先的没有更新成功,仍然返回顺序为先的
            if content_object.status == '4':
                msg = '顺序为先的状态是待更新, 返回该工单'
                return (msg, content_object)
            elif content_object.status == '3':
                msg = '顺序为先的工单已经更新完成，返回顺序后的'
                return (msg, another_pair_hotupdate)
            else:
                msg = '顺序为先的状态不是待更新，返回None'
                return (msg, None)
        else:
            if another_pair_hotupdate.status == '3':
                msg = '顺序为先的工单已经更新完成，返回顺序后的'
                return (msg, another_pair_hotupdate)
            elif another_pair_hotupdate.status == '4':
                msg = '顺序为先的工单是待更新状态, 返回顺序为先的'
                return (msg, another_pair_hotupdate)
            else:
                msg = '顺序后为的工单，返回None'
                return (msg, None)
    except ServerHotUpdate.DoesNotExist:
        msg = '没有找绑定的后端热更新'
        another_pair_hotupdate = None
    except ClientHotUpdate.DoesNotExist:
        msg = '没有找绑定的前端热更新'
        another_pair_hotupdate = None
    except MultipleObjectsReturned:
        msg = '找到多个绑定的热更新'
        another_pair_hotupdate = None
    except Exception as e:
        msg = str(e)
        another_pair_hotupdate = None
    return (msg, another_pair_hotupdate)


def get_next_hot_update(project, area_name, content_object=None):
    """根据时间和优先级获取一下个执行的
    热更新工单

    ####说明####
    绑定执行的工单具有相同的优先级,修改了一个工单的优先级，另一个也会修改
    如果修改了一个工单的优先级，但是另一个没有提交
    则另一个工单提交时候优先级和绑定的相同
    ############

    查找下一个热更新工单的办法
    1 首先从前端热更新和后端热更新根据项目和地区过滤
    排除掉状态为3(也就是更新成功)或者优先级为3(也就是暂停的工单)
    2 根据我们的排序(创建时间和优先级)找出第一个工单
    如果这个工单的状态为4(待更新)，这里分两种情况
        a 如果这个工单不是前后端绑定的,则返回这个工单
        b 如果是前后端绑定的话
            b1 如果找到了绑定的更新单，则按照顺序为先的那个执行
            b2 如果没有找到, 返回None
    如果这个工单的状态不为4(待更新), 则返回None

    每次热更新审批完成后，都会出发调用此方法
    每次热更新完成后，也会出发调用此方法

    如果content_object是热更新任务完成后调用的，那么他的顺序一定为先
    则返回和他绑定的另一个没有执行工单
    """

    # 如果有content_object, 那么说明是任务完成后调用的
    if content_object:
        if content_object.pair_code is not None:
            if content_object.order == '先':
                return _get_pair_hotupdate(content_object)
        result = ''
        next_hot_update = None

        list_hot_update = []

        project = content_object.project
        area_name = content_object.area_name

        # 前端热更新根据项目地区排除掉状态为3(也就是更新成功)或者优先级为3(也就是暂停的工单)
        list_hot_client = ClientHotUpdate.objects.filter(
            project=project, area_name=area_name).exclude(Q(status=3) | Q(priority=3))
        # 后端热更新根据项目地区排除掉状态为3(也就是更新成功)或者优先级为3(也就是暂停的工单)
        list_hot_server = ServerHotUpdate.objects.filter(
            project=project, area_name=area_name).exclude(Q(status=3) | Q(priority=3))

        # 合并这两个工单
        list_hot_update.extend(list_hot_client)
        list_hot_update.extend(list_hot_server)

        # 按照排序算法找出第一个工单
        list_hot_update = sorted(list_hot_update, key=lambda obj: obj.create_time)
        list_hot_update = sorted(list_hot_update, key=lambda obj: obj.priority, reverse=True)

        if list_hot_update:
            hot_obj = list_hot_update[0]
            if hot_obj.status != '4':
                result = hot_obj.title + '状态不是待更新，请检查是否已经审批完成'
                return (result, next_hot_update)
            return _get_pair_hotupdate(hot_obj)
        else:
            result = '没有找到下一个%s, %s 要更新的工单' % (project.project_name, area_name)
            next_hot_update = None
            return (result, next_hot_update)
    # 如果没有，说明是审批完成后调用的
    else:
        result = ''
        next_hot_update = None

        list_hot_update = []

        # project = content_object.project
        # area_name = content_object.area_name

        # 前端热更新根据项目地区排除掉状态为3(也就是更新成功)或者优先级为3(也就是暂停的工单)
        list_hot_client = ClientHotUpdate.objects.filter(
            project=project, area_name=area_name).exclude(Q(status=3) | Q(priority=3))
        # 后端热更新根据项目地区排除掉状态为3(也就是更新成功)或者优先级为3(也就是暂停的工单)
        list_hot_server = ServerHotUpdate.objects.filter(
            project=project, area_name=area_name).exclude(Q(status=3) | Q(priority=3))

        # 合并这两个工单
        list_hot_update.extend(list_hot_client)
        list_hot_update.extend(list_hot_server)

        # 按照排序算法找出第一个工单
        list_hot_update = sorted(list_hot_update, key=lambda obj: obj.create_time)
        list_hot_update = sorted(list_hot_update, key=lambda obj: obj.priority, reverse=True)

        if list_hot_update:
            hot_obj = list_hot_update[0]
            return _get_pair_hotupdate(hot_obj)
        else:
            result = '没有找到下一个%s, %s 要更新的工单' % (project.project_name, area_name)
            next_hot_update = None
            return (result, next_hot_update)


def unlock_hot_update(uuid, ops):
    """热更新完成以后根据项目和地区来
    解锁，并且执行下一个热更新队列任务
    """

    hot_update_log = HotUpdateLog(uuid)

    result = False

    try:
        """找到其他相同url的运维管理机一起解锁"""
        url = ops.url
        all_ops = OpsManager.objects.filter(url__icontains=url)
        for x in all_ops:
            ops_status = x.status
            if int(ops_status) == 2:
                # 如果状态是cmdb热更新状态，解锁
                x.status = '0'
                x.save()
                result = True
            else:
                hot_update_log.logger.error('当前状态不是2，退出')
    except Exception as e:
        hot_update_log.logger.error(str(e))

    return result


def ws_notify():
    """以websocket的方式通知浏览器刷新
    """

    msg = {"message": "update_table"}
    Channel("myupdate").send(msg)


def get_hot_server_processing(hot_server):
    """获取在更新的过程中的数据
    """

    if hot_server.status in ('2', '3'):
        # 如果是更新成功或者失败
        result = hot_server.get_detail_data()
        result['message'] = 'finished'  # 表示已经更新完成
    elif hot_server.status in ('4', '0'):
        # 如果是待更新或者未处理
        result = {}
        result['status'] = hot_server.status
        result['message'] = 'ready'  # 表示还没开始
    else:
        # 如果是更新中，从redis里面获取数据
        result = get_hot_server_process_from_redis(hot_server.uuid)
        result['status'] = hot_server.status
        result['message'] = 'update'  # 表示需要更新
    return result


def ws_hot_server_notify(hot_server_id):
    """通知热更新详细刷新
    """
    hot_server = ServerHotUpdate.objects.get(id=hot_server_id)
    # process_info = get_hot_server_processing(hot_server)
    result = get_hot_server_processing(hot_server)
    result['hot_server_id'] = hot_server_id
    # msg = {"message": "update_table", "hot_server_id": hot_server_id, "process_info": process_info}
    Channel("hot_detail_update").send(result)


def hot_update_file_list_to_string(update_file_list):
    """将后端热更新的更新文件转为string
    前端页面需要使用
    """

    update_file_string = ""

    for x in update_file_list:
        file_name = x['file_name']
        fmd5 = x['file_md5']

        mystring = file_name + '    ' + fmd5 + '\n'
        update_file_string += mystring

    return update_file_string


def hot_server_update_server_list_to_string(update_server_list):
    """将要更新的区服列表转为string
    """

    update_server_string = ""

    for x in update_server_list:
        gtype = x['gtype']
        pf_name = x['pf_name']
        srv_name = x['srv_name']
        srv_id = x['srv_id']
        ip = x['ip']

        mystring = gtype + '    ' + pf_name + '    ' + srv_name + '    ' + srv_id + '    ' + ip + '\n'
        update_server_string += mystring

    return update_server_string


def hot_server_update_server_list_to_tree(update_server_list):
    """将要更新的区服列表转化为tree
    格式为:
    {
        "game": {
            "qq平台": [
                {'srv_name': '少年295区', 'ip': 'ip', 'srv_id': 'qq_1'},
                {'srv_name': '少年295区', 'ip': 'ip', 'srv_id': 'qq_2'},
            ],
            "37平台": [
                {'srv_name': '双线7服', ip': 'ip', 'srv_id': '37_1'},
                {'srv_name': '双线1服', ip': 'ip', 'srv_id': '37_2'},
            ],
        },
        "cross": {
            sougou平台": [
                {'srv_name': '跨服1服', 'ip': 'ip', 'srv_id': 'sougou_cross_1'},
                {'srv_name': '跨服12服', 'ip': 'ip', 'srv_id': 'sougou_cross_2'},
            ],
        },
        "cross_center": {
            "yy平台": [
                {'srv_name': '跨服中央1服', 'ip': 'ip', 'srv_id': 'yy_cross_center_1'},
                {'srv_name': '跨服中央12服', 'ip': 'ip' 'srv_id': 'yy_cross_center_2'},
            ],
            "4399平台": [
                {'srv_name': '跨服中央9服', 'ip': 'ip' 'srv_id': '4399_cross_center_1'},
                {'srv_name': '跨服中央13服', 'ip': 'ip' 'srv_id': '4399_cross_center_2'},
            ],
        }
    }
    """

    all_server_list = defaultdict(lambda: defaultdict(list))
    for server_list in update_server_list:
        gtype = server_list.pop('gtype')
        pf_name = server_list.pop('pf_name')
        all_server_list[gtype][pf_name].append(server_list)

    all_server_list.default_factory = None

    for x in all_server_list:
        all_server_list[x].default_factory = None

    new_data = dict(all_server_list)
    return new_data


def _pair_code_order_updatetype_available(project, area_name, pair_code, order, update_type):
    """根据项目+地区+绑定代号+先后顺序+热更类型
    来确定该代号和顺序是否有用
    """

    msg = ""
    success = True

    list_client = ClientHotUpdate.objects.filter(
        project=project, area_name=area_name, pair_code=pair_code, status__in=['0', '4'])

    list_server = ServerHotUpdate.objects.filter(
        project=project, area_name=area_name, pair_code=pair_code, status__in=['0', '4'])

    if update_type == 'hot_client':
        if list_client:
            msg = "该代号已经有其他的前端热更新使用了，换另外一个吧"
            success = False
            return (msg, success)

        # 找到后端热更新使用的顺序
        if list_server:
            hot_server = ServerHotUpdate.objects.get(
                project=project, area_name=area_name, pair_code=pair_code, status__in=['0', '4'])
            if order == hot_server.order:
                msg = '该代号顺序已经被绑定一起执行的后端热更新使用，换一个吧'
                success = False
                return (msg, success)
    elif update_type == 'hot_server':
        if list_server:
            msg = "该代号已经有其他的后端热更新使用了，换另外一个吧"
            success = False
            return (msg, success)
        if list_client:
            client_hot = ClientHotUpdate.objects.get(
                project=project, area_name=area_name, pair_code=pair_code, status__in=['0', '4'])
            if order == client_hot.order:
                msg = '该代号顺序已经被绑定一起执行的前端热更新使用，换一个吧'
                success = False
                return (msg, success)
    else:
        msg = "未知的热更新类型"
        success = False
    return (msg, success)


def gen_pull_file_path(update_type, project, area_name):
    """找到执行pull获取文件celery 任务需要的file_path参数值
    这里的area_name 为cn
    """
    PREFIX = '/data/version_update'

    if update_type == 'hot_client':
        type_path = 'client'
    elif update_type == 'hot_server':
        type_path = 'server'
    else:
        raise Exception('未知的热更新类型')

    # project_path = CMDB_PROJECT_MAP.get(project.project_name_en, None)
    # if project_path is None:
    #    raise Exception('没有找到该项目对应的版本接收机上的目录')

    project_path = project.project_name_en
    if project.project_name_en in ('mjfz',):
        return os.path.join(PREFIX, type_path)
    else:
        return os.path.join(PREFIX, type_path, project_path, area_name)


def get_workflow_process_status_dict():
    """获取所有的workflows中
    process_status的值，dict形式
    """
    workflow_id_model_dict = {
        x.id: {**x.workflow_type.model_class().status_dict(), **{100: '全部'}} for x in Workflow.objects.all()}

    return workflow_id_model_dict


def get_gamserver_project():
    """获取区服列表的项目
    """
    project_list = [x['project'] for x in GameServer.objects.values('project').annotate(count=Count('project'))]

    return GameProject.objects.filter(id__in=project_list)


def get_weixin_api_token():
    """获取微信接口token"""
    SECRET = 'nqWHzGLO5y2xasTN6Zhcd0kT9kua-NFIxgFrzxDsVd0'
    corpid = 'ww07fea2b7f6cafa5b'
    url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=' + corpid + '&corpsecret=' + SECRET
    headers = {'Accept': 'application/json'}

    try:
        res = requests.post(url, headers=headers, timeout=60, verify=False)
        if res.status_code == 200:
            r = res.json()
            if r['errcode'] == 0:
                access_token = r['access_token']
                now = datetime.now()
                expires_time = (now + timedelta(seconds=7200))
                if not WXAccessToken.objects.filter(access_token=access_token):
                    WXAccessToken.objects.create(access_token=access_token, expires_time=expires_time)
                return {'success': True, 'data': access_token, 'msg': 'ok'}
            else:
                return {'success': False, 'msg': r['errmsg']}
        else:
            return {'success': False, 'msg': str(res)}
    except Exception as e:
        return {'success': False, 'msg': str(e)}


def check_valid_wx_token():
    """检查可用微信token"""
    now = datetime.now()
    for x in WXAccessToken.objects.filter(valid=1):
        """失效所有过期token"""
        if x.expires_time < now:
            x.valid = 0
            x.save()
    wx_token = WXAccessToken.objects.filter(valid=1).order_by('-id')
    if wx_token and wx_token[0].expires_time > now:
        return wx_token[0].access_token
    else:
        return None


def ws_update_game_server_action(update_msg):
    """刷新区服操作结果
    """
    msg = {"message": update_msg, 'group_name': 'game_server_action'}
    Channel('update_game_server_action').send(msg)


def ws_update_game_server_action_record(update_msg):
    """刷新区服操作记录表
    """
    msg = {"message": update_msg, 'group_name': 'game_server_action_record'}
    Channel('update_game_server_action_record').send(msg)


def format_game_server_action_result(hostlist):
    """
    格式化区服管理操作返回结果数据
    入参数据格式如下：
    {
        '10.10.102.14': [
            {'node_name': 'cross_vng_6', 'msg': 'xxxx', 'success': True},
            {'node_name': 'vng_2', 'msg': 'xxxx', 'success': True},
        ],
        '10.10.102.13': [
            {'node_name': 'vng_1', 'msg': 'xxxx', 'success': True},
        ]
    }
    出参数据格式如下：
    [
        {'game_server': game_server_obj1, 'success': True, 'msg': msg},
        {'game_server': game_server_obj2, 'success': True, 'msg': msg},
        {'game_server': game_server_obj3, 'success': True, 'msg': msg},
    ]
    """
    result_data = []
    for ip, srv_list in hostlist.items():
        for srv in srv_list:
            srv_id = srv['node_name']
            success = srv['success']
            msg = srv['msg']
            game_server = GameServer.objects.filter(ip=ip, srv_id=srv_id)
            result_data.append({'game_server': game_server, 'success': success, 'msg': msg})
    return result_data


def get_celery_worker_status():
    """获取当前运行中的celery worker"""
    ERROR_KEY = "ERROR"
    app = celery
    app.Celery(broker=REDIS_URL)
    try:
        insp = app.task.control.inspect()
        d = insp.stats()
        if not d:
            d = {ERROR_KEY: 'No running Celery workers were found.'}
    except IOError as e:
        from errno import errorcode
        msg = "Error connecting to the backend: " + str(e)
        if len(e.args) > 0 and errorcode.get(e.args[0]) == 'ECONNREFUSED':
            msg += ' Check that the Redis server is running.'
        d = {ERROR_KEY: msg}
    except ImportError as e:
        d = {ERROR_KEY: str(e)}
    return d


def not_empty(s):
    return s and s.strip()


def format_hot_update_file_list(update_file_list, del_key):
    """格式化热更新update_file_list字段，去掉不需要的参数"""
    result_list = []
    for file in update_file_list:
        del file[del_key]
        result_list.append(file)
    return result_list


def get_the_same_url_of_ops_task(obj, ops, update_type):
    """找出热更新任务的子任务中，是否存在相同url的运维管理机，有则返回对应的子任务，否则返回None"""
    url = ops.url
    if update_type == 'hot_client':
        for task in obj.clienthotupdatersynctask_set.all():
            if task.ops.url == url:
                return task
    elif update_type == 'hot_server':
        for task in obj.serverhotupdatersynctask_set.all():
            if task.ops.url == url:
                return task
    else:
        return None


def ws_update_host_compression_list():
    """刷新机器回收列表"""
    msg = {"message": 'update_table'}
    Channel('update_host_compression_list').send(msg)


def ws_update_host_compression_log(id):
    """刷新机器回收日志"""
    apply_obj = HostCompressionApply.objects.get(pk=id)
    log = apply_obj.hostcompressionlog.log
    msg = {"message": 'update_log', 'host_compression_id': id, 'log': log}
    Channel('update_host_compression_log').send(msg)


def ws_update_host_compression_detail(id):
    """更新机器回收详情"""
    msg = {'message': 'update_detail', 'obj_id': id, }
    Channel('update_host_compression_detail').send(msg)


def write_host_compression_log(level, content, obj):
    """更新机器回收任务日志字段内容"""
    try:
        with transaction.atomic():
            log_obj = obj.hostcompressionlog
            now = str(datetime.now())[:23]
            complete_log = now + ' - ' + obj.uuid + ' - ' + level + ' - ' + content + '\n'
            log_obj.log += complete_log
            log_obj.save()
            """刷新机器回收日志"""
            ws_update_host_compression_log(obj.id)
    except:
        pass


def isPowerOfTwo(n):
    """
    判断n是否2的幂次放
    """
    if n == 0:
        return False
    elif (n & (n - 1) == 0):
        return True
    else:
        return False


def _delete_workflow_state(state):
    """
    指定删除流程某个状态
    这里的删除不删除state记录因为考虑到以前的工单可能关联到该状态，所以这里只删除对应的transition和state与transition之间的关系
    1.如果是中间状态，则更改前一状态及后一状态的指针
    2.如果是最后状态，则删除前一状态的指针
    3.如果是第一个状态，同时修改流程的初始状态为后一状态，后一状态的拒绝指针指向自己
    4.如果唯一状态，则清除流程的初始状态
    """
    try:
        workflow = state.workflow
        pre_state = state.get_pre_state()
        latter_state = state.get_latter_state()
        if pre_state and latter_state:
            if pre_state == state:
                pre_transition = pre_state.transition.filter(condition='拒绝')
                if pre_transition:
                    pre_transition.delete()
                workflow.init_state = latter_state
                workflow.save(update_fields=['init_state'])
                latter_state_reject_transition = latter_state.transition.filter(condition='拒绝')
                if latter_state_reject_transition:
                    latter_state_reject_transition.update(**{'destination': latter_state})
            else:
                pre_transition = pre_state.transition.filter(condition='同意')
                if pre_transition:
                    pre_transition = pre_transition[0]
                    pre_transition.destination = latter_state
                    pre_transition.save(update_fields=['destination'])
                latter_transition = latter_state.transition.filter(condition='拒绝')
                if latter_transition:
                    latter_transition.update(**{'destination': pre_state})
        if pre_state and not latter_state:
            if pre_state == state:
                workflow.init_state = None
                workflow.save(update_fields=['init_state'])
                pre_transition = pre_state.transition.filter(condition='拒绝')
                if pre_transition:
                    pre_transition.delete()
            else:
                pre_transition = pre_state.transition.filter(condition='同意')
                if pre_transition:
                    pre_transition.delete()
        if not pre_state and latter_state:
            latter_transition = latter_state.transition.filter(condition='拒绝')
            if latter_transition:
                latter_transition.delete()
            workflow.init_state = latter_state
            workflow.save(update_fields=['init_state'])
        if not (pre_state or latter_state):
            workflow.init_state = None
            workflow.save(update_fields=['init_state'])

        """删除残留的审批链指针"""
        try:
            state.transition.all().delete()
        except:
            pass
        """检查是否还存在审批链，若不存在，则设置流程初始化状态为None"""
        if not Transition.objects.filter(workflow=workflow):
            workflow.init_state = None
            workflow.save(update_fields=['init_state'])
    except Exception as e:
        raise Exception(str(e))


def _add_workflow_state(workflow, state_name):
    """添加流程状态"""
    try:
        state = State.objects.filter(workflow=workflow, name=state_name)
        if state:
            new_state = state[0]
            """删除新添加状态后面旧的审批连"""
            new_state.transition.filter(condition='同意').delete()
        else:
            new_state = State.objects.create(workflow=workflow, name=state_name)
        """如果是第一个状态，则初始化init_state"""
        if State.objects.filter(workflow=workflow).count() == 1 or workflow.init_state is None:
            workflow.init_state = new_state
            workflow.save(update_fields=['init_state'])
            """初始状态的拒绝指针指向自己"""
            reject_transition = Transition.objects.filter(name=workflow.init_state.name + '拒绝', workflow=workflow,
                                                          condition='拒绝')
            if reject_transition:
                reject_transition = reject_transition[0]
                reject_transition.destination = workflow.init_state
                reject_transition.save(update_fields=['destination'])
            else:
                reject_transition = Transition.objects.create(name=new_state.name + '拒绝', workflow=workflow,
                                                              destination=workflow.init_state, condition='拒绝')
                workflow.init_state.transition.add(reject_transition)
        else:
            pre_state = get_workflow_state_order(workflow)[-1]
            reject_transition = Transition.objects.filter(name=new_state.name + '拒绝', workflow=workflow,
                                                          condition='拒绝')
            if reject_transition:
                reject_transition = reject_transition[0]
                reject_transition.destination = pre_state
                reject_transition.save(update_fields=['destination'])
            else:
                reject_transition = Transition.objects.create(name=new_state.name + '拒绝', workflow=workflow,
                                                              destination=pre_state, condition='拒绝')
                new_state.transition.add(reject_transition)

            agree_transition = Transition.objects.filter(name=pre_state.name + '同意', workflow=workflow,
                                                         destination=new_state, condition='同意')
            if agree_transition:
                agree_transition = agree_transition[0]
                agree_transition.destination = new_state
                agree_transition.save(update_fields=['destination'])
            else:
                agree_transition = Transition.objects.create(name=pre_state.name + '同意', workflow=workflow,
                                                             destination=new_state, condition='同意')
                pre_state.transition.add(agree_transition)
    except Exception as e:
        raise Exception(str(e))


def new_set_state_obj_user(obj, workflow_obj, user, project=None, assigned_to=None, **kwargs):
    """新版-设置工单流程审批连中涉及的用户"""
    if project is not None:
        project_id = project.id
    else:
        project_id = ''
    success, msg, approve_user_list, approve_chain_dict = get_approve_user_chain(workflow=workflow_obj,
                                                                                 applicant_id=user.id,
                                                                                 project_id=project_id, **kwargs)
    for state_obj, username in approve_chain_dict.items():
        if username is not None:
            username = username.split(',')
            user_objs = User.objects.filter(username__in=username)
        else:
            user_objs = [user]
        # 创建obj, state 和user的关联
        sor = StateObjectUserRelation.objects.create(content_object=obj, state=state_obj)
        # 添加用户
        if '运维负责人' in state_obj.name:
            for user_obj in user_objs:
                sor.users.add(user_obj)
        elif '运维' in state_obj.name and assigned_to is not None:
            sor.users.add(assigned_to)
        else:
            for user_obj in user_objs:
                sor.users.add(user_obj)
            # 添加额外审批人员
            if state_obj.specified_users.all() and '创畅' not in user.organizationmptt_set.first().get_ancestors_name():
                for extra_user in state_obj.specified_users.all():
                    sor.users.add(extra_user)


def get_user_workflow_apply(user):
    """找出用户在cmdb创建或者申请人为自己，且未完成审批的所有工单流程id列表"""
    creator_wse_list = WorkflowStateEvent.objects.filter(is_cancel=0, is_current=1, state_value=None,
                                                         creator__username=user.username).exclude(state__name='完成')
    applicant_wse_list = [x for x in
                          WorkflowStateEvent.objects.filter(is_cancel=0, is_current=1, state_value=None).exclude(
                              state__name='完成') if x.content_object.applicant == user]
    wse_chain = chain(creator_wse_list, applicant_wse_list)
    wse_list = list(set(wse_chain))
    return wse_list


def cancel_workflow_apply(wse_id):
    """
    取消状态审批中的工单: 1.模拟拒绝工单 2.将工单的取消状态设置为True
    """
    try:
        success = True
        msg = 'ok'
        """找出当前工单节点的拒绝指针"""
        wse = WorkflowStateEvent.objects.get(pk=wse_id)
        if wse.is_cancel == 0 and wse.is_current == 1 and wse.state.name != '完成':
            if wse.state.transition.filter(condition='拒绝'):
                transition_id = wse.state.transition.filter(condition='拒绝')[0].id
                transition = Transition.objects.get(id=transition_id)
                """拒绝工单流程"""
                msg, success, new_wse = do_transition(wse, transition, wse.creator)
                if success:
                    """设置工单取消状态为True"""
                    new_wse.is_cancel = 1
                    new_wse.save()
                else:
                    raise Exception(msg)
            else:
                raise Exception('没有找到 %s 对应的transition流程' % wse.state)

    except Exception as e:
        success = False
        msg = str(e)
    finally:
        return success, msg


def format_svn_scheme_by_wx_task(svn_scheme_obj):
    """将svn权限方案转化为字符串
    ===============>

    项目:剑雨江湖 仓库:plan 仓库内子路径: path 权限: 读<br>
    项目:三生三世 仓库:test 仓库内子路径: www 权限: 读写<br>
    """

    path_perm_str = ''

    if svn_scheme_obj:
        for x in svn_scheme_obj.svnschemedetail_set.all():
            path_perm_str += '    仓库:%s 仓库内子路径:%s 权限:%s<br>' % \
                             (x.svn_repo.name, x.svn_path, x.get_svn_perm_display())

    return path_perm_str


def format_svn_content_by_wx_task(path_perm):
    """ 将svn的目录和权限的json转化为字符串

       [
        {'project_id': 'id1', 'project': project1, 'repo_id': id1, 'repo': 'repo1',  'path': 'path1', 'perm': 'perm1'},
        {'project_id': 'id2', 'project': project2, 'repo_id': id2, 'repo': 'repo2',  'path': 'path2', 'perm': 'perm2'},
      ]
        =================>
        仓库:plan 仓库内子路径: path 权限: 读<br>
        仓库:test 仓库内子路径: www 权限: 读写<br>
    """

    path_perm_str = ''

    for x in path_perm:
        path_perm_str += '    仓库:%s 仓库内子路径:%s 权限:%s<br>' % (x['repo'], x['path'], x['perm'])

    return path_perm_str


def format_svn_info_by_wx_task(obj):
    """
    将svn权限方案和自定义方案转化为字符串，如果两种方案存在冲突，已自定义方案为准
    ===============>

    项目:剑雨江湖 仓库:plan 仓库内子路径: path 权限: 读<br>
    项目:三生三世 仓库:test 仓库内子路径: www 权限: 读写<br>
    """
    data = format_svn(obj)
    svn_info = json.loads(data['svn_info'])
    svn_str = ''
    for x in svn_info:
        privilege = x['privilege']
        if privilege == 'r':
            privilege = '读'
        if privilege == 'w':
            privilege = '写'
        if privilege == 'rw':
            privilege = '读写'
        svn_str += '    仓库:{}  路径:{}  权限:{}<br>'.format(x['svnlibrary'], x['svnpath'], privilege)

    return svn_str


def format_ser_perm_ips_by_wx_task(ip_list):
    """将ip的列表转化为字符串形式

    ['ip1', 'ip2', 'ip3']
    ======================>
    ip1<br>
    ip2<br>
    ip3<br>
    """

    ip_str = ''

    for ip in ip_list:
        ip_str += '    %s<br>' % (ip['ip'])

    return ip_str


def format_machine_config_by_wx_task(config):
    """
    服务器申请配置格式化
    输入：
    [
        {
            "config_cpu_value": "4",
            "config_number": "1",
            "config_disk_value": "1024",
            "config_mem_value": "8"
        },
        {
            "config_cpu_value": "8",
            "config_number": "2",
            "config_disk_value": "2048",
            "config_mem_value": "16"
        }，
    ]
    输出：
        CPU：4核  内存：8G  硬盘：1024G  数量：1台<br>
        CPU：8核  内存：16G  硬盘：2048G  数量：2台<br>
    """
    config_str = ''
    for c in config:
        config_str += '    CPU：{}核  内存：{}G  硬盘：{}G  数量：{}台<br>'.format(c['config_cpu_value'], c['config_mem_value'],
                                                                       c['config_disk_value'], c['config_number'])

    return config_str


def format_delete_svn_or_ser_project_by_wx_task(project):
    """
    格式化需要删除的svn项目
    输入：['27', '24', '16']
    输出：
    剑雨江湖，三生三世，神灵契约3d
    """
    project_list = []
    for x in project:
        project = GameProject.objects.get(pk=x)
        project_list.append(project.project_name)

    return '，'.join(project_list)


def format_mysql_instance_by_wx_task(content):
    """
    格式化申请的mywql数据库信息
    输入
    [{"permission": "select", "instance": "129.204.180.165:3306", "passwd": "xxxxx", "dbs": ["gms_data_22", "log_api_22", "recharge_22", "web_gms_api_22"]}]
    输出：
        实例：129.204.180.165:3306  库名："gms_data_22, log_api_22, recharge_22, web_gms_api_22"  权限：select<br>
    """
    instance_str = ''
    for c in content:
        instance_str += '    实例：{}  库：{}  权限：{}<br>'.format(c['instance'], ','.join(c['dbs']), c['permission'])

    return instance_str


def get_wx_task_card_data(touser, wse, handle=None, purchase=None, change_approve=None):
    """生成微信任务卡消息内容"""
    success = True
    msg = 'ok'
    data = {}
    if not PRODUCTION_ENV:
        touser = 'chenjiefeng'
    try:
        obj = wse.content_object
        prefix = obj._meta.label_lower.split('.')[1]
        task_id = prefix + '-' + str(wse.id)
        applicant = obj.applicant.username
        department = obj.applicant.organizationmptt_set.first().get_ancestors_except_self()
        title = obj.title
        yl_network_admin = SpecialUserParamConfig.objects.get(
            param='YL_NETWORK_ADMINISTRATOR').get_user_first_name_list()
        cc_network_admin = SpecialUserParamConfig.objects.get(
            param='CC_NETWORK_ADMINISTRATOR').get_user_first_name_list()
        admin = yl_network_admin + cc_network_admin
        remark = '<div class=\"highlight\">备注：只提供审批功能，若问题已处理，请在下一个任务卡片中选择已处理！</div>'
        description = ''
        try:
            workflow_type = '-' + obj.workflows.first().content_type.workflow_set.first().name
        except:
            workflow_type = ''
        if isinstance(obj, SVNWorkflow):
            svn_project = obj.project.project_name
            reason = obj.reason
            svn_info = format_svn_info_by_wx_task(obj)
            description = '申请人：{}<br>部门：{}<br>项目：{}<br>方案：<br>{}<br>原因：{}'.format(
                applicant, department, svn_project, svn_info, reason)
        if isinstance(obj, ServerPermissionWorkflow):
            project = obj.project.project_name
            reason = obj.reason
            is_root = '是' if obj.is_root else '否'
            temporary = '是' if obj.temporary else '否'
            group = obj.group
            start_end_time = str(obj.start_time) + ' 至 ' + str(obj.end_time) + '<br>' if obj.temporary else ''
            ips = format_ser_perm_ips_by_wx_task(json.loads(obj.ips))
            description = '申请人：{}<br>部门：{}<br>项目：{}<br>root权限：{}<br>分组：{}<br>临时：{}<br>{}主机：<br>{}<br>原因：{}'.format(
                applicant, department, project, is_root, group, temporary, start_end_time, ips, reason)
        if isinstance(obj, FailureDeclareWorkflow):
            classification = obj.class_dict()[int(obj.classification)]
            content = obj.content
            if handle:
                remark = ''
            description = '申请人：{}<br>部门：{}<br>标题：{}<br>分类：{}<br>描述：{}<br>{}'.format(
                applicant, department, title, classification, content, remark)
        if isinstance(obj, Wifi):
            ip_or_mac = obj.mac
            reason = obj.reason
            wifi_name = 'wifi名称：' + obj.name + '<br>' if obj.name != 'Null' else ''
            description = '申请人：{}<br>部门：{}<br>IP或MAC地址：{}<br>{}<br>理由：{}'.format(
                applicant, department, ip_or_mac, wifi_name, reason)
            if touser in admin and not handle:
                description += remark
        if isinstance(obj, ComputerParts):
            reason = obj.reason
            description = '申请人：{}<br>部门：{}<br>标题：{}<br>理由：{}<br>'.format(
                applicant, department, title, reason)
            if touser in admin and not handle:
                description += remark
        if isinstance(obj, VersionUpdate):
            content = obj.content
            project = obj.project.project_name
            server_list = obj.server_list
            start_end_time = str(obj.start_time) + ' 至 ' + str(obj.end_time)
            server_version = obj.server_version
            server_attention = obj.server_attention
            client_version = obj.client_version
            client_attention = obj.client_attention
            description = '申请人：{}<br>部门：{}<br>标题：{}<br>项目：{}<br>更新区服：{}<br>起止时间：{}<br>后端版本号：{}<br>后端注意事项：{}<br>前端版本号：{}<br>前端注意事项：{}<br>更新内容：{}'.format(
                applicant, department, title, project, server_list, start_end_time, server_version, server_attention,
                client_version, client_attention, content)
        if isinstance(obj, ClientHotUpdate):
            hot_update_type = '前端'
            project = obj.project.project_name
            area = obj.get_area_name()
            client_version = obj.get_client_version()
            reason = obj.reason
            description = '申请人：{}<br>部门：{}<br>标题：{}<br>类型：{}<br>项目：{}<br>地区：{}<br>版本号：{}<br>原因：{}'.format(
                applicant, department, title, hot_update_type, project, area, client_version, reason)
        if isinstance(obj, ServerHotUpdate):
            hot_update_type = '后端'
            project = obj.project.project_name
            area = obj.get_area_name()
            server_version = obj.server_version
            reason = obj.reason
            description = '申请人：{}<br>部门：{}<br>标题：{}<br>类型：{}<br>项目：{}<br>地区：{}<br>版本号：{}<br>原因：{}'.format(
                applicant, department, title, hot_update_type, project, area, server_version, reason)
        if isinstance(obj, Machine):
            project = obj.project.project_name
            purpose = obj.purpose
            ip_type = obj.get_ip_type_display()
            config = format_machine_config_by_wx_task(json.loads(obj.config))
            requirements = obj.requirements
            description = '申请人：{}<br>部门：{}<br>标题：{}<br>项目：{}<br>内/外网：{}<br>配置：<br>{}<br>用途：{}<br>其他：{}'.format(
                applicant, department, title, project, ip_type, config, purpose, requirements)
        if isinstance(obj, ProjectAdjust):
            new_department = obj.new_department_group.get_ancestors_except_self()
            delete_svn_perm = format_delete_svn_or_ser_project_by_wx_task(
                json.loads(obj.svn_projects)) if obj.delete_svn and obj.svn_projects else '无'
            delete_ser_perm = format_delete_svn_or_ser_project_by_wx_task(
                json.loads(obj.serper_projects)) if obj.delete_svn and obj.serper_projects else '无'
            description = '申请人：{}<br>原部门：{}<br>标题：{}<br>新部门：{}<br>删除svn权限：{}<br>删除服务器权限：{}'.format(
                applicant, department, title, new_department, delete_svn_perm, delete_ser_perm)
        if isinstance(obj, MysqlWorkflow):
            reason = obj.reason
            content = format_mysql_instance_by_wx_task(json.loads(obj.content))
            description = '申请人：{}<br>部门：{}<br>数据库：<br>{}<br>原因：{}'.format(
                applicant, department, content, reason)

        if handle:
            data = {
                "touser": touser,
                "msgtype": "taskcard",
                "agentid": 1000004,
                "taskcard": {
                    "title": "CMDB工单是否已处理" + workflow_type,
                    "description": description,
                    "task_id": task_id + '-handle',
                    "btn": [
                        {
                            "key": "is_handle",
                            "name": "已处理",
                            "replace_name": "已处理",
                            "is_bold": True
                        },
                    ]
                }
            }
        elif purchase:
            data = {
                "touser": touser,
                "msgtype": "taskcard",
                "agentid": 1000004,
                "taskcard": {
                    "title": "CMDB服务器申请是否已购买",
                    "description": description,
                    "task_id": task_id + '-purchase',
                    "btn": [
                        {
                            "key": "is_purchase",
                            "name": "已购买",
                            "replace_name": "已购买",
                            "is_bold": True
                        },
                    ]
                }
            }
        else:
            if change_approve:
                task_id += '-change-approve'
            data = {
                "touser": touser,
                "msgtype": "taskcard",
                "agentid": 1000004,
                "taskcard": {
                    "title": "CMDB工单审批" + workflow_type,
                    "description": description,
                    "task_id": task_id,
                    "btn": [
                        {
                            "key": "yes",
                            "name": "同意",
                            "replace_name": "已同意",
                            "is_bold": True
                        },
                        {
                            "key": "no",
                            "name": "拒绝",
                            "replace_name": "已拒绝",
                            "color": "red",
                        }
                    ]
                }
            }

    except Exception as e:
        msg = '获取任务卡片data内容失败：' + str(e)
        success = False
    finally:
        return {'success': success, 'msg': msg, 'data': data}


def update_wx_taskcard_status(touser, wse, handle=None, purchase=None):
    """更新微信任务卡片按钮状态为已选择"""
    log = SendWxTaskCardLog()
    try:
        if not PRODUCTION_ENV:
            touser = ['chenjiefeng']
        obj = wse.content_object
        prefix = obj._meta.label_lower.split('.')[1]
        task_id = prefix + '-' + str(wse.id)
        if wse.state_value == '同意':
            clicked_key = 'yes'
        elif wse.state_value == '拒绝':
            clicked_key = 'no'
        else:
            if not (handle or purchase):
                raise Exception('流程还没有审批，wse id：{}'.format(wse.id))
        if handle:
            task_id += '-handle'
            clicked_key = 'is_handle'
        if purchase:
            task_id += '-purchase'
            clicked_key = 'is_purchase'

        """获取微信接口token"""
        token = check_valid_wx_token()
        if token is None:
            result = get_weixin_api_token()
            if result['success']:
                token = result['data']
            else:
                msg = result['msg']
                raise Exception(msg)

        data = {
            "userids": touser,
            "agentid": 1000004,
            "task_id": task_id,
            "clicked_key": clicked_key
        }
        url = 'https://qyapi.weixin.qq.com/cgi-bin/message/update_taskcard?access_token=' + token
        headers = {'Accept': 'application/json'}

        res = requests.post(url, json=data, headers=headers, timeout=60, verify=False)
        if res.status_code == 200:
            r = res.json()
            log.logger.info(r)
            if r['errcode'] == 0:
                msg = '{}: 更新企业微信任务卡片成功，wse id：{}'.format(touser, wse.id)
                log.logger.info(msg)
                if r.get('invaliduser', None):
                    log.logger.error('更新企业微信任务卡片失败的用户：' + str(r.get('invaliduser')))
            elif r['errcode'] == 40014:
                wx_token = WXAccessToken.objects.filter(access_token=token)
                wx_token.update(valid=0)
                get_weixin_api_token()
                update_wx_taskcard_status(touser, wse)
            else:
                msg = r['errmsg']
                raise Exception(msg)
        else:
            msg = str(res)
            raise Exception(msg)
    except Exception as e:
        msg = '{}: 更新企业微信任务卡片按钮状态失败 wse id {}，原因：{}'.format(touser, wse.id, str(e))
        log.logger.error(msg)


def format_game_server_action_data(game_server):
    """格式化区服管理操作请求数据"""
    ops_game_server = {}
    for g in game_server:
        ops = g.get_ops_manager()
        if ops:
            if ops not in ops_game_server.keys():
                ops_game_server[ops] = [g.srv_id]
            else:
                game_server_id_list = ops_game_server[ops]
                game_server_id_list.append(g.srv_id)
                ops_game_server[ops] = game_server_id_list
    return ops_game_server


def get_celery_worker_relate_tasks():
    """获取celery worker关联的tasks函数"""
    app = celery
    app.Celery(broker=REDIS_URL)
    try:
        insp = app.task.control.inspect()
        queues = insp.active_queues()
        data = dict()
        for key, values in queues.items():
            tasks = [v.get('name', None) for v in values]
            tasks = list(filter(None, tasks))
            data[key] = tasks

        return data
    except Exception as e:
        return {}


def wechat_account_check(touser):
    """
    根据touser参数查找cmdb与企业微信帐号转换关系表
    如果能找到，则相应帐号需要做转换
    """
    try:
        if isinstance(touser, list):
            for first_name in touser:
                user = User.objects.get(first_name=first_name)
                transfer = WechatAccountTransfer.objects.filter(cmdb_account=user)
                if transfer:
                    touser[touser.index(first_name)] = transfer[0].wechat_account
            return touser
        elif isinstance(touser, str):
            touser_list = touser.split('|')
            for first_name in touser_list:
                user = User.objects.get(first_name=first_name)
                transfer = WechatAccountTransfer.objects.filter(cmdb_account=user)
                if transfer:
                    touser = touser.replace(first_name, transfer[0].wechat_account)
            return touser
        else:
            return touser
    except Exception as e:
        return touser


def version_update_check_push_dir_util(version_update_type, version, project, area):
    """
    版本更新单-根据前后段版本号检查推送目录是否存在
    参数：
        version_update_type: client或server  # 前端或后端
        version: 版本号
        project: 项目
        area: 地区
    返回：
        {'success': success, 'msg': msg}
    """
    success = True
    msg = 'ok'
    try:
        ops = OpsManager.objects.filter(room__area=area, project=project)
        if not ops:
            raise Exception('找不到运维管理机')
        ops = ops[0]
        url = ops.get_url() + 'update/check_version/'
        token = ops.token
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Token {}'.format(token)
        }
        post_data = {
            'type': version_update_type,
            'version': version,
        }
        s = Session()
        s.mount('https://', HTTPAdapter(max_retries=Retry(total=5, status_forcelist=[408])))
        r = s.post(url, headers=headers, json=json.dumps(post_data), timeout=30, verify=False)
        if r.status_code != 200:
            raise Exception(str(r))
        res = r.json()
        if not res['Accepted']:
            if version_update_type == 'server':
                msg = '推送目录不存在，请检查后端版本号 {}'.format(version)
            if version_update_type == 'client':
                msg = '推送目录不存在，请检查前端版本号 {}'.format(version)
            raise Exception(msg)
    except Exception as e:
        success = False
        msg = str(e)
    finally:
        return success, msg
