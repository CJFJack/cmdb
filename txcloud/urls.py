from django.conf.urls import url
from txcloud.views import *

urlpatterns = [
    url(r'^purchase_server/$', purchase_server, name='购买腾讯云服务器填单页面'),
    url(r'^get_server_region/$', get_server_region, name='获取服务器地域'),
    url(r'^get_server_zone/$', get_server_zone, name='获取服务器可用区'),
    url(r'^get_instance_type/$', get_instance_type, name='获取实例机型'),
    url(r'^get_instance_config_info/$', get_instance_config_info, name='获取实例配置'),
    url(r'^get_image_version/$', get_image_version, name='获取镜像版本'),
    url(r'^get_server_project/$', get_server_project, name='获取服务器项目列表数据'),
    url(r'^get_security_group/$', get_security_group, name='获取安全组'),
    url(r'^inquiry_price/$', inquiry_price, name='服务器购买前面询价'),
    url(r'^run_instance/$', run_instance, name='发起购买服务器'),
    url(r'^get_server_zone_number/$', get_server_zone_number, name='获取实例机型可用区数量'),
    url(r'^mysql_purchase/$', mysql_purchase, name='购买腾讯云mysql数据库填单页面'),
    url(r'^get_mysql_zone/$', get_mysql_zone, name='获取云mysql数据库可用区'),
    url(r'^get_mysql_config/$', get_mysql_config, name='获取云数据库mysql可售配置信息'),
    url(r'^get_mysql_region/$', get_mysql_region, name='获取云数据库mysql地域'),
    url(r'^get_mysql_engine/$', get_mysql_engine, name='获取云mysql数据库版本'),
    url(r'^get_mysql_framework/$', get_mysql_framework, name='获取云mysql数据库架构'),
    url(r'^get_mysql_price/$', get_mysql_price, name='获取云数据库mysql实例价格'),
    url(r'^get_mysql_default_params/$', get_mysql_default_params, name='获取腾讯云数据库初始化参数'),
    url(r'^create_txcloud_mysql/$', create_txcloud_mysql, name='创建云数据库实例mysql'),
    url(r'^open_mysql_wan/$', open_mysql_wan, name='开通数据库外网访问'),
]
