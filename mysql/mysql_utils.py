# -*- encoding: utf-8 -*-

import string

import json

import random

import MySQLdb
import MySQLdb.cursors as mc

from cmdb.logs import MysqlPermissionLog

from mysql.mysql_config import INTERNET_IP
from users.channels_utils import ws_notify_clean_user

from users.models import UserClearStatus

# import _mysql_exceptions
DictCursor = mc.DictCursor
SSCursor = mc.SSCursor
SSDictCursor = mc.SSDictCursor
Cursor = mc.Cursor

mysql_log = MysqlPermissionLog()


def gen_password(n=18):
    """生成随机八位数字大小写字母组成的密码
    """
    return ''.join(random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for _ in range(n))


def has_instance_account(cursor, username, host):
    """判断数据库实例是否有该账号
    """

    sql = "select host, user from user where user='{username}' and host='{host}';".format(
        username=username, host=host)
    cursor.execute(sql)

    result = cursor.fetchall()    # 取第一个账号信息

    if len(result) == 0:
        return False
    else:
        return True


class Cursor(object):
    def __init__(self,
                 cursorclass=DictCursor,
                 host='127.0.0.1', user='root',
                 passwd='redhat', db='mysql',
                 port=3306, driver=MySQLdb,
                 ):
        self.cursorclass = cursorclass
        self.host = host
        self.port = int(port)
        self.user = user
        self.passwd = passwd
        self.db = db
        self.driver = driver
        self.connection = self.driver.connect(
            host=host, user=user, passwd=passwd, db=db,
            port=self.port, cursorclass=cursorclass)
        self.cursor = self.connection.cursor()

    def __iter__(self):
        for item in self.cursor:
            yield item

    def __enter__(self):
        return self.cursor

    def __exit__(self, ext_type, exc_value, traceback):
        self.cursor.close()
        if isinstance(exc_value, Exception):
            self.connection.rollback()
        else:
            self.connection.commit()
        self.connection.close()


def show_dbs_query(cursor):
    """查询dbs的sql
    """

    sql = "show databases"
    cursor.execute(sql)
    dbs = cursor.fetchall()

    return dbs


def add_user_privileges_query(cursor, username, list_dbs, permission, white_list):
    """给某个mysql实例的用户添加某些dbs的某个权限
    username: 'yanwenchi'
    list_dbs: ['web_gms_api_10', 'log_api', 'web_gms_system', 'test']
    permission: 'ALL PRIVILEGES'
    """

    IPS = INTERNET_IP + white_list
    IPS = tuple(list(set(IPS)))
    # IPS = ('127.0.0.1', )

    passwd = gen_password()

    ret_passwd = None

    for db in list_dbs:
        for ip in IPS:
            if not has_instance_account(cursor, username, ip):
                sql_add_user = "GRANT {permission} on {db}.* to '{username}'@'{ip}' identified by '{passwd}';".format(
                    permission=permission, db=db, username=username, ip=ip, passwd=passwd)
                ret_passwd = passwd
            else:
                sql_add_user = "GRANT {permission} on {db}.* to '{username}'@'{ip}';".format(
                    permission=permission, db=db, username=username, ip=ip)
            mysql_log.logger.info('赋权的sql语句: %s' % (sql_add_user))
            cursor.execute(sql_add_user)

    sql_flush_privileges = 'flush privileges;'
    cursor.execute(sql_flush_privileges)

    return ret_passwd


def get_instance_dbs(**instance_info):
    """根据一个instance，获取下面的dbs
    """

    with Cursor(**instance_info) as cursor:
        dbs = show_dbs_query(cursor)

    return dbs


def add_instance_user_privileges(username, list_dbs, permission, white_list, **instance_info):
    """添加实例的用户权限
    """

    with Cursor(**instance_info) as cursor:
        return add_user_privileges_query(cursor, username, list_dbs, permission, white_list)


def _remove_instance_account(cursor, username):
    IPS = INTERNET_IP

    for ip in IPS:
        if has_instance_account(cursor, username, ip):
            sql = "drop user '{username}'@'{ip}';".format(username=username, ip=ip)
            cursor.execute(sql)


def remove_instance_account(username, **instance_info):
    """删除一个mysql实例的用户账号
    """

    with Cursor(**instance_info) as cursor:
        _remove_instance_account(cursor, username)


def remove_instance_account_update_info(
        ucs, username, value_lock, instance_host_port, white_list, **instance_info):
    """删除一个mysql实例的用户账号
    然后更新用户清除的mysql_permission信息
    如果有异常，记录该异常
    value_lock的作用是防止多个线程会同时修改造成数据不一致
    """

    try:
        IPS = INTERNET_IP + white_list
        IPS = tuple(list(set(IPS)))
        for ip in IPS:
            with Cursor(**instance_info) as cursor:
                if has_instance_account(cursor, username, ip):
                    sql = "drop user '{username}'@'{ip}';".format(username=username, ip=ip)
                    mysql_log.logger.info('数据库实例: %s:%s 清除用户的sql语句: %s' % (
                        instance_info.get('host'), instance_info.get('port'), sql))
                    cursor.execute(sql)

        success = True
        result = '清除成功'
    except Exception as e:
        result = str(e)
        success = False
    finally:
        with value_lock:
            ucs = UserClearStatus.objects.get(id=ucs.id)
            mysql_permission = json.loads(ucs.mysql_permission)
            mysql_permission[instance_host_port] = {}
            mysql_permission[instance_host_port]['result'] = result
            mysql_permission[instance_host_port]['success'] = success
            ucs.mysql_permission = json.dumps(mysql_permission)
            ucs.save(update_fields=['mysql_permission'])
        ws_notify_clean_user(ucs.profile.user.id)
