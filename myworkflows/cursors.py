# -*- encoding: utf-8 -*-
import MySQLdb
import MySQLdb.cursors as mc
DictCursor = mc.DictCursor
SSCursor = mc.SSCursor
SSDictCursor = mc.SSDictCursor
Cursor = mc.Cursor


class Cursor(object):
    def __init__(self,
                 cursorclass=DictCursor,
                 host='127.0.0.1', user='root',
                 passwd='redhat', db='server_manager',
                 port=3306, driver=MySQLdb,
                 ):
        self.cursorclass = cursorclass
        self.host = host
        self.user = user
        self.passwd = passwd
        self.db = db
        self.driver = driver
        self.connection = self.driver.connect(
            host=host, user=user, passwd=passwd, db=db,
            cursorclass=cursorclass)
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
