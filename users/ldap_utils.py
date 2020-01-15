# -*- encoding: utf8 -*-

"""封装一些LDAP的操作
"""

from ldap3 import Server, Connection
from ldap3.core.exceptions import LDAPBindError, LDAPExceptionError
from ldap3 import MODIFY_REPLACE
from mysql.mysql_utils import gen_password


class LDAP(object):
    """ldap
    """

    _server_name = '192.168.10.98'
    _port = 389
    _user = 'cn=Manager,dc=chuangyu,dc=com'
    _password = 'Cy20160906'

    def __init__(self):
        self.s = Server(
            host=self._server_name, port=self._port, use_ssl=False, get_info='ALL')
        self.c = Connection(self.s, user=self._user, password=self._password)
        if not self.c.bind():
            raise LDAPBindError('bind() error')

    def unbind(self):
        return self.c.unbind()

    def set_password(self):
        """随机生成10为的密码
        """
        return gen_password(10)

    def _get_current_uid(self):
        """获取ou=people里面最大的uidnumber
        为后面的添加提供uidNumber
        """
        search_base = 'ou=Yuanli,dc=chuangyu,dc=com'
        search_filter = '(objectClass=*)'
        attributes = ['uidNumber']

        result = self.c.search(
            search_base=search_base, search_scope='LEVEL', search_filter=search_filter, attributes=attributes)
        if not result:
            raise LDAPExceptionError('获取people最大uid失败!')
        try:
            return max([x['attributes']['uidNumber'] for x in self.c.response])
        except:
            return 0

    def add_people_ou(self, uid, gid, userPassword=None):
        """给ou=people添加记录
        可以提供密码，如果不提供，随机生成一个
        """
        dn = 'uid={},ou=Yuanli,dc=chuangyu,dc=com'.format(uid)
        object_class = ['account', 'posixAccount', 'top']
        uidNumber = str(self._get_current_uid() + 1)
        homeDirectory = '{}@chuangyunet.com'.format(uid)
        if userPassword is None:
            userPassword = self.set_password()
        attrs = {
            'cn': uid, 'gidNumber': str(gid), 'homeDirectory': homeDirectory,
            'uid': uid, 'uidNumber': uidNumber, 'userPassword': userPassword
        }

        return self.c.add(dn, object_class, attrs)

    def get_group_dn_by_gid(self, gid):
        """通过gid来找到ou=group的dn名称
        """
        search_base = 'ou=Yuanli,dc=chuangyu,dc=com'
        search_scope = 'SUBTREE'
        search_filter = '(objectClass=*)'
        attributes = ['gidNumber']

        result = self.c.search(
            search_base=search_base, search_scope=search_scope, search_filter=search_filter, attributes=attributes)

        if not result:
            search_base = 'ou=People,dc=chuangyu,dc=com'
            result = self.c.search(
                search_base=search_base, search_scope=search_scope, search_filter=search_filter, attributes=attributes)
            if not result:
                msg = '查找gid{} ou=group的dn失败'.format(gid)
                raise LDAPExceptionError(msg)

        for x in self.c.response:
            gidNumber = x['attributes']['gidNumber']
            if gidNumber and gidNumber == gid:
                return x['dn']
        else:
            msg = '查找gid{} ou=group的dn失败'.format(gid)
            raise LDAPExceptionError(msg)

    def get_user_gid(self, dn):
        """获取一个dn也就是ou=Yuanli的用户的gid
        """
        search_scope = 'SUBTREE'
        search_filter = '(objectClass=*)'
        attributes = ['gidNumber']

        result = self.c.search(search_base=dn, search_scope=search_scope, search_filter=search_filter, attributes=attributes)
        if not result:
            raise LDAPExceptionError('该账号不存在'.format(dn))

        response = self.c.response
        if response:
            return response[0]['attributes']['gidNumber']
        else:
            raise LDAPExceptionError('记录{}没有gidNumber'.format(dn))

    def add_group_ou(self, gid, uid):
        """给ou=group添加记录
        先根据gid找到dn
        然后在添加uid
        uid接收list和字符串的格式
        """
        if isinstance(uid, list):
            list_uid = uid
        else:
            list_uid = [uid]
        dn = self.get_group_dn_by_gid(gid)
        modify_attr = {'memberUid': ('MODIFY_ADD', list_uid)}

        return self.c.modify(dn, modify_attr)

    def delete_people_ou(self, uid):
        """删除ou=people的dn
        """
        dn = 'uid={},ou=People,dc=chuangyu,dc=com'.format(uid)
        return self.c.delete(dn)

    def delete_yuanli_ou(self, uid):
        """删除ou=yuanli的dn
        """
        dn = 'uid={},ou=Yuanli,dc=chuangyu,dc=com'.format(uid)
        return self.c.delete(dn)

    def delete_group_ou(self, gid, uid, dn=None):
        """删除ou=group里面的某个记录
        如果有dn，则不用根据gid查找
        不然，需要先根据gid查找出dn

        uid接收list或者单个字符串, 最后全部转化为list形式
        """
        if isinstance(uid, list):
            list_uid = uid
        else:
            list_uid = [uid]

        modify_attr = {'memberUid': ('MODIFY_DELETE', list_uid)}
        if dn is not None:
            dn = dn
        else:
            dn = self.get_group_dn_by_gid(gid)

        return self.c.modify(dn, modify_attr)

    def change_user_password(self, uid, new_password):
        """修改用户密码"""
        dn = 'uid={},ou=Yuanli,dc=chuangyu,dc=com'.format(uid)
        result = self.c.modify(dn, {'userPassword': [(MODIFY_REPLACE, [new_password])]})
        if not result:
            dn = 'uid={},ou=People,dc=chuangyu,dc=com'.format(uid)
            result = self.c.modify(dn, {'userPassword': [(MODIFY_REPLACE, [new_password])]})
        return result
