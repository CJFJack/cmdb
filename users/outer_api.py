# -*- encoding: utf-8 -*-
"""清除用户调用的外部接口
"""

from users.models import UserProfileHost
from users.models import UserClearStatus
from users.ldap_utils import LDAP

from assets.models import OpsManager, Host

from cmdb.logs import CleanUserLog, OpenVPNLog
from netmiko import ConnectHandler
from django.db import transaction

# import collections

import re

import json

import requests

from requests.packages.urllib3.util import Retry
from requests.adapters import HTTPAdapter
from requests import Session


def get_ops_manager_from_user(user, project=None):
    """根据一个用户，从服务器权限列表中
    获取到所有关联的运维管理机
    """
    # default_url = 'https://192.168.40.8/api/'
    # add_default = False    # 为了防止多次添加默认的管理机，设置这个标志位

    #######
    # project 参数是list project实例
    # ==> [p1, p2]
    #######
    profile = user.profile

    if project:
        user_profile_host = UserProfileHost.objects.filter(user_profile=profile,
                                                           host__belongs_to_game_project__in=project)
    else:
        user_profile_host = UserProfileHost.objects.filter(user_profile=profile)

    list_host = {x.host for x in user_profile_host if x.host.status == 1}

    list_ops_manager = set()

    # 40.8默认的运维管理机需要ip
    default_ip_list = []
    # 是否需要默认40.8管理机标志
    use_default = False

    for h in list_host:
        try:
            ops_manager = OpsManager.objects.get(project=h.belongs_to_game_project, room=h.belongs_to_room)
        except OpsManager.DoesNotExist:
            if h.telecom_ip:
                default_ip_list.append(h.telecom_ip + ':' + str(h.sshport))
            else:
                default_ip_list.append(h.internal_ip + ':' + str(h.sshport))
            use_default = True
        else:
            # 避免添加重复的管理机
            if ops_manager.url not in [x.url for x in list_ops_manager]:
                list_ops_manager.add(ops_manager)

    # 去掉包含'bak的ip'
    default_ip_list = [x for x in default_ip_list if 'bak' not in x]

    return (list_ops_manager, default_ip_list, use_default)


def get_all_ops_manager(projects=None):
    """
    排除 已归还/停用/windows 的服务器主机
    如果有所属运维管理机的，则加入list_ops_manager中返回
    如果没有，则找出该主机的电信IP，没有则使用内网IP，加入default_ip_list中返回，供默认管理机40.8使用，
    """

    list_host = [x for x in Host.objects.filter(system=0).exclude(status=2).exclude(status=4)]
    if projects:
        list_host = [x for x in Host.objects.filter(system=0, belongs_to_game_project__in=projects).exclude(status=2).exclude(status=4)]
    list_ops_manager = set()

    # 40.8默认的运维管理机需要ip
    default_ip_list = []
    # 是否需要默认40.8管理机标志
    use_default = False

    """没有运维管理机的主机，找出电信IP或内网IP"""
    for h in list_host:
        if not h.opsmanager:
            if h.telecom_ip:
                default_ip_list.append(h.telecom_ip + ':' + str(h.sshport))
            else:
                default_ip_list.append(h.internal_ip + ':' + str(h.sshport))
            use_default = True
    """添加状态为可用的运维管理机"""
    ops_objs = OpsManager.objects.filter(enable=1)
    if projects:
        ops_objs = OpsManager.objects.filter(project__in=projects, enable=1)
    for x in ops_objs:
        if x.url not in [x.url for x in list_ops_manager] and x.get_manager_host_status():
            list_ops_manager.add(x)

    """去掉包含'bak的ip"""
    default_ip_list = [x for x in default_ip_list if 'bak' not in x]

    return list_ops_manager, default_ip_list, use_default


def clean_server(list_ops_manager, default_ip_list, use_default, user, ucs):
    """list_ops_manager是运维管理机下的ip列表
    username是英文名

    list_ip格式
    ["ops_manager_obj1", "ops_manager_obj2"]

    发送给运维管理机删除用户key的格式
    {
        'username': username
    }

    如果是40.8的默认运维管理机
    传多一个ip_list
    {
        'username': username，
        'ip_list': [ip1:port, ip2:port]
    }

    运维管理机返回json字符串，格式为
    {"Accepted": True or False}
    表示管理机已经成功接收到请求
    """

    # 如果需要使用默认的运维管理机
    default_url = 'https://192.168.40.8/api/'
    default_ops = OpsManager.objects.get(url=default_url)
    if use_default:
        if default_ops not in list_ops_manager:
            list_ops_manager.add(OpsManager.objects.get(url=default_url))

    log = CleanUserLog()

    p = re.compile(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")

    # 去掉具有相同ip的运维管理机
    ops_ip = list(set([re.findall(p, x.url)[0] for x in list_ops_manager]))

    ucs = UserClearStatus.objects.get(id=ucs.id)
    ucs.server_permission = json.dumps({'ops_ip': ops_ip})
    ucs.save(update_fields=['server_permission'])

    # status_list = []    # 多次发送请求后的结构  1成功 0失败
    username = user.first_name

    # data = {"username": username}

    # default_dict = collections.defaultdict(dict)

    for ops_manager in list_ops_manager:
        try:
            server_permission = json.loads(ucs.server_permission)  # 这里取出来最新的server_permission的结果
            ip = re.findall(p, ops_manager.url)[0]
            url = ops_manager.url + 'user/user_del/'
            token = ops_manager.token
            if ops_manager.url == default_url:
                data = {"username": username, "ip_list": default_ip_list}
            else:
                data = {"username": username}
            authorized_token = "Token " + token

            headers = {
                'Accept': 'application/json',
                'Authorization': authorized_token,
                'Connection': 'keep-alive',
            }
            s = Session()
            log.logger.info('开始清除用户%s服务器权限，运维管理机%s，data=%s' % (username, ops_manager.url, json.dumps(data)))
            s.mount('https://', HTTPAdapter(max_retries=Retry(total=5, status_forcelist=[408])))
            r = s.post(url, headers=headers, json=data, verify=False, timeout=30)
            result = r.json()
            if result.get('Accepted', False):
                log.logger.info('清除用户%s服务器权限-发送到管理机%s 成功' % (username, ops_manager.url))
                # status_list.append(1)
            else:
                # status_list.append(0)
                log.logger.info(result)
                with transaction.atomic():
                    ucs = UserClearStatus.objects.get(id=ucs.id)
                    server_permission = json.loads(ucs.server_permission)
                    server_permission.update({ip: {'success': False}})
                    ucs.server_permission = json.dumps(server_permission)
                    ucs.save(update_fields=['server_permission'])
        except Exception as e:
            msg = str(e)
            log.logger.info('清除用户%s服务器权限-发送到管理机%s 失败: %s' % (username, ops_manager.url, msg))
            with transaction.atomic():
                ucs = UserClearStatus.objects.get(id=ucs.id)
                server_permission = json.loads(ucs.server_permission)
                server_permission.update({ip: {'success': False}})
                ucs.server_permission = json.dumps(server_permission)
                ucs.save(update_fields=['server_permission'])
        # finally:
        #     ucs.save(update_fields=['server_permission'])


def clean_svn(user, ucs, project=None):
    """清除用户的svn全部权限
    请求的数据格式
    {"username": username}
    返回的数据格式
    {"success": True, "result": '删除成功'}
    """
    username = user.first_name
    data = {"username": username}
    url = 'https://192.168.40.11/api/deluser/'
    if project:
        data = {"username": username, "project": project.svn_repo}
        url = 'https://192.168.40.11/api/delproprivilege/'
    log = CleanUserLog()

    ucs = UserClearStatus.objects.get(id=ucs.id)

    try:
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Token d11205fc792d2d2def44ca55e5252dcbdcea6961',
            'Connection': 'keep-alive',
        }
        r = requests.post(url, headers=headers, json=data, verify=False)
        svn = r.json()
        if project:
            if ucs.svn:
                temp_ucs_svn = json.loads(ucs.svn)
                temp_ucs_svn[project.project_name_en] = svn
                ucs.svn = json.dumps(temp_ucs_svn)
            else:
                ucs.svn = json.dumps({project.project_name_en: svn})
        else:
            ucs.svn = json.dumps(svn)
        if project:
            log.logger.info('清除用户%s 项目%s svn完成' % (username, project.project_name))
        else:
            log.logger.info('清除用户%s svn完成' % (username,))
    except Exception as e:
        ucs.svn = json.dumps({"success": False, "result": str(e), "project": project.project_name})
        log.logger.error('清除用户%s 项目%s svn失败' % (username, project.project_name))
    finally:
        ucs.save(update_fields=['svn'])


def clean_svn2(user, ucs):
    """清除用户的svn全部权限
    请求的数据格式
    {"username": username}
    返回的数据格式
    {"success": True, "result": '删除成功'}
    """
    username = user.first_name
    data = {"username": username}
    log = CleanUserLog()

    ucs = UserClearStatus.objects.get(id=ucs.id)

    try:
        url = 'https://192.168.40.18/api/deluser/'
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Token d17e17d4730c830b644f34bc309a6a09dbff40b1',
            'Connection': 'keep-alive',
        }
        r = requests.post(url, headers=headers, json=data, verify=False)
        svn2 = r.json()
        ucs.svn2 = json.dumps(svn2)
        log.logger.info('清除用户%s svn2完成' % (username))
    except Exception as e:
        ucs.svn2 = json.dumps({"success": False, "result": str(e)})
        log.logger.info('清除用户%s svn2失败' % (username))
    finally:
        ucs.save(update_fields=['svn2'])


def clean_samba(user, ucs):
    """清理用户的samba权限
    请求的数据格式
    {"username": username}
    返回的数据格式
    {"success": True, "result": '删除成功'}
    """
    username = user.first_name
    data = {"username": username}
    log = CleanUserLog()
    ucs = UserClearStatus.objects.get(id=ucs.id)

    try:
        url = "https://192.168.40.11/api/delsamba/"
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Token d11205fc792d2d2def44ca55e5252dcbdcea6961',
            'Connection': 'keep-alive',
        }
        r = requests.post(url, headers=headers, json=data, verify=False)
        samba = r.json()
        ucs.samba = json.dumps(samba)
        log.logger.info('清除用户%s samba完成' % (username))
    except Exception as e:
        ucs.samba = json.dumps({"success": False, "result": str(e)})
        log.logger.info('清除用户%s samba失败' % (username))
    finally:
        ucs.save(update_fields=['samba'])


def clean_ldap(user, ucs):
    """清除ldap账号
    返回的数据格式
    {"success": True, "result": '删除成功'}
    """
    ldap = LDAP()
    uid = user.first_name
    ucs = UserClearStatus.objects.get(id=ucs.id)

    try:
        # 清除ou=people和ou=Yuanli账号
        dn = 'uid={},ou=Yuanli,dc=chuangyu,dc=com'.format(uid)
        try:
            gid = ldap.get_user_gid(dn)
        except:
            dn = 'uid={},ou=People,dc=chuangyu,dc=com'.format(uid)
            gid = ldap.get_user_gid(dn)
        if not (ldap.delete_people_ou(uid) or ldap.delete_yuanli_ou(uid)):
            result = ldap.c.result['message'] + ldap.c.result['description']
            raise Exception(result)

        # 清除ou=group部门里面的记录
        # if not ldap.delete_group_ou(gid, uid):
        #     result = ldap.c.result['message'] + ldap.c.result['description']
        #     raise Exception(result)

        ucs.ldap = json.dumps({"success": True, "result": ''})

        ldap.unbind()

    except Exception as e:
        ucs.ldap = json.dumps({"success": False, "result": str(e)})
    finally:
        ucs.save(update_fields=['ldap'])


def delete_ent_qq(user, ucs):
    """清除企业QQ账号
    返回的数据格式
    {"ret": True, "mgs": '删除成功'}
    """

    qq_account = user.first_name
    ucs = UserClearStatus.objects.get(id=ucs.id)

    try:
        url = 'https://119.29.79.89/api/imqq/del_qq_user/'
        token = 'f2adb29775f75886ca6b54dc28266231e4fb943d'
        headers = {'Accept': 'application/json', 'Authorization': 'Token ' + token}
        data = {'account': qq_account}
        postdata = json.dumps(data)
        res = requests.post(url, json=postdata, headers=headers, timeout=60, verify=False)

        if res.status_code == 200:
            r = res.json()
            ucs.ent_qq = json.dumps(r)

    except Exception as e:
        ucs.ent_qq = json.dumps({"success": False, "result": str(e)})
    finally:
        ucs.save(update_fields=['ent_qq'])


def delete_ent_email(email_account, ucs):
    """清除企业邮箱账号
    返回的数据格式
    {"ret": True, "msg": '删除成功'}
    """

    # if user.organizationmptt_set.all()[0].ent_email:
    #     email_account = user.organizationmptt_set.all()[0].ent_email
    # else:
    #     email_account = user.email

    ucs = UserClearStatus.objects.get(id=ucs.id)

    try:
        url = 'https://119.29.79.89/api/imqq/del_mail_user/'
        token = 'f2adb29775f75886ca6b54dc28266231e4fb943d'
        headers = {'Accept': 'application/json', 'Authorization': 'Token ' + token}
        data = {'userid': email_account}
        postdata = json.dumps(data)
        res = requests.post(url, json=postdata, headers=headers, timeout=60, verify=False)

        if res.status_code == 200:
            r = res.json()
            ent_email = ucs.ent_email
            if ent_email:
                ent_email = json.loads(ent_email)
                ent_email[email_account] = r
                ucs.ent_email = json.dumps(ent_email)
            else:
                ucs.ent_email = json.dumps({email_account: r})
    except Exception as e:
        if ucs.ent_email:
            ent_email = json.loads(ent_email)
            ent_email[email_account] = {"success": False, "msg": str(e)}
            ucs.ent_email = json.dumps(ent_email)

        else:
            ucs.ent_email = json.dumps({"success": False, "msg": str(e), 'email': email_account})
    finally:
        ucs.save(update_fields=['ent_email'])


def delete_user_wifi(user, ucs):
    """
    :param user: 用户名，拼音全拼
    :return: {'ret':True,'msg':'删除成功'}
    """
    ucs = UserClearStatus.objects.get(id=ucs.id)
    user = user.first_name
    apinfo = {
        'device_type': 'cisco_wlc',
        'ip': '172.16.199.200',
        'username': 'skynet',
        'password': 'skynet@2017swItch',
        'port': 22
    }
    try:
        net_connect = ConnectHandler(**apinfo)
        net_connect.enable()
        cmd = 'show macfilter summary'
        result = net_connect.send_command(cmd)

        macinfos = []
        del_staut = True

        # 查出用户所有mac地址
        for macinfo in result.split('\n'):
            if user in macinfo:
                macinfos.append(macinfo.split()[0])

        for mac in macinfos:
            cmd = 'config macfilter delete {0}'.format(mac)
            result = net_connect.send_command(cmd)
            if 'Deleted MAC Filter' not in result:
                del_staut = False

        net_connect.disconnect()
        if del_staut:
            ucs.wifi = json.dumps({'ret': True, 'msg': '删除成功'})
        else:
            ucs.wifi = json.dumps({'ret': False, 'msg': '删除失败'})
    except Exception as e:
        try:
            net_connect.disconnect()
        except:
            pass
        ucs.wifi = json.dumps({"success": False, "result": str(e)})
        return {'ret': False, 'msg': str(e)}
    finally:
        ucs.save(update_fields=['wifi'])


def create_user_for_openvpn(username, email):
    """
    开通openvpn帐号
    返回格式：
    {'msg': '', 'result': True}
    """
    log = OpenVPNLog()
    url = 'https://192.168.40.11/api/addvpnuser/'
    token = 'd11205fc792d2d2def44ca55e5252dcbdcea6961'
    authorized_token = "Token " + token
    headers = {
        'Accept': 'application/json',
        'Authorization': authorized_token,
        'Connection': 'keep-alive',
    }
    data = {
        'username': username,
        'email': email
    }
    try:
        s = Session()
        s.mount('https://', HTTPAdapter(max_retries=Retry(total=3, status_forcelist=[408])))
        r = s.post(url, headers=headers, json=data, verify=False, timeout=30)
        if r.status_code == 200:
            result = r.json()
            log.logger.info(result)
            return result
        else:
            log.logger.info(str(r))
            raise Exception('发送到40.11失败' + str(r))
    except Exception as e:
        log.logger.info(str(e))
        return {'msg': str(e), 'result': False}


def delete_user_for_openvpn(user, ucs):
    """
    删除openvpn帐号
    返回格式：
    {'result': True, 'msg: ''}
    """
    log = OpenVPNLog()
    ucs = UserClearStatus.objects.get(id=ucs.id)
    username = user.first_name
    url = 'https://192.168.40.11/api/delvpnuser/'
    token = 'd11205fc792d2d2def44ca55e5252dcbdcea6961'
    authorized_token = "Token " + token
    headers = {
        'Accept': 'application/json',
        'Authorization': authorized_token,
        'Connection': 'keep-alive',
    }
    data = {
        'username': username,
    }
    try:
        s = Session()
        s.mount('https://', HTTPAdapter(max_retries=Retry(total=3, status_forcelist=[408])))
        r = s.post(url, headers=headers, json=data, verify=False, timeout=30)
        if r.status_code == 200:
            result = r.json()
            if result['result']:
                ucs.openvpn = json.dumps({'ret': True, 'msg': '删除成功'})
                org = user.organizationmptt_set.filter(type=2)
                org.update(**{'openvpn': 0})
            else:
                ucs.openvpn = json.dumps({'ret': False, 'msg': result['msg']})
            log.logger.info(result)
            return result
        else:
            ucs.openvpn = json.dumps({'ret': False, 'msg': '删除失败!' + str(r)})
            log.logger.info(str(r))
            raise Exception('发送到40.11失败' + str(r))
    except Exception as e:
        ucs.openvpn = json.dumps({'ret': False, 'msg': '删除失败!' + str(e)})
        log.logger.info(str(e))
        return {'msg': str(e), 'result': False}
    finally:
        ucs.save(update_fields=['openvpn'])


def modify_password_for_openvpn(username, passwd):
    """修改openvpn帐号密码"""
    log = OpenVPNLog()
    url = 'https://192.168.40.11/api/modvpnuser/'
    token = 'd11205fc792d2d2def44ca55e5252dcbdcea6961'
    authorized_token = "Token " + token
    headers = {
        'Accept': 'application/json',
        'Authorization': authorized_token,
        'Connection': 'keep-alive',
    }
    data = {
        'username': username,
        'passwd': passwd
    }
    try:
        s = Session()
        s.mount('https://', HTTPAdapter(max_retries=Retry(total=3, status_forcelist=[408])))
        r = s.post(url, headers=headers, json=data, verify=False, timeout=30)
        if r.status_code == 200:
            result = r.json()
            log.logger.info(result)
            return result
        else:
            log.logger.info(str(r))
            raise Exception('发送到40.11失败' + str(r))
    except Exception as e:
        log.logger.info(str(e))
        return {'msg': str(e), 'result': False}
