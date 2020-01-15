from django.conf.urls import url
from zabbix.views import *

urlpatterns = [
    url(r'^zabbix/$', zabbix, name='zabbix'),
]
