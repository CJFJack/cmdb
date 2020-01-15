from django.shortcuts import render, reverse, get_object_or_404, redirect
from django.http import HttpResponseRedirect, JsonResponse, Http404
from django.http import HttpResponse

from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import PermissionDenied

from django.conf import settings

from django.db import IntegrityError

from django.db.models import Count

# from users.models import GroupSection
from users.utils import *
from users.config import *
from users.outer_api import *
from users.channels_utils import ws_notify_clean_user

from users.roles import is_group_leader

from users.ldap_groups import LDAP_GROUPS
from users.ldap_utils import LDAP

from assets.utils import get_user_serper_project
from assets.utils import get_user_svn_project
from assets.models import GameProject
# from assets.models import GroupSection
from myworkflows.utils import user_add_nofity
from myworkflows.models import SpecialUserParamConfig
from myworkflows.models import State
from mysql.mysql_utils import gen_password
from it_assets.models import CompanyCode, Assets, Position, LogAssets, AssetsWarehousingRegion
from api_user.utils import make_new_user_info_share_content

from itsdangerous import *

from tasks import send_mail, add_qq_user, add_email_account
from tasks import remove_mysql_permission

from django.views import generic
from datetime import datetime, timedelta
from cmdb.logs import *
from copy import deepcopy
from urllib.parse import unquote

import requests
import json
import xlwt


# import re


def user_login(request):
    """处理用户登录

    如果用户名和密码成功
    login(request, user)
    同时则跳转到相应的页面

    如果没有，登录页面显示登录失败的消息
    """
    if request.method == "GET":
        return render(request, 'login.html')

    if request.method == "POST":
        user_name = request.POST["username"]
        password = request.POST["password"]
        try:
            if not password:
                return render(request, 'login.html', {'msg': '请输入密码'})
            user = User.objects.get(Q(username=user_name) | Q(first_name=user_name))
            if not user.is_active:
                return render(request, 'login.html', {'msg': '用户禁止登陆'})
        except User.MultipleObjectsReturned:
            return render(request, 'login.html', {'msg': '用户名不正确，请确定是否使用完整的中文名或者拼音登录？'})
        except User.DoesNotExist:
            return render(request, 'login.html', {'msg': '用户不存在, 确定是使用中文名或者拼音名登录？'})
        user = authenticate(username=user.username, password=password)
        if user is not None:
            login(request, user)

            if request.user.is_superuser:
                # 模拟登录jenkins获取cookie，存入本地数据库备用
                save_jenkins_cookie(user_name, password)
                # 模拟登录zabbix获取cookie，存入本地数据库备用
                save_zabbix_cookie(user_name, password)

            # 跳转登录后页面
            if request.user.is_superuser:
                next_page = unquote(request.POST.get('next', '/dashboard/'))
            else:
                next_page = unquote(request.POST.get('next', '/myworkflows/approve_list/'))
            try:
                if request.user.is_superuser:
                    return HttpResponseRedirect(next_page or '/dashboard/')
                else:
                    return HttpResponseRedirect(next_page or '/myworkflows/approve_list/')
            except:
                if request.user.is_superuser:
                    return HttpResponseRedirect('/dashboard/')
                else:
                    return HttpResponseRedirect('/myworkflows/approve_list/')
        else:
            msg = '认证失败'
            return render(request, 'login.html', {'msg': msg})


"""
def user_register(request):
    "用户注册页面
    "

    if request.method == "GET":
        return render(request, 'register.html')

    if request.method == "POST":
        raw_data = json.loads(request.body.decode('utf-8'))
        msg = 'ok'

        try:
            with transaction.atomic():
                username = raw_data.get('username')
                first_name = raw_data.get('first_name')
                first_name = first_name.lower()    # 转为化小写

                # 用正则判断是否拼音满足要求
                p = re.compile(r'(^[a-z])(\d)?')
                if not re.match(p, first_name):
                    raise IndexError

                if re.match(p, username):
                    raise IndentationError

                # 强制拼音也是唯一的
                first_name_user = User.objects.filter(first_name=first_name)
                if first_name_user:
                    raise NameError

                email = first_name + '@forcegames.cn'
                group = raw_data.get('group')
                password = raw_data.get('password')
                # game_project = raw_data.get('game_project', None)
                project_group = raw_data.get('project_group', None)

                # 创建用户
                u = User.objects.create(username=username, first_name=first_name, email=email)
                u.set_password(password)
                u.save()

                # 用户关联到部门
                u.groups.add(Group.objects.get(id=group))

                # 创建用户扩展属性
                profile = Profile.objects.create(user=u)

                # 如果属于某个项目组的分组
                if project_group:
                    profile.project_group = ProjectGroup.objects.get(id=project_group)
                    profile.save()

                success = True

        except IntegrityError:
            msg = '用户已经存在'
            success = False
        except Group.DoesNotExist:
            msg = '部门不存在'
            success = False
        except NameError:
            msg = '拼音已经存在，你需要添加一些额外的标识'
            success = False
        except IndexError:
            msg = '拼音名称不满足要求，字母加上数字(如果有重复的话)'
            success = False
        except IndentationError:
            msg = '请填写中文名'
            success = False
        except Exception as e:
            msg = str(e)
            success = False

        return JsonResponse({'data': success, 'msg': msg})
"""


def forget_password(request):
    '忘记密码页面'
    if request.method == "GET":
        token = request.GET.get('token', None)
        if token:
            try:
                s = TimedJSONWebSignatureSerializer(SECRET_KEY)
                s.loads(token)
                return render(request, 'reset_password.html')
            except Exception as e:
                return HttpResponse('该链接已经失效')
        else:
            return render(request, 'forget_password.html')

    if request.method == "POST":
        raw_data = json.loads(request.body.decode('utf-8'))
        msg = 'ok'
        try:
            email = raw_data.get('email')
            u = User.objects.get(first_name=email)
            real_email = u.email
            token = make_serialier_url(u.id)
            url = 'http://192.168.100.66/forget_password/?token=%s' % (token)
            subject, content = make_content_for_reset_password(u.username, real_email, url)
            to_list = [real_email]
            send_mail(to_list, subject, content)
            wechat_content = make_wechat_content_for_reset_password(u.username, url)
            send_weixin_message(touser=u.first_name, content=wechat_content)
            success = True
        except User.DoesNotExist:
            msg = '没有找到%s，请核实登录名！' % (email,)
            success = False
        except Exception as e:
            msg = str(e)
            success = False
        return JsonResponse({'success': success, 'msg': msg})


def reset_password(request):
    "邮件重置密码"
    pdata = json.loads(request.body.decode('utf-8'))
    new_passwd1 = pdata.get('new_passwd1', None)
    new_passwd2 = pdata.get('new_passwd2', None)
    token = pdata.get('token', None)

    msg = ''

    if request.method == "POST":
        try:
            if token:
                s = TimedJSONWebSignatureSerializer(SECRET_KEY)
                id = s.loads(token).get('id', None)
                if id:
                    u = User.objects.get(id=id)
                    if new_passwd1 == new_passwd2:
                        u.set_password(new_passwd1)
                        u.save()
                        success = True
                    else:
                        msg = '两次密码不同'
                        success = False
                else:
                    msg = '没有找到id'
            else:
                msg = '没有找到token'
                success = False
        except User.DoesNotExist:
            msg = '用户不存在'
            success = False
        except SignatureExpired:
            msg = '该链接已经失效'
            success = False
        except BadSignature:
            msg = '该链接错误'
            success = False
        except Exception as e:
            msg = '重置密码失败'
            success = False
        return JsonResponse({'data': msg, 'success': success})


def user_logout(request):
    if request.method == "GET":
        """注销一个用户"""
        logout(request)
        return HttpResponseRedirect(settings.LOGIN_URL)


def new_passwd(request):
    if request.method == "GET":
        head = {'value': '新的密码', 'username': request.user.username}
        return render(request, 'new_passwd.html', {'head': head})

    if request.method == "POST":
        pdata = json.loads(request.body.decode('utf-8'))
        new_passwd1 = pdata.get('new_passwd1', None)
        new_passwd2 = pdata.get('new_passwd2', None)

        if new_passwd1 == new_passwd2:
            request.user.set_password(new_passwd1)
            request.user.save()
            msg = ''
            success = True
        else:
            msg = '两次密码不同'
            success = False
        return JsonResponse({'data': msg, 'success': success})


def user_list(request):
    """用户列表页面"""
    head = {'value': '用户', 'username': request.user.username}
    all_project = [{'id': x.id, 'text': x.project_name} for x in GameProject.objects.filter(status=1)]
    all_project_group = [{'id': x['name'], 'text': x['name']} for x in ProjectGroup.objects.values(
        'name').annotate(c=Count('name'))]
    all_group = [{'id': x.id, 'text': x.name} for x in Group.objects.all()]
    is_superuser = json.dumps(request.user.is_superuser)
    return render(
        request, 'user_list.html',
        {
            'head': head, 'all_project': all_project,
            'all_group': all_group, 'is_superuser': is_superuser,
            'all_project_group': all_project_group,
        }
    )


def data_user_list(request):
    """用户列表数据"""

    if request.method == "POST":
        raw_get = request.POST.dict()
        raw_data = []
        start = int(raw_get.get('start', 0))
        draw = raw_get.get('draw', 0)
        length = int(raw_get.get('length', 10))
        search_value = raw_get.get('search[value]', '')

        """
        1 超级用户管理员可以查看和修改员工信息
        2 普通用户只能查看信息
        """

        # 自定义的查询标签
        filter_username = raw_get.get('filter_username', '')
        filter_first_name = raw_get.get('filter_first_name', '')
        filter_email = raw_get.get('filter_email', '')
        filter_project = raw_get.get('filter_project', '全部')
        filter_project_group = raw_get.get('filter_project_group', '全部')
        filter_group = raw_get.get('filter_group', '全部')
        filter_is_superuser = raw_get.get('filter_is_superuser', '全部')
        filter_is_active = raw_get.get('filter_is_active', '全部')

        sub_query = Q()

        if filter_username:
            sub_query.add(Q(username__contains=filter_username), Q.AND)

        if filter_first_name:
            sub_query.add(Q(first_name__icontains=filter_first_name), Q.AND)

        if filter_email:
            sub_query.add(Q(email__icontains=filter_email), Q.AND)

        if filter_project != '全部':
            sub_query.add(Q(profile__project_group__project=GameProject.objects.get(id=filter_project)), Q.AND)

        if filter_project_group != '全部':
            sub_query.add(Q(profile__project_group__name=filter_project_group), Q.AND)

        if filter_is_superuser == '0':
            sub_query.add(Q(is_superuser=True), Q.AND)
        elif filter_is_superuser == '1':
            sub_query.add(Q(is_superuser=False), Q.AND)

        if filter_group != '全部':
            sub_query.add(Q(groups=Group.objects.get(id=filter_group)), Q.AND)

        if filter_is_active == '0':
            sub_query.add(Q(is_active=True), Q.AND)
        elif filter_is_active == '1':
            sub_query.add(Q(is_active=False), Q.AND)

        if not request.user.is_superuser:
            sub_query.add(Q(is_active=1), Q.AND)

        if search_value:
            query = User.objects.select_related(
                'profile__project_group').select_related(
                'profile__project_group__project').prefetch_related('groups').filter(
                Q(username__contains=search_value) |
                Q(first_name__icontains=search_value) |
                Q(email__icontains=search_value) |
                Q(profile__project_group__project__project_name__contains=search_value) |
                Q(profile__project_group__name__contains=search_value) |
                Q(groups__name__contains=search_value) & sub_query)
        else:
            query = User.objects.select_related(
                'profile__project_group').select_related(
                'profile__project_group__project').prefetch_related('groups').filter(sub_query)
        recordsTotal = query.count()
        raw_data = query[start: start + length]

        user_list = []

        for u in raw_data:
            is_superuser = '管理员' if u.is_superuser else '普通用户'

            if u.profile.group_section:
                game_project_group = []
                for project_group in u.profile.group_section.projectgroup_set.all():
                    link_name = "<a href='/users/group_section/?group_id={}'>{}</a>".format(
                        u.profile.group_section.group.id, project_group.project.project_name + '-' + project_group.name)
                    game_project_group.append(link_name)
                else:
                    game_project_group = ','.join(game_project_group)
            else:
                game_project_group = ''

            if u.profile.group_section:
                group_section = '<a href="/users/group_section/?group_id={}">{}</a>'.format(
                    u.profile.group_section.group.id, u.profile.group_section.name)
            else:
                group_section = ''
            user_list.append({
                'id': u.id,
                'username': u.username,
                'first_name': u.first_name,
                'email': u.email,
                # 'game_project': u.profile.project_group.project.project_name if u.profile.project_group else '',
                'game_project_group': game_project_group,
                'groups': ','.join([x.name for x in u.groups.all()]),
                'group_section': group_section,
                'is_superuser': is_superuser,
                'is_active': '是' if u.is_active else '否'
            })
        data = {"data": user_list, 'draw': draw, 'recordsTotal': recordsTotal, 'recordsFiltered': recordsTotal}
        return JsonResponse(data)


def get_group_leader_subordinates(group_leader):
    """获取部门负责人的下属员工
    如果没有，返回空的list
    """
    list_subordinate = []

    list_group = [x.group for x in GroupProfile.objects.filter(group_leader=group_leader)]

    for g in list_group:
        list_subordinate.extend(g.user_set.all())

    return list_subordinate


def get_data_user(request):
    """根据用户id获取用户的信息

    管理员用户可以修改任意用户的信息
    普通用户只能修改自己的信息

    group_info用户分组的数据, format:
    [
        {'id': 'group_id1': 'name': 'group_name1'},
        {'id': 'group_id2': 'name': 'group_name2'},
        ...
    ]

    game_project_info 用户的项目数据， format:
    [
        {'id': 'project_id1', 'project_name': 'project_name1'},
        {'id': 'project_id2', 'project_name': 'project_name2'},
        ...
    ]
    """

    if request.method == "POST":
        id = json.loads(request.body.decode('utf-8')).get('id')

        try:
            modify_user_obj = User.objects.get(id=id)

            if modify_user_obj in get_group_leader_subordinates(request.user):
                subordinate_user = True
            else:
                subordinate_user = False

            # immutable参数用来前端是否屏蔽某些不能修改的选项
            if request.user.is_superuser:
                immutable = False
                subordinate_user = True
            else:
                immutable = True
                # subordinate_user = False

            # 如果是管理员用或者修改自己的帐号
            if request.user.is_superuser or request.user == modify_user_obj or subordinate_user:

                # 用户的分组,只有一个分组
                try:
                    group = modify_user_obj.groups.all()[0]
                    group_id = group.id
                    group_name = group.name
                except IndexError:
                    group_id = '0'
                    group_name = '选择中心机构'

                # 用户的项目list,只有一个项目
                has_project_group = modify_user_obj.profile.project_group
                if has_project_group:
                    project_id = has_project_group.id
                    project_name = has_project_group.project.project_name
                    project_group_id = has_project_group.id
                    project_group_name = has_project_group.name
                else:
                    project_id = '0'
                    project_name = '选择项目'
                    project_group_id = '0'
                    project_group_name = '选择项目分组'

                if modify_user_obj.profile.group_section:
                    group_section_id = modify_user_obj.profile.group_section.id
                    group_section_name = modify_user_obj.profile.group_section.name
                else:
                    group_section_id = '0'
                    group_section_name = '部门分组'

                data = {
                    'id': id,
                    'username': modify_user_obj.username,
                    'first_name': modify_user_obj.first_name,
                    'email': modify_user_obj.email,
                    'group_id': group_id,
                    'group_name': group_name,
                    'group_section_id': group_section_id,
                    'group_section_name': group_section_name,
                    'project_id': project_id,
                    'project_name': project_name,
                    'project_group_id': project_group_id,
                    'project_group_name': project_group_name,
                    'is_superuser': modify_user_obj.is_superuser,
                    'is_active': modify_user_obj.is_active,
                }

                success = True
            else:
                data = '不能获取其他用户的信息'
                success = False
        except User.DoesNotExist:
            data = '用户不存在'
            success = False
        except Exception as e:
            data = str(e)
            success = False

        return JsonResponse(
            {'data': data, 'success': success, 'immutable': immutable, 'subordinate_user': subordinate_user})


def add_or_edit_user(request):
    """增加或者修改用户信息"""

    if request.method == "POST":
        raw_data = json.loads(request.body.decode('utf-8'))
        msg = 'ok'
        editFlag = raw_data.pop('editFlag')
        id = raw_data.pop('id')
        group = raw_data.pop('group')
        group_section = raw_data.pop('group_section')
        project_group = raw_data.pop('project_group')
        ldap_group = raw_data.pop('ldap_group')

        try:
            if group_section == "0":
                group_section = None
                group = Group.objects.get(id=group)
            else:
                group_section = GroupSection.objects.get(id=group_section)
                # 部门是部门分组所在的部门
                # 为了防止选错，造成的数据不一致
                group = group_section.group

            if project_group == '0':
                project_group = None
            else:
                project_group = ProjectGroup.objects.get(id=project_group)
            with transaction.atomic():
                if editFlag:
                    u = User.objects.filter(id=id)
                    # 编辑模式下，只能管理员帐号才能将用户类型设置为管理员
                    is_superuser = raw_data.get('is_superuser')
                    if request.user.is_superuser or is_superuser == '0':
                        u.update(**raw_data)
                        s = u[0]
                        s.groups.clear()
                        s.groups.add(group)
                        s.profile.project_group = None  # 全部都是None
                        # 添加唯一的分组属性
                        s.profile.one_group = group
                        s.profile.group_section = group_section
                        s.profile.save()
                        success = True
                    else:
                        msg = '不能修改为管理员帐号'
                        success = False
                else:
                    # 只有管理员才能添加用户
                    if request.user.is_superuser:

                        first_name = raw_data.get('first_name')
                        if User.objects.filter(first_name=first_name):
                            raise Exception('用户拼音: %s 已经存在' % (first_name))

                        u = User.objects.create(**raw_data)
                        u.set_password('redhat')  # 设置初始密码
                        u.save()
                        profile = Profile.objects.create(user=u)

                        # 添加部门和部门分组
                        profile.one_group = group
                        profile.group_section = group_section
                        profile.save()
                        u.groups.add(group)

                        # 添加LDAP账号
                        if ldap_group != '0':
                            ldap = LDAP()
                            password = gen_password(10)
                            gid = int(ldap_group)
                            uid = u.first_name
                            ldap.add_people_ou(uid, gid, userPassword=password)
                            ldap.add_group_ou(gid, uid)
                            ldap.unbind()

                            to_list = [u.email]
                            subject = '入职CMDB和wifi账号信息'
                            content = user_add_nofity(u.first_name, password)

                            send_mail.delay(to_list, subject, content)

                        success = True
                    else:
                        msg = '普通用户不能添加帐号'
                        success = False
        except ProjectGroup.DoesNotExist:
            msg = '游戏项目分组不存在'
            success = False
        except Group.DoesNotExist:
            msg = '分组不存在'
            success = False
        except IntegrityError:
            msg = '用户 %s 已经存在' % (raw_data.get('username'))
            success = False
        except Exception as e:
            msg = str(e)
            success = False
        return JsonResponse({'data': success, 'msg': msg})


def passwd_data_user(request):
    """修改用户密码

    管理员用户可以修改所有用户的密码

    普通用户只能修改自己的密码
    """
    if request.method == "POST":
        raw_data = json.loads(request.body.decode('utf-8'))
        msg = 'ok'
        id = raw_data.pop('id')

        try:
            passwd_user = User.objects.get(id=id)

            if request.user.is_superuser or request.user == passwd_user:
                password = raw_data.get('password')
                passwd_user.set_password(password)
                passwd_user.save()
                success = True

                # 修改自己的密码成功后logout当前用户，重新登录
                if request.user == passwd_user:
                    logout_required = True
                else:
                    logout_required = False
            else:
                msg = '不能修改其他帐号密码'
                success = False
                logout_required = False
        except User.DoesNotExist:
            msg = '用户不存在'
            success = False
        except Exception as e:
            msg = str(e)
            success = False
        return JsonResponse({'data': success, 'msg': msg, 'logout_required': logout_required})


def del_user(request):
    """删除用户

    只有管理员用户可以删除其他用户

    不能自己删除自己
    """

    if request.method == "POST":
        del_data = json.loads(request.body.decode('utf-8'))
        try:
            objs = User.objects.filter(id__in=del_data)

            # 只有管理员用户才能删除其他用户
            if request.user.is_superuser:

                # 不能删除自己
                if request.user not in objs:
                    with transaction.atomic():
                        objs.delete()
                        success = True
                        msg = 'ok'
                else:
                    msg = '不能删除自己'
                    success = False
            else:
                msg = '没有权限删除用户'
                success = False

        except Exception as e:
            msg = str(e)
            success = False
        return JsonResponse({'data': success, 'msg': msg})


def group_list(request):
    """分组列表页面"""

    head = {'value': '部门', 'username': request.user.username}
    data = {'upper_group_leader': is_group_leader(request.user) | request.user.is_superuser}
    print(is_group_leader(request.user) | request.user.is_superuser)

    return render(request, 'group_list.html', {'head': head, 'data': data})


def data_group_list(request):
    """分组的数据"""

    if request.method == "GET":
        raw_get = request.GET.dict()
        raw_data = []
        draw = raw_get.get('draw', 0)

        # 只有管理员用户才能查看所有的分组，和修改分组里面的用户
        if True:
            all_group = Group.objects.all()
            recordsTotal = len(all_group)

            for g in all_group:
                try:
                    group_leader = g.groupprofile.group_leader.username
                except Group.groupprofile.RelatedObjectDoesNotExist:
                    group_leader = ''

                name = g.name
                parent_name = g.groupprofile.parent_group.name if g.groupprofile.parent_group else ''

                is_public = '是' if g.groupprofile.is_public else '否'

                # 添加项目链接
                proj_link = '<a href="/assets/game_project_list/?project_name={}">{}</a>'
                raw_data.extend([
                    {
                        'id': g.id, 'name': name, 'parent_name': parent_name,
                        'group_leader': group_leader, 'is_public': is_public,
                        'company': g.groupprofile.to_root().company.name,
                        'projects': ','.join(
                            [
                                proj_link.format(x.project_name, x.project_name) for x in g.gameproject_set.all()
                            ]
                        ),
                    }
                ])

            data = {"data": raw_data, 'draw': draw, 'recordsTotal': recordsTotal, 'recordsFiltered': recordsTotal}

            return JsonResponse(data)


def list_group_leaf(request):
    """展示部门的叶子节点
    专为游戏项目设计
    """

    data = []

    get_leaf_nodes = GroupProfile.get_leaf_nodes()

    for node in get_leaf_nodes:
        id = node.group.id
        if node.parent_group is None:
            text = node.group.name
        else:
            text = node.parent_group.name + '-' + node.group.name
        data.append({'id': id, 'text': text})

    return JsonResponse(data, safe=False)


def list_ldap_groups(request):
    """下拉展示ldap部门列表
    """

    data = []

    q = request.POST.get('q', '')

    ldap_groups = {key: value for key, value in LDAP_GROUPS.items() if q in value}

    for key, value in ldap_groups.items():
        data.append({'id': key, 'text': value})

    return JsonResponse(data, safe=False)


def list_group_section(request):
    """展示部门管理分组
    """
    if request.method == "POST":
        data = []

        # 是否需要展示部门 例如研发一前端技术部-三生三世组
        # 默认为0， 代表不需要展示
        show_group = request.POST.get('show_group', '0')

        if show_group == '1':
            for section in GroupSection.objects.all():
                id = section.id
                text = section.group.name + '-' + section.name
                data.append({'id': id, 'text': text})
            return JsonResponse(data, safe=False)

        group = request.POST.get("group", None)

        if group is None:
            return JsonResponse(data, safe=False)

        try:
            group = Group.objects.get(id=group)
        except Group.DoesNotExist:
            return JsonResponse(data, safe=False)
        else:
            for section in GroupSection.objects.filter(group=group):
                data.append({'id': section.id, 'text': section.name})
            return JsonResponse(data, safe=False)


def list_group_section_all(request):
    """展示全部的部门分组
    研发一前端技术部-管理分组赵松杰
    """

    if request.method == "POST":
        data = []
        q = request.POST.get('q', '')
        for section in GroupSection.objects.filter(Q(group__name__contains=q) | Q(name__contains=q)):
            name = section.group.name + '-' + section.name
            data.append({'id': section.id, 'text': name})

        return JsonResponse(data, safe=False)


def list_department_group_all(request):
    """展示全部的部门分组
    研发一前端技术部-管理分组赵松杰
    """

    if request.method == "POST":
        data = []
        q = request.POST.get('q', '')
        """
        2018.12修改，使用新组织架构表构建分组
        """
        for department_group in OrganizationMptt.objects.filter(type=1, is_department_group=1). \
                filter(Q(name__contains=q) | Q(parent__name__contains=q)):
            name = department_group.parent.name + '-' + department_group.name
            data.append({'id': department_group.id, 'text': name})

        return JsonResponse(data, safe=False)


def get_group_org(request):
    """获取组织架构"""
    if request.method == "GET":
        return JsonResponse(GroupProfile.get_group_org(), safe=False)


def add_or_edit_group(request):
    """添加或者修改分组

    只有管理员帐号才能添加分组
    """

    if request.method == "POST":
        if request.user.is_superuser:
            raw_data = json.loads(request.body.decode('utf-8'))
            msg = 'ok'
            editFlag = raw_data.pop('editFlag')
            id = raw_data.pop('id')
            group_leader = raw_data.pop("group_leader")
            parent_group = raw_data.pop("parent_group")
            company = raw_data.pop('company')
            if parent_group == '0':
                parent_group = None
                # 一级部门需要选择公司
                company = CompanyCode.objects.get(id=company)
            else:
                parent_group = Group.objects.get(id=parent_group)
                company = None

            is_public = json.loads(raw_data.pop("is_public"))

            try:
                if editFlag:
                    obj = Group.objects.filter(id=id)
                    obj.update(**raw_data)
                    g = obj[0]
                    try:
                        gp = g.groupprofile
                    except Group.groupprofile.RelatedObjectDoesNotExist:
                        gp = GroupProfile.objects.create(group=g)
                    # 不能把父部门设置为自己
                    if parent_group and parent_group.id == g.id:
                        raise Exception('不能把父部门设置为自己')
                    gp.group_leader = User.objects.get(id=group_leader)
                    gp.is_public = is_public
                    gp.parent_group = parent_group
                    gp.company = company
                    gp.save()
                    success = True
                else:
                    g = Group.objects.create(**raw_data)
                    gp = GroupProfile.objects.create(group=g, parent_group=parent_group, company=company)
                    gp.group_leader = User.objects.get(id=group_leader)
                    gp.is_public = is_public
                    gp.save()
                    success = True
            except Exception as e:
                msg = str(e)
                success = False
            return JsonResponse({'data': success, 'msg': msg})


def get_data_group(request):
    """获取分组的信息

    只有管理员才能获取分组的信息
    """

    if request.method == "POST":
        if request.user.is_superuser:
            try:
                id = json.loads(request.body.decode('utf-8')).get('id')

                group_obj = Group.objects.get(id=id)
                parent_group_id = group_obj.groupprofile.parent_group.id if group_obj.groupprofile.parent_group else '0'
                parent_group_name = group_obj.groupprofile.parent_group.name if group_obj.groupprofile.parent_group else '无'

                company_id = group_obj.groupprofile.company.id if group_obj.groupprofile.company else '0'
                company_name = group_obj.groupprofile.company.name if group_obj.groupprofile.company else '选择公司'

                data = {
                    'id': group_obj.id,
                    'company_id': company_id,
                    'company_name': company_name,
                    'name': group_obj.name,
                    'group_leader_id': group_obj.groupprofile.group_leader.id,
                    'group_leader_name': group_obj.groupprofile.group_leader.username,
                    'parent_group_id': parent_group_id,
                    'parent_group_name': parent_group_name,
                    'is_public': group_obj.groupprofile.is_public,
                }

                success = True

            except Group.DoesNotExist:
                data = '部门不存在'
                success = False
            except Exception as e:
                data = str(e)
                success = False
            return JsonResponse({'data': data, 'success': success})


def del_group(request):
    """删除分组

    只有管理员才能执行该操作
    """

    if request.method == "POST":
        if request.user.is_superuser:
            try:
                del_data = json.loads(request.body.decode('utf-8'))
                objs = Group.objects.filter(id__in=del_data)
                with transaction.atomic():
                    objs.delete()
                    success = True
                    msg = 'ok'
            except Exception as e:
                msg = str(e)
                success = False
            return JsonResponse({'data': success, 'msg': msg})


def group_info(request):
    """分组下的所有用户页面

    只有管理员能看到改页面
    """

    if request.method == "GET":
        if True:
            try:
                group_id = request.GET.get('group_id')
                group = Group.objects.get(id=group_id)
                head = {'value': group.name, 'username': request.user.username}
                return render(request, 'group_info.html', {'head': head})
            except Group.DoesNotExist:
                raise Http404('分组没有找到')


def data_group_info(request):
    """分组用户数据

    只有管理员才能获取数据
    """

    if request.method == "POST":
        raw_get = request.POST.dict()
        raw_data = []
        draw = raw_get.get('draw', 0)
        group_id = raw_get.get('group_id')

        # 只有管理员能看到分组的用户数据
        if True:

            group = Group.objects.get(id=group_id)

            # all_user = group.user_set.all()

            all_user = User.objects.filter(is_active=1, profile__one_group=group)

            recordsTotal = len(all_user)

            for u in all_user:
                raw_data.extend([{'id': u.id, 'username': u.username}])

            data = {"data": raw_data, 'draw': draw, 'recordsTotal': recordsTotal, 'recordsFiltered': recordsTotal}

            return JsonResponse(data)


def group_section(request):
    """部门管理分组
    只有管理员或者部门负责人才能看到相应的数据
    """

    if request.method == "GET":
        id = request.GET.get('group_id', 0)
        try:
            group = Group.objects.get(id=id)
        except Group.DoesNotExist as e:
            raise e
        else:
            group_leader = group.groupprofile.group_leader
            if request.user.is_superuser or request.user.id == group_leader.id:
                head = {'value': group.name, 'username': request.user.username}
                return render(request, 'group_section.html', {"head": head})
            else:
                return render(request, '403.html')


def data_group_section(request):
    """部门分组页面数据
    """
    if request.method == "POST":
        raw_get = request.POST.dict()
        draw = raw_get.get('draw', 0)
        group_id = raw_get.get('group_id')

        try:
            group = Group.objects.get(id=group_id)
        except Group.DoesNotExist as e:
            raise e
        else:
            group_leader = group.groupprofile.group_leader
            if request.user.is_superuser or request.user.id == group_leader.id:
                group_section = GroupSection.objects.filter(group=group)
                recordsTotal = group_section.count()
                data = {
                    "data": [x.show_all() for x in group_section], 'draw': draw,
                    'recordsTotal': recordsTotal, 'recordsFiltered': recordsTotal
                }
            else:
                data = []
            return JsonResponse(data)


def add_or_edit_group_section(request):
    """添加或者修改部门管理分组

    只有管理员帐号才能添加分组
    部门负责人也可以
    """

    if request.method == "POST":
        raw_data = json.loads(request.body.decode('utf-8'))
        group_id = raw_data.pop("group_id")
        group = Group.objects.get(id=group_id)
        if request.user.is_superuser or request.user.id == group.groupprofile.group_leader.id:
            msg = 'ok'
            editFlag = raw_data.pop('editFlag')
            id = raw_data.pop('id')
            name = raw_data.pop("name")
            leader = raw_data.pop("leader")
            allocation = raw_data.pop("allocation", None)
            if allocation is None:
                allocation = []
            list_project_group = ProjectGroup.objects.filter(id__in=allocation)

            try:
                leader = User.objects.get(id=leader)
                if editFlag:
                    group_section = GroupSection.objects.get(id=id)
                    group_section.name = name
                    group_section.leader = leader
                    group_section.save()

                    # 先把和该部门分组的相关的项目分组设置为None
                    for progro in ProjectGroup.objects.filter(group_section=group_section):
                        progro.group_section = None
                        progro.save()

                    # 然后项目分组重新绑定部门分组
                    for progro in list_project_group:
                        progro.group_section = group_section
                        progro.save()

                    success = True
                else:
                    group_section = GroupSection.objects.create(group=group, name=name, leader=leader)

                    # 给项目组增加指定的部门分组
                    # 校花-前端组==> 研发一前端技术部-校花组
                    for progro in list_project_group:
                        progro.group_section = group_section
                        progro.save()
                    success = True
            except Exception as e:
                raise e
                msg = str(e)
                success = False
            return JsonResponse({'data': success, 'msg': msg})


def get_data_group_section(request):
    """获取分组的信息

    只有管理员才能获取分组的信息
    部门负责人也可以
    """

    if request.method == "POST":
        raw_data = json.loads(request.body.decode('utf-8'))
        id = raw_data.get('id')
        try:
            group_section = GroupSection.objects.get(id=id)
            group = group_section.group
        except Exception as e:
            raise e
        if request.user.is_superuser or request.user.id == group.groupprofile.group_leader.id:
            try:
                data = group_section.edit_data()

                success = True

            except Group.DoesNotExist:
                data = '部门不存在'
                success = False
            except Exception as e:
                data = str(e)
                success = False
            return JsonResponse({'data': data, 'success': success})


def del_group_section(request):
    """删除管理分组

    只有管理员才能执行该操作
    部门负责人也可以
    """

    if request.method == "POST":
        del_data = json.loads(request.body.decode('utf-8'))
        objs = GroupSection.objects.filter(id__in=del_data)
        if request.user.is_superuser or request.user.id == objs[0].group.groupprofile.group_leader.id:
            try:
                with transaction.atomic():
                    objs.delete()
                    success = True
                    msg = 'ok'
            except Exception as e:
                msg = str(e)
                success = False
            return JsonResponse({'data': success, 'msg': msg})
        else:
            msg = '权限拒绝'
            success = False
            return JsonResponse({'data': success, 'msg': msg})


def add_group_user(request):
    """给分组添加用户

    管理员才能执行此操作
    """

    if request.method == "POST":

        if request.user.is_superuser:
            raw_data = json.loads(request.body.decode('utf-8'))
            msg = 'ok'

            try:
                group = Group.objects.get(id=raw_data.get('group_id'))
                list_user = User.objects.filter(id__in=raw_data.get('listUserId'))
                group.user_set.add(*list_user)
                success = True
            except Group.DoesNotExist:
                msg = '分组不存在'
                success = False
            except Exception as e:
                msg = str(e)
                success = False
            return JsonResponse({'data': success, 'msg': msg})


def del_group_user(request):
    """删除分组用户

    管理员才能执行此操作
    """

    if request.method == "POST":
        if request.user.is_superuser:
            try:
                del_data = json.loads(request.body.decode('utf-8'))
                group = Group.objects.get(id=del_data.get('group_id'))
                list_user_obj = User.objects.filter(id__in=del_data.get('listUserId'))
                group.user_set.remove(*list_user_obj)
                success = True
                msg = 'ok'
            except Exception as e:
                msg = str(e)
                success = False
            return JsonResponse({'data': success, 'msg': msg})


def group_permission(request):
    """分组权限

    只有管理员才能给分组赋予权限
    """

    if request.user.is_superuser:
        head = {"value": '分组和权限', 'username': request.user.username}
        return render(request, 'group_permission.html', {"head": head})
    else:
        return render(request, '403.html', {"head": {'username': request.user.username}})


def get_group_permission(request):
    """根据group id来获取相应的权限

    只有管理员才能执行此操作
    """
    if request.method == "POST":
        if request.user.is_superuser:
            pdata = json.loads(request.body.decode('utf-8'))
            group = Group.objects.get(id=pdata.get('group_id'))
            listGroupPermCodeName = [p.codename for p in group.permissions.all()]

            return JsonResponse(listGroupPermCodeName, safe=False)


def get_org_section_permission(request):
    """根据org_id来获取相应的权限

    只有管理员才能执行此操作
    """
    if request.method == "POST":
        if request.user.is_superuser:
            pdata = json.loads(request.body.decode('utf-8'))
            org = OrganizationMptt.objects.get(id=pdata.get('org_id'))
            listGroupPermCodeName = [p.codename for p in org.permission.all()]
            return JsonResponse(listGroupPermCodeName, safe=False)


def save_group_permission(request):
    """保存分组和权限

    只有管理员才能执行此操作
    """
    if request.method == "POST":
        msg = 'ok'
        add_data = json.loads(request.body.decode('utf-8'))
        listPermObj = []
        if request.user.is_superuser:
            try:
                group = Group.objects.get(id=add_data.get('group_id'))
                listPermNames = add_data.get('listChecked')
                # Add permission objs
                for n in listPermNames:
                    try:
                        p = Permission.objects.get(codename=n)
                        listPermObj.append(p)
                    except Permission.DoesNotExist:
                        msg = '权限名称{codename}不存在'.format(codename=n)
                        success = False
                        return JsonResponse({'data': success, 'msg': msg})

                # clear the current permission
                group.permissions.clear()

                # add new permisssions
                group.permissions.add(*listPermObj)

                success = True

            except Group.DoesNotExist:
                msg = '分组不存在'
                success = False
            except Exception as e:
                msg = str(e)
                success = False
            return JsonResponse({'data': success, 'msg': msg})


def user_permission(request):
    """用户权限

    只有管理员才能给分组赋予权限
    """
    if request.user.is_superuser:
        head = {"value": '用户权限管理', 'username': request.user.username}
        return render(request, 'user_permission.html', {"head": head})
    else:
        return render(request, '403.html', {"head": {'username': request.user.username}})


def api_permission(request):
    """API权限控制
    """
    if request.user.is_superuser:
        head = {"value": 'API权限控制', 'username': request.user.username}
        return render(request, 'api_permission.html', {"head": head})
    else:
        return render(request, '403.html', {"head": {'username': request.user.username}})


def get_user_permission(request):
    """根据user id来获取相应的权限

    只有管理员才能执行此操作
    """
    if request.method == "POST":
        if request.user.is_superuser:
            pdata = json.loads(request.body.decode('utf-8'))
            api_type = pdata.get('type', None)
            user = User.objects.get(id=pdata.get('user_id'))
            if api_type is not None:
                if api_type == 'api':
                    listUserPermCodeName = [p.codename for p in user.user_permissions.all() if
                                            p.codename.startswith('api')]
            else:
                listUserPermCodeName = [p.codename for p in user.user_permissions.all()]

            return JsonResponse(listUserPermCodeName, safe=False)


def save_user_permission(request):
    """保存用户和权限

    只有管理员才能执行此操作
    """
    if request.method == "POST":
        msg = 'ok'
        add_data = json.loads(request.body.decode('utf-8'))
        listPermObj = []
        if request.user.is_superuser:
            try:
                user = User.objects.get(id=add_data.get('user_id'))
                listPermNames = add_data.get('listChecked')
                # Add permission objs
                for n in listPermNames:
                    try:
                        p = Permission.objects.get(codename=n)
                        listPermObj.append(p)
                    except Permission.DoesNotExist:
                        msg = '权限名称{codename}不存在'.format(codename=n)
                        success = False
                        return JsonResponse({'data': success, 'msg': msg})

                old_permission = [x.codename for x in user.user_permissions.all()]

                # clear the current permission
                user.user_permissions.clear()

                # add new permisssions
                user.user_permissions.add(*listPermObj)

                new_permission = [x.codename for x in user.user_permissions.all()]

                # 记录权限修改日志
                delete_list = []
                for p in old_permission:
                    if p not in new_permission:
                        delete_list.append(p)
                add_list = []
                for p in new_permission:
                    if p not in old_permission:
                        add_list.append(p)
                change_content = ''
                if delete_list:
                    change_content = change_content + '删除权限：' + ','.join([x for x in delete_list]) + '     '
                if add_list:
                    change_content = change_content + '增加权限：' + ','.join([x for x in add_list])
                record = PermissionChangeRecord(operation_user=request.user, object=2, change_user=user.username,
                                                change_content=change_content)
                record.save()

                success = True

            except User.DoesNotExist:
                msg = '用户不存在'
                success = False
            except Exception as e:
                msg = str(e)
                success = False
            return JsonResponse({'data': success, 'msg': msg})


def clean(request):
    """清除用户页面

    只有管理员才有权限清除
    """
    if request.user.is_superuser:
        id = request.GET.get('id')
        u = User.objects.get(id=int(id))
        # if u.is_active:
        #     return HttpResponse('当前用户不是离职状态,不能清除')
        if request.user == u:
            return HttpResponse('不能清除自己')
        else:
            head = {"value": '清除用户' + '-' + u.username, 'username': request.user.username}
            projects = GameProject.objects.filter(status=1)
            try:
                ucs = UserClearStatus.objects.get(profile=u.profile)
                data = ucs.show_process_info()
                # 默认清除选项
                clean_option = get_user_clean_failed_option(ucs)
            except UserClearStatus.DoesNotExist:
                data = ''
                # 默认清除选项
                clean_option = get_user_clean_failed_option()
            return render(request, 'clean_user.html', {"head": head, "data": data, "projects": projects,
                                                       'clean_option': clean_option})
    else:
        return render(request, '403.html', {"head": {'username': request.user.username}})


def do_clean(request):
    """执行清除用户
    """

    if request.method == "POST":
        raw_data = json.loads(request.body.decode('utf-8'))
        id = raw_data.get('id')
        list_clean_type = raw_data.get('listChecked')
        remark = ''

        user = User.objects.get(id=id)
        ucs, _ = UserClearStatus.objects.get_or_create(profile=user.profile)

        for clean_type in list_clean_type:
            if clean_type == 'clean_server':
                remark += '清理服务器权限,'
                server_clean_type = raw_data.get('server_clean_type', 'all')
                if server_clean_type == 'section':
                    server_projects = raw_data.get('server_projects', [])
                    projects = GameProject.objects.filter(id__in=server_projects)
                    list_ops_manager, default_ip_list, use_default = get_all_ops_manager(projects=projects)
                    # 设置权限记录为失效
                    UserProfileHost.objects.filter(user_profile=user.profile,
                                                   host__belongs_to_game_project__in=projects).update(**{"is_valid": 0})
                else:
                    list_ops_manager, default_ip_list, use_default = get_all_ops_manager()
                    # 设置权限记录为失效
                    UserProfileHost.objects.filter(user_profile=user.profile).update(**{"is_valid": 0})
                clean_server(list_ops_manager, default_ip_list, use_default, user, ucs)
                ws_notify_clean_user(user.id)
            if clean_type == 'clean_svn':
                remark += '清理SVN,'
                svn_clean_type = raw_data.get('svn_clean_type', 'all')
                if svn_clean_type == 'section':
                    ucs.svn = ''
                    ucs.save(update_fields=['svn'])
                    svn_projects = raw_data.get('svn_projects', [])
                    projects = GameProject.objects.filter(id__in=svn_projects)
                    for project in projects:
                        clean_svn(user, ucs, project=project)
                else:
                    clean_svn(user, ucs)
                ws_notify_clean_user(user.id)
            # if clean_type == 'clean_svn2':
            #     clean_svn2(user, ucs)
            #     ws_notify_clean_user(user.id)
            if clean_type == 'clean_samba':
                remark += '清理samba,'
                clean_samba(user, ucs)
                ws_notify_clean_user(user.id)
            if clean_type == 'clean_mysql':
                remark += '清理mysql,'
                remove_mysql_permission.delay(user.first_name)
                # ws_notify_clean_user(user.id)
            if clean_type == 'clean_mysql_force':
                remark += '强制清理mysql,'
                remove_mysql_permission.delay(user.first_name, force=True)
            if clean_type == 'clean_ldap':
                remark += '清理ldap,'
                clean_ldap(user, ucs)
                ws_notify_clean_user(user.id)
            if clean_type == 'delete_ent_qq':
                remark += '清理企业qq,'
                delete_ent_qq(user, ucs)
                ws_notify_clean_user(user.id)
            if clean_type == 'delete_ent_email':
                for email in user.email.split(','):
                    remark += '清理企业邮箱' + email + ','
                    delete_ent_email(email, ucs)
                    ws_notify_clean_user(user.id)
            if clean_type == 'delete_user_wifi':
                remark += '清理wifi,'
                delete_user_wifi(user, ucs)
                ws_notify_clean_user(user.id)
            if clean_type == 'delete_openvpn_user':
                remark += '清理openvpn,'
                delete_user_for_openvpn(user, ucs)
                ws_notify_clean_user(user.id)
        """记录操作日志"""
        UserChangeRecord.objects.create(create_user=request.user, change_obj=user.username, type=4, remark=remark)
        return JsonResponse({"success": True, "result": "ok"})


def get_not_active_user(request):
    """离职人员API文档
    """
    if request.method == "GET":
        if request.user.is_superuser:
            return render(request, 'get_not_active_user.html')
        else:
            return render(request, '403.html')


def user_profile(request):
    """用户设置
    """
    if request.method == "GET":
        head = {'value': '用户设置', 'username': request.user.username}
        hot_update_email_approve = request.user.profile.hot_update_email_approve
        wechat_approve = request.user.organizationmptt_set.first().wechat_approve
        account = request.user.first_name
        email = request.user.email.split(',')
        email_count = len(list(email))
        svn_projects = get_user_svn_project(request.user)
        svn_change_passwd = False
        if svn_projects:
            svn_change_passwd = True
        return render(request, 'user_profile.html',
                      {'head': head, 'hot_update_email_approve': hot_update_email_approve,
                       'account': account, 'svn_change_passwd': svn_change_passwd, 'email': email,
                       'email_count': email_count, 'wechat_approve': wechat_approve})


def set_email_approve(request):
    """开启邮件审批的功能
    """
    if request.method == "POST":
        try:
            raw_data = json.loads(request.body.decode('utf-8'))
            hot_update_email_approve = raw_data.get('hot_update_email_approve')
            profile = request.user.profile
            org_user_obj = OrganizationMptt.objects.get(user=request.user)
            profile.hot_update_email_approve = hot_update_email_approve
            org_user_obj.hot_update_email_approve = hot_update_email_approve
            org_user_obj.save()
            profile.save()
            msg = ''
            success = True
        except Exception as e:
            msg = str(e)
            success = False
        return JsonResponse({'data': success, 'msg': msg})


def set_wechat_approve(request):
    """开启微信审批的功能
    """
    if request.method == "POST":
        try:
            raw_data = json.loads(request.body.decode('utf-8'))
            wechat_approve = raw_data.get('wechat_approve')
            org_user_obj = OrganizationMptt.objects.get(user=request.user)
            org_user_obj.wechat_approve = wechat_approve
            org_user_obj.save()
            msg = ''
            success = True
        except Exception as e:
            msg = str(e)
            success = False
        return JsonResponse({'data': success, 'msg': msg})


def group_users_api(request):
    """部门用户api文档
    """
    if request.method == "GET":
        if request.user.is_superuser:
            return render(request, 'group_users_api_doc.html')
        else:
            return render(request, '403.html')


def user_svn_serper_projects(request):
    """获取用户的svn和服务器权限的项目
    """
    if request.method == "POST":
        user_id = json.loads(request.body.decode('utf-8')).get('user')
        user = User.objects.get(id=user_id)
        data = {'success': True}

        serper_projects = get_user_serper_project(user)
        serper_projects_obj = GameProject.objects.filter(id__in=serper_projects)
        data['serper_projects'] = [{'id': x.id, 'text': x.project_name} for x in serper_projects_obj]

        svn_projects = get_user_svn_project(user)
        if svn_projects is None:
            data['success'] = False
        else:
            svn_projects_obj = GameProject.objects.filter(id__in=svn_projects)
            data['svn_projects'] = [{'id': x.id, 'text': x.project_name} for x in svn_projects_obj]
        return JsonResponse(data)


class UserDesertView(generic.View):
    """用户离职类"""

    def get(self, request, user_id):
        if request.user.is_superuser:
            username = User.objects.get(pk=user_id)
            user_assets = Assets.objects.filter(user=username)
            position = Position.objects.all()
            warehousing_region = AssetsWarehousingRegion.objects.all()
            org = OrganizationMptt.objects.filter(user_id=user_id)
            if org:
                org_id = org[0].id
                return render(request, 'user_desert.html',
                              {'user_assets': user_assets, 'user_id': user_id, 'position': position,
                               'username': username, 'org_id': org_id, 'warehousing_region': warehousing_region})
        else:
            return render(request, '403.html')

    def post(self, request, user_id):
        if 'assets_recover' in request.POST:
            user = User.objects.get(pk=user_id)
            if request.user == user:
                return HttpResponseRedirect('/users/clean/?id=' + str(user.id))
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
            recover_list = []
            position_list = []
            warehousing_region_list = []
            for key in request.POST:
                if key[0:5] == 'check' and key != 'checkAll':
                    recover_list.append(request.POST[key])
            for key in request.POST:
                if key == 'recover_position':
                    position_list = request.POST.getlist(key)
            for key in request.POST:
                if key == 'recover_warehousing_region':
                    warehousing_region_list = request.POST.getlist(key)
            for assets_id in recover_list:
                assets = Assets.objects.get(pk=assets_id)
                pre_user = assets.auth_user.username
                assets.status = 0
                for position_id in position_list:
                    t = position_id.split('-')
                    if t[0] == str(assets_id):
                        assets.pos_id = t[1]
                for warehousing_region_id in warehousing_region_list:
                    t = warehousing_region_id.split('-')
                    if t[0] == str(assets_id):
                        assets.warehousing_region_id = t[1]
                assets.user = request.user.username
                assets.auth_user = request.user
                organization = OrganizationMptt.objects.get(user=request.user)
                assets.using_department = organization.get_ancestors_except_self()
                assets.belongs_to_new_organization = organization.get_ancestors_except_self()
                assets.save()
                """写入资产变更记录"""
                log_assets = LogAssets(event=4, etime=datetime.now(), log_user=request.user.username,
                                       user=request.user.username, number=1, assets_id=assets_id, pos_id=assets.pos_id,
                                       purchase=0, pre_user=pre_user)
                log_assets.save()
            return HttpResponseRedirect('/users/clean/?id=' + str(user.id))
        if 'assets_print' in request.POST:
            assets_obj_list = []
            for key in request.POST:
                if key[0:5] == 'check':
                    assets_obj_list.append(Assets.objects.get(pk=int(request.POST[key])))
            return render(request, 'it_assets_application_form.html', {'assets_obj_list': assets_obj_list})


def create_recover_assets_list(request):
    recover_list = []
    for key in request.POST:
        if key[0:5] == 'check':
            recover_list.append(request.POST[key])
    return HttpResponse(json.dumps({'recover_list': recover_list}), content_type='application/json')


class OrganizationView(generic.View):
    def get(self, request):
        """
        获取组织架构树状态图
        """
        org_mptt = OrganizationMptt.objects.all()
        return render(request, 'users_organization.html', {'org_mptt': org_mptt})

    def post(self, request):
        """
        增加组织架构节点
        from users.models import OrganizationMptt
        rock = OrganizationMptt.objects.create(name="Rock")
        blues = OrganizationMptt.objects.create(name="Blues")
        OrganizationMptt.objects.create(name="Hard Rock", parent=rock)
        OrganizationMptt.objects.create(name="Pop Rock", parent=rock)
        """
        name = request.POST['name']
        parent = request.POST['parent']
        leader = request.POST['leader']
        is_public = request.POST['is_public']
        is_department_group = request.POST['is_department_group']
        if parent != "0":
            parent_obj = OrganizationMptt.objects.get(id=parent)
            org = OrganizationMptt.objects.create(name=name, parent=parent_obj, is_public=is_public, leader=leader,
                                                  type=1,
                                                  is_department_group=is_department_group)
        else:
            org = OrganizationMptt.objects.create(name=name, is_public=is_public, leader=leader, type=1,
                                                  is_department_group=is_department_group)
        """记录操作日志"""
        UserChangeRecord.objects.create(create_user=request.user, change_obj=org.name, type=1)

        return HttpResponseRedirect(reverse('organization'))


def organization_tree(request):
    if request.method == 'POST':
        tree = get_organization_tree()
        return JsonResponse({'tree': tree})


def list_new_organization(request):
    """下拉展示组织架构节点"""
    if request.method == "POST":
        data = []
        # 查询参数
        q = request.POST.get('q', None)
        if not q:
            q = ''
        all_organization = OrganizationMptt.objects.filter(Q(name__icontains=q) |
                                                           Q(parent__name__icontains=q) |
                                                           Q(parent__parent__name__icontains=q) |
                                                           Q(parent__parent__parent__name__icontains=q)).filter(type=1)
        for x in all_organization:
            data.append({'id': x.id, 'text': x.get_ancestors_name()})
        return JsonResponse(data, safe=False)


class OrganizationEditView(generic.View):
    """组织节点编辑类"""

    def get(self, request, org_id):
        """获取组织架构编辑页面"""
        org = OrganizationMptt.objects.get(pk=org_id)
        if org.type == 1:
            if request.user.is_superuser:
                return render(request, 'users_organization_iframe_section_edit.html', {'org': org})
            else:
                return render(request, '403_without_nav.html')
        if org.type == 2:
            if request.user.has_perm('users.view_user_info'):
                user = User.objects.get(pk=org.user_id)
                email = user.email.split(',')
                share_info = make_new_user_info_share_content(org.id)
                return render(request, 'users_organization_iframe_user_edit.html',
                              {'org': org, 'user': user, 'email': email, 'share_info': share_info})
            else:
                return render(request, '403_without_nav.html')

    def post(self, request, org_id):
        """编辑节点或用户"""
        org_obj = OrganizationMptt.objects.get(pk=org_id)
        remark = ''
        """记录修改前的对象"""
        org_obj_old = deepcopy(org_obj)
        if request.user.is_superuser:
            if 'org_save' in request.POST:
                """修改部门节点"""
                name = request.POST['name']
                leader = request.POST['leader']
                is_public = request.POST['is_public']
                if is_public == "True":
                    is_public = True
                if is_public == "False":
                    is_public = False
                is_department_group = request.POST['is_department_group']
                if is_department_group == "True":
                    is_department_group = True
                if is_department_group == "False":
                    is_department_group = False
                parent_id = request.POST['parent']
                org_obj.name = name
                org_obj.leader = int(leader)
                org_obj.is_public = is_public
                org_obj.is_department_group = is_department_group
                pre_ancestors = org_obj.get_ancestors_name()
                if parent_id != 'None':
                    parent_obj = OrganizationMptt.objects.get(pk=parent_id)
                    org_obj.move_to(parent_obj)
                org_obj.save()
                new_ancestors = org_obj.get_ancestors_name()
                """
                如果部门节点所在的组织架构发生改变，则对应资产的使用部门也要相应改变；
                using_department和belongs_to_new_organization两个字段只是为了优化检索速度，实际并不通过这两个字段与用户关联
                """
                if new_ancestors != pre_ancestors:
                    for assets in Assets.objects.select_related('auth_user').filter(
                            belongs_to_new_organization__icontains=pre_ancestors):
                        belongs_to_new_organization = assets.get_ancestor()
                        assets.using_department = belongs_to_new_organization
                        assets.belongs_to_new_organization = belongs_to_new_organization
                        assets.save(update_fields=['using_department', 'belongs_to_new_organization'])
                """记录修改后的对象"""
                org_obj_new = deepcopy(org_obj)
                """对比修改字段"""
                org_fields = ['name', 'parent', 'leader', 'is_department_group', 'is_public']
                remark = compare_fields_with_objects(org_obj_old, org_obj_new, org_fields)
                """如果有修改内容，则记录变更日志"""
                if remark != '':
                    UserChangeRecord.objects.create(create_user=request.user, change_obj=org_obj.name, type=2,
                                                    remark=remark)

                return HttpResponseRedirect(reverse('org_edit_href'))
            if 'org_user_save' in request.POST:
                """修改用户节点"""
                user_id = request.POST['user_id']
                username = request.POST['edit_username']
                first_name = request.POST['first_name']
                email = request.POST['email']
                is_superuser = request.POST['is_superuser']
                is_staff = False
                if int(is_superuser) == 1:
                    is_superuser = True
                    is_staff = True
                if int(is_superuser) == 0:
                    is_superuser = False
                    is_staff = False
                is_active = request.POST['is_active']
                if int(is_active) == 1:
                    is_active = True
                if int(is_active) == 0:
                    is_active = False
                is_register = request.POST['is_register']
                if int(is_register) == 1:
                    is_register = True
                if int(is_register) == 0:
                    is_register = False
                password = request.POST.get('edit_password', None)
                ancestors_id = request.POST['ancestors-user-edit']
                sex = request.POST['sex']
                title = request.POST['title']
                ent_qq = request.POST['ent_qq']
                if not ent_qq:
                    ent_qq = None
                ent_email = request.POST['ent_email']
                if not ent_email:
                    ent_email = None
                """修改用户相关信息"""
                user_obj = User.objects.get(pk=user_id)
                """先记录修改前的对象，再修改用户对象"""
                user_obj_old = deepcopy(user_obj)
                user_obj.username = username
                user_obj.first_name = first_name
                user_obj.email = email
                user_obj.is_superuser = is_superuser
                user_obj.is_staff = is_staff
                user_obj.is_active = is_active
                if password:
                    user_obj.set_password(password)
                user_obj.save()
                """同步更新旧的用户扩展表，以免数据不一致"""
                if Profile.objects.filter(user_id=user_id):
                    profile = Profile.objects.get(user_id=user_id)
                    profile.status = is_active
                    profile.save()
                org_obj.name = username
                org_obj.is_active = is_active
                org_obj.is_register = is_register
                org_obj.sex = sex
                org_obj.title = title
                org_obj.ent_qq = ent_qq
                org_obj.ent_email = ent_email
                org_obj.save()
                """修改用户所属部门节点"""
                parent_obj = OrganizationMptt.objects.get(id=ancestors_id)
                pre_parent_obj = org_obj.parent
                org_obj.move_to(parent_obj)
                org_obj.save()
                """修改用户所拥有资产表Assets中使用部门"""
                if pre_parent_obj != org_obj.parent:
                    belongs_to_new_organization = org_obj.get_ancestors_except_self()
                    for assets in Assets.objects.filter(auth_user_id=org_obj.user_id):
                        assets.belongs_to_new_organization = belongs_to_new_organization
                        assets.save()
                """记录修改后的对象"""
                user_obj_new = deepcopy(user_obj)
                org_obj_new = deepcopy(org_obj)
                """定义需要比较字段"""
                user_fields = ['username', 'first_name', 'email', 'password', 'is_superuser']
                org_fields = ['title', 'parent', 'is_active', 'ent_qq', 'ent_email', 'is_register']
                user_diff = compare_fields_with_objects(user_obj_old, user_obj_new, user_fields)
                obj_diff = compare_fields_with_objects(org_obj_old, org_obj_new, org_fields)
                remark = user_diff + obj_diff
                """如果有修改内容，则记录变更日志"""
                if remark != '':
                    UserChangeRecord.objects.create(create_user=request.user, change_obj=org_obj.name, type=2,
                                                    remark=remark)
                """如果状态为离职，需要从以下表中删除：
                运维角色分组
                工单流程-特殊人员配置
                工单流程-流程审批人设置
                """
                if not is_active:
                    """角色分组"""
                    for r in Role.objects.prefetch_related('user').all():
                        r.user.remove(user_obj)
                    """工单流程-特殊人员配置"""
                    for s in SpecialUserParamConfig.objects.prefetch_related('user').all():
                        s.user.remove(user_obj)
                    """工单流程-流程审批人设置"""
                    for s in State.objects.prefetch_related('specified_users').all():
                        s.specified_users.remove(user_obj)

                return HttpResponseRedirect(reverse('org_edit_href'))
        else:
            return render(request, '403.html')


def organization_delete(request, org_id):
    """组织架构节点或者用户删除"""
    try:
        org_obj = get_object_or_404(OrganizationMptt, pk=org_id)
        name = org_obj.name
        if org_obj.type == 1:
            if org_obj.project.all():
                raise Exception('该部门有负责的项目，请先修改其项目的关联部门')
            for child in org_obj.get_all_children_obj_list():
                if child.type == 2:
                    raise Exception('该部门下还有用户，请先将用户移到其他部门或小组')
            org_obj.delete()
        if org_obj.type == 2:
            try:
                user_profile = Profile.objects.get(user_id=org_obj.user_id)
            except:
                pass
            else:
                user_profile.delete()
            try:
                user = User.objects.get(pk=org_obj.user_id)
            except:
                pass
            else:
                user.delete()
            org_obj.delete()
        """记录操作日志"""
        UserChangeRecord.objects.create(create_user=request.user, change_obj=name, type=3)
        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"success": False, 'msg': str(e)})


def organization_user_add(request):
    """新组织架构页面新增用户"""
    try:
        if request.user.is_superuser:
            raw_data = json.loads(request.body.decode('utf-8'))
            msg = 'ok'
            remark = ''
            username = raw_data.pop('username')
            username = username.strip()
            first_name = raw_data.pop('first_name')
            first_name = first_name.strip()
            if User.objects.filter(first_name=first_name) or User.objects.filter(username=username):
                raise IntegrityError
            email = raw_data.get('email', '')
            org = raw_data.pop('org')
            is_superuser = raw_data.pop('is_superuser')
            is_open_ldap = raw_data.pop('is_open_ldap')
            sex = raw_data.pop('sex')
            title = raw_data.pop('title')
            is_open_qq = raw_data.pop('is_open_qq')
            is_open_email = raw_data.pop('is_open_email')
            ent_email = raw_data.get('ent_email', '')
            user = User.objects.create(username=username, first_name=first_name, email=email, is_superuser=is_superuser)
            user_id = user.id
            user.set_password('redhat')
            user.save()
            Profile.objects.create(user_id=user.id, status=1)
            parent = OrganizationMptt.objects.get(pk=org)
            org = OrganizationMptt.objects.create(name=username, hot_update_email_approve=0, user_id=user_id, type=2,
                                                  parent=parent, is_active=1, sex=sex, title=title)
            organization_char = org.get_ancestors_except_self_by_slash()

            # 添加企业QQ帐号
            if is_open_qq == '1':
                remark += '开通企业QQ,'
                add_qq_user.delay(first_name, username, sex, organization_char, title, org.id)

            # 添加企业邮箱
            if is_open_email == '1':
                for x in ent_email:
                    if x == '1':
                        remark += '开通forcegames企业邮箱,'
                        add_email_account.delay(first_name + '@forcegames.cn', username, sex, organization_char, title,
                                                org.id)
                    if x == '2':
                        remark += '开通chuangyunet企业邮箱,'
                        add_email_account.delay(first_name + '@chuangyunet.com', username, sex, organization_char,
                                                title, org.id)
                if '1' in ent_email:
                    user.email = first_name + '@forcegames.cn'
                    user.save()
                if '2' in ent_email:
                    user.email = first_name + '@chuangyunet.com'
                    user.save()
                if '1' in ent_email and '2' in ent_email:
                    user.email = first_name + '@chuangyunet.com' + ',' + first_name + '@forcegames.cn'
                    user.save()

            # 添加LDAP账号
            if is_open_ldap == '1':
                remark += '开通LDAP,'
                ldap = LDAP()
                password = gen_password(10)
                gid = int('20000000')
                uid = user.first_name
                ldap.add_people_ou(uid, gid, userPassword=password)
                ldap.add_group_ou(gid, uid)
                ldap.unbind()

                to_list = [user.email]
                subject = '入职CMDB和wifi账号信息'
                content = user_add_nofity(user.first_name, password)

                send_mail.delay(to_list, subject, content, 10)

            success = True
            """记录操作日志"""
            UserChangeRecord.objects.create(create_user=request.user, change_obj=org.name, type=1, remark=remark)
        else:
            msg = '普通用户不能添加帐号'
            success = False
    except IntegrityError:
        msg = '该用户已存在'
        success = False
    except Exception as e:
        msg = str(e)
        success = False
    return JsonResponse({'data': success, 'msg': msg})


def organization_section_add(request):
    """新组织架构页面新增部门"""
    try:
        msg = 'ok'
        if request.user.is_superuser:
            raw_data = json.loads(request.body.decode('utf-8'))
            parent = raw_data.pop('parent')
            raw_data['type'] = 1
            if parent != "0":
                parent_obj = OrganizationMptt.objects.get(id=parent)
                raw_data['parent'] = parent_obj
                org = OrganizationMptt.objects.create(**raw_data)
            else:
                org = OrganizationMptt.objects.create(**raw_data)
            """记录操作日志"""
            UserChangeRecord.objects.create(create_user=request.user, change_obj=org.name, type=1)
            success = True
        else:
            msg = '普通用户不能添加帐号'
            success = False
    except IntegrityError:
        msg = '该用户已存在'
        success = False
    except Exception as e:
        msg = str(e)
        success = False
    return JsonResponse({'data': success, 'msg': msg})


class NewDepartmentPermView(generic.View):
    """新部门权限设置页面"""

    def get(self, request):
        if request.user.is_superuser:
            all_sections = OrganizationMptt.objects.filter(type=1, is_active=1).exclude(name='离职接收部')
            return render(request, 'new_department_permission.html', {'all_sections': all_sections})
        else:
            return render(request, '403.html')

    def post(self, request):
        if request.user.is_superuser:
            msg = 'ok'
            add_data = json.loads(request.body.decode('utf-8'))
            listPermObj = []
            if request.user.is_superuser:
                try:
                    org_obj = OrganizationMptt.objects.get(id=add_data.get('org_id'))
                    listPermNames = add_data.get('checked_list')
                    # Add permission objs
                    for n in listPermNames:
                        try:
                            p = Permission.objects.get(codename=n)
                            listPermObj.append(p)
                        except Permission.DoesNotExist:
                            msg = '权限名称{codename}不存在'.format(codename=n)
                            success = False
                            return JsonResponse({'data': success, 'msg': msg})

                    old_permission = [x.codename for x in org_obj.permission.all()]
                    user_obj_list = org_obj.get_all_children_user_obj_list()

                    # clear user permission
                    # clear org and children section permission relation
                    org_obj.permission.clear()
                    for user in user_obj_list:
                        user.user_permissions.clear()
                    for child in org_obj.get_all_children_section_obj_list():
                        child.permission.clear()

                    # add user permission
                    for user in user_obj_list:
                        user.user_permissions.add(*listPermObj)

                    # add org and its children section permission relation
                    org_obj.permission.add(*listPermObj)
                    for child in org_obj.get_all_children_section_obj_list():
                        child.permission.add(*listPermObj)

                    new_permission = [x.codename for x in org_obj.permission.all()]

                    # 记录操作记录
                    delete_list = []
                    for p in old_permission:
                        if p not in new_permission:
                            delete_list.append(p)
                    add_list = []
                    for p in new_permission:
                        if p not in old_permission:
                            add_list.append(p)
                    change_content = ''
                    if delete_list:
                        change_content = change_content + '删除权限：' + ','.join([x for x in delete_list]) + '     '
                    if add_list:
                        change_content = change_content + '增加权限：' + ','.join([x for x in add_list])

                    PermissionChangeRecord.objects.create(operation_user=request.user, object=1,
                                                          change_department=org_obj, change_content=change_content)

                    success = True

                except Group.DoesNotExist:
                    msg = '分组不存在'
                    success = False
                except Exception as e:
                    msg = str(e)
                    success = False
                return JsonResponse({'data': success, 'msg': msg})
        else:
            return render(request, '403.html')


def permission_change_record(request):
    """权限修改记录"""
    if request.user.is_superuser:
        all_record = PermissionChangeRecord.objects.order_by('-id')[0:100]
        return render(request, 'permission_change_record_list.html', {'all_record': all_record})
    else:
        return render(request, '403.html')


def edit_ent_qq(request):
    """编辑企业QQ信息"""
    data = json.loads(request.body.decode('utf-8'))
    account = data.get('account', '')
    name = data.get('name', '')
    sex = data.get('sex', '')
    title = data.get('title', '')
    password = data.get('password', '')
    if name == '' and sex == '' and title == '' and password == '':
        return JsonResponse({'data': False, 'msg': '你什么都没输入哦！'})
    postdata = {}
    postdata['account'] = account
    if name != '':
        postdata['name'] = name
    if title != '':
        postdata['title'] = title
    if sex != '':
        postdata['gender'] = sex
    if password != '':
        postdata['password'] = password
    log = AddEntQQAccountLog()
    log.logger.info('编辑企业QQ信息:' + str(account))
    # 发送修改请求
    try:
        url = 'https://119.29.79.89/api/imqq/mod_qq_user/'
        token = 'f2adb29775f75886ca6b54dc28266231e4fb943d'
        headers = {'Accept': 'application/json', 'Authorization': 'Token ' + token}
        data = postdata
        postdata = json.dumps(data)
        res = requests.post(url, json=postdata, headers=headers, timeout=60, verify=False)
        if res.status_code == 200:
            r = res.json()
            if 'ret' in r.keys():
                dict = {'data': r['ret'], 'msg': r['msg']}
            if 'res' in r.keys():
                dict = {'data': r['res'], 'msg': r['msg']}
            log.logger.info('编辑企业QQ信息:' + r['msg'])
            return JsonResponse(dict)
        else:
            log.logger.info('编辑企业QQ信息:' + str(res))
            return JsonResponse({'data': False, 'msg': str(res)})
    except Exception as e:
        log.logger.info('编辑企业QQ信息:' + str(e))
        return JsonResponse({'data': False, 'msg': str(e)})


def edit_ent_email(request):
    """编辑企业邮箱信息"""
    data = json.loads(request.body.decode('utf-8'))
    userid = data.get('userid', '')
    name = data.get('name', '')
    gender = data.get('gender', '')
    position = data.get('position', '')
    password = data.get('password', '')
    enable = data.get('enable', '')
    org_id = data.get('department', '0')
    if name == '' and gender == '' and position == '' and password == '' and enable == '' and org_id == '0':
        return JsonResponse({'data': False, 'msg': '你还没有填写修改项目哦！'})
    postdata = {}
    postdata['userid'] = userid
    if name != '':
        postdata['name'] = name
    if position != '':
        postdata['position'] = position
    if gender != '':
        postdata['gender'] = gender
    if password != '':
        postdata['password'] = password
    if enable != '':
        postdata['enable'] = enable
    if org_id != '0':
        org_obj = OrganizationMptt.objects.get(pk=org_id)
        department = org_obj.get_ancestors_by_slash()
        postdata['department'] = department
    log = AddEntEmailAccountLog()
    log.logger.info('编辑企业邮箱信息:' + str(userid))
    # 发送修改请求
    try:
        url = 'https://119.29.79.89/api/imqq/mod_mail_user/'
        token = 'f2adb29775f75886ca6b54dc28266231e4fb943d'
        headers = {'Accept': 'application/json', 'Authorization': 'Token ' + token}
        data = postdata
        postdata = json.dumps(data)
        res = requests.post(url, json=postdata, headers=headers, timeout=60, verify=False)
        if res.status_code == 200:
            r = res.json()
            log.logger.info('编辑企业QQ信息:' + r['msg'])
            return JsonResponse({'data': r['ret'], 'msg': r['msg']})
        else:
            log.logger.info('编辑企业QQ信息:' + str(res))
            return JsonResponse({'data': False, 'msg': str(res)})
    except Exception as e:
        log.logger.info('编辑企业QQ信息:' + str(e))
        return JsonResponse({'data': False, 'msg': str(e)})


def change_svn_passwd(request):
    """修改svn密码"""
    data = json.loads(request.body.decode('utf-8'))
    username = data.get('username', '')
    passwd = data.get('passwd', '')

    # 发送修改请求
    try:
        url = 'https://192.168.40.11/api/change_svn_pwd/'
        token = 'd11205fc792d2d2def44ca55e5252dcbdcea6961'
        headers = {'Accept': 'application/json', 'Authorization': 'Token ' + token}
        data = {'username': username, 'passwd': passwd}
        res = requests.post(url, data=data, headers=headers, timeout=60, verify=False)
        if res.status_code == 200:
            r = res.json()
            return JsonResponse({'data': r['status'], 'msg': r['msg']})
    except Exception as e:
        return JsonResponse({'data': False, 'msg': str(e)})


def change_ldap_passwd(request):
    """修改ldap密码"""
    data = json.loads(request.body.decode('utf-8'))
    username = data.get('username', '')
    passwd = data.get('passwd', '')

    try:
        ldap = LDAP()
        result = ldap.change_user_password(uid=username, new_password=passwd)
        if result:
            return JsonResponse({'data': result, 'msg': '修改成功'})
        else:
            raise Exception('修改失败')
    except Exception as e:
        return JsonResponse({'data': False, 'msg': str(e)})


def get_user_clean_page(request, user_id):
    """跳转用户清理权限页面"""
    user_obj = User.objects.get(pk=user_id)
    org_obj = OrganizationMptt.objects.get(user=user_obj)
    """记录擦操作日志"""
    if user_obj.is_active:
        remark = '修改在职状态为离职'
        UserChangeRecord.objects.create(create_user=request.user, change_obj=org_obj.name, type=2, remark=remark)

    user_obj.is_active = 0
    org_obj.is_active = 0
    desert_department = OrganizationMptt.objects.get(name='离职接收部')
    remark = '部门:' + org_obj.get_ancestors_except_self_by_slash() + '-->' + '原力互娱/离职接收部'
    org_obj.move_to(desert_department)
    user_obj.save()
    org_obj.save()
    UserChangeRecord.objects.create(create_user=request.user, change_obj=org_obj.name, type=2, remark=remark)
    """找出由该用户创建或者申请人为该用户的所有未完成审批的工单，将其取消"""
    cancel_desired_user_workflow_apply.delay(user_id)
    # 将用户从角色分组中移除
    for r in Role.objects.prefetch_related('user').all():
        r.user.remove(user_obj)
    # 工单流程-特殊人员配置
    for s in SpecialUserParamConfig.objects.prefetch_related('user').all():
        s.user.remove(user_obj)
    # 工单流程-流程审批人设置
    for s in State.objects.prefetch_related('specified_users').all():
        s.specified_users.remove(user_obj)

    return HttpResponseRedirect('/users/clean/?id=' + user_id)


def downloads(request):
    """到处用户列表"""
    if request.method == 'POST':
        file_suffix = int(time.time())
        file_name = 'users_' + str(file_suffix) + '.xls'
        download_path = os.path.join(os.path.dirname(__file__), 'downloads', file_name)

        def gen_excel(download_path):
            if request.user.is_superuser or request.user.has_perm('users.download_users_info_list'):
                wb = xlwt.Workbook()
                sheet_name = wb.add_sheet("user")

                # 第一行记录字段
                row1 = sheet_name.row(0)

                col_fields = [
                    '所属部门', '姓名', '用户名', '邮箱'
                ]

                try:
                    for index, field in enumerate(col_fields):
                        row1.write(index, field)

                    desert_department = OrganizationMptt.objects.get(name='离职接收部')
                    all_users = OrganizationMptt.objects.select_related('user').filter(type=2).exclude(
                        parent=desert_department)

                    nrow = 1

                    for user in all_users:
                        row = sheet_name.row(nrow)
                        for index, field in enumerate(col_fields):
                            if index == 0:
                                value = user.get_ancestors_except_self()
                            elif index == 1:
                                value = user.user.username
                            elif index == 2:
                                value = user.user.first_name
                            elif index == 3:
                                value = user.user.email
                            row.write(index, value)
                        nrow += 1

                    wb.save(download_path)
                    data = file_name
                    success = True

                except Exception as e:
                    data = str(e)
                    success = False

                return {'data': data, 'success': success}
            else:
                success = False
                return {'msg': '没有权限', 'success': success}

        return JsonResponse(gen_excel(download_path))


def user_research_result(request):
    """获取用户搜索列表页面"""
    if request.user.has_perm('users.view_user_info'):
        if request.method == 'GET':
            result = request.GET['result']
            result = json.loads(result)
            org_id_list = [x['dataId'] for x in result]
            org_object_list = OrganizationMptt.objects.filter(id__in=org_id_list)
            return render(request, 'users_organization_search_result.html', {'org_object_list': org_object_list})
    else:
        return render(request, '403_without_nav.html')


def cmdb_user_add_api(request):
    """cmdb账号API接口文档"""
    if request.user.has_perm('users.api_doc'):
        return render(request, 'cmdb_user_add_confirm_delete_api_doc.html')
    else:
        return render(request, '403.html')


def add_vpn_user(request):
    """开通vpn帐号"""
    if request.method == 'POST':
        if request.user.is_superuser:
            try:
                raw_data = json.loads(request.body.decode('utf-8'))
                first_name = raw_data.get('first_name', '')
                user = User.objects.get(first_name=first_name)
                if user.is_active:
                    email = list(user.email.split(','))
                    res = create_user_for_openvpn(username=first_name, email=email)
                    if res['result']:
                        """更新cmdb用户vpn开通状态"""
                        user.organizationmptt_set.all().update(openvpn=1)
                        return JsonResponse({'success': True, 'msg': res['msg']})
                    else:
                        raise Exception(res['msg'])
                else:
                    raise Exception('离职用户不允许开通vpn帐号')
            except Exception as e:
                return JsonResponse({'success': False, 'msg': str(e)})


def modify_vpn_user(request):
    """修改vpn帐号密码"""
    if request.method == 'POST':
        if request.user.is_superuser:
            try:
                raw_data = json.loads(request.body.decode('utf-8'))
                first_name = raw_data.get('first_name', '')
                passwd = raw_data.get('passwd', '')
                if passwd == '':
                    raise Exception('密码不能为空')
                user = User.objects.get(first_name=first_name)
                if user.is_active:
                    res = modify_password_for_openvpn(username=first_name, passwd=passwd)
                    if res['result']:
                        return JsonResponse({'success': True, 'msg': res['msg']})
                    else:
                        raise Exception(res['msg'])
                else:
                    raise Exception('离职用户不允许修改vpn帐号密码')
            except Exception as e:
                return JsonResponse({'success': False, 'msg': str(e)})


def users_change_record(request):
    """用户变更（新增/修改/删除/清理权限）记录表"""
    if request.method == 'GET':
        if request.user.is_superuser:
            # today = datetime.now()
            # oneday = timedelta(days=7)
            # yesterday = today - oneday
            # all_record = UserChangeRecord.objects.filter(create_time__gt=yesterday).order_by('-id')
            all_record = UserChangeRecord.objects.order_by('-id')
            return render(request, 'users_change_record.html', {'all_record': all_record})
        else:
            return render(request, '403.html')


def role_group(request):
    """角色分组页面"""
    if request.method == 'GET':
        if request.user.is_superuser:
            return render(request, 'role_group.html')
        else:
            return render(request, '403.html')


def data_role_group(request):
    """角色分组数据"""
    if request.method == "POST":
        if request.user.is_superuser:
            try:
                raw_get = request.POST.dict()

                search_value = raw_get.get('search[value]', '')
                start = int(raw_get.get('start', 0))
                draw = raw_get.get('draw', 0)
                length = int(raw_get.get('length', 10))

                if search_value:
                    query = Role.objects.prefetch_related('user').filter((
                        Q(name__icontains=search_value))
                    ).distinct()

                else:
                    query = Role.objects.prefetch_related('user').all()

                raw_data = query[start: start + length]
                recordsTotal = query.count()
                data = {"data": [i.show_all() for i in raw_data], 'draw': draw, 'recordsTotal': recordsTotal,
                        'recordsFiltered': recordsTotal}
                return JsonResponse(data)
            except Exception as e:
                print(str(e))


def add_or_edit_role_group(request):
    """增加或者修改角色分组"""

    if request.method == "POST":
        raw_data = json.loads(request.body.decode('utf-8'))
        msg = 'ok'
        editFlag = raw_data.pop('editFlag')
        id = raw_data.pop('id')

        relate_user = raw_data.pop('relate_user')
        relate_user = list(User.objects.filter(id__in=relate_user))

        try:

            if editFlag:
                r = Role.objects.filter(id=id)
                r.update(**raw_data)
                r[0].user.clear()
                r[0].user.add(*relate_user)
                success = True
            else:
                if request.user.is_superuser:
                    r = Role.objects.create(**raw_data)
                    r.user.add(*relate_user)
                    success = True
                else:
                    raise PermissionDenied
        except PermissionDenied:
            msg = '没有权限'
            success = False
        except Exception as e:
            msg = str(e)
            success = False

        return JsonResponse({'data': success, 'msg': msg})


def get_role_group_data(request):
    """获取角色分组数据"""
    if request.method == 'POST':
        if request.user.is_superuser:
            id = json.loads(request.body.decode('utf-8')).get('id')
            obj = Role.objects.get(id=id)
            edit_data = obj.edit_data()
            return JsonResponse(edit_data)


def del_role_group(request):
    """删除角色分组数据"""

    if request.method == "POST":
        del_data = json.loads(request.body.decode('utf-8'))
        try:
            objs = Role.objects.filter(id__in=del_data)
            objs.delete()

            success = True
            msg = 'ok'

        except PermissionDenied:
            msg = '权限拒绝'
            success = False
        except Exception as e:
            msg = str(e)
            success = False

        return JsonResponse({'data': success, 'msg': msg})


def list_role_group(request):
    """下拉展示角色分组"""

    if request.method == "POST":
        data = []

        q = request.POST.get('q', None)
        all_roles = Role.objects.all()
        if q:
            all_roles = [x for x in all_roles if x.name == q]
        for x in all_roles:
            data.append({'id': x.id, 'text': x.name})

        return JsonResponse(data, safe=False)


def cmdb_get_role_user_info_api(request):
    """cmdb获取角色分组信息api文档"""
    if request.method == 'GET':
        if request.user.is_superuser:
            return render(request, 'cmdb_get_roleuser_info_api.html')
        else:
            return render(request, '403.html')


def batch_user_desert_page(request):
    """批量离职"""
    if request.method == 'GET':
        if request.user.is_superuser:
            all_pos = Position.objects.all()
            return render(request, 'batch_user_desert.html', {'all_pos': all_pos})
        else:
            return render(request, '403.html')

    if request.method == 'POST':
        success = True
        msg = 'ok'
        try:
            raw_data = json.loads(request.body.decode('utf-8'))
            user_list = raw_data['user_list']
            pos_id = raw_data['pos_id']
            user_list = user_list.split('\n')
            user_list = list(filter(lambda s: s.strip(), user_list))
            user_list = list(map(lambda s: s.strip(), user_list))
            for username in user_list:
                User.objects.get(username=username)

            batch_user_desert(user_list, pos_id, request.user)

        except User.DoesNotExist:
            msg = '用户不存在'
            success = False
        except Exception as e:
            msg = str(e)
            success = False
        finally:
            return JsonResponse({'success': success, 'msg': msg})


def recently_clean_user(request):
    """最近清除权限的用户"""
    if request.method == 'GET':
        if request.user.is_superuser:
            return render(request, 'recently_clean_user.html')
        else:
            return render(request, '403.html')

    if request.method == 'POST':
        success = True
        msg = 'ok'
        try:
            raw_data = json.loads(request.body.decode('utf-8'))
            start = raw_data.get('start', '2019-07-16')
            user_list = [x.change_obj for x in
                         UserChangeRecord.objects.filter(create_time__gt=start, type=4).order_by('-create_time')]
            user_list = list(set(user_list))
            process_info = ''
            for u in user_list:
                user = User.objects.filter(username=u)
                if user:
                    user = user[0]
                    ucs = UserClearStatus.objects.get(profile=user.profile)
                    process_info += '<h1>' + user.username + '</h1>'
                    process_info += ucs.show_process_info()
            msg = process_info
        except Exception as e:
            success = False
            msg = str(e)
        finally:
            return JsonResponse({'data': success, 'msg': msg})


def data_user_change_record(request):
    """用户变更记录数据"""
    if request.method == 'POST':
        raw_get = request.POST.dict()
        search_value = raw_get.get('search[value]', '')
        start = int(raw_get.get('start', 0))
        draw = raw_get.get('draw', 0)
        length = int(raw_get.get('length', 10))

        filter_create_user = raw_get.get('filter_create_user', '')
        filter_change_obj = raw_get.get('filter_change_obj', '')

        # 添加sub_query
        sub_query = Q()

        if filter_change_obj != '':
            sub_query.add(Q(change_obj__icontains=filter_change_obj), Q.AND)

        if filter_create_user != '':
            sub_query.add(Q(create_user__username__icontains=filter_create_user), Q.AND)

        if search_value:
            type_dict = UserChangeRecord.TYPE
            change_type = 0
            for d in type_dict:
                if d[1] == search_value:
                    change_type = d[0]

            query = UserChangeRecord.objects.select_related(
                'create_user').filter((Q(create_user__username__icontains=search_value) |
                                       Q(change_obj__icontains=search_value) |
                                       Q(remark__icontains=search_value) |
                                       Q(type=change_type)
                                       ) & sub_query).order_by('-create_time')
        else:
            query = UserChangeRecord.objects.select_related(
                'create_user').filter(sub_query).order_by('-create_time')

        raw_data = query[start: start + length]
        recordsTotal = query.count()

        data = {
            "data": [i.show_all() for i in raw_data], 'draw': draw,
            'recordsTotal': recordsTotal, 'recordsFiltered': recordsTotal
        }
        return JsonResponse(data)


def open_ent_qq(request):
    """开通企业QQ"""
    success = True
    msg = 'ok'
    log = AddEntQQAccountLog()
    try:
        data = json.loads(request.body.decode('utf-8'))
        log.logger.info('开通企业QQ信息:' + json.dumps(data))
        first_name = data.get('account', '')
        username = data.get('name', '')
        sex = data.get('gender', '')
        organization_char = data.get('department', '')
        title = data.get('title', '')
        org_id = OrganizationMptt.objects.get(name=username).id
        # 调用接口开通企业qq
        success, msg = add_qq_user(first_name, username, sex, organization_char, title, org_id)
    except Exception as e:
        success = False
        msg = str(e)
        log.logger.info('开通企业QQ信息:' + str(e))
    finally:
        return JsonResponse({'success': success, 'msg': msg})


def open_ent_email(request):
    """开通企业邮箱"""
    success = False
    msg = ''
    log = AddEntEmailAccountLog()
    try:
        data = json.loads(request.body.decode('utf-8'))
        log.logger.info('开通企业QQ信息:' + json.dumps(data))
        first_name = data.get('account', '')
        username = data.get('name', '')
        sex = data.get('gender', '')
        organization_char = data.get('department', '')
        title = data.get('title', '')
        org_id = OrganizationMptt.objects.get(name=username).id
        suffix = data.get('suffix')
        # 调用接口开通企业邮箱
        for s in suffix:
            success, reason = add_email_account(first_name + s, username, sex, organization_char, title, org_id)
            msg += reason
    except Exception as e:
        success = False
        msg = str(e)
        log.logger.info('开通企业QQ信息:' + str(e))
    finally:
        return JsonResponse({'success': success, 'msg': msg})


class UsersShareInfoTemp(generic.View):
    """用户入职信息模板"""

    def get(self, request):
        if request.user.is_superuser:
            with open('users/users_share_info_template.txt', 'r') as f:
                template_content = f.read()
            return render(request, 'users_share_info_template.html', {'template_content': template_content})
        else:
            return render(request, '403.html')

    def post(self, request):
        success = True
        msg = 'ok'
        try:
            raw_data = json.loads(request.body.decode('utf-8'))
            template_content = raw_data.get('template_content')
            preview = raw_data.get('preview', False)
            with open('users/users_share_info_template.txt', 'w') as f:
                f.write(template_content)
            # 发送企业微信消息预览
            if preview:
                content = make_new_user_info_share_content(request.user.organizationmptt_set.first().id)
                send_weixin_message(touser=request.user.first_name, content=content)
        except Exception as e:
            success = False
            msg = str(e)
        return JsonResponse({'success': success, 'msg': msg})
