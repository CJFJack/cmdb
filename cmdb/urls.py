"""cy_devops URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from users.views import *
from assets.views import *
from mysql.views import *
from ops.views import *
from views import index
from views import cmdb_release_notes
from django.contrib import admin

urlpatterns = [
    url(r'^assets/', include('assets.urls')),
    url(r'^mysql/', include('mysql.urls')),
    url(r'^ops/', include('ops.urls')),
    url(r'^error_version/$', error_version, name='error_version'),
    url(r'^users/', include('users.urls')),
    url(r'^api/', include('api.urls')),
    url(r'^api_push/', include('api_push.urls')),
    url(r'^api_clean_user/', include('api_clean_user.urls')),
    url(r'^api_user/', include('api_user.urls')),
    url(r'^api_svn/', include('api_svn.urls')),
    url(r'^api_mysql/', include('api_mysql.urls')),
    url(r'^api_web/', include('api_web.urls')),
    url(r'^myworkflows/', include('myworkflows.urls')),
    url(r'^it_assets/', include('it_assets.urls')),
    url(r'^webapi/', include('webapi.urls')),
    url(r'^user_login', user_login, name='登录页面'),
    url(r'^user_logout', user_logout, name='退出登录'),
    # url(r'^user_register', user_register, name='注册页面'),
    url(r'^forget_password', forget_password, name='忘记密码页面'),
    url(r'^$', index, name='首页'),
    url(r'^admin/', admin.site.urls),  # django-admin管理页面
    url(r'^dashboard/', include('dashboard.urls')),
    url(r'^api_wechat/', include('api_wechat.urls')),
    url(r'^jenkins/', include('jenkins.urls')),
    url(r'^txcloud/', include('txcloud.urls')),
    url(r'^cmdb_release_notes/$', cmdb_release_notes, name='cmdb更新日志'),
    url(r'^zabbix/', include('zabbix.urls')),
]
