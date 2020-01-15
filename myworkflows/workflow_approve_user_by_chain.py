from users.models import OrganizationMptt
from assets.models import GameProject
from myworkflows.models import Transition
from myworkflows.models import SpecialUserParamConfig


def get_workflow_state_order(workflow):
    """获取workflow state的链表

    从workflow的init_state出发，找到transition为同意的destination
    """

    init_state = workflow.init_state

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


def dedupe(items):
    """去除一个list中重复的
    值，并且保持原来的顺序
    """
    seen = set()
    for item in items:
        if item not in seen:
            yield item
            seen.add(item)


def get_department_group_leader(org):
    """
    获取部门组长
    1.如果申请人是部门组长，则返回None
    2.如果申请人所在部门没有分组，或申请人不在分组里面，则返回None
    3.如果以上都不符合，则返回部门组长名字
    """
    department_group = org.get_department_group_obj()
    if department_group:
        department_group_leader = department_group.get_leader_username()
        if department_group_leader == '':
            raise Exception('申请人所在部门分组没有设置负责人，请联系运维网络管理组')
        else:
            return department_group_leader
    else:
        return None


def get_department_leader(org, is_game_project=False):
    """
    获取部门负责人
    1.如果申请人是部门负责人
        - 如果是游戏项目，则部门负责人改为公司负责人
        - 如果不是，则返回None
    2.如果以上都不符合，则返回部门负责人名字
    """
    department = org.get_department_obj()
    if department:
        department_leader = department.get_leader_username()
        if department_leader == '':
            raise Exception('申请人所在部门没有设置负责人，请联系运维网络管理组')
        elif department_leader == org.name:
            if is_game_project:
                # 如果部门上一层还有节点，并且有设置负责人，而且不是申请人，则返回上一层负责人
                if org.get_department_obj() and org.get_department_obj().get_parent_leader_obj() and org.get_department_obj().get_parent_leader_obj().username != org.name:
                    return org.get_department_obj().get_parent_leader_obj().username
                # 如果申请人不是最上级负责人，则返回最上级负责人
                if OrganizationMptt.objects.first().get_leader_username() == org.name:
                    return None
                else:
                    return OrganizationMptt.objects.first().get_leader_username()
            else:
                return None
        else:
            return department_leader
    else:
        return None


def get_project_leader(org, project):
    """
    获取项目负责人
    1.如果申请人是项目负责人，则返回None
    2.如果不是，则返回项目负责人名字
    """
    project_leader = project.leader
    if not project_leader:
        raise Exception('项目负责人不存在')
    if org.user_id != project_leader.id:
        return project_leader.username
    else:
        return None


def get_center_leader(org, project):
    """
    获取中心负责人
    1.如果申请人是中心负责人，则返回None
    2.如果不是，则返回游戏项目所属部门的负责人
    """
    if not project.organizationmptt_set.all():
        raise Exception('所选的游戏项目没有所属部门')
    center_leader_id = project.organizationmptt_set.all()[0].leader
    if center_leader_id == 0:
        raise Exception("游戏项目所属部门没有设置负责人")
    center_leader = OrganizationMptt.objects.get(user_id=center_leader_id)

    if org.id != center_leader.id:
        return center_leader.name
    else:
        return None


def get_operation_network_leader():
    """
    获取运维网络组成员
    """
    org = OrganizationMptt.objects.get(name='网络管理组')
    return org.get_leader_username()


def get_approve_user_chain(workflow, **kwargs):
    """获取审批人元链"""
    success = True
    msg = 'ok'
    approve_user_list = []
    approve_chain_dict = {}
    order_state = get_workflow_state_order(workflow)
    applicant_id = kwargs.get('applicant_id', '')
    project_id = kwargs.get('project_id', '')
    try:
        if project_id != '':
            project = GameProject.objects.get(id=project_id)
            is_game_project = project.is_game_project
        else:
            if workflow.name == '服务器权限申请':
                is_game_project = True
            else:
                is_game_project = False

        if applicant_id == '':
            username = kwargs.get('username', '')
            org = OrganizationMptt.objects.get(name=username)
        else:
            org = OrganizationMptt.objects.get(user_id=applicant_id)
        for state in order_state:
            if state.name == '部门组长':
                department_group_leader = get_department_group_leader(org)
                if department_group_leader:
                    approve_user_list.append(department_group_leader)
                approve_chain_dict[state] = department_group_leader
            if state.name == '部门负责人':
                department_leader = get_department_leader(org, is_game_project=is_game_project)
                if department_leader:
                    approve_user_list.append(department_leader)
                approve_chain_dict[state] = department_leader
            if state.name == '项目负责人':
                project_leader = get_project_leader(org, project)
                if project_leader:
                    approve_user_list.append(project_leader)
                approve_chain_dict[state] = project_leader
            if state.name == '中心负责人':
                center_leader = get_center_leader(org, project)
                if center_leader:
                    approve_user_list.append(center_leader)
                approve_chain_dict[state] = center_leader
            if state.name == '运维':
                if '创畅' in org.get_ancestors_except_self():
                    cc_network_administrator = SpecialUserParamConfig.objects.get(
                        param='CC_NETWORK_ADMINISTRATOR').get_user_list()
                    operation_network_leader = cc_network_administrator[0]
                    # 如果都找不到运维审批人，则返回运维网络组负责人
                    if not operation_network_leader:
                        operation_network_leader = get_operation_network_leader()
                else:
                    operation_network_leader = get_operation_network_leader()
                if operation_network_leader:
                    approve_user_list.append(operation_network_leader)
                approve_chain_dict[state] = operation_network_leader
            if state.name == '运维负责人':
                ops_charge = ','.join([ops.username for ops in project.get_relate_role_user()])
                approve_user_list.append(ops_charge)
                approve_chain_dict[state] = ops_charge
            if state.name == '后端负责人':
                server_charge = kwargs.get('server_charge', '')
                approve_user_list.append(server_charge)
                approve_chain_dict[state] = server_charge
            if state.name == '前端负责人':
                client_charge = kwargs.get('client_charge', '')
                approve_user_list.append(client_charge)
                approve_chain_dict[state] = client_charge
            if state.name == '策划负责人':
                plan_charge = kwargs.get('plan_charge', '')
                approve_user_list.append(plan_charge)
                approve_chain_dict[state] = plan_charge
            if state.name == '测试负责人':
                test_charge = kwargs.get('test_charge', '')
                approve_user_list.append(test_charge)
                approve_chain_dict[state] = test_charge

        if approve_user_list:
            pre_msg = '审批人员链: '
            approve_user_chain = '==>'.join([x for x in list(dedupe(approve_user_list))])
            pre_msg += approve_user_chain
            msg = pre_msg + ' <strong>审批人员有错误?可能申请人所在的部门不对!请联系运维处理</strong>'
        else:
            msg = '你是部门负责人，不需要审批'

    except Exception as e:
        success = False
        msg = str(e)
    finally:
        return success, msg, approve_user_list, approve_chain_dict
