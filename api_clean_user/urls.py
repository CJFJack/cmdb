# -*- encoding: utf-8 -*-

from django.conf.urls import url
from api_clean_user import views
from rest_framework.urlpatterns import format_suffix_patterns


urlpatterns = [
    url(r'^clean_user_callback/$', views.CleanUserCallBack.as_view(), name='清除用户服务器权限回调'),
    url(r'^clean_user_by_project_callback/$', views.CleanUserByProjectCallBack.as_view(), name='根据项目清除用户服务器权限回调'),
    url(r'^get_not_active_user/$', views.GetNotActiveUser.as_view(), name='获取离职用户列表'),
    url(r'^test/$', views.Test.as_view(), name='获取离职用户列表'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
