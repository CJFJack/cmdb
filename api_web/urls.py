# -*- encoding: utf-8 -*-

from django.conf.urls import url
from api_web import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    url(r'^InstallGameServer.Create/$', views.InstallGameServerCreate.as_view(), name='增加开服计划'),
    url(r'^InstallGameServer.Delete/$', views.InstallGameServerDelete.as_view(), name='删除开服计划'),
    url(r'^InstallGameServer.Modify/$', views.InstallGameServerModify.as_view(), name='修改开服计划'),
    url(r'^InOrUninstallGameSrvCallback/$', views.InOrUninstallGameSrvCallback.as_view(), name='装/卸服回调'),
    url(r'^GameServerOff.Create/$', views.GameServerOffCreate.as_view(), name='游戏区服下线新增计划'),
    url(r'^GameServerOff.Delete/$', views.GameServerOffDelete.as_view(), name='游戏区服下线删除计划'),
    url(r'^ModifySrvOpenTimeSchedule.Create/$', views.ModifySrvOpenTimeScheduleCreate.as_view(), name='生成修改开服时间计划'),
    url('^GameServerMerge.Create/$', views.GameServerMergeCreate.as_view(), name='创建合服计划'),
    url('^RecvWebMaintenanceInfo/$', views.RecvWebMaintenanceInfo.as_view(), name='web挂维护后同步给cmdb的API接口'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
