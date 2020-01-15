# -*- encoding: utf-8- -*-
from requests.packages.urllib3.util import Retry
from requests.adapters import HTTPAdapter
from requests import Session
from assets.models import OpsManager
from txcloud.models import ServerZoneNumber
import random
import string


def gen_password():
    """随机生成10位数密码，由大写字母/小写字母/数字组成"""
    src = string.ascii_letters + string.digits
    list_passwd_all = random.sample(src, 5)
    list_passwd_all.extend(random.sample(string.digits, 1))
    list_passwd_all.extend(random.sample(string.ascii_lowercase, 2))
    list_passwd_all.extend(random.sample(string.ascii_uppercase, 2))
    random.shuffle(list_passwd_all)
    str_passwd = ''.join(list_passwd_all)
    return str_passwd


def make_purchase_tx_server_email(ip, host_init, cloud_account):
    """生成购买腾讯云服务器后通知邮件的内容"""
    if host_init.syndic_ip:
        remark = '请登录cmdb，进入“服务器资源-主机初始化”查看初始化结果！'
    else:
        remark = '请登录cmdb，进入“服务器资源-主机初始化”补充syndic_ip并执行主机初始化！'
    template = "<html>" + \
               "<head>" + \
               "<meta charset=\"UTF-8\">" + \
               "</head>" + \
               "<body>" + \
               "<p>cmdb 购买腾讯云服务器成功(使用帐号：{})，服务器信息如下</p>".format(cloud_account) + \
               "<ul>" + \
               "<li>外网IP：{}</li>".format(ip) + \
               "<li>初始帐号：root</li>" + \
               "<li>初始密码：{}</li>".format(host_init.password) + \
               "</ul>" + \
               "<p>{}</p>".format(remark) + \
               "</body>" + \
               "</html>"

    return template


def make_purchase_tx_mysql_email(mysql_obj, cloud_account):
    """生成购买腾讯云mysql数据库后通知邮件的内容"""
    template = "<html>" + \
               "<head>" + \
               "<meta charset=\"UTF-8\">" + \
               "</head>" + \
               "<body>" + \
               "<p>cmdb 购买腾讯云MySQL数据库成功(使用帐号：{})，并已完成初始化，数据库信息如下</p>".format(cloud_account) + \
               "<ul>" + \
               "<li>内网IP：{}</li>".format(mysql_obj.host) + \
               "<li>内网端口：{}</li>".format(mysql_obj.port) + \
               "<li>帐号信息：请登录cmdb,进入数据库列表查看</li>" + \
               "</ul>" + \
               "<p>备注：若需要开通外网访问，请登录cmdb-数据库列表，选择数据库实例，点击开通外网访问！</p>" + \
               "</body>" + \
               "</html>"

    return template


def get_host_init_business():
    """获取主机初始化业务类型"""
    success = True
    msg = 'ok'
    try:
        url = 'https://119.29.79.89/api/install/Init_Type/'
        token = 'bda6d0ff9803476bc0763c4f1912a2c5ba7145bc'
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Token {}'.format(token)
        }
        post_data = {}
        s = Session()
        s.mount('https://', HTTPAdapter(max_retries=Retry(total=5, status_forcelist=[408])))
        r = s.post(url, headers=headers, json=post_data, timeout=30, verify=False)
        if r.status_code != 200:
            raise Exception(str(r))
        res = r.json()
        if not res['Accepted']:
            raise Exception(res['data'])
        msg = res['data']

    except Exception as e:
        success = False
        msg = str(e)
    finally:
        return success, msg


def get_syndic_ip(project, room):
    """根据项目和机房获取运维管理机的内网IP，即syndic_ip"""
    success = True
    data = 'ok'
    try:
        ops_manager = OpsManager.objects.get(project=project, room=room)
        host = ops_manager.host_set.filter(belongs_to_business__business_name='manager', status=1)
        if host:
            data = host.first().internal_ip
        else:
            raise Exception

    except Exception as e:
        data = ''
        success = False
    finally:
        return success, data


def get_server_zone_number(instance_type):
    """根据实例规格获取实例可用区数量"""
    number = 0
    try:
        obj = ServerZoneNumber.objects.filter(instance_type=instance_type)
        if obj:
            number = obj[0].get_zone_number()
    except Exception as e:
        pass
    return number
