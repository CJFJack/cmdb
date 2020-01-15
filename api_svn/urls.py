# -*- encoding: utf-8 -*-

from django.conf.urls import url
from api_svn import views
from rest_framework.urlpatterns import format_suffix_patterns


urlpatterns = [
    url(r'^project_svn/$', views.ProjectSvn.as_view(), name='项目的svn仓库'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
