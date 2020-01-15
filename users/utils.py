# -*- encoding: utf-8 -*-
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from users.config import *
from users.models import *
from tasks import cancel_desired_user_workflow_apply
from mptt.utils import get_cached_trees
from cmdb.logs import APIUserLog
from tasks import send_weixin_message
from tasks import send_qq
from users.outer_api import *
from it_assets.models import Assets
from it_assets.models import LogAssets
from it_assets.models import Position
from tasks import *
from jenkins.login_jenkins import get_jenkins_cookie
from jenkins.models import JenkinsCookie
from zabbix.utils import get_zabbix_cookie_v2
from zabbix.models import ZabbixCookie
from cmdb.settings import JENKINS_40_8_URL
from cmdb.settings import JENKINS_40_8_HOST
from cmdb.settings import JENKINS_40_15_URL
from cmdb.settings import JENKINS_40_15_HOST
# from cmdb.settings import JENKINS_yuanli_extranal_HOST
# from cmdb.settings import JENKINS_yuanli_extranal_URL
from cmdb.settings import ZABBIX_HOST

import requests
import json


def is_project_group_leader(user):
    """判断一个user是否为部门领导
    """
    pass


def make_serialier_url(id, expiration=1200):
    """根据用户id生成一个
    包含该id的url token
    """
    s = Serializer(SECRET_KEY, expiration)
    return s.dumps({'id': id}).decode('utf-8')


def make_content_for_reset_password(username, email, url):
    """编写重置密码邮件的内容
    """
    subject = '重置你的cmdb账号密码'

    template = "<html>" + \
               "<head>" + \
               "<meta charset='utf-8'>" + \
               "</head>" + \
               "<body>" + \
               "<h3>欢迎, %s</h3>" + \
               "<p><b>你的邮箱地址: %s</b></p>" + \
               "<h3>我们发送重置cmdb账号密码的如下链接，请访问该链接来重置你的cmdb账号密码</h3>" + \
               "<p><b>点击<a href=%s>重置链接</a></b></p>" + \
               "</body>" + \
               "</html>"

    content = template % (username, email, url)

    return (subject, content)


def make_wechat_content_for_reset_password(username, url):
    """编写重置密码企业微信的内容
    """
    template = '欢迎, {}\n请访问该链接来重置你的cmdb账号密码（如果打开失败，请使用谷歌或火狐浏览器!）\n<a href=\"{}\">点击重置链接</a>'
    content = template.format(username, url)

    return content


def send_token_mail(to_list, subject, content):
    """将生成的重置密码的链接发送到邮件中
    """
    pass


def format_department_char_and_get_org_id(department):
    """
    格式化组织架构字符串，并得到对应的user_organizationmptt表的id值
    参数格式如： '原力互娱/运维部/网络管理组'
    """
    all_org = [{'id': x.id, 'text': x.get_ancestors_by_slash()} for x in OrganizationMptt.objects.filter(type=1)]
    for org in all_org:
        if org['text'] == department:
            return org['id']
    return None


def compare_fields_with_objects(old_object, new_object, compare_fields):
    """
    对比同一个的model中不同的两个object中，不同的字段，返回字段及其变化的值，如：
    用户名:test1-->test2,性别:男-->女,部门:运维部-->财务部,
    """
    result = ''
    diff_fields = list(
        filter(lambda field: getattr(old_object, field, None) != getattr(new_object, field, None),
               compare_fields))
    diff_char = [convert_field_to_chinese(x, old_object) + ':' + str(getattr(old_object, x, None)) + '-->' + str(
        getattr(new_object, x, None)) + ',' for x in diff_fields if x != 'password' and x != 'leader' and x != 'parent']
    for x in diff_char:
        result += x
    if 'password' in diff_fields:
        result += '修改密码,'
    if 'leader' in diff_fields:
        old_leader_id = getattr(old_object, 'leader', 0)
        if int(old_leader_id) != 0:
            old_user = User.objects.get(pk=old_leader_id).username
        else:
            old_user = ''
        new_leader_id = getattr(new_object, 'leader', 0)
        if int(new_leader_id) != 0:
            new_user = User.objects.get(pk=new_leader_id).username
        else:
            new_user = ''
        result += '负责人:' + old_user + '-->' + new_user + ','
    if 'parent' in diff_fields:
        old_parent = old_object.get_ancestors_except_self_by_slash()
        new_parent = new_object.get_ancestors_except_self_by_slash()
        result += '部门:' + old_parent + '-->' + new_parent + ','
    if 'is_active' in diff_fields and not new_object.is_active:
        """如果修改用户离职状态，并且修改为离职，则找出所有该用户的未审批完成的工单，进行取消"""
        cancel_desired_user_workflow_apply.delay(new_object.user.id)
    return result


def convert_field_to_chinese(field_name, object):
    """转换django内置表的字段名为中文解释"""
    if type(object._meta.get_field(field_name).verbose_name) == str:
        return object._meta.get_field(field_name).verbose_name
    else:
        if field_name == 'username':
            return '中文名'
        if field_name == 'first_name':
            return '姓名拼音'
        if field_name == 'email':
            return '邮箱'
        if field_name == 'password':
            return '密码'
        if field_name == 'username':
            return '中文名'
        if field_name == 'is_superuser':
            return '是否管理员'
        else:
            return field_name


def get_organization_tree():
    """获取组织架构树状数据"""
    root_node = get_cached_trees(OrganizationMptt.objects.all())[0]
    tree_list = []
    tree_dict = dict()
    tree_dict['dataId'] = root_node.id
    if root_node.user:
        tree_dict['text'] = root_node.name + '   ' + root_node.user.first_name
    else:
        tree_dict['text'] = root_node.name
    tree_dict['nodes'] = sorted(get_child_node_list(root_node), key=lambda x: x['text'])
    leader_username = root_node.get_leader_username()
    if leader_username:
        tag = '负责人：' + leader_username
        tree_dict['tags'] = [tag]
    else:
        tree_dict['tags'] = [str(root_node.get_title())]
    tree_list.append(tree_dict)
    return tree_list


def get_child_node_list(node):
    """递归查找子节点数据"""
    child_list = []
    child_nodes = node.get_children()
    if child_nodes:
        for child in child_nodes:
            child_dict = dict()
            if child.user:
                child_dict['text'] = child.name + '   ' + child.user.first_name
            else:
                child_dict['text'] = child.name
            child_dict['dataId'] = child.id
            child_dict['type'] = child.type
            leader_username = child.get_leader_username()
            if leader_username:
                tag = '负责人：' + leader_username
                child_dict['tags'] = [tag]
            else:
                child_dict['tags'] = [str(child.get_title())]
            if child.get_children():
                child_dict['nodes'] = get_child_node_list(child)

            child_list.append(child_dict)
            child_list = sorted(child_list, key=lambda x: x['type'], reverse=True)
        return child_list


def create_organization(org_char_by_slash, parent_org=None):
    """
    递归创建组织架构节点：
    param:
        org_char_by_slash: 原力互娱/运维部/业务运维组
        parent_org: 组织架构节点对象实例
    return: None
    """
    log = APIUserLog()
    org_name_list = org_char_by_slash.split('/')
    if org_name_list:
        name = org_name_list.pop(0)
        """检查组织节点是否已存在"""
        if parent_org:
            org = OrganizationMptt.objects.filter(name=name, parent=parent_org)
        else:
            org = OrganizationMptt.objects.filter(name=name)
        """如果不存在则新建"""
        if not org:
            if parent_org:
                org = OrganizationMptt.objects.create(name=name, type=1, parent=parent_org)
            else:
                org = OrganizationMptt.objects.create(name=name, type=1)
            log.logger.info('创建组织架构节点成功： {}'.format(org.get_ancestors_by_slash()))
            """发送微信提醒相关人员补充节点其他信息，包括节点负责人/是否公共部门/是否部门下分组等"""
            send_user = OrganizationMptt.objects.get(name='网络管理组').get_leader_firstname()
            content = 'cmdb新增部门节点： {}，请登录cmdb补充部门负责人, 是否公共部门, 是否部门下分组等信息'.format(org.get_ancestors_by_slash())
            send_weixin_message.delay(touser=send_user, content=content)
        else:
            org = org[0]
        """检查节点列表中是否还有元素，有则继续递归"""
        if org_name_list:
            org_char_by_slash = '/'.join(org_name_list)
            create_organization(org_char_by_slash, parent_org=org)


def batch_user_desert(user_list, pos_id, request_user):
    """批量清除权限"""
    for username in user_list:
        user_id = User.objects.get(username=username).id
        remark = ''

        user = User.objects.get(id=user_id)
        ucs, _ = UserClearStatus.objects.get_or_create(profile=user.profile)

        remark += '清理服务器权限,'
        list_ops_manager, default_ip_list, use_default = get_all_ops_manager()
        # 设置权限记录为失效
        UserProfileHost.objects.filter(user_profile=user.profile).update(**{"is_valid": 0})
        clean_server(list_ops_manager, default_ip_list, use_default, user, ucs)

        remark += '清理SVN,'
        clean_svn(user, ucs)

        remark += '清理samba,'
        clean_samba(user, ucs)

        remark += '清理mysql,'
        remove_mysql_permission.delay(user.first_name)

        remark += '强制清理mysql,'
        remove_mysql_permission.delay(user.first_name, force=True)

        remark += '清理ldap,'
        clean_ldap(user, ucs)

        remark += '清理企业qq,'
        delete_ent_qq(user, ucs)

        for email in user.email.split(','):
            remark += '清理企业邮箱' + email + ','
            delete_ent_email(email, ucs)

        remark += '清理wifi,'
        delete_user_wifi(user, ucs)

        remark += '清理openvpn,'
        delete_user_for_openvpn(user, ucs)

        """记录操作日志"""
        UserChangeRecord.objects.create(create_user=request_user, change_obj=user.username, type=4, remark=remark)

        """关闭cmdb帐号，移至离职接收部"""
        user.is_active = 0
        user.save()
        org_user = OrganizationMptt.objects.get(user=user)
        org_user.is_active = 0
        org_dessert = OrganizationMptt.objects.get(name='离职接收部')
        org_user.move_to(org_dessert)
        org_user.save()
        """用户离职，需要从以下表中删除：
        运维角色分组
        工单流程-特殊人员配置
        工单流程-流程审批人设置
        """
        # 运维角色分组
        for r in Role.objects.prefetch_related('user').all():
            r.user.remove(user)
        # 工单流程-特殊人员配置
        for s in SpecialUserParamConfig.objects.prefetch_related('user').all():
            s.user.remove(user)
        # 工单流程-流程审批人设置
        for s in State.objects.prefetch_related('specified_users').all():
            s.specified_users.remove(user)
        """批量回收资产"""
        recover_list = [a.id for a in Assets.objects.filter(user=username)]
        for assets_id in recover_list:
            assets = Assets.objects.get(pk=assets_id)
            pre_user = assets.auth_user.username
            assets.status = 0
            assets.pos_id = pos_id
            assets.user = request_user.username
            assets.auth_user = request_user
            organization = OrganizationMptt.objects.get(user=request_user)
            assets.using_department = organization.get_ancestors_except_self()
            assets.belongs_to_new_organization = organization.get_ancestors_except_self()
            assets.save()
            """写入资产变更记录"""
            log_assets = LogAssets(event=4, etime=datetime.now(), log_user=request_user.username,
                                   user=request_user.username, number=1, assets_id=assets_id, pos_id=assets.pos_id,
                                   purchase=0, pre_user=pre_user)
            log_assets.save()


def save_jenkins_cookie(username, password):
    """模拟登录jenkins，保存cookie"""
    try:
        user = User.objects.get(Q(username=username) | Q(first_name=username))
        # jenkins_192.168.40.8
        success, msg, cookie_40_8 = get_jenkins_cookie(username, password, jenkins_url=JENKINS_40_8_URL,
                                                       jenkins_host=JENKINS_40_8_HOST)

        JenkinsCookie.objects.update_or_create(user=user, jenkins_ip='192.168.40.8',
                                               defaults={'cookie': cookie_40_8, 'status': success, 'msg': msg})

        # jenkins_192.168.40.15
        success, msg, cookie_40_15 = get_jenkins_cookie(username, password, jenkins_url=JENKINS_40_15_URL,
                                                        jenkins_host=JENKINS_40_15_HOST)
        JenkinsCookie.objects.update_or_create(user=user, jenkins_ip='192.168.40.15',
                                               defaults={'cookie': cookie_40_15, 'status': success, 'msg': msg})

        # jenkins_原力外网
        # success, msg, cookie_yuanli_extranal = get_jenkins_cookie(username, password, jenkins_url=JENKINS_yuanli_extranal_URL,
        #                                                           jenkins_host=JENKINS_yuanli_extranal_HOST)
        # JenkinsCookie.objects.update_or_create(user=user, jenkins_ip='jenkins.yl666.yl',
        #                                        defaults={'cookie': cookie_yuanli_extranal, 'status': success, 'msg': msg})

    except Exception as e:
        print(str(e))


def save_zabbix_cookie(username, password):
    """模拟登录zabbix，保存cookie"""
    try:
        user = User.objects.get(Q(username=username) | Q(first_name=username))
        success, cookie_dict, msg = get_zabbix_cookie_v2(username, password)
        ZabbixCookie.objects.update_or_create(user=user, zabbix_ip=ZABBIX_HOST,
                                              defaults={'cookie': json.dumps(cookie_dict), 'status': success,
                                                        'msg': msg})
    except Exception as e:
        print(str(e))


def get_last_user_clean_option(ucs=None):
    """
    获取上一次清理用户时的选项：
    """
    clean_option = dict()
    for f in UserClearStatus._meta._get_fields():
        if ucs:
            clean_option[f.name] = True if ucs.__getattribute__(f.name) else False
        else:
            clean_option[f.name] = False
    if ucs:
        server_projects = set()
        if ucs.server_permission:
            for ops_ip in json.loads(ucs.server_permission).get('ops_ip', []):
                ops_obj = OpsManager.objects.filter(url__icontains=ops_ip)
                if not ops_obj:
                    continue
                server_projects.add(ops_obj[0].project.id)
        clean_option['server_projects'] = list(server_projects)
        svn_projects = set()
        if ucs.svn:
            for project_name_en in json.loads(ucs.svn):
                project_obj = GameProject.objects.filter(project_name_en=project_name_en)
                if not project_obj:
                    continue
                svn_projects.add(project_obj[0].id)
        clean_option['svn_projects'] = list(svn_projects)
    else:
        clean_option['server_projects'] = clean_option['svn_projects'] = []

    return clean_option


def get_user_clean_failed_option(ucs=None):
    """
    获取用户权限清理结果，若清理失败，则为True或失败的项目id集合的列表，否则为False：
    {
        'server_permission': [37, 56, 78],
        'svn': True,
        'mysql': False,
        ...
    }
    """
    clean_result_dict = dict()

    for f in UserClearStatus._meta._get_fields():
        if f.name in ('id', 'profile'):
            continue
        clean_result_dict.setdefault(f.name, False)
        if not ucs:
            continue
        if not ucs.__getattribute__(f.name):
            continue

        field_value = json.loads(ucs.__getattribute__(f.name))
        if not (field_value.get('success', True) and field_value.get('ret', True)):
            clean_result_dict[f.name] = True

    # 查找是否有清理服务器权限失败的项目
    if ucs and ucs.server_permission:
        list_server_projects = []
        server_permission = json.loads(ucs.server_permission)
        for ops_ip in server_permission.get('ops_ip', []):
            if not server_permission.get(ops_ip, {'success': False}).get('success'):
                ops = OpsManager.objects.filter(url='https://' + ops_ip + '/api/')
                if not ops:
                    continue
                list_server_projects.append(ops[0].project.id)
        if list_server_projects:
            clean_result_dict['server_permission'] = list_server_projects

    # 查找是否有清理SVN权限失败的项目
    if ucs and ucs.svn:
        svn = json.loads(ucs.svn)
        list_svn_projects = []
        for project_name_en in svn:
            project_obj = GameProject.objects.filter(project_name_en=project_name_en)
            if not project_obj:
                continue
            if not svn.get(project_name_en, {'success': True}).get('success'):
                list_svn_projects.append(project_obj[0].id)
        if list_svn_projects:
            clean_result_dict['svn'] = list_svn_projects

    # 查找是否有清理mysql权限失败的项目
    if ucs and ucs.mysql_permission:
        mysql_permission = json.loads(ucs.mysql_permission)
        for mysql_instance in mysql_permission.get('mysql_instance', []):
            if not mysql_permission.get(mysql_instance, {'success', False}).get('success'):
                clean_result_dict['mysql_permission'] = True
                break

    return clean_result_dict
