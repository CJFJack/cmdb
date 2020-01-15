from django.conf.urls import url
from dashboard.views import *

urlpatterns = [
    url('^$', dashboard_page, name='仪表盘'),
    url('^hot_update_pie/$', hot_update_pie, name='热更新饼图'),
    url('^host_migrate_pie/$', host_migrate_pie, name='主机迁服饼图'),
    url('^host_recover_pie/$', host_recover_pie, name='主机回收饼图'),
    url('^game_server_off_pie/$', game_server_off_pie, name='区服下线饼图'),
    url('^modsrv_opentime_pie/$', modsrv_opentime_pie, name='修改开服时间饼图'),
    url('^system_cron_pie/$', system_cron_pie, name='系统作业饼图'),
    url('^game_server_action_pie/$', game_server_action_pie, name='区服管理操作饼图数据'),
    url('^host_initialize_pie/$', host_initialize_pie, name='主机初始化饼图数据'),
    url('^game_server_merge_pie/$', game_server_merge_pie, name='合服计划饼图数据'),
    url('^game_server_install_pie/$', game_server_install_pie, name='装服计划饼图数据'),
    url('^version_update_pie/$', version_update_pie, name='版本更新饼图数据'),
]
