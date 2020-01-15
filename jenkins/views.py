from django.shortcuts import redirect
from jenkins.models import JenkinsCookie
from cmdb.settings import JENKINS_40_8_URL
from cmdb.settings import JENKINS_40_15_URL
# from cmdb.settings import JENKINS_yuanli_extranal_URL


def jenkins_40_8(request):
    ip_or_domain = request.get_host().split(':')[0]
    redirect_url = 'http://' + ip_or_domain + ':' + JENKINS_40_8_URL.split(':')[-1]
    response = redirect(redirect_url)
    user = request.user
    cookie_obj, created = JenkinsCookie.objects.get_or_create(user=user, jenkins_ip='192.168.40.8')
    response['Set-Cookie'] = cookie_obj.cookie
    return response


def jenkins_40_15(request):
    ip_or_domain = request.get_host().split(':')[0]
    redirect_url = 'http://' + ip_or_domain + ':' + JENKINS_40_15_URL.split(':')[-1]
    response = redirect(redirect_url)
    user = request.user
    cookie_obj, created = JenkinsCookie.objects.get_or_create(user=user, jenkins_ip='192.168.40.15')
    response['Set-Cookie'] = cookie_obj.cookie
    return response


# def jenkins_yuanli_extranal(request):
#     ip_or_domain = request.get_host().split(':')[0]
#     redirect_url = 'https://' + ip_or_domain + '/j3/'
#     response = redirect(redirect_url)
#     user = request.user
#     cookie_obj, created = JenkinsCookie.objects.get_or_create(user=user, jenkins_ip='jenkins.yl666.yl')
#     response['Set-Cookie'] = cookie_obj.cookie
#     return response
