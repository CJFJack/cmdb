from django.conf.urls import url
from mysql.views import *


urlpatterns = [
    url(r'^instance/$', instance, name='数据库实例'),
    url(r'^data_instance/$', data_instance, name='数据库实例数据'),
    url(r'^mysql_instance_api/$', mysql_instance_api, name='数据库实例api文档'),
    url(r'^list_mysql_instance/$', list_mysql_instance, name='下拉mysql实例列表'),
    url(r'^list_mysql_instance_db/$', list_mysql_instance_db, name='下拉mysql实例DB列表'),
    url(r'^add_or_edit_mysql/$', add_or_edit_mysql, name='新增或编辑mysql实例信息'),
    url(r'^get_instance_info/$', get_instance_info, name='获取数据库实例信息'),
    url(r'^del_mysql_instance/$', del_mysql_instance, name='删除mysql实例'),
    url(r'^mysql_history/$', mysql_history, name='数据库实例变更记录'),
    url(r'^data_mysql_history/$', data_mysql_history, name='数据库变更追踪数据'),
    url(r'^get_mysql_history/$', get_mysql_history, name='获取数据库变更记录'),
]
