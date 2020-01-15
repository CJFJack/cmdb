# -*- encoding: utf-8 -*-
from assets.models import Host
from assets.models import Area
from myworkflows.models import ServerHotUpdate
from myworkflows.models import ClientHotUpdate

import json
from requests.packages.urllib3.util import Retry
from requests.adapters import HTTPAdapter
from requests import Session
from cmdb.settings import PRODUCTION_ENV
from tasks import send_weixin_rebot


def make_host_recover_email_content(obj):
    """生成机器回收任务完成后通知负责人回收云平台主机邮件内容"""
    td_template = ''
    host_ip_list = [detail.ip for detail in obj.hostcompressiondetail_set.all()]
    hosts = Host.objects.filter(telecom_ip__in=host_ip_list)
    for host in hosts:
        td_template += "<tr><td>" + host.belongs_to_game_project.project_name + "</td>" + \
                       "<td>" + host.belongs_to_room.area.chinese_name + '-' + host.belongs_to_room.room_name + "</td>" + \
                       "<td>" + host.get_host_class_display() + "</td>" + \
                       "<td>" + host.telecom_ip + "</td></tr>"

    url = "https://192.168.100.66/myworkflows/host_compression_apply_list/"
    template = "<html>" + \
               "<head>" + \
               "<meta charset=\"utf-8\">" + \
               "</head>" + \
               "<body>" + \
               "<h3>机器回收申请工单，内容如下:</h3>" + \
               "<p><b>工单申请人: </b>%s</p>" + \
               "<p><b>标题: </b>%s</p>" + \
               "<p><b>回收机器列表如下:</b></p>" + \
               "<table border=\"1\" cellspacing=\"0\" cellpadding=\"5\">" + \
               "<thead>" + \
               "<th>项目</th>" + \
               "<th>机房</th>" + \
               "<th>机器归属</th>" + \
               "<th>外网电信IP</th>" + \
               "</thead>" + \
               "<tbody>" + \
               td_template + \
               "</tbody>" + \
               "</table>" + \
               "<p><b>请确认以上机器是否需要登录云平台进行机器回收，详情请登录cmdb查看工单明细</b></p>" + \
               "<a href=\"%s\">%s</a>" + \
               "</body>" + \
               "</html>"
    content = template % (obj.apply_user, obj.title, url, url)
    return content


def make_host_compression_result_email_content(obj, action_type):
    """生成主机迁服回收结果邮件内容"""
    td_template = ''
    for detail in obj.hostcompressiondetail_set.all():
        td_template += "<tr><td>" + detail.get_host_obj().belongs_to_game_project.project_name + "</td>" + \
                       "<td>" + detail.get_host_obj().belongs_to_room.area.chinese_name + '-' + detail.get_host_obj().belongs_to_room.room_name + "</td>" + \
                       "<td>" + detail.get_host_obj().telecom_ip + "</td></tr>"

    url = "https://192.168.100.66/myworkflows/host_compression_apply_list/"
    template = "<html>" + \
               "<head>" + \
               "<meta charset=\"utf-8\">" + \
               "</head>" + \
               "<body>" + \
               "<h3>主机迁服 / 回收申请:</h3>" + \
               "<p><b>工单申请人: </b>%s</p>" + \
               "<p><b>标题: </b>%s</p>" + \
               "<p><b>机器列表如下:</b></p>" + \
               "<table border=\"1\" cellspacing=\"0\" cellpadding=\"5\">" + \
               "<thead>" + \
               "<th>项目</th>" + \
               "<th>机房</th>" + \
               "<th>外网电信IP</th>" + \
               "</thead>" + \
               "<tbody>" + \
               td_template + \
               "</tbody>" + \
               "</table>" + \
               "<p><b>以上机器已经<span style=\"color: red;\">%s</span>完成</b></p>" + \
               "<p>详情请登录<a href=\"%s\">cmdb</a>查看</p>" + \
               "</body>" + \
               "</html>"
    content = template % (obj.apply_user, obj.title, action_type, url)
    return content


def make_game_server_off_email_content(content, obj):
    """生成区服下架计划邮件内容"""
    td_template = ''
    url = "https://192.168.100.66/ops/game_server_off_list/"
    for task in obj.gameserveroffdetail_set.all():
        td_template += "<tr><td>" + task.game_server.project.project_name + "</td>" + \
                       "<td>" + task.game_server.host.belongs_to_room.area.chinese_name + "</td>" + \
                       "<td>" + task.game_server.srv_id + "</td>" + \
                       "<td>" + task.get_status_display() + "</td></tr>"

    template = "<html>" + \
               "<head>" + \
               "<meta charset=\"utf-8\">" + \
               "</head>" + \
               "<body>" + \
               "<h3>%s</h3>" + \
               "<table border=\"1\" cellspacing=\"0\" cellpadding=\"5\">" + \
               "<thead>" + \
               "<th>项目</th>" + \
               "<th>地区</th>" + \
               "<th>cmdb区服Id</th>" + \
               "<th>下线结果</th>" + \
               "</thead>" + \
               "<tbody>" + \
               td_template + \
               "</tbody>" + \
               "</table>" + \
               "<p><b>详情请登录cmdb查看工单明细</b></p>" + \
               "%s" + \
               "</body>" + \
               "</html>"

    content = template % (content, url)
    return content


def make_modsrv_opentime_email_content(content, obj):
    """生成修改开服时间计划邮件内容"""
    td_template = ''
    url = "https://192.168.100.66/ops/modify_srv_open_time_schedule_list/"
    for task in obj.modifyopensrvscheduledetail_set.all():
        td_template = "<td>" + task.game_server.project.project_name + "</td>" + \
                      "<td>" + task.game_server.host.belongs_to_room.area.chinese_name + "</td>" + \
                      "<td>" + task.game_server.srv_id + "</td>" + \
                      "<td>" + task.get_status_display() + "</td>"

    template = "<html>" + \
               "<head>" + \
               "<meta charset=\"utf-8\">" + \
               "</head>" + \
               "<body>" + \
               "<h3>%s</h3>" + \
               "<table border=\"1\" cellspacing=\"0\" cellpadding=\"5\">" + \
               "<thead>" + \
               "<th>项目</th>" + \
               "<th>地区</th>" + \
               "<th>cmdb区服Id</th>" + \
               "<th>修改开服时间结果</th>" + \
               "</thead>" + \
               "<tbody>" + \
               td_template + \
               "</tbody>" + \
               "</table>" + \
               "<p><b>详情请登录cmdb查看工单明细</b></p>" + \
               "%s" + \
               "</body>" + \
               "</html>"

    content = template % (content, url)
    return content


def send_robot_message(content_object):
    """热更新完成后调用微信群机器人接口发送消息"""
    try:
        if isinstance(content_object, ServerHotUpdate):
            update_type = '后端'
            version = content_object.server_version
        elif isinstance(content_object, ClientHotUpdate):
            update_type = '前端'
            version = content_object.client_version
        else:
            update_type = '未知更新类型'
            version = ''

        area_name = content_object.area_name
        area = Area.objects.filter(short_name=content_object.area_name)
        if area:
            area_name = area[0].chinese_name

        status = content_object.get_status_display()
        if status == '更新成功':
            update_result = '>更新结果: <font color=\"info\">{}</font> \n'.format(content_object.get_status_display())
        else:
            update_result = '>更新结果: <font color=\"warning\">{}</font> \n'.format(content_object.get_status_display())

        send_info = "<font color=\"warning\">[{}更新]</font> \n".format(update_type) + \
                    update_result + \
                    ">项目: <font color=\"comment\">{}</font> \n".format(content_object.project.project_name) + \
                    ">地区: <font color=\"comment\">{}</font> \n".format(area_name) + \
                    ">发起人: <font color=\"comment\">{}</font> \n".format(content_object.creator.username)

        if isinstance(content_object, ClientHotUpdate):
            content = json.loads(content_object.content)
            if 'xxxxxxx' in version:
                cdn_dir_version = '\n'.join(list(set([c.get('cdn_dir', '') + ' : ' + c.get('version', '') for c in content])))
            else:
                cdn_dir_version = '\n'.join(list(set([c.get('cdn_dir', '') + ' : ' + version for c in content])))
            send_info += '>cdn目录版本: <font color=\"comment\">{}</font> \n'.format(cdn_dir_version)
        else:
            send_info += '>版本: <font color=\"comment\">{}</font> \n'.format(version)

        send_info += ">标题: <font color=\"comment\">{}</font> \n".format(content_object.title)
        send_info += ">原因: <font color=\"comment\">{}</font> \n".format(content_object.reason if content_object.reason else '无')

        if PRODUCTION_ENV:
            url = content_object.project.wx_robot
        else:
            url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=9fc0c5b2-90f3-4a30-8537-70b67c24d247'
        if not url:
            return False, '没有配置微信机器人接口地址'

        success, result = send_weixin_rebot(url, send_info)
        if not success:
            raise Exception(result)

        return True, '发送微信机器人通知成功'
    except Exception as e:
        return False, str(e)
