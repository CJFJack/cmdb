# -*- coding: utf-8 -*-

from collections import defaultdict
import traceback

# Create your views here.

from rest_framework.views import APIView
from django.http import JsonResponse
from django.db import transaction

from django.contrib.auth.models import User
from users.models import OrganizationMptt, Profile, OuterAccountTemp, UserChangeRecord, Role
from tasks import add_qq_user
from tasks import add_email_account
from tasks import send_mail
from tasks import send_weixin_message
from users.utils import format_department_char_and_get_org_id
from users.utils import create_organization
from users.ldap_utils import LDAP
from myworkflows.utils import user_add_nofity
from mysql.mysql_utils import gen_password
from cmdb.api_permissions import api_permission
from users.views import organization_delete
from cmdb.logs import APIUserLog
from api_user.utils import make_new_user_info_share_content
from myworkflows.models import SpecialUserParamConfig
from django.db.models import Q


class GroupUsers(APIView):
    """获取部门的所有用户
    返回的数据格式如下:
    {
        "部门1": {"email1": ['staff1', 'staff2']},
        "部门2": {"email2": ['staff3', 'staff4']},
    }
    """

    def get(self, request, format=None):
        org_users = defaultdict(lambda: defaultdict(list))

        all_users = User.objects.prefetch_related('organizationmptt_set').filter(is_active=1)
        resp = 0
        reason = ''

        try:
            for u in all_users:
                org = u.organizationmptt_set.all()[0]
                if org.get_parent_leader_obj():
                    org_users[org.get_ancestors_except_self_by_slash()][org.get_parent_leader_obj().email].append(u.first_name)
                else:
                    org_users[org.get_ancestors_except_self_by_slash()]['无'].append(u.first_name)
            reason = org_users
        except Exception as e:
            traceback.print_exc()
            reason = str(e)
            resp = 1
        return JsonResponse({'reason': reason, 'resp': resp})


@api_permission(api_perms=['api_cmdb_user_add'])
class UserAdd(APIView):
    """
    开通cmdb帐号接口
    请求格式：
    {
        'username': '测试中文名字',
        'first_name': 'test_pinyin',
        'position': '运维测试工程师',
        'department': '原力互娱/运维部/网络管理组',
        'gender': 1,           # 1： 男  2： 女
        'is_qq': 1,            # 是否开通企业QQ   1： 是  0： 否
        'is_email': 1,         # 是否开通企业邮箱  0： 否  1：是，开通forcegames.cn  2：是，开通chuangyunet.com   3：是，同时开通forcegames.cn和chuangyunet.com
        'is_wifi': 1,          # 是否开通wifi    1： 是  0：否
    }
    返回数据：
    {'success': True, 'msg': 'ok，初始密码为redhat'}
    """

    def post(self, request):
        success = True
        msg = 'ok，初始密码为redhat'
        need_param = (
            'username', 'first_name', 'position', 'department', 'gender', 'is_qq', 'is_email', 'is_wifi'
        )
        log = APIUserLog()
        try:
            with transaction.atomic():
                raw_data = request.data
                log.logger.info(raw_data)
                username = raw_data.get('username', '')
                username = username.strip()
                first_name = raw_data.get('first_name', '')
                first_name = first_name.strip()
                position = raw_data.get('position', '')
                department = raw_data.get('department', '')
                gender = raw_data.get('gender', '')
                is_qq = raw_data.get('is_qq', '')
                is_email = raw_data.get('is_email', '')
                is_wifi = raw_data.get('is_wifi', '')

                for param in need_param:
                    if param == '':
                        raise Exception('缺少参数：%s' % param)

                # 若用户已存在，
                user = User.objects.filter(Q(first_name=first_name) | Q(username=username))
                if user:
                    user = user[0]
                    if user.is_active == 1:
                        raise Exception('用户%s(%s)已存在' % (username, first_name))

                if int(is_email) == 1:
                    email = first_name + '@forcegames.cn'
                elif int(is_email) == 2:
                    email = first_name + '@chuangyunet.com'
                elif int(is_email) == 3:
                    email = first_name + '@forcegames.cn' + ',' + first_name + '@chuangyunet.com'
                elif int(is_email) == 0:
                    email = ''
                else:
                    raise Exception('参数%s格式不正确' % 'is_email')

                # 获取员工所属组织节点id，若所属组织节点不存在，则新增组织节点
                if department.split('/')[0] != OrganizationMptt.objects.first().name:
                    department = OrganizationMptt.objects.first().name + '/' + department
                create_organization(department)
                parent_id = format_department_char_and_get_org_id(department=department)
                if parent_id is not None:
                    parent = OrganizationMptt.objects.get(pk=parent_id)
                else:
                    raise Exception('创建组织架构失败，请联系cmdb管理员！')

                # 创建cmdb帐号
                if user:
                    user.email = email
                    user.is_superuser = 0
                    user.save(update_fields=['email', 'is_superuser', 'is_active'])
                    org = user.organizationmptt_set.first()
                    org.hot_update_email_approve = 0
                    org.parent = parent
                    org.sex = gender
                    org.title = position
                    org.is_register = 0
                    org.save(update_fields=['hot_update_email_approve', 'parent', 'sex', 'title', 'is_register'])
                else:
                    user = User.objects.create(username=username, first_name=first_name, email=email, is_superuser=0,
                                               is_active=0)
                    Profile.objects.create(user_id=user.id, status=1)
                    org = OrganizationMptt.objects.create(name=username, hot_update_email_approve=0, user=user, type=2,
                                                          parent=parent, is_active=0, sex=gender, title=position,
                                                          is_register=0)

                user.set_password('redhat')
                user.save()

                """将是否开通外部帐号保存到临时表，到员工确认报到入职后才正式开通"""
                OuterAccountTemp.objects.update_or_create(org=org, is_email=is_email, is_qq=is_qq, is_ldap=is_wifi)
                """记录操作日志"""
                UserChangeRecord.objects.create(create_user=request.user, change_obj=org.name, type=1)

                log.logger.info(msg)
                return JsonResponse({'success': success, 'msg': msg})

        except Exception as e:
            success = False
            msg = str(e)
            log.logger.error(msg)
            return JsonResponse({'success': success, 'msg': msg})


@api_permission(api_perms=['api_cmdb_confirm_register'])
class UserConfirm(APIView):
    """
    确认用户报到入职API
    请求参数：
    {
        'username': 'xxxx'    # 用户中文名
    }
    或
    {
        'first_name': 'xxxx'  # 用户拼音
    }
    返回参数：
    {'success': True, 'msg': 'ok'}
    """

    def post(self, request):
        msg = '确认入职成功'
        success = True
        log = APIUserLog()
        try:
            raw_data = request.data
            log.logger.info(raw_data)
            username = raw_data.get('username', None)
            first_name = raw_data.get('first_name', None)
            """检查必要参数"""
            if not (username or first_name):
                raise Exception('用户名或者用户拼音至少需要一个')
            if username:
                org = OrganizationMptt.objects.filter(name=username)
            else:
                org = OrganizationMptt.objects.filter(user__first_name=first_name)
            if org:
                org.update(**{'is_register': 1, 'is_active': 1})
                user = org[0].user
                user.is_active = 1
                user.save(update_fields=['is_active'])

                """记录操作日志"""
                UserChangeRecord.objects.create(create_user=request.user, change_obj=org[0].name, type=5)

                """查找临时表，判断是否需要开通外部帐号"""
                outer_account = OuterAccountTemp.objects.filter(org=org)
                if outer_account:
                    outer_account = outer_account[0]
                    is_email = outer_account.is_email
                    is_qq = outer_account.is_qq
                    is_wifi = outer_account.is_ldap
                    org = org[0]
                    organization_char = org.get_ancestors_except_self_by_slash()

                    # 添加企业邮箱
                    if int(is_email) == 1:
                        log.logger.info('{} 开通企业邮箱forcegames帐号'.format(first_name))
                        add_email_account(org.user.first_name + '@forcegames.cn', org.name, org.sex,
                                          organization_char, org.title, org.id)
                    if int(is_email) == 2:
                        log.logger.info('{} 开通企业邮箱chuangyunet帐号'.format(first_name))
                        add_email_account(org.user.first_name + '@chuangyunet.com', org.name, org.sex,
                                          organization_char, org.title, org.id)
                    if int(is_email) == 3:
                        log.logger.info('{} 开通企业邮箱forcegames和chuangyunet帐号'.format(first_name))
                        add_email_account(org.user.first_name + '@forcegames.cn', org.name, org.sex,
                                          organization_char, org.title, org.id)
                        add_email_account(org.user.first_name + '@chuangyunet.com', org.name, org.sex,
                                          organization_char, org.title, org.id)

                    # 添加企业QQ帐号
                    if int(is_qq) == 1:
                        log.logger.info('{} 开通企业QQ帐号'.format(first_name))
                        add_qq_user(org.user.first_name, org.name, org.sex, organization_char, org.title, org.id)

                    # 添加wifi
                    if int(is_wifi) == 1:
                        log.logger.info('{} 开通ldap帐号'.format(first_name))
                        ldap = LDAP()
                        password = gen_password(10)
                        gid = int('20000000')
                        uid = org.user.first_name
                        ldap.add_people_ou(uid, gid, userPassword=password)
                        ldap.add_group_ou(gid, uid)
                        ldap.unbind()
                        to_list = [org.user.email]
                        subject = '入职CMDB和wifi账号信息'
                        content = user_add_nofity(org.user.first_name, password)
                        send_mail.delay(to_list, subject, content, 10)

                    # 删除临时表记录
                    outer_account.delete()

                    # 发送新入职员工信息给前台(企业微信)
                    content = make_new_user_info_share_content(org.id)
                    try:
                        touser_list = SpecialUserParamConfig.objects.get(param='LL_RECEPTION').user.all()
                        touser = '|'.join([x.first_name for x in touser_list])
                    except:
                        touser = None
                    if touser:
                        send_weixin_message.delay(touser=touser, content=content)

            else:
                raise Exception('用户不存在')

        except Exception as e:
            msg = str(e)
            success = False
        finally:
            if success:
                log.logger.info(msg)
            else:
                log.logger.error(msg)
            return JsonResponse({'success': success, 'msg': msg})


@api_permission(api_perms=['api_cmdb_user_delete'])
class UserDel(APIView):
    """
    删除cmdb用户API
    请求参数：
    {
        'username': 'xxxx'    # 用户中文名
    }
    或
    {
        'first_name': 'xxxx'  # 用户拼音
    }
    返回参数：
    {'success': True, 'msg': 'ok'}
    """

    def post(self, request):
        msg = '删除成功'
        success = True
        log = APIUserLog()
        try:
            raw_data = request.data
            log.logger.info(raw_data)
            username = raw_data.get('username', None)
            first_name = raw_data.get('first_name', None)
            """检查必要参数"""
            if not (username or first_name):
                raise Exception('用户名或者用户拼音至少需要一个')
            if username:
                org = OrganizationMptt.objects.filter(name=username)
            else:
                org = OrganizationMptt.objects.filter(user__first_name=first_name)
            if org:
                org = org[0]
                if org.is_register == 1:
                    raise Exception('用户 %s 已报到入职，不能删除' % org.name)
                else:
                    organization_delete(request, org.id)
            else:
                raise Exception('用户不存在')

        except Exception as e:
            success = False
            msg = str(e)
        finally:
            if success:
                log.logger.info(msg)
            else:
                log.logger.error(msg)
            return JsonResponse({'success': success, 'msg': msg})


class RoleInfo(APIView):
    """
    获取角色分组的信息
    返回数据格式：
    {
        'data': {
            '原力运维小组': {
                'project': ['超神荣耀', '校花', '剑雨江湖', '剑雨手游', '三生三世', '少年H5', '超神学院', '超神学院', '少年群侠传', '少年3D'],
                'mail': ['lixiaolong@forcegames.cn', 'liangjun@forcegames.cn'],
                'project_en': [...],
                'user': ['lixiaolong', 'liangjun'],
            },
            '创畅外派小组': {
                'project': ['骑战三国', '名将分争'],
                'mail': ['lixiaolong@chuangyunet.com'],
                'project_en': ['qzsg', 'mjfz'],
                'user': ['lixiaolong'],
            },
            '运维组': {
                'project': ['原力内网', '原力腾讯云'],
                'mail': ['41816456@qq.com'],
                'project_en': ['ylnw', 'yltxy'],
                'user': ['lixiaolong'],
            }
        },
        'success': True
    }
    """

    def get(self, request):
        success = True
        data = dict()
        try:
            raw_data = request.query_params
            role_name = raw_data.get('name', '')
            if role_name:
                objs = Role.objects.filter(name=role_name)
            else:
                objs = Role.objects.all()
            for r in objs:
                name = r.name
                info_data = dict()
                project = list(set([p.project_name for p in r.project.all()]))
                project_en = list(set([p.project_name_en for p in r.project.all()]))
                send_list = [u.email for u in r.user.all()]
                mail = set()
                for x in send_list:
                    for y in x.split(','):
                        mail.add(y)
                mail = list(mail)
                first_name = [u.first_name for u in r.user.all()]
                user = set()
                for x in first_name:
                    user.add(x)
                user = list(user)

                info_data['project'] = project
                info_data['project_en'] = project_en
                info_data['mail'] = mail
                info_data['user'] = user
                data[name] = info_data

        except Exception as e:
            success = False
            data = str(e)
        finally:
            return JsonResponse({'success': success, 'data': data})
