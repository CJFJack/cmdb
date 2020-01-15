# -*- encoding: utf-8 -*-

from django.conf.urls import url
from api_mysql import views
from rest_framework.urlpatterns import format_suffix_patterns


urlpatterns = [
    url(r'^Instance.Create/$', views.InstanceCreate.as_view(), name='增加实例'),
    url(r'^Instance.Modify/$', views.InstanceModify.as_view(), name='修改实例'),
    url(r'^Instance.Delete/$', views.InstanceDelete.as_view(), name='修改实例'),
    url(r'^Instance.List/$', views.InstanceList.as_view(), name='查看实例'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
