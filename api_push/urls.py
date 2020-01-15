# -*- encoding: utf-8 -*-

from django.conf.urls import url
from api_push import views
from rest_framework.urlpatterns import format_suffix_patterns


urlpatterns = [
    url(r'^get_lockstatus/$', views.get_lockstatus.as_view(), name='获取推送系统锁状态'),
    url(r'^get_lock/$', views.get_lock.as_view(), name='为推送系统加锁'),
    url(r'^get_unlock/$', views.get_unlock.as_view(), name='推送系统解锁'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
