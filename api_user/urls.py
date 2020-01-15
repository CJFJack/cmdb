# -*- encoding: utf-8 -*-

from django.conf.urls import url
from api_user import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    url(r'^group_users/$', views.GroupUsers.as_view(), name='部门用户'),  # 已作废
    url(r'^user_add/$', views.UserAdd.as_view(), name='添加cmdb用户接口'),
    url(r'^user_confirm/$', views.UserConfirm.as_view(), name='确认cmdb用户报到入职接口'),
    url(r'^user_delete/$', views.UserDel.as_view(), name='删除cmdb用户接口'),
    url(r'^role_info$', views.RoleInfo.as_view(), name='删除cmdb用户接口'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
