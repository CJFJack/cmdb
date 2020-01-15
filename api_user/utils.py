# -*- coding: utf-8 -*-
from users.models import OrganizationMptt


def make_new_user_info_share_content(org_id):
    """生成新员工信息，用于发送企业微信，及页面展示"""
    org = OrganizationMptt.objects.get(pk=org_id)
    with open('users/users_share_info_template.txt', 'r') as f:
        template_content = f.read()
    return template_content.format(chinese_name=org.name, pinyin=org.user.first_name, ent_qq=str(org.ent_qq or ''),
                                   ent_email=str(org.ent_email or ''))
    # return '新员工入职信息: {chinese_name}\n\n温馨提示:\ncmdb账号: ({pinyin}(或者 {chinese_name})) 密码: redhat(首次登录后会提示强制修改)\n企业QQ: {qq_num} 密码: Ylhy@20181211(首次登录后会提示强制修改密码)\n企业邮箱账号: {ent_email} 密码: Ylhy@20181211(首次登录后会提示强制修改密码)\n其中公司WiFi: Cy-public 账号密码已经发送到你的企业邮箱\n当前cmdb系统支持修改企业QQ密码、企业邮箱密码、SVN密码\n如有疑问请联系运维网络组!!!\n【备注:如果是创畅、海南创娱、广州创娱、广州起源新入职员工请打开OpenVPN（账号已发至企业邮箱）后再访问以下网址】\n1.进入cmdb原力互娱运维管理系统: https://cmdb.cy666.com/user_login/\n2.电脑故障申报以及办公电脑和配件申请的方法: http://192.168.100.100:8090/pages/viewpage.action?pageId=2818112\n3.企业邮箱登录网址: https://exmail.qq.com/cgi-bin/loginpage\n4.修改企业QQ密码、企业邮箱密码、SVN密码: http://192.168.100.100:8090/pages/viewpage.action?pageId=2818091\n'.format(
    #     chinese_name=org.name, pinyin=org.user.first_name, qq_num=str(org.ent_qq or ''),
    #     ent_email=str(org.ent_email or ''))
