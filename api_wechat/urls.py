from django.conf.urls import url, include
from api_wechat import views

urlpatterns = [
    url(r'^auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^WechatMsgReceive$', views.WechatMsgReceiveAPI.as_view(), name='微信信息回调接口'),
]