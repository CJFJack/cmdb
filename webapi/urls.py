from django.conf.urls import url
from webapi.views import *

urlpatterns = [
    url('^web_get_cdn_list_api/$', web_get_cdn_list_api, name='web-获取cdn目录api接口-列表'),
    url('^data_web_get_cdn_list_api/$', data_web_get_cdn_list_api, name='web-获取cdn目录api接口-列表数据'),
    url('^add_or_edit_get_cdn_list_api/$', add_or_edit_get_cdn_list_api, name='增加或者编辑获取cdn目录api信息'),
    url('^delete_get_cdn_list_api/$', delete_get_cdn_list_api, name='删除获取cdn目录api配置信息'),
    url('^get_get_cdn_list_api/$', get_get_cdn_list_api, name='获取获取cdn目录api编辑数据'),
]
