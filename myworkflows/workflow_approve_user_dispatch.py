from functools import update_wrapper

from collections import UserDict

# from django.contrib.contenttypes.models import ContentType

from myworkflows.exceptions import UserNotInGroup
from myworkflows.exceptions import GroupExtentionError
from myworkflows.exceptions import WorkflowStateUserRelationError

from myworkflows.utils import is_group_leader
from myworkflows.utils import is_orgnization_group_leader, is_organization_leader
from myworkflows.utils import is_group_section_leader

from assets.models import GameProject
from django.contrib.auth.models import User
from users.models import OrganizationMptt


def dedupe(items):
    """去除一个list中重复的
    值，并且保持原来的顺序
    """
    seen = set()
    for item in items:
        if item not in seen:
            yield item
            seen.add(item)


class MappingProxyType(UserDict):
    def __init__(self, data):
        UserDict.__init__(self)
        self.data = data


def workflow_approve_user_dispatch(func):
    registry = {}

    def dispatch(value):
        return registry.get(value, func)

    def register(value, func=None):
        if func is None:
            return lambda f: register(value, f)

        registry[value] = func
        return func

    def wrapper(*args, **kwargs):
        return dispatch(args[0])(*args, **kwargs)

    wrapper.register = register
    wrapper.dispatch = dispatch
    wrapper.registry = MappingProxyType(registry)
    update_wrapper(wrapper, func)
    return wrapper


@workflow_approve_user_dispatch
def workflow_approve_user(workflow, *args, **kwargs):
    success = False
    data = '没有注册该流程的审批用户预览'
    return (data, success)


@workflow_approve_user.register('svnworkflow')
def svn_workflow_approve_user(workflow_class_name, *args, **kwargs):
    # 获取workflow流程对象
    try:
        project_id = kwargs.get('project_id')
        applicant_id = kwargs.get('applicant_id')

        project = GameProject.objects.get(id=project_id)
        applicant = User.objects.get(id=applicant_id)
        org = OrganizationMptt.objects.get(user_id=applicant_id)

        """
        2018.12修改，获取审批链，关联新组织架构，同时计算出第一步，第二步，即部门组长和部门负责人
        """
        if not org.parent or org.parent_id == 1:
            raise Exception('用户%s没有分配到部门' % (applicant.username))

        approve_user_list = org.get_all_parent_leader_list(project.is_game_project)
        approve_user_list.reverse()
        approve_user_list = approve_user_list[:2]

        # 第三步
        # 项目负责人
        project_leader = project.leader
        if not project_leader:
            raise WorkflowStateUserRelationError('项目负责人不存在')
        if applicant.id != project_leader.id:
            # approve_user_list.append(project_leader)
            approve_user_list.append(project_leader.username)

        success = True

        pre_msg = '审批人员链: '
        # approve_user_chain = '==>'.join([x.username for x in list(dedupe(approve_user_list))])
        approve_user_chain = '==>'.join([x for x in list(dedupe(approve_user_list))])
        pre_msg += approve_user_chain
        msg = pre_msg + ' <strong>审批人员有错误?可能申请人所在的部门不对!请联系运维处理</strong>'

    except GroupExtentionError as e:
        msg = str(e)
        success = False
    except User.DoesNotExist:
        msg = '用户没有找到'
        success = False
    except GameProject.DoesNotExist:
        msg = '没有项目没有'
        success = False
    except WorkflowStateUserRelationError as e:
        msg = str(e)
        success = False
    except UserNotInGroup as e:
        msg = str(e)
        success = False
    except Exception as e:
        msg = str(e)
        success = False
    return (success, msg)


@workflow_approve_user.register('serverpermissionworkflow')
def serverpermission_workflow_approve_user(workflow_class_name, *args, **kwargs):
    try:
        username = kwargs.get('username')
        applicant = User.objects.get(username=username)
        org = OrganizationMptt.objects.get(user_id=applicant.id)

        # 第一步
        # 部门组长审批人
        # 如果有部门组长，是部门管理分组的组长
        # 如果没有部门组长，则直接通过
        # 第二步
        # 部门负责人

        """
        2018.12修改，获取审批链，关联新组织架构，合并第一步，第二步
        """
        if not org.parent or org.parent_id == 1:
            raise Exception('用户%s没有分配到部门' % (applicant.username))

        approve_user_list = org.get_all_parent_leader_list(True)
        approve_user_list.reverse()
        approve_user_list = approve_user_list[:2]

        success = True

        pre_msg = '审批人员链: '
        # approve_user_chain = '==>'.join([x.username for x in list(dedupe(approve_user_list))])
        approve_user_chain = '==>'.join([x for x in list(dedupe(approve_user_list))])
        pre_msg += approve_user_chain
        msg = pre_msg + ' <strong>审批人员有错误?可能申请人所在的部门不对!请联系运维处理</strong>'

    except GameProject.DoesNotExist:
        msg = '项目不存在'
        success = False
    except User.DoesNotExist:
        msg = '用户没有找到'
        success = False
    except Exception as e:
        msg = str(e)
        success = False
    return (success, msg)


@workflow_approve_user.register('wifi')
def wifi_workflow_approve_user(workflow_class_name, *args, **kwargs):
    try:
        applicant_id = kwargs.get('applicant_id')
        applicant = User.objects.get(id=applicant_id)

        """2018.12修改，关联新组织架构表，部门的负责人"""
        org = OrganizationMptt.objects.filter(user=applicant)
        if not org:
            raise Exception('用户没有在新组织架构中')
        else:
            org = org[0]
            if not org.parent:
                raise UserNotInGroup('用户没有在部门里面')
            else:
                if org.parent.leader == 0 and org.parent.parent.leader == 0:
                    raise GroupExtentionError("申请人所在的部门没有设置负责人")
        department_leader = org.get_department_obj().get_leader_username()
        if applicant.username != department_leader:
            msg = '部门审批负责人: ' + department_leader + ' <strong>审批人员有错误?可能申请人所在的部门不对!请联系运维处理</strong>'
        else:
            msg = '你是部门负责人，不需要审批'

        success = True

    except User.DoesNotExist:
        msg = '用户没有找到'
        success = False
    except Exception as e:
        msg = str(e)
        success = False
    return (success, msg)


@workflow_approve_user.register('computerparts')
def computerparts_workflow_approve_user(workflow_class_name, *args, **kwargs):
    try:
        applicant_id = kwargs.get('applicant_id')
        applicant = User.objects.get(id=applicant_id)
        org = OrganizationMptt.objects.get(user_id=applicant.id)

        """
        2018.12修改，获取审批链，关联新组织架构，合并第一步，第二步，即部门组长和部门负责人
        """
        if not org.parent or org.parent_id == 1:
            raise Exception('用户%s没有分配到部门' % (applicant.username))

        approve_user_list = org.get_all_parent_leader_list(False)
        approve_user_list.reverse()
        approve_user_list = approve_user_list[:2]

        success = True

        pre_msg = '审批人员链: '
        approve_user_chain = '==>'.join([x for x in list(dedupe(approve_user_list))])
        pre_msg += approve_user_chain
        if approve_user_list:
            msg = pre_msg + ' <strong>审批人员有错误?可能申请人所在的部门不对!请联系运维处理</strong>'
        else:
            msg = '你是部门负责人，不需要审批'

    except User.DoesNotExist:
        msg = '用户没有找到'
        success = False
    except Exception as e:
        msg = str(e)
        success = False
    return (success, msg)


@workflow_approve_user.register('machine')
def machine_approve_user(workflow_class_name, *args, **kwargs):
    # 获取workflow流程对象
    try:
        project_id = kwargs.get('project_id')
        applicant_id = kwargs.get('applicant_id')

        project = GameProject.objects.get(id=project_id)
        applicant = User.objects.get(id=applicant_id)

        # 审批用户链
        approve_user_list = []

        """2018.12修改，关联新组织架构表"""
        # 第一步
        # 部门的负责人
        org = OrganizationMptt.objects.filter(user=applicant)
        if not org:
            raise Exception('用户没有在新组织架构中')
        else:
            org = OrganizationMptt.objects.get(user=applicant)
            if not org.parent:
                raise UserNotInGroup('用户没有在部门里面')
            else:
                if org.parent.leader == 0 and org.parent.parent.leader == 0:
                    raise GroupExtentionError("申请人所在的部门没有设置负责人")
        department_leader = org.get_department_obj().get_leader_username()
        if applicant.username != department_leader:
            approve_user_list.append(department_leader)

        # 第二步
        # 项目负责人
        project_leader = project.leader
        if not project_leader:
            raise WorkflowStateUserRelationError('项目负责人不存在')
        if applicant.id != project_leader.id:
            approve_user_list.append(project_leader.username)

        # 第三步
        # 中心负责人
        if not project.organizationmptt_set.all():
            raise Exception('所选的游戏项目没有所属部门')
        center_leader_id = project.organizationmptt_set.all()[0].leader
        if center_leader_id == 0:
            raise GroupExtentionError("游戏项目所属部门没有设置负责人")
        center_leader = User.objects.get(pk=center_leader_id)

        if applicant.id != center_leader.id:
            approve_user_list.append(center_leader.username)

        success = True

        pre_msg = '审批人员链: '
        approve_user_chain = '==>'.join([x for x in list(dedupe(approve_user_list))])
        pre_msg += approve_user_chain
        msg = pre_msg + ' <strong>审批人员有错误?可能申请人所在的部门不对!请联系运维处理</strong>'

    except GroupExtentionError as e:
        msg = str(e)
        success = False
    except User.DoesNotExist:
        msg = '用户没有找到'
        success = False
    except GameProject.DoesNotExist:
        msg = '没有项目没有'
        success = False
    except WorkflowStateUserRelationError as e:
        msg = str(e)
        success = False
    except UserNotInGroup as e:
        msg = str(e)
        success = False
    except Exception as e:
        msg = str(e)
        success = False
    return (success, msg)


@workflow_approve_user.register('projectadjust')
def projectadjust_approve_user(workflow_class_name, *args, **kwargs):
    try:
        applicant_id = kwargs.get('applicant_id')
        applicant = User.objects.get(id=applicant_id)

        # 部门的负责人
        """2018.12修改，关联新组织架构表"""
        org = OrganizationMptt.objects.filter(user=applicant)
        if not org:
            raise Exception('用户没有在新组织架构中')
        else:
            org = OrganizationMptt.objects.get(user=applicant)
            if not org.parent:
                raise UserNotInGroup('用户没有在部门里面')
            else:
                if org.parent.leader == 0 and org.parent.parent.leader == 0:
                    raise GroupExtentionError("申请人所在的部门没有设置负责人")
        department_leader = org.get_department_obj().get_leader_username()
        if applicant.username != department_leader:
            msg = '审批人员链: ' + department_leader + ' <strong>审批人员有错误?可能申请人所在的部门不对!请联系运维处理</strong>'
        else:
            msg = '你是部门负责人，不需要审批'

        success = True

    except User.DoesNotExist:
        msg = '用户没有找到'
        success = False
    except Exception as e:
        msg = str(e)
        success = False
    return (success, msg)


@workflow_approve_user.register('mysqlworkflow')
def mysql_workflow_approve_user(workflow_class_name, *args, **kwargs):
    try:
        username = kwargs.get('username')
        applicant = User.objects.get(username=username)
        org = OrganizationMptt.objects.get(user=applicant)

        # 第一步
        # 小组长审批人
        # 如果有小组长，是部门管理分组的组长
        # 如果没有小组长，则需要申请人自己审批
        # 第二步
        # 部门的负责人

        """
        2018.12修改，获取审批链，关联新组织架构，合并第一步，第二步
        """
        if not org.parent or org.parent_id == 1:
            raise Exception('用户%s没有分配到部门' % (applicant.username))

        approve_user_list = org.get_all_parent_leader_list(False)
        approve_user_list.reverse()
        approve_user_list = approve_user_list[:2]

        pre_msg = '审批人员链: '
        # approve_user_chain = '==>'.join([x.username for x in list(dedupe(approve_user_list))])
        approve_user_chain = '==>'.join([x for x in list(dedupe(approve_user_list))])
        pre_msg += approve_user_chain
        msg = pre_msg + ' <strong>审批人员有错误?可能申请人所在的部门不对!请联系运维处理</strong>'

        success = True

    except GameProject.DoesNotExist:
        msg = '项目不存在'
        success = False
    except User.DoesNotExist:
        msg = '用户没有找到'
        success = False
    except Exception as e:
        msg = str(e)
        success = False
    return (success, msg)
