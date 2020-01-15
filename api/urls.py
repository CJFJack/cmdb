from django.conf.urls import url, include
from api import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    url(r'^auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^Host.List/$', views.HostDetail.as_view(), name='获取主机记录'),
    url(r'^Host.Create/$', views.HostCreate.as_view(), name='增加主机'),
    url(r'^Host.Modify/$', views.HostModify.as_view(), name='修改主机'),
    url(r'^lockOpsManager$', views.LockOpsManager.as_view(), name='给运维管理机加锁'),
    url(r'^unlockOpsManager$', views.UnLockOpsManager.as_view(), name='给运维管理机加锁'),
    url(r'^addUserHost$', views.UserHostAdd.as_view(), name='增加服务器权限'),
    url(r'^delUserHost$', views.UserHostDel.as_view(), name='删除服务器永久权限'),
    url(r'^gameservers$', views.GameServerList.as_view(), name='获取区服列表'),
    url(r'^newSrvCallBack$', views.NewSrvCallBack.as_view(), name='新建游戏服'),
    url(r'^updateClientPara$', views.UpdateClientPara.as_view(), name='更新服务器参数配置（前端更新）接口（页游）'),
    url(r'^updateSrvPara$', views.UpdateSrvPara.as_view(), name='更新服务器参数配置（后端更新）接口（页游）'),
    url(r'^delSrvRelateInfo$', views.DelSrvRelateInfo.as_view(), name='删除某个服的数据接口'),
    url(r'^modifySrvRelateInfo$', views.ModifySrvRelateInfo.as_view(), name='修改服务器相关信息接口'),
    url(r'^batchModifyCdn$', views.BatchModifyCdn.as_view(), name='根据条件批量修改cdn地址接口'),
    url(r'^mergeSrvCallBack$', views.MergeSrvCallBack.as_view(), name='合服完成回调接口'),
    url(r'^BatchModifyGameServerStatus/$', views.BatchModifyGameServerStatus.as_view(), name='批量修改区服状态接口'),

    url(r'^hotupdateCallBack/$', views.HotClientCallBack.as_view(), name='前端热更新完成后的回调接口'),
    url(r'^HotServerCallBack/$', views.HotServerCallBack.as_view(), name='后端热更新完成后的回调接口'),
    url(r'^HotServerOnFinishedCallBack/$', views.HotServerOnFinishedCallBack.as_view(), name='后端热更新完成后的总的回调接口'),

    url(r'^RsyncOnFinishedCallBack/$', views.RsyncOnFinishedCallBack.as_view(), name='版本接收机完成rsync传送文件以后回调接口'),
    url(r'^snsyHotClientCallBack/$', views.SNSYHotClientCallBack.as_view(), name='SNSY前端热更新完成后的回调接口'),
    url(r'^csxyHotClientCallBack/$', views.CSXYHotClientCallBack.as_view(), name='超神学院前端热更新完成后的回调接口'),

    url(r'^GameServerOffCallBack/$', views.GameServerOffCallBack.as_view(), name='区服下线回调接口'),
    url(r'^HostMigrationCallBack/$', views.HostMigrationCallBack.as_view(), name='主机迁服回调接口'),
    url(r'^HostRecoverCallBack/$', views.HostRecoverCallBack.as_view(), name='主机回收回调接口'),
    url(r'^ModSrvOpenTimeCallBack/$', views.ModSrvOpenTimeCallBack.as_view(), name='修改开服时间回调接口'),
    url(r'^GameServerActionCallback/$', views.GameServerActionCallback.as_view(), name='区服操作回调接口'),
    url(r'^HostInitializeCallback/$', views.HostInitializeCallback.as_view(), name='主机安装salt-minion和初始化结果回调接口'),
    url(r'^VersionUpdatePlan/$', views.VersionUpdatePlan.as_view(), name='审批完成的版本更新计划'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
