# -*- encoding: utf-8 -*-
import requests
from pyquery import PyQuery as pq
from cmdb.logs import JenkinsLoginLog


def get_jenkins_cookie(username, password, jenkins_url, jenkins_host):
    """模拟登录jenkins获取cookie"""
    success = True
    msg = 'ok'
    Cookie = ''
    log = JenkinsLoginLog()
    try:
        # 获取登录需要的cookie和Jenkins_Crumb
        res = requests.get(jenkins_url + '/login?from=%2F')
        response_headers = res.headers
        Cookie = response_headers['Set-Cookie']
        html = res.content.decode('utf-8')
        doc = pq(html)
        doc("script:contains('Jenkins-Crumb')")
        Jenkins_Crumb = doc("script:contains('Jenkins-Crumb')").text().split('\"')[3]

        # 请求登录
        login_data = {
            'j_username': username,
            'j_password': password,
            'from': '/',
            'Jenkins-Crumb': Jenkins_Crumb,
            'json': {'j_username': username, 'j_password': password, 'remember_me': True, 'from': '/',
                     'Jenkins-Crumb': Jenkins_Crumb},
            'Submit': '登录'
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0',
            'Cookie': Cookie,
            'Host': jenkins_host,
            'Origin': jenkins_url,
            'Referer': jenkins_url + '/login?from=/',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Upgrade-Insecure-Requests': '1',
            'Accept-Language': 'zh-CN,zh;q=0.9'
        }
        res = requests.post(jenkins_url + '/j_acegi_security_check', data=login_data, headers=headers,
                            allow_redirects=False)
        response_headers = res.headers
        Cookie = response_headers['Set-Cookie']
        Location = response_headers['Location']
        if 'loginError' in Location:
            raise Exception('帐号或密码不正确，登录失败')

        log.logger.info('{} 登录 {} 成功获取cookie'.format(username, jenkins_host))

    except Exception as e:
        success = False
        msg = str(e)
        log.logger.error('{} 登录 {} 失败，原因：{}'.format(username, jenkins_host, msg))

    finally:
        return success, msg, Cookie
