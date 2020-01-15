from django.conf.urls import url
from jenkins.views import *

urlpatterns = [
    url(r'^jenkins_40_8/$', jenkins_40_8, name='jenkins_40.8'),
    url(r'^jenkins_40_15/$', jenkins_40_15, name='jenkins_40.15'),
]
