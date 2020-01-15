# -*- encoding: utf-8 -*-

from celery import Celery

app = Celery()

import celeryconfig

app.config_from_object(celeryconfig)

# from myworkflows.mails import SendEmail
# from myworkflows.mails import RecieveMail


import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import imapy
from imapy.query_builder import Q as IQ

import re
import uuid

from concurrent import futures
import threading

import os
import operator

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cmdb.settings")

import django

django.setup()

from django.db.models import Q

from myworkflows.models import WorkflowStateEvent
from myworkflows.utils import do_transition, get_state_user, make_email_notify

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from cmdb.logs import *
# from cmdb.mail_notify import hot_update_mail_notify
# from cmdb.qq_notify import hot_update_qq_notify
from cmdb.settings import PRODUCTION_ENV
from cmdb.settings import MSG_CHANNEL
from myworkflows.utils import make_email
from myworkflows.utils import SVN_EXCUTORS
from myworkflows.utils import format_svn
from myworkflows.utils import ws_notify
from myworkflows.utils import get_sor
from myworkflows.utils import get_next_hot_update
from myworkflows.utils import get_qq_notify
from myworkflows.utils import get_wx_notify
from myworkflows.utils import get_hot_update_all_related_user
from myworkflows.utils import get_workflow_state_order
from myworkflows.utils import get_wse
from myworkflows.utils import get_weixin_api_token
from myworkflows.utils import check_valid_wx_token
from myworkflows.utils import ws_update_game_server_action
from myworkflows.utils import format_game_server_action_result
from myworkflows.utils import format_hot_update_file_list
from myworkflows.utils import write_host_compression_log
from myworkflows.utils import ws_update_host_compression_list
from myworkflows.utils import get_user_workflow_apply
from myworkflows.utils import cancel_workflow_apply
from myworkflows.utils import get_wx_task_card_data
from myworkflows.utils import update_wx_taskcard_status
from myworkflows.utils import ws_update_game_server_action_record
from myworkflows.utils import format_game_server_action_data
from myworkflows.utils import wechat_account_check
from myworkflows.utils import version_update_check_push_dir_util
from myworkflows.models import *
from myworkflows.config import *
from myworkflows.rsync_conf import *
from myworkflows.exceptions import HotUpdateBlock
from myworkflows.rsync_utils import get_rsync_path
from myworkflows.rsync_utils import get_rsync_config
from myworkflows.hot_server_utils import revise_server_list
from assets.models import *
from assets.utils import ws_update_task_result
from assets.utils import format_saltstack_configfile_path
from assets.utils import format_saltstack_execute_result
from assets.utils import write_host_initialize_log
from assets.utils import saltstack_test_ping
from assets.utils import ws_update_host_initialize_list
from assets.utils import format_saltstack_host_initialize_result
from assets.utils import format_saltstack_host_check_result
from assets.TXcloudCdnRefresh import *
from assets.BScloudCdnRefresh import *
from users.models import UserProfileHost

from ops.models import InstallGameServer
from ops.models import GameServerOff
from ops.models import ModifyOpenSrvSchedule
from ops.models import GameServerMergeSchedule
from ops.models import InstallGameServerRecord
from ops.utils import game_install_notify
from ops.utils import write_game_server_off_log
from ops.utils import ws_update_game_server_off_list
from ops.utils import write_modify_srv_open_time_schedule_log
from ops.utils import ws_modify_srv_open_time_schedule_list

from txcloud.TXCloud import TXCloudTC3
from txcloud.utils import make_purchase_tx_server_email
from txcloud.utils import make_purchase_tx_mysql_email
from txcloud.exceptions import TxCloudError

from mysql.models import MysqlInstance
from mysql.utils import ws_update_mysql_list
from api_wechat.wx_callback_whitelist import wx_whitelist_ip

import hashlib
from collections import defaultdict

import requests
from requests.packages.urllib3.util import Retry
from requests.adapters import HTTPAdapter
from requests import Session
import shutil

from test_tasks import file_push_test_8
from test_tasks import file_push_test_15
from test_tasks import file_push_test_cc
from test_tasks import file_push_test_slqy3d_cn
from test_tasks import do_test_hot_client
from test_tasks import do_test_hot_server

from myworkflows.myredis import load_to_redis

from mysql.mysql_utils import add_instance_user_privileges
from mysql.mysql_utils import remove_instance_account
from mysql.mysql_utils import remove_instance_account_update_info

ml = MailLog()
sqq = SendQQLog()
mrl = MailReceivLog()
ent_email = AddEntEmailAccountLog()
ent_qq = AddEntQQAccountLog()

from django.db import connections

import json
from datetime import datetime
from datetime import timedelta
import time

import traceback

from users.outer_api import get_ops_manager_from_user
from users.models import UserClearStatus, OrganizationMptt, Profile, Role
from users.channels_utils import ws_notify_clean_user
from netmiko import ConnectHandler
from assets.salt_api_tasks import salt_init
from django.db import transaction
from django.forms.models import model_to_dict


# hot_update_log = HotUpdateLog()


def close_old_connections():
    for conn in connections.all():
        conn.close_if_unusable_or_obsolete()


class SendEmail(object):

    def __init__(self, to_list, subject, content):
        self._host = 'smtp.exmail.qq.com'
        self._port = 465
        self._user = 'devopsteam@forcegames.cn'
        self._passwd = 'Khgey@520199'
        send_list = []
        for x in to_list:
            for y in x.split(','):
                send_list.append(y)
        self.to_list = send_list
        self.subject = subject
        self.content = content

    def send(self):
        '发送邮件'
        try:
            print(self.to_list)
            server = smtplib.SMTP_SSL(self._host, self._port)
            server.login(self._user, self._passwd)
            server.sendmail("<%s>" % self._user, self.to_list, self.get_attach())
            print('send mail to %s ok' % (','.join(self.to_list)))
            ml.logger.info('%s: send mail to %s ok' % (self.subject, ','.join(self.to_list)))
        except Exception as e:
            print(e)
            ml.logger.error('%s: send mail failed' % (self.subject))
        finally:
            server.close()

    def get_attach(self):
        '构造邮件内容'
        attach = MIMEMultipart()
        txt = MIMEText(self.content, 'html', 'utf-8')
        attach.attach(txt)

        # 主题,最上面的一行
        attach["Subject"] = self.subject

        # 显示在发件人
        attach["From"] = "DevOps Team<%s>" % self._user

        # 收件人列表
        attach["To"] = ";".join(self.to_list)

        return attach.as_string()


class RecieveMail(object):
    """收取邮件，根据匹配subject来执行审批
    """

    def __init__(self):

        self._host = 'imap.exmail.qq.com'
        self._port = 993
        self._username = 'devopsteam@forcegames.cn'
        self._password = 'Khgey@520199'

    def recieve_unseen(self, count=5):
        '收取未读的邮箱,这里默认每次只收取5个'
        try:
            mrl.logger.info('开始连接imap.exmail.qq.com...')
            box = imapy.connect(
                host=self._host,
                port=self._port,
                username=self._username,
                password=self._password,
                ssl=True,
                timeout=30,
            )
        except Exception as e:
            mrl.logger.error('连接邮件imap服务器出错:%s' % (str(e)))
            return None

        q = IQ()

        emails = box.folder('INBOX').emails(
            q.unseen()
        )[0:count]

        emails = list(reversed(emails))

        p = re.compile(r'.*#工单流程')

        # 重新连接数据库
        close_old_connections()

        for mail in emails:
            try:
                subject = mail['subject']
                from_email = mail['from_email']
                user = User.objects.filter(email__icontains=from_email)
                if user:
                    user = user[0]
                else:
                    raise Exception('邮箱匹配用户失败，请核实邮箱地址 {}'.format(from_email))
                username = user.username
                # 如果匹配到的是工单流程的主题的邮件，则需要处理
                # 如果不是，这里就标记为已读
                if p.match(subject):
                    user = User.objects.get(username=username)
                    wse = subject.split("#")[3].split('=')[1]  # 'Re:#工单流程#剑雨后端SVN申请#wse=92' ==> 92
                    wse = WorkflowStateEvent.objects.get(id=int(wse))
                    reply = mail['text'][0]['text'].strip()
                    if reply.startswith('yes'):
                        transition = wse.state.transition.get(condition='同意')
                        mrl.logger.info('%s: %s: 同意处理' % (subject, username))

                        # 获取本轮审批有权先审批的user object列表
                        approve_user_list = [u for u in wse.users.all()]
                        # 转化流程状态
                        msg, success, new_wse = do_transition(wse, transition, user)

                        # 如果审批成功
                        if success:
                            # 审批完成后更新企业微信任务卡片按钮状态
                            touser = [u.first_name for u in wse.users.all()]
                            if touser:
                                update_wx_taskcard_status(touser, wse)

                            # 从审批人列表中排除当前审批人
                            approve_user_list.remove(user)
                            # 如果前一审批节点有多个审批人，则把最新审批结果通知到除当前审批人之外的审批人
                            if approve_user_list:
                                # 邮件通知
                                to_list = [x.email for x in approve_user_list]
                                subject = wse.content_object.title + '#审批结果'
                                content = '你的小伙伴： {}，已经 {} 工单申请#{}'.format(user.username, transition.condition,
                                                                           wse.content_object.title)
                                send_mail.delay(to_list, subject, content)
                                # 都要发送qq弹框提醒
                                users = ','.join([x.first_name for x in approve_user_list])
                                data = get_qq_notify()
                                send_qq.delay(users, subject, subject, content, '')
                                # 发送wx弹框提醒
                                wx_users = '|'.join([x.first_name for x in approve_user_list])
                                send_weixin_message.delay(touser=wx_users, content=content)

                            # 批完成后把sor中的users审批用户复制到wse的users审批用户中
                            sor = get_sor(new_wse.state, new_wse.content_object)
                            if sor:
                                users = tuple(sor.users.all())
                                new_wse.users.add(*users)

                            wse_users = new_wse.users.all()

                            if wse_users:
                                if isinstance(new_wse.content_object, ClientHotUpdate) or \
                                        isinstance(new_wse.content_object, ServerHotUpdate):
                                    # 邮件通知
                                    to_list = [x.email for x in wse_users if not x.profile.hot_update_email_approve]
                                    if to_list:
                                        subject, content = make_email_notify(True)
                                        send_mail.delay(to_list, subject, content)

                                    # 邮件审批
                                    approve_list = [x.email for x in wse_users if x.profile.hot_update_email_approve]
                                    if approve_list:
                                        subject, content = make_email(new_wse)
                                        send_mail.delay(approve_list, subject, content)
                                else:
                                    subject, content = make_email_notify(True)
                                    to_list = [x.email for x in wse_users]
                                    send_mail.delay(to_list, subject, content)
                                # 都要发送qq弹框和wechat消息提醒
                                users = ','.join([x.first_name for x in wse_users])
                                wx_users = '|'.join([x.first_name for x in wse_users if
                                                     not x.organizationmptt_set.first().wechat_approve])
                                data = get_qq_notify()
                                if users:
                                    send_qq.delay(
                                        users, data['window_title'], data['tips_title'], data['tips_content'],
                                        data['tips_url'])
                                # 如果是版本更新单，就发送微信文字提醒
                                if isinstance(new_wse.content_object, VersionUpdate):
                                    if wx_users:
                                        data = get_wx_notify()
                                        send_weixin_message.delay(touser=wx_users, content=data)

                                # 如果不是版本更新单，发送企业微信审批
                                if not isinstance(new_wse.content_object, VersionUpdate):
                                    touser = '|'.join([u.first_name for u in wse_users if
                                                       u.is_active and u.organizationmptt_set.first().wechat_approve == 1])
                                    if touser:
                                        result = get_wx_task_card_data(touser, new_wse)
                                        if result['success']:
                                            send_task_card_to_wx_user.delay(touser, result['data'])

                            else:
                                # 自动执行前端热更新
                                if isinstance(new_wse.content_object, ClientHotUpdate) and new_wse.state.name == '完成':
                                    # 工单完成以后，修改工单的状态
                                    content_object = new_wse.content_object
                                    content_object.status = '4'
                                    content_object.save()
                                    ws_notify()

                                    # 如果当前项目和地区没有锁，则找到下一个更新去执行
                                    status_list = [x.ops.status for x in
                                                   content_object.clienthotupdatersynctask_set.all()]
                                    if len(list(set(status_list))) == 1 and '0' in status_list:
                                        # do_hot_client.delay(new_wse.id)
                                        msg, next_hot_update = get_next_hot_update(
                                            content_object.project, content_object.area_name)
                                        if next_hot_update:
                                            if next_hot_update.status == '4':
                                                do_hot_update(next_hot_update)
                                        else:
                                            """更新任务没有自动执行原因字段"""
                                            content_object.no_auto_execute_reason = msg
                                            content_object.save(update_fields=['no_auto_execute_reason'])
                                            # 发送邮件告警
                                            # to_list = list(set([x.email for x in content_object.project.related_user.all()]))
                                            to_list = list(
                                                set([x.email for x in content_object.project.get_relate_role_user()]))
                                            subject = '热更新审批完成后没有自动执行'
                                            content = '项目:{} 地区:{}，热更新:{} 没有自动执行,请查看原因'.format(
                                                content_object.project.project_name, content_object.area_name,
                                                content_object.title)
                                            send_mail.delay(to_list, subject, content)
                                    else:
                                        # 热更新审批完成后没有触发执行
                                        # 需要发送告警给相应的运维负责人
                                        # users = ','.join([x.first_name for x in new_wse.content_object.project.related_user.all()])
                                        users = ','.join([x.first_name for x in
                                                          new_wse.content_object.project.get_relate_role_user()])
                                        # wx_users = '|'.join([x.first_name for x in new_wse.content_object.project.related_user.all()])
                                        wx_users = '|'.join([x.first_name for x in
                                                             new_wse.content_object.project.get_relate_role_user()])
                                        window_title = '项目地区锁:热更新审批完成后不能自动执行'
                                        tips_title = '项目地区锁:热更新审批完成后不能自动执行'
                                        tips_content = '项目:{} 地区:{} 已经上锁，热更新:{} 不能自动执行'.format(
                                            content_object.project.project_name, content_object.area_name,
                                            content_object.title)
                                        tips_url = 'https://192.168.100.66/myworkflows/hot_server_list/'
                                        send_qq.delay(
                                            users, window_title, tips_title, tips_content, tips_url)
                                        send_weixin_message.delay(
                                            wx_users, tips_title + tips_content + tips_url)

                                        # 发送邮件告警
                                        # to_list = [x.email for x in content_object.project.related_user.all()]
                                        to_list = list(
                                            set([x.email for x in content_object.project.get_relate_role_user()]))
                                        subject = '项目地区锁:热更新审批完成后不能自动执行'
                                        content = '项目:{} 地区:{} 已经上锁，热更新:{} 不能自动执行'.format(
                                            content_object.project.project_name, content_object.area_name,
                                            content_object.title)
                                        send_mail.delay(to_list, subject, content)

                                        """更新任务没有自动执行原因字段"""
                                        content_object.no_auto_execute_reason = tips_content
                                        content_object.save(update_fields=['no_auto_execute_reason'])

                                # 自动执行后端热更新
                                if isinstance(new_wse.content_object, ServerHotUpdate) and new_wse.state.name == '完成':
                                    # 工单完成以后，修改工单的状态
                                    content_object = new_wse.content_object
                                    content_object.status = '4'
                                    content_object.save()
                                    ws_notify()

                                    # 加载热更新的区服数据到redis中
                                    # load_to_redis(new_wse.content_object)

                                    # 如果当前项目和地区没有锁，则直接发送到任务队列里面
                                    status_list = [x.ops.status for x in
                                                   content_object.serverhotupdatersynctask_set.all()]
                                    if len(list(set(status_list))) == 1 and '0' in status_list:
                                        msg, next_hot_update = get_next_hot_update(
                                            content_object.project, content_object.area_name)
                                        if next_hot_update:
                                            if next_hot_update.status == '4':
                                                do_hot_update(next_hot_update)
                                        else:
                                            """更新任务没有自动执行原因字段"""
                                            content_object.no_auto_execute_reason = msg
                                            content_object.save(update_fields=['no_auto_execute_reason'])
                                            # 发送邮件告警
                                            # to_list = [x.email for x in content_object.project.related_user.all()]
                                            to_list = list(
                                                set([x.email for x in content_object.project.get_relate_role_user()]))
                                            subject = '热更新审批完成后没有自动执行'
                                            content = '项目:{} 地区:{}，热更新:{} 没有自动执行,请查看原因: {}'.format(
                                                content_object.project.project_name, content_object.area_name,
                                                content_object.title, msg)
                                            send_mail.delay(to_list, subject, content)
                                    else:
                                        # 热更新审批完成后没有触发执行
                                        # 需要发送告警给相应的运维负责人
                                        # users = ','.join([x.first_name for x in new_wse.content_object.project.related_user.all()])
                                        users = ','.join([x.first_name for x in
                                                          new_wse.content_object.project.get_relate_role_user()])
                                        # wx_users = '|'.join([x.first_name for x in new_wse.content_object.project.related_user.all()])
                                        wx_users = '|'.join([x.first_name for x in
                                                             new_wse.content_object.project.get_relate_role_user()])
                                        window_title = '项目地区锁:热更新审批完成后不能自动执行'
                                        tips_title = '项目地区锁:热更新审批完成后不能自动执行'
                                        tips_content = '项目:{} 地区:{} 已经上锁，热更新:{} 不能自动执行'.format(
                                            content_object.project.project_name, content_object.area_name,
                                            content_object.title)
                                        tips_url = 'https://192.168.100.66/myworkflows/hot_server_list/'
                                        send_qq.delay(
                                            users, window_title, tips_title, tips_content, tips_url)
                                        send_weixin_message.delay(
                                            wx_users, tips_title + tips_content + tips_url)

                                        # 发送邮件告警
                                        # to_list = [x.email for x in content_object.project.related_user.all()]
                                        to_list = list(
                                            set([x.email for x in content_object.project.get_relate_role_user()]))
                                        subject = '项目地区锁:热更新审批完成后不能自动执行'
                                        content = '项目:{} 地区:{} 已经上锁，热更新:{} 不能自动执行'.format(
                                            content_object.project.project_name, content_object.area_name,
                                            content_object.title)
                                        send_mail.delay(to_list, subject, content)

                                        """更新任务没有自动执行原因字段"""
                                        content_object.no_auto_execute_reason = tips_content
                                        content_object.save(update_fields=['no_auto_execute_reason'])

                            mrl.logger.info('%s: %s: 处理结果:%s %s' % (subject, username, msg, success))
                        else:
                            mrl.logger.info('%s: %s: 处理结果:%s %s' % (subject, username, msg, success))
                    elif reply.startswith('no'):
                        transition = wse.state.transition.get(condition='拒绝')
                        mrl.logger.info('%s: %s: 拒绝处理' % (subject, username))
                        msg, success, new_wse = do_transition(wse, transition, user, opinion='邮件拒绝')

                        if success:
                            # 审批完成后更新企业微信任务卡片按钮状态
                            touser = [u.first_name for u in wse.users.all()]
                            if touser:
                                update_wx_taskcard_status(touser, wse)

                            to_list = [new_wse.creator.email]
                            subject, content = make_email_notify(False)
                            send_mail.delay(to_list, subject, content)

                            # 发送qq弹框提醒
                            users = new_wse.creator.first_name if User.objects.get(
                                id=new_wse.creator.id).is_active else ''
                            wx_users = new_wse.creator.first_name if User.objects.get(
                                id=new_wse.creator.id).is_active else ''

                            window_title = "你的申请被拒绝"
                            tips_title = "你的申请被拒绝"
                            tips_content = "链接:请登录CMDB查看(只能使用谷歌或者火狐浏览器)"
                            tips_url = "http://192.168.100.66/myworkflows/approve_list/"

                            send_qq.delay(users, window_title, tips_title, tips_content, tips_url)
                            send_weixin_message.delay(wx_users, tips_title + tips_content + tips_url)

                            mrl.logger.info('%s: %s: 处理结果:%s %s' % (subject, username, msg, success))

                            # 前端热更新或者后端热更新工单拒绝以后
                            # 需要把PRIORITY改为3，也就是暂停的级别
                            # 这么做是为了防止阻塞后面正常审批完成的工单执行
                            if isinstance(new_wse.content_object, ClientHotUpdate) or \
                                    isinstance(new_wse.content_object, ServerHotUpdate):
                                content_object = new_wse.content_object
                                content_object.priority = '3'
                                content_object.save()
                        else:
                            mrl.logger.info('%s: %s: 处理结果:%s %s' % (subject, username, msg, success))
                    else:
                        mrl.logger.warn('%s: %s: 没有匹配到指令' % (subject, username))
                else:
                    mrl.logger.warn('%s: %s: 没有匹配到主题' % (subject, username))
            except Exception as e:
                mrl.logger.error('%s: %s: %s' % (from_email, subject, str(e)))
            finally:
                # 主题邮件全部标记为已读
                mail.mark('Seen')
        box.logout()


@app.task(ignore_result=True)
def send_mail(to_list, subject, content, second=None):
    """发送邮件给相关的人"""
    if second is not None:
        time.sleep(second)
    mail = SendEmail(to_list, subject, content)
    mail.send()


@app.task()
def recieve_mail():
    """收取邮件"""
    r = RecieveMail()
    r.recieve_unseen()


@app.task()
def send_qq(users, window_title, tips_title, tips_content, tips_url):
    if MSG_CHANNEL == 0 or MSG_CHANNEL == 1:
        try:
            url = 'https://119.29.79.89/api/imqq/sendmsg/'

            headers = {
                'Accept': 'application/json',
                'Authorization': 'Token 12312412513634675475686583568'
            }

            data = {
                "users": users,
                "window_title": window_title,
                "tips_title": tips_title,
                "tips_content": tips_content,
                "tips_url": tips_url,
            }

            s = Session()
            s.mount('https://', HTTPAdapter(max_retries=Retry(total=5, status_forcelist=[408])))
            r = s.post(url, headers=headers, data=data, timeout=30, verify=False)
            result = r.json()

            if result.get('res', None) == 'success':
                sqq.logger.info('%s: 发送qq提醒成功: %s' % (users, json.dumps(data)))
            else:
                sqq.logger.error('%s: 发送qq提醒失败: %s-%s' % (users, json.dumps(data), r.text))

        except Exception as e:
            sqq.logger.error('%s: 发送qq提醒失败: %s-%s' % (users, str(e), r.text))


@app.task()
def add_qq_user(first_name, username, sex, organization_char, title, org_id):
    success = True
    msg = 'ok'
    try:
        url = 'https://119.29.79.89/api/imqq/add_qq_user/'

        token = '12312412513634675475686583568'
        headers = {'Accept': 'application/json', 'Authorization': 'Token ' + token}

        data = {
            'account': first_name,
            'name': username,
            'gender': sex,
            'department': organization_char,
            'title': title,
        }
        postdata = json.dumps(data)

        s = Session()
        s.mount('https://', HTTPAdapter(max_retries=Retry(total=5, status_forcelist=[408])))
        res = s.post(url, json=postdata, headers=headers, timeout=60, verify=False)
        with transaction.atomic():
            org_obj = OrganizationMptt.objects.get(pk=org_id)
            if res.status_code == 200:
                result = res.json()

                if result['ret']:
                    ent_qq.logger.info('%s: 开通企业QQ成功，QQ号码: %s' % (first_name, result['qq']))
                    org_obj.ent_qq = result['qq']
                    org_obj.save()
                else:
                    ent_qq.logger.error('%s: 开通企业QQ失败，原因： %s' % (first_name, result['msg']))
                    org_obj.ent_qq = result['msg']
                    org_obj.save()
                    success = False
                    msg = result['msg']

    except Exception as e:
        success = False
        msg = str(e)
        ent_qq.logger.error('%s: 开通企业QQ失败，原因： %s' % (first_name, str(e)))
    finally:
        return success, msg


@app.task()
def add_email_account(first_name, username, sex, organization_char, title, org_id):
    success = True
    msg = 'ok'
    try:
        url = 'https://119.29.79.89/api/imqq/add_mail_user/'

        token = '12312412513634675475686583568'
        headers = {'Accept': 'application/json', 'Authorization': 'Token ' + token}

        data = {
            'userid': first_name,
            'name': username,
            'gender': sex,
            'department': organization_char,
            'position': title,
        }
        postdata = json.dumps(data)

        s = Session()
        s.mount('https://', HTTPAdapter(max_retries=Retry(total=5, status_forcelist=[408])))
        res = s.post(url, json=postdata, headers=headers, timeout=60, verify=False)
        with transaction.atomic():
            org_obj = OrganizationMptt.objects.get(pk=org_id)
            if res.status_code == 200:
                result = res.json()

                if result['ret']:
                    ent_email.logger.info('%s: 开通企业邮箱成功' % (result['email']))
                    if org_obj.ent_email:
                        org_obj.ent_email = org_obj.ent_email + ',' + first_name
                    else:
                        org_obj.ent_email = first_name
                    org_obj.save()
                else:
                    ent_email.logger.error('%s: 开通企业邮箱失败，原因： %s' % (first_name, result['msg']))
                    if org_obj.ent_email:
                        org_obj.ent_email = org_obj.ent_email + ',' + result['msg']
                    else:
                        org_obj.ent_email = result['msg']
                    org_obj.save()
                    success = False
                    msg = result['msg']

    except Exception as e:
        success = False
        msg = str(e)
        ent_email.logger.error('%s: 开通企业邮箱失败，原因： %s' % (first_name, str(e)))
    finally:
        return success, msg


def get_ops_manager_url(project, om):
    """根据项目和机房获取运维管理机的url
    """
    DETAULT_URL = 'https://192.168.40.8/api/'
    DETAULT_TOKEN = '12312412513634675475686583568'
    # try:
    #     om = OpsManager.objects.get(project=project, room=room)
    #     return (om.url, om.token)
    # except OpsManager.DoesNotExist:
    #     return (DETAULT_URL, DETAULT_TOKEN)
    if om:
        return (om.get_url(), om.token)
    else:
        return (DETAULT_URL, DETAULT_TOKEN)


def update_serperworkflow_ips(serper_workflow_instance, data):
    """根据接口返回的数据更新服务器权限流程的ip数据

    data的数据格式:
    {
        'ip1': True,
        'ip2': False,
    }

    data有可能有None

    ips 是json格式, format:
    [
        {id: id, ip: ip1-room_name},
        {id: id, ip: ip2-room_name},
    ]
    """
    if data is not None:
        ips = json.loads(serper_workflow_instance.ips)

        for ip_info in ips:
            ip = ip_info['ip'].split('-')[0].split(':')[0]
            for data_ip, value in data.items():
                if ip == data_ip:
                    ip_info['result'] = value

        serper_workflow_instance.ips = json.dumps(ips)

        serper_workflow_instance.save()


def add_user_host_list(serper_workflow_instance):
    """添加权限到权限汇总表中
    """
    applicant = serper_workflow_instance.applicant
    user_profile = applicant.profile
    if not user_profile:
        user_profile = Profile.objects.create(user=applicant)

    ips = json.loads(serper_workflow_instance.ips)

    # hosts = list(set([x['id'].split('_', 1)[0] for x in ips]))

    # hosts = Host.objects.filter(id__in=hosts)

    if serper_workflow_instance.is_root:
        is_root = 1
    else:
        is_root = 0

    if serper_workflow_instance.temporary:
        temporary = 1
    else:
        temporary = 0

    start_time = serper_workflow_instance.start_time
    end_time = serper_workflow_instance.end_time

    for ip_info in ips:
        host = Host.objects.get(id=ip_info['id'].split('_', 1)[0])
        if ip_info.get('result', False):
            # 如果记录存在，保存
            if not UserProfileHost.objects.filter(
                    user_profile=user_profile, host=host, start_time=start_time,
                    end_time=end_time, temporary=temporary, is_root=is_root
            ):
                UserProfileHost.objects.create(
                    user_profile=user_profile, host=host, start_time=start_time,
                    end_time=end_time, temporary=temporary, is_root=is_root)


def qq_notify_on_server_permission_failed(server_permission_workflow_obj):
    """当服务器权限自动添加失败以后
    调用此函数发送qq提醒给相应的项目负责人
    """

    if server_permission_workflow_obj.status == 1:
        try:
            url = 'https://119.29.79.89/api/imqq/sendmsg/'

            headers = {
                'Accept': 'application/json',
                'Authorization': 'Token 12312412513634675475686583568'
            }

            project = server_permission_workflow_obj.project
            users = ','.join([x.first_name for x in project.related_user.all() if x.is_active])

            data = {
                "users": users,
                "window_title": "服务器权限添加失败",
                "tips_title": "服务器权限添加失败",
                "tips_content": "链接:请登录CMDB处理(只能使用谷歌或者火狐浏览器)",
                "tips_url": "http://192.168.100.66/myworkflows/apply_history_all/",
            }

            r = requests.post(url, headers=headers, data=data, timeout=30, verify=False)
            result = r.json()

            if result.get('res', None) == 'success':
                ml.logger.info('%s: 发送qq提醒成功' % (users))
            else:
                ml.logger.error('%s: 发送qq提醒失败' % (users))

        except Exception as e:
            ml.logger.error('%s: 发送qq提醒失败-%s' % (users, str(e)))


def format_server_permission(server_permission_workflow_obj):
    """将一个服务器权限的数据添加到对接接口

    参数格式:
    [
        {
            'ip_list': ['10.1.1.1', '10.1.1.2', '10.1.1.3'],
            'username': 'yanwenchi',
            'groupname': 'phper',
            'add_time': 'ts1',
            'del_time': 'ts2'
            'authorized_key': 'key',
            'om': opsmanager_obj,
        },
        {
            'ip_list': ['192.168.1.1'],
            'username': 'yanwenchi',
            'groupname': 'phper',
            'add_time': 'ts1',
            'del_time': 'ts2'
            'authorized_key': 'key',
            'om': opsmanager_obj2,
        },
    ]

    """

    # def get_index(room, ip_info_list):
    #     for index, ip_info in enumerate(ip_info_list):
    #         if room == ip_info['room']:
    #             return index
    #     return None

    def get_om_index(om, ip_info_list):
        for index, ip_info in enumerate(ip_info_list):
            if om == ip_info['om']:
                return index
        return None

    ip_info_list = []

    # ips format: ['192.168.1.1:22-room1', '192.168.1.2:22-room2', '192.168.1.3:22-room2', '1.1.1.1:22-room34']
    # ips = [x['ip'] for x in json.loads(server_permission_workflow_obj.ips)]
    ips = [{'id': x['id'].split('_')[0], 'ip': x['ip']} for x in json.loads(server_permission_workflow_obj.ips)]

    # 通用的数据
    username = server_permission_workflow_obj.applicant.first_name
    groupname = server_permission_workflow_obj.group

    # 如果是临时的权限，时间和申请的一样
    # 如果是永久的权限，开始时间是当前的时间戳，结束时间一般设置三年后
    if server_permission_workflow_obj.temporary:
        add_time = int(server_permission_workflow_obj.start_time.timestamp())
        del_time = int(server_permission_workflow_obj.end_time.timestamp())
    else:
        add_time = int(datetime(1990, 10, 10).timestamp())
        del_time = int(datetime(2027, 10, 10).timestamp())

    temporary = server_permission_workflow_obj.temporary
    authorized_key = server_permission_workflow_obj.key

    for x in ips:
        ip = x['ip'].split('-')[0].split(':')[0]
        ip_info = {}
        host_id = x['id']
        om = Host.objects.get(pk=host_id).get_opsmanager_obj()
        if ip_info_list:
            index = get_om_index(om, ip_info_list)
            if index is not None:
                ip_info_list[index]['ip_list'].extend([ip])
            else:
                ip_info['ip_list'] = [ip]
                ip_info['username'] = username
                ip_info['groupname'] = groupname
                ip_info['add_time'] = add_time
                ip_info['del_time'] = del_time
                ip_info['temporary'] = temporary
                ip_info['authorized_key'] = authorized_key
                ip_info['om'] = om
                ip_info_list.append(ip_info)
        else:
            ip_info['ip_list'] = [ip]
            ip_info['username'] = username
            ip_info['groupname'] = groupname
            ip_info['add_time'] = add_time
            ip_info['del_time'] = del_time
            ip_info['temporary'] = temporary
            ip_info['authorized_key'] = authorized_key
            ip_info['om'] = om
            ip_info_list.append(ip_info)

        # room = x.split('-', 2)[1]
        # ip = x.split('-', 2)[0].split(':')[0]
        # ip_info = {}
        #
        # if ip_info_list:
        #     index = get_index(room, ip_info_list)
        #     if index is not None:
        #         ip_info_list[index]['ip_list'].extend([ip])
        #     else:
        #         ip_info['ip_list'] = [ip]
        #         ip_info['username'] = username
        #         ip_info['groupname'] = groupname
        #         ip_info['add_time'] = add_time
        #         ip_info['del_time'] = del_time
        #         ip_info['temporary'] = temporary
        #         ip_info['authorized_key'] = authorized_key
        #         ip_info['room'] = room
        #         ip_info_list.append(ip_info)
        # else:
        #     ip_info['ip_list'] = [ip]
        #     ip_info['username'] = username
        #     ip_info['groupname'] = groupname
        #     ip_info['add_time'] = add_time
        #     ip_info['del_time'] = del_time
        #     ip_info['temporary'] = temporary
        #     ip_info['authorized_key'] = authorized_key
        #     ip_info['room'] = room
        #     ip_info_list.append(ip_info)

    # 将room转化为room对象
    # for x in ip_info_list:
    #     x['room'] = Room.objects.get(room_name=x['room'])

    # 将ip_list转为化json
    for x in ip_info_list:
        x['ip_list'] = json.dumps(x['ip_list'])

    return ip_info_list


@app.task(ignore_result=True)
def workflow_add_server_permission(wse_id):
    """自动添加服务器权限"""
    wse = WorkflowStateEvent.objects.get(id=wse_id)
    content_object = wse.content_object

    serper_log = SerPerLog()

    try:
        # 重新连接数据库
        close_old_connections()
        if isinstance(content_object, ServerPermissionWorkflow):
            ip_info_list = format_server_permission(content_object)
            status_list = []

            for ip_info in ip_info_list:
                url_prefix, token = get_ops_manager_url(content_object.project, ip_info['om'])
                ip_info.pop('om')
                if url_prefix is None or token is None:
                    # content_object.status = 1
                    # content_object.save()
                    status_list.append(1)
                    serper_log.logger.info('no pos manager found')
                    # success = True
                    # data = '添加失败'
                    continue
                url = url_prefix + USERADD
                authorized_token = "Token " + token
                headers = {
                    'Accept': 'application/json',
                    'Authorization': authorized_token,
                    'Connection': 'keep-alive',
                }

                try:
                    r = requests.post(url, headers=headers, data=ip_info, verify=False, timeout=60)
                    """返回的数据格式如下：
                    {
                        'status': 0 or 1,
                        'data': {'ip1': True, 'ip2': False}
                    }
                    """
                    # serper_log.logger.info('%s: %s' % (content_object.title, r.text))
                    result = r.json()
                    # content_object.status = result['status']
                    status_list.append(result['status'])
                    update_serperworkflow_ips(content_object, result['data'])
                    # content_object.save()
                except Exception as e:
                    # content_object.status = 1
                    status_list.append(1)
                    # content_object.save()
                    serper_log.logger.info('%s: %s' % (url, str(e)))
                    # success = False
                    # data = '连接超时'
                    continue

            # 修改流程状态
            if 1 in status_list:
                content_object.status = 1
            else:
                content_object.status = 0

            content_object.save()

            add_user_host_list(content_object)

            # 如果添加权限失败，发送邮件和企业微信消息
            if content_object.status == 1:
                to_list = content_object.project.get_relate_role_user_email_list()
                subject = '服务器权限添加失败'
                content = '服务器权限添加失败，请查看原因！<br>项目：{}<br>申请人：{}<br>工单标题：{}'.format(
                    content_object.project.project_name,
                    content_object.applicant.username,
                    content_object.title
                )
                send_mail.delay(to_list, subject, content)
                wx_users = content_object.project.get_relate_role_user_wechat_list()
                send_weixin_message.delay(touser=wx_users, content=content)

    except requests.exceptions.ConnectionError:
        content_object.status = 1
        content_object.save()
        serper_log.logger.info('timeout')
    except OpsManager.DoesNotExist:
        content_object.status = 1
        content_object.save()
        serper_log.logger.info('no pos manager found')
    except Room.DoesNotExist:
        content_object.status = 1
        content_object.save()
        serper_log.logger.info('no room found')
    except Exception as e:
        traceback.print_exc()
        content_object.status = 1
        content_object.save()
        serper_log.logger.info('%s' % (str(e)))


def format_mysql_permission(content_object):
    """格式化mysql账号信息
    """
    account_info = ""

    for p in json.loads(content_object.content):
        if p.get('passwd', None) is None:
            s = "<li>{}，您已拥有该数据库实例的帐号，密码请翻查邮件记录！</li>".format(json.dumps(p))
        else:
            s = "<li>{}</li>".format(json.dumps(p))
        account_info += s

    html_info = "<ul>" + account_info + "</ul>"

    return html_info


def send_mail_on_mysql_instance_success(content_object):
    """数据库权限添加成功后发送邮件通知
    告诉密码和账号信息
    """
    if isinstance(content_object, MysqlWorkflow):
        subject = '你的mysql权限添加完成'

        content = "<html>" + \
                  "<head>" + \
                  "<meta charset='utf-8'>" + \
                  "</head>" + \
                  "<body>" + \
                  "<h3>你的mysql权限添加完成</h3>" + \
                  "<p><b>以下是你的mysql账号信息</b></p>" + \
                  "%s" + \
                  "</body>" + \
                  "</html>"
        content = content % (format_mysql_permission(content_object))

        to_list = [content_object.applicant.email]

        send_mail.delay(to_list, subject, content)


@app.task(ignore_result=True)
def add_mysql_permission(wse_id):
    wse = WorkflowStateEvent.objects.get(id=wse_id)
    content_object = wse.content_object
    mysql_log = MysqlPermissionLog()
    result = True
    data = '执行成功'

    # 重新连接数据库
    close_old_connections()

    if isinstance(content_object, MysqlWorkflow):
        content = json.loads(content_object.content)
        username = content_object.applicant.first_name
        for c in content:
            try:
                instance = c.get('instance')
                host = instance.split(':')[0]
                port = instance.split(':')[1]
                instance = MysqlInstance.objects.get(host=host, port=port)
                instance_info = {}
                instance_info['host'] = instance.host
                instance_info['port'] = instance.port
                instance_info['user'] = instance.user
                instance_info['passwd'] = instance.password

                # 白名单
                if instance.white_list is not None:
                    white_list = tuple(json.loads(instance.white_list))
                else:
                    white_list = ()

                list_dbs = c['dbs']
                permission = c['permission']

                passwd = add_instance_user_privileges(username, list_dbs, permission, white_list, **instance_info)
                c['passwd'] = passwd

                mysql_log.logger.info('数据库实例%s:%s 添加用户%s 数据库%s 权限%s 成功' % (
                    host, port, username, json.dumps(list_dbs), permission))
            except MysqlInstance.DoesNotExist:
                result = False
                data = '数据库实例不存在'
                content_object.status = 1
                content_object.save()
                mysql_log.logger.error('%s: %s没有找到mysql实例' % (host, port))
            except Exception as e:
                result = False
                data = str(e)
                content_object.status = 1
                content_object.save()
                mysql_log.logger.error('%s:%s 错误 %s' % (host, port, str(e)))
        else:
            content_object.status = 0
            content_object.content = json.dumps(content)
            content_object.save()
            send_mail_on_mysql_instance_success(content_object)

    return result, data


@app.task(ignore_result=True)
def _remove_mysql_permission(username):
    """清除用户的mysql账号
    """

    all_instance = MysqlInstance.objects.all()
    # all_instance = MysqlInstance.objects.filter(host='127.0.0.1')

    mysql_instance = [x.host + ':' + x.port for x in all_instance]

    user = User.objects.get(first_name=username)
    ucs = UserClearStatus.objects.get(profile=user.profile)

    mysql_permission = {}
    mysql_permission['mysql_instance'] = mysql_instance
    ucs.mysql_permission = json.dumps(mysql_permission)
    ucs.save(update_fields=['mysql_permission'])
    ws_notify_clean_user(user.id)

    for instance in all_instance:
        try:
            instance_info = {}
            instance_info['host'] = instance.host
            instance_info['port'] = instance.port
            instance_info['user'] = instance.user
            instance_info['passwd'] = instance.password

            instance_host_port = instance.host + ':' + instance.port

            remove_instance_account(username, **instance_info)
            mysql_permission[instance_host_port] = {}
            mysql_permission[instance_host_port]['result'] = '清除成功'
            mysql_permission[instance_host_port]['success'] = True
        except Exception as e:
            result = str(e)
            success = False
            mysql_permission[instance_host_port] = {}
            mysql_permission[instance_host_port]['result'] = result
            mysql_permission[instance_host_port]['success'] = success
        finally:
            ucs.mysql_permission = json.dumps(mysql_permission)
            ucs.save(update_fields=['mysql_permission'])
            ws_notify_clean_user(user.id)


@app.task(ignore_result=True)
def remove_mysql_permission(username, force=False):
    """清除用户的mysql账号
    force用来判断是否强制清除所有的账号，
    那些已经清除成功的账号也要重新清除

    没有force的话，多次清除，只会清除失败的账号
    """

    all_instance = MysqlInstance.objects.all()
    # all_instance = MysqlInstance.objects.filter(host='127.0.0.1')

    mysql_instance = [x.host + ':' + x.port for x in all_instance]

    user = User.objects.get(first_name=username)
    ucs = UserClearStatus.objects.get(profile=user.profile)

    """
    mysql_permission = {}
    mysql_permission['mysql_instance'] = mysql_instance
    ucs.mysql_permission = json.dumps(mysql_permission)
    ucs.save(update_fields=['mysql_permission'])
    ws_notify_clean_user(user.id)
    """

    # 第一次执行，通常是没有mysql_permission值，为None
    # 多次执行，只会清除失败的
    if force or ucs.mysql_permission is None:
        mysql_permission = {}
    else:
        mysql_permission = json.loads(ucs.mysql_permission)
        # 由于是重新执行，将失败的修改，为了在页面展示正在清除中
        for instance in mysql_permission.keys():
            if instance != 'mysql_instance':
                if mysql_permission.get(instance, {}).get('success', False) is not True:
                    mysql_permission[instance] = {}

    mysql_permission['mysql_instance'] = mysql_instance
    ucs.mysql_permission = json.dumps(mysql_permission)
    ucs.save(update_fields=['mysql_permission'])
    ws_notify_clean_user(user.id)

    value_lock = threading.Lock()
    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        for instance in all_instance:
            instance_info = {}
            instance_info['host'] = instance.host
            instance_info['port'] = instance.port
            instance_info['user'] = instance.user
            instance_info['passwd'] = instance.password

            instance_host_port = instance.host + ':' + instance.port

            if force or mysql_permission.get(instance_host_port, {}).get('success', False) is not True:
                # 白名单
                if instance.white_list is not None:
                    white_list = tuple(json.loads(instance.white_list))
                else:
                    white_list = ()
                executor.submit(
                    remove_instance_account_update_info, ucs, username,
                    value_lock, instance_host_port, white_list, **instance_info)


@app.task(ignore_result=True)
def set_user_host():
    shost_log = SHostLog()

    try:
        # 重新连接数据库
        close_old_connections()

        temporary_permission = UserProfileHost.objects.filter(temporary=1, is_valid=1)

        for t in temporary_permission:
            now = datetime.now()
            if now > t.end_time:
                t.is_valid = 0
                t.save()
        shost_log.logger.info('set host status ok')
    except Exception as e:
        shost_log.logger.error('%s' % (str(e)))


@app.task(ignore_result=True)
def hotupdate_timeout():
    """
    每隔10分钟检测前端和后端热更新工单，如果出现以下两种情况则发送通知
    1. 工单提交申请后超过30分钟还没执行
    2. 工单开始更新后，超过30分钟还没完成
    """

    # 默认的超时时间是30分钟
    DEFAULT_INTERVAL = 30 * 60

    DEFAULT_NOTIFIER = 3

    timeout_log = HotUpdateTimeOutLog()

    try:
        # 重新连接数据库
        close_old_connections()

        # 从wse中找到前端热更新或者后端热更新
        # 当前状态is_current=True并且 state不是完成的
        list_ctype = ContentType.objects.filter(model__in=['clienthotupdate', 'serverhotupdate'])

        # 这里也要排除掉拒绝掉的工单
        # list_wse = WorkflowStateEvent.objects.filter(is_current=True, content_type__in=list_ctype).exclude(
        #     state__name='完成').exclude(state_value='拒绝')
        list_wse = WorkflowStateEvent.objects.filter(is_current=True, content_type__in=list_ctype).filter(
            Q(hot_server_workflow__status__in=['0', '1', '4']) |
            Q(hot_client_workflow__status__in=['0', '1', '4'])).exclude(state_value='拒绝')

        for wse in list_wse:
            content_object = wse.content_object
            if content_object.status in ('0', '4'):
                # 如果这个工单默认的超时时间内没有执行
                # 发送qq提醒
                create_time = content_object.create_time
                if int((datetime.now() - create_time).total_seconds()) > DEFAULT_INTERVAL:
                    list_ops_manager = OpsManager.objects.filter(
                        project=content_object.project, area=content_object.area_name)
                    list_ops_manager_status = [x.status for x in list_ops_manager]
                    # 只要是空闲的时候
                    if (len(list(set(list_ops_manager_status))) == 1 and '0' in list_ops_manager_status):
                        notifier = content_object.notifier
                        if notifier <= DEFAULT_NOTIFIER:
                            first_name = content_object.applicant.first_name
                            window_title = '你的热更新还没有执行'
                            tips_title = '你的热更新还没有执行'
                            tips_content = '你的工单: %s 已经超过30分钟没有执行,请登录CMDB处理并联系相应的人员完成审批' % (content_object.title)
                            tips_url = 'http://192.168.100.66/myworkflows/apply_history/'
                            send_qq.delay(first_name, window_title, tips_title, tips_content, tips_url)
                            send_weixin_message.delay(first_name, tips_title + tips_content + tips_url)

                            # 发送邮件提醒给相关的运维负责人
                            to_list = [x.email for x in content_object.project.related_user.all()]
                            subject = '热更新还没有执行或者审批'
                            content = '项目:{}\n标题:{}'.format(content_object.project.project_name, content_object.title)
                            send_mail.delay(to_list, subject, content)

                            timeout_log.logger.info(
                                '%s 发送热更新没有审批或执行提醒给%s 成功' % (content_object.title, content_object.applicant.username))
                            content_object.notifier += 1
                            content_object.save()
                        else:
                            timeout_log.logger.info('%s提醒次数为%d, 超过最大提醒数,不发送qq提醒' % (content_object.title, notifier))
            # 如果是在更新中，检测更新时间是否超时
            if content_object.status == '1':
                # 最后的审批时间是运营审批节点的审批时间
                state = get_workflow_state_order(wse.state.workflow)[2]
                approve_time = get_wse(state, wse.content_object).approve_time
                if int((datetime.now() - approve_time).total_seconds()) > DEFAULT_INTERVAL:
                    # 发送邮件提醒给相关的运维负责人
                    to_list = [x.email for x in content_object.project.related_user.all()]
                    subject = '热更新一直在更新中超过30分钟'
                    content = '项目:{}\n标题:{}'.format(content_object.project.project_name, content_object.title)
                    send_mail.delay(to_list, subject, content)

                    timeout_log.logger.info(
                        '%s 发送热更新更新中超时提醒成功' % (content_object.title))

    except Exception as e:
        timeout_log.logger.error('%s' % (str(e)))


@app.task(ignore_result=False)
def clean_project_serper(wse_id, list_project_id):
    """根据项目清除用户服务器权限
    """
    log = CleanProjectServer()
    wse = WorkflowStateEvent.objects.get(id=wse_id)
    content_object = wse.content_object
    user = content_object.applicant
    # project = content_object.raw_project_group.project if content_object.raw_project_group else None
    project = GameProject.objects.filter(id__in=list_project_id)
    list_ops_manager, default_ip_list, use_default = get_ops_manager_from_user(user, project=project)
    # 设置权限记录为失效
    UserProfileHost.objects.filter(
        user_profile=user.profile, host__belongs_to_game_project__in=project).update(**{"is_valid": 0})

    default_url = 'https://192.168.40.8/api/'
    if use_default:
        list_ops_manager.add(OpsManager.objects.get(url=default_url))

    p = re.compile(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")
    content_object.delete_serper_info = json.dumps(
        {'ops_ip': [re.findall(p, x.get_url())[0] for x in list_ops_manager]})
    content_object.save()

    username = user.username

    for ops_manager in list_ops_manager:
        try:
            close_old_connections()
            delete_serper_info = json.loads(content_object.delete_serper_info)  # 这里取出来最新的delete_serper_info的结果
            ip = re.findall(p, ops_manager.get_url())[0]
            url = ops_manager.get_url() + 'user/user_del/'
            token = ops_manager.token
            if ops_manager.get_url() == default_url:
                data = {"username": username, "ip_list": default_ip_list, 'id': content_object.id}
            else:
                data = {"username": username, 'id': content_object.id}
            authorized_token = "Token " + token

            headers = {
                'Accept': 'application/json',
                'Authorization': authorized_token,
                'Connection': 'keep-alive',
            }
            s = Session()
            s.mount('https://', HTTPAdapter(max_retries=Retry(total=3, status_forcelist=[408])))
            r = s.post(url, headers=headers, json=data, verify=False, timeout=10)
            result = r.json()
            if result.get('Accepted', False):
                log.logger.info('清除用户%s服务器权限-发送到管理机%s 成功' % (username, ops_manager.get_url()))
                # status_list.append(1)
            else:
                # status_list.append(0)
                delete_serper_info.update({ip: {'success': False}})
                content_object.delete_serper_info = json.dumps(delete_serper_info)
                content_object.status = 1
                content_object.save()
        except Exception as e:
            msg = str(e)
            log.logger.info('清除用户%s服务器权限-发送到管理机%s 失败: %s' % (username, ops_manager.get_url(), msg))
            delete_serper_info.update({ip: {'success': False}})
            content_object.delete_serper_info = json.dumps(delete_serper_info)
            content_object.status = 1
            content_object.save()


@app.task(ignore_result=True)
def add_svn_workflow(wse_id):
    """自动添加svn权限"""
    wse = WorkflowStateEvent.objects.get(id=wse_id)
    content_object = wse.content_object
    svn_log = SVNLog()
    error = False

    if isinstance(content_object, SVNWorkflow):
        try:
            # 重新连接数据库
            close_old_connections()

            payload = format_svn(content_object)
            url = 'https://192.168.40.11/api/addprivilege/'
            headers = {
                'Accept': 'application/json',
                'Authorization': 'Token 12312412513634675475686583568',
                'Connection': 'keep-alive',
            }
            r = requests.post(url, headers=headers, data=payload, verify=False)
            svn_log.logger.info('%s: %d: %s' % (content_object.title, r.status_code, r.text))
            msg = r.json()
            result = msg['result']
            data = msg['data']
            if result:
                content_object.status = 0
                svn_log.logger.info('ok')
            else:
                error = True
                content_object.status = 2
                svn_log.logger.info('%s' % (data))
            content_object.save()
        except requests.exceptions.ConnectionError:
            error = True
            svn_log.logger.info('time_out')
            content_object.status = 2
            content_object.save()
        except Exception as e:
            error = True
            svn_log.logger.info('%s' % (str(e)))
            content_object.status = 2
            content_object.save()
        finally:
            # 如果添加失败，发送邮件和企业微信消息
            if error:
                to_list = content_object.project.get_relate_role_user_email_list()
                subject = 'SVN权限添加失败'
                content = 'SVN权限添加失败，请查看原因！<br>项目：{}<br>申请人：{}<br>工单标题：{}'.format(
                    content_object.project.project_name,
                    content_object.applicant.username,
                    content_object.title
                )
                send_mail.delay(to_list, subject, content)
                wx_users = content_object.project.get_relate_role_user_wechat_list()
                send_weixin_message.delay(touser=wx_users, content=content)


@app.task(ignore_result=True)
def clean_svn_workflow(wse_id, project_id):
    wse = WorkflowStateEvent.objects.get(id=wse_id)
    content_object = wse.content_object
    # project = content_object.raw_project_group.project if content_object.raw_project_group else None
    svn_log = SVNLog()

    if project_id is None:
        svn_log.logger.info('需要清除的svn项目为空，不做任何处理')
        return None
    else:
        project = GameProject.objects.get(id=project_id)

    try:
        # 重新连接数据库
        close_old_connections()
        url = 'https://192.168.40.11/api/delproprivilege/'
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Token 12312412513634675475686583568',
            'Connection': 'keep-alive',
        }
        username = content_object.applicant.first_name
        # project_name_en = project.project_name_en
        svn_repo = project.svn_repo
        payload = {'username': username, 'project': svn_repo}
        r = requests.post(url, headers=headers, data=payload, verify=False)
        svn_log.logger.info('%s: %d: %s' % (content_object.title, r.status_code, r.text))
        msg = r.json()
        if msg.get('success', False):
            if content_object.status != 1:
                content_object.status = 0
                content_object.save()
            svn_log.logger.info('清除用户%s 项目%s SVN 权限成功' % (username, svn_repo))
        else:
            content_object.status = 1
            content_object.save()
            # svn_log.logger.info('clean svn failed %s' % (msg.get('result')))
            svn_log.logger.info('清除用户%s 项目%s SVN 权限失败: %s' % (username, svn_repo, msg.get('result', '')))
    except requests.exceptions.ConnectionError:
        svn_log.logger.info('time_out')
        content_object.status = 1
        content_object.save()
    except Exception as e:
        svn_log.logger.info('%s' % (str(e)))
        content_object.status = 1
        content_object.save()


def has_ops_manager(all_hot_client_info, ops_manager_id):
    """all_hot_client_info列表中是否含有ops_manager_id
    """

    for x in all_hot_client_info:
        if ops_manager_id == x.get('ops_manager', 0):
            return True

    return False


def get_index(all_hot_client_info, ops_manager_id):
    """根据ops_manager_id获取在all_hot_client_info
    里面的index，如果没有返回None
    """

    for index, x in enumerate(all_hot_client_info):
        if ops_manager_id == x.get('ops_manager', 0):
            return index

    return None


def format_hot_client_data(content, uuid, client_type, update_file_list, version):
    """构造前端热更新数据
    content的数据格式：
    [
        {
            "cdn_dir": "qq_s1", "area_name": "大陆", "cdn_root_url": "res.qxz.zhi-ming.com",
            "client_version": "008400000", "id": 44554, "project": 24
        }
    ]
    ==============>
    需要的数据格式为
    {
        'update_type': 'hot_client',
        'client_type': 0 or 1,
        'data': [
            {'cdn_root_url': 'res.ssss.chuangyunet.com', 'cdn_dir': 't1', 'version': 'axxx_13342', 'client_type': 'cn_ios'},
            {'cdn_root_url': 'res.ssss.chuangyunet.com', 'cdn_dir': 'test_r1'},
            {'cdn_root_url': 'res.ssss.chuangyunet.com', 'cdn_dir': 's1'},
            {'cdn_root_url': 'res.ssss.chuangyunet.com', 'cdn_dir': 'r1'}
        ],
        'uuid': 'xxx',
        'version': '003100000',
        'update_file_list': [
            {'file_name': 'a.txt', 'file_md5': abe347d3fdff45f1078102c4637852a5},
            {'file_name': 'b.txt', 'file_md5': 5724c05c650550ac8034129ad7a4d915}
        ]
    }
    """
    hot_client_data = {}
    hot_client_data['update_type'] = 'hot_client'
    hot_client_data['client_type'] = client_type
    hot_client_data['data'] = content
    hot_client_data['uuid'] = uuid
    hot_client_data['version'] = version
    hot_client_data['update_file_list'] = update_file_list

    return hot_client_data


def _format_hot_client_data(content, uuid, client_type, update_file_list):
    """构造前端热更新数据
    uuid就是前端热更新的id
    """
    all_hot_client_info = []

    """经过第一次数据转化
    为了根据项目和地区机房生成ops_manager
    生成的数据格式如下:
    [
        {'data': [], 'ops_manager': 1, 'update_type': 'hot_client', 'uuid': 'xxx', 'version': '003100000'}
    ]
    """
    for t in content:
        room = t.get('room')
        project = t.get('project')
        area = t.get('area_name')
        ops_manager = OpsManager.objects.get(
            project=GameProject.objects.get(id=project), room=Room.objects.get(id=room), area=area)

        if not has_ops_manager(all_hot_client_info, ops_manager.id):
            hot_client_info = {}
            hot_client_info['ops_manager'] = ops_manager.id
            hot_client_info['uuid'] = uuid
            hot_client_info['update_type'] = 'hot_client'
            hot_client_info['version'] = t.get('client_version')
            hot_client_info['client_type'] = client_type
            hot_client_info['data'] = []
            hot_client_info['update_file_list'] = update_file_list

            all_hot_client_info.append(hot_client_info)

    """第二次数据转为
    根据第一次的ops_manager来确定data
    数据格式如下:
    [
        {
            'ops_manager': 1,
            'update_type': 'hot_client',
            'client_type': 0 or 1,
            'data': [
                {'cdn_root_url': 'res.ssss.chuangyunet.com', 'cdn_dir': 't1'},
                {'cdn_root_url': 'res.ssss.chuangyunet.com', 'cdn_dir': 'test_r1'},
                {'cdn_root_url': 'res.ssss.chuangyunet.com', 'cdn_dir': 's1'},
                {'cdn_root_url': 'res.ssss.chuangyunet.com', 'cdn_dir': 'r1'}
            ],
            'uuid': 'xxx', 'version': '003100000',
            'update_file_list': [
                {'file_name': 'a.txt', 'file_md5': abe347d3fdff45f1078102c4637852a5},
                {'file_name': 'b.txt', 'file_md5': 5724c05c650550ac8034129ad7a4d915}
            ]
        }
    ]
    """
    for t in content:
        room = t.get('room')
        project = t.get('project')
        area = t.get('area_name')
        ops_manager = OpsManager.objects.get(
            project=GameProject.objects.get(id=project), room=Room.objects.get(id=room), area=area)

        if has_ops_manager(all_hot_client_info, ops_manager.id):
            index = get_index(all_hot_client_info, ops_manager.id)
            if index is not None:
                hot_client_info = all_hot_client_info[index]
                cdn_root_url = t.get('cdn_root_url')
                cdn_dir = t.get('cdn_dir')
                hot_client_info['data'].append({'cdn_root_url': cdn_root_url, 'cdn_dir': cdn_dir})
            else:
                raise Exception('hot_client: format data error, step two index not found')

    return all_hot_client_info


def _format_hot_server_data_(update_server_list):
    """构造热更新后端数据
    过期的函数
    数据库中的json格式:
    [
        {'gtype': 'game', 'srv_id': '37_1', 'pf_name': '37', 'ip': '10.104.104.36', 'srv_name': 'S1'},
        {'gtype': 'game', 'srv_id': '37_2', 'pf_name': '37', 'ip': '10.135.44.1', 'srv_name': 'S2'},
        {'gtype': 'game', 'srv_id': '37_3', 'pf_name': '37', 'ip': '10.186.0.163', 'srv_name': 'S3'},
        {'gtype': 'game', 'srv_id': '360_2', 'pf_name': '360', 'ip': '10.135.185.108', 'srv_name': 'S2'},
        {'gtype': 'game', 'srv_id': '360_3', 'pf_name': '360', 'ip': '10.135.58.58', 'srv_name': 'S3'},
        {'gtype': 'cross', 'srv_id': 'sogou_1', 'pf_name': 'sogou', 'ip': '10.135.117.44', 'srv_name': 'cross_sogou_1'},
        {'gtype': 'cross', 'srv_id': 'sogou_2', 'pf_name': 'sogou', 'ip': '10.104.227.20', 'srv_name': 'cross_sogou_2'},
        {'gtype': 'cross_center', 'srv_id': 'sogou', 'pf_name': 'sogou', 'ip': '10.104.107.56', 'srv_name': 'sogou'}
    ]
    ==========================================>>
    "update_server_list": {
        "game": {
            "10.1.1.1": ['qq_1', 'qq_2'],
            "10.1.1.2": ['qq_3', 'qq_4'],
        },
        "cross": {
            "192.168.1.1": ['cross_1', 'corss_2'],
            "192.168.1.3": ['cross_3', 'corss_4'],
        },
        "cross_center": {
            "172.17.26.12": ['center_1', 'center_2'],
            "172.17.26.15": ['center_4', 'center_6'],
        }
    },
    """

    def create_or_update_srv_id_list(type_update_server_list, ip, srv_id):
        # 第一次没有数据list
        if type_update_server_list.get(ip, None) is None:
            type_update_server_list[ip] = [srv_id]
        else:
            # 后期直接append数据进去
            type_update_server_list[ip].append(srv_id)

    new_update_server_list = {}

    list_game_type = ["game", "cross", "cross_center"]

    # 构造三个游戏服类型的字典
    for x in list_game_type:
        new_update_server_list[x] = {}

    for data in update_server_list:
        type_update_server_list = new_update_server_list[data['gtype']]
        ip = data['ip']
        srv_id = data['srv_id']
        create_or_update_srv_id_list(type_update_server_list, ip, srv_id)

    return new_update_server_list


def format_hot_server_data(update_server_list):
    """构造热更新后端数据
    数据库中的json格式:
    [
        {'gtype': 'game', 'srv_id': '37_1', 'pf_name': '37', 'ip': '10.104.104.36', 'srv_name': 'S1'},
        {'gtype': 'game', 'srv_id': '37_2', 'pf_name': '37', 'ip': '10.135.44.1', 'srv_name': 'S2'},
        {'gtype': 'game', 'srv_id': '37_3', 'pf_name': '37', 'ip': '10.186.0.163', 'srv_name': 'S3'},
        {'gtype': 'game', 'srv_id': '360_2', 'pf_name': '360', 'ip': '10.135.185.108', 'srv_name': 'S2'},
        {'gtype': 'game', 'srv_id': '360_3', 'pf_name': '360', 'ip': '10.135.58.58', 'srv_name': 'S3'},
        {'gtype': 'cross', 'srv_id': 'sogou_1', 'pf_name': 'sogou', 'ip': '10.135.117.44', 'srv_name': 'cross_sogou_1'},
        {'gtype': 'cross', 'srv_id': 'sogou_2', 'pf_name': 'sogou', 'ip': '10.104.227.20', 'srv_name': 'cross_sogou_2'},
        {'gtype': 'cross_center', 'srv_id': 'sogou', 'pf_name': 'sogou', 'ip': '10.104.107.56', 'srv_name': 'sogou'}
    ]
    ==========================================>>
    "update_server_list": {
        "game": {
            "10.1.1.1": ['qq_1', 'qq_2'],
            "10.1.1.2": ['qq_3', 'qq_4'],
        },
        "cross": {
            "192.168.1.1": ['cross_1', 'corss_2'],
            "192.168.1.3": ['cross_3', 'corss_4'],
        },
        "cross_center": {
            "172.17.26.12": ['center_1', 'center_2'],
            "172.17.26.15": ['center_4', 'center_6'],
        }
    },
    """

    new_update_server_list = defaultdict(lambda: defaultdict(list))

    for server in update_server_list:
        game_type = server.get('gtype', 'unknow')
        ip = server.get('ip', 'unknow')
        srv_id = server.get('srv_id', 'unknow')
        new_update_server_list[game_type][ip].append(srv_id)

    return new_update_server_list


def cmdb_hotupdate_qq_notify(all_users, content_obj, finish_ok):
    """cmdb执行的热更新错误，发送qq提醒
    """

    window_title = "热更新结果通知"
    obj_title = content_obj.title

    if finish_ok:
        tips_title = "热更新执行成功"
        tips_content = "本次热更新: " + obj_title + " 执行成功"
    else:
        tips_title = "热更新执行失败"
        tips_content = "本次热更新: " + obj_title + " 执行失败, 请联系运维负责人处理"

    # 全部需要通知的人
    # all_users = get_hot_update_all_related_user(content_obj)
    # all_users = ','.join([x.first_name for x in all_users])

    send_qq.delay(all_users, window_title, tips_title, tips_content, '#')


def cmdb_hotupdate_wx_notify(all_users, content_obj, finish_ok):
    """cmdb执行的热更新错误，发送qq提醒
    """

    window_title = "热更新结果通知"
    obj_title = content_obj.title

    if finish_ok:
        tips_title = "热更新执行成功"
        tips_content = "本次热更新: " + obj_title + " 执行成功"
    else:
        tips_title = "热更新执行失败"
        tips_content = "本次热更新: " + obj_title + " 执行失败, 请联系运维负责人处理"

    # 全部需要通知的人
    # all_users = get_hot_update_all_related_user(content_obj)
    # all_users = '|'.join([x.first_name for x in all_users])

    send_weixin_message.delay(all_users, window_title + tips_title + tips_content, '#')


def cmdb_hotupdate_mail_notify(to_list, content_obj, finish_ok):
    """cmdb执行的热更新错误，发送邮件提醒
    """

    if finish_ok:
        subject = content_obj.title + '#热更新成功'
        content = '热更新: ' + content_obj.title + ' 更新成功.'
    else:
        subject = content_obj.title + '#热更新失败'
        content = '热更新: ' + content_obj.title + ' 更新失败, 请联系运维负责人处理'

    send_mail.delay(to_list, subject, content)


@app.task(ignore_result=True)
def do_hot_client(content_object_id):
    """发送前端热更新请求到管理机
    走本地的celery worker
    """
    close_old_connections()
    content_object = ClientHotUpdate.objects.get(id=content_object_id)
    hot_update_log = HotUpdateLog(content_object.uuid)
    try:
        # cmdb上面的错误 用于cmdb出错以后发送邮件报警
        CMDB_ERROR = False

        # 首先去检查lock项目和地区，如果lock失败，直接引发一个异常
        """2019.3修改，运维管理机通过工单子任务表RsyncTask来获取"""
        list_ops_manager_id = [x.ops_id for x in content_object.clienthotupdatersynctask_set.all()]
        """找到其他url相同的运维管理机，事实为同一台管理机，一起上锁"""
        all_list_ops_manager_id = []
        for ops_id in list_ops_manager_id:
            ops_obj = OpsManager.objects.get(pk=ops_id)
            url = ops_obj.url
            for x in OpsManager.objects.filter(url__icontains=url):
                all_list_ops_manager_id.append(x.id)
        list_ops_manager = OpsManager.objects.filter(id__in=all_list_ops_manager_id)
        list_ops_manager_status = [x.status for x in list_ops_manager]

        if not (len(list(set(list_ops_manager_status))) == 1 and '0' in list_ops_manager_status):
            content_object.status = '4'
            content_object.save()
            raise HotUpdateBlock('%s: 项目和地区已经被锁,进入待更新状态' % content_object.title)
            # hot_update_log.logger.info('%s: 项目和地区已经被锁,进入待更新状态' % (content_object.title))
        else:
            # lock
            hot_update_log.logger.info('%s: 开始执行' % content_object.title)
            update_status = {'status': '2'}
            list_ops_manager.update(**update_status)
            hot_update_log.logger.info('hot_client: %s-成功上锁' % content_object.title)

            """
            2019.3修改
            遍历热更新的子任务，依次发送对应的热更新数据到相应的运维管理机
            """
            for task in content_object.clienthotupdatersynctask_set.all():
                content = json.loads(task.content)
                update_file_list = json.loads(task.update_file_list)
                update_file_list = format_hot_update_file_list(update_file_list, 'area_dir')

                hot_client_data = format_hot_client_data(
                    content, content_object.uuid, content_object.client_type, update_file_list,
                    content_object.client_version)

                # 获取运维管理机
                ops_manager = task.ops
                if not ops_manager.enable:
                    raise Exception('运维管理机状态已禁用: {}'.format(ops_manager.get_url()))

                # 发送前端热更新数据给运维管理机
                url = ops_manager.get_url() + CLIENT_HOT
                token = ops_manager.token
                authorized_token = "Token " + token

                headers = {
                    'Accept': 'application/json',
                    'Authorization': authorized_token,
                    'Connection': 'keep-alive',
                }

                s = Session()
                s.mount('https://', HTTPAdapter(max_retries=Retry(total=3, status_forcelist=[408])))
                r = s.post(url, headers=headers, json=hot_client_data, verify=False, timeout=10)
                if r.status_code == 200:
                    result = r.json()
                    if result.get('Accepted', False):
                        hot_update_log.logger.info('hot_client: %s-发送消息到管理机%s成功' % (content_object.title, ops_manager))
                    else:
                        content_object.status = '2'
                        content_object.save()
                        hot_update_log.logger.error('hot_client: %s-发送消息到管理机%s失败' % (content_object.title, ops_manager))
                        raise Exception('hot_client: %s-发送消息到管理机%s失败' % (content_object.title, ops_manager))
                else:
                    raise Exception(
                        'hot_client: %s-发送消息到管理机%s失败: %s' % (content_object.title, ops_manager, str(r.status_code)))

    except OpsManager.DoesNotExist:
        msg = 'hot_client: ops manager not found'
        hot_update_log.logger.error('hot_client: %s' % msg)
        content_object.status = '2'
        content_object.save()
        CMDB_ERROR = True
    except requests.exceptions.ConnectionError:
        content_object.status = '2'
        content_object.save()
        CMDB_ERROR = True
        hot_update_log.logger.error('hot_client: %s: %s time out' % (content_object.title, url))
    except GameProject.DoesNotExist:
        msg = 'hot_client: game project not found'
        hot_update_log.logger.error('hot_client: %s' % msg)
        content_object.status = '2'
        content_object.save()
        CMDB_ERROR = True
    except Room.DoesNotExist:
        msg = 'hot_client: room not found'
        hot_update_log.logger.error('hot_client: %s' % (msg))
        content_object.status = '2'
        content_object.save()
        CMDB_ERROR = True
    except HotUpdateBlock as e:
        msg = str(e)
        hot_update_log.logger.error('hot_client: %s' % (msg))
        CMDB_ERROR = True
    except Exception as e:
        msg = str(e)
        hot_update_log.logger.error('hot_client: %s' % (msg))
        content_object.status = '2'
        content_object.save()
        CMDB_ERROR = True

    # 通知客户端刷新状态
    content_object.save()
    ws_notify()

    if CMDB_ERROR:
        # 通知所有相关人员本次更新失败
        all_user_objs = get_hot_update_all_related_user(content_object, project_ops_user=True)
        all_users = ','.join([x.first_name for x in all_user_objs])
        all_wx_users = '|'.join([x.first_name for x in all_user_objs])
        cmdb_hotupdate_qq_notify(all_users, content_object, False)
        cmdb_hotupdate_wx_notify(all_wx_users, content_object, False)
        to_list = [x.email for x in all_user_objs]
        cmdb_hotupdate_mail_notify(to_list, content_object, False)


@app.task(ignore_result=True)
def do_hot_server(content_object_id):
    """执行热更新后端
    """
    # cmdb上面的错误 用于cmdb出错以后发送邮件报警
    CMDB_ERROR = False

    close_old_connections()
    content_object = ServerHotUpdate.objects.get(id=content_object_id)
    hot_update_log = HotUpdateLog(content_object.uuid)
    try:
        # 首先去检查lock项目和地区，如果lock失败，直接引发一个异常
        """2019.3修改，运维管理机通过工单子任务表RsyncTask来获取"""
        list_ops_manager_id = [x.ops_id for x in content_object.serverhotupdatersynctask_set.all()]
        """找到其他url相同的运维管理机，事实为同一台管理机，一起上锁"""
        all_list_ops_manager_id = []
        for ops_id in list_ops_manager_id:
            ops_obj = OpsManager.objects.get(pk=ops_id)
            url = ops_obj.url
            for x in OpsManager.objects.filter(url__icontains=url):
                all_list_ops_manager_id.append(x.id)
        list_ops_manager = OpsManager.objects.filter(id__in=all_list_ops_manager_id)
        list_ops_manager_status = [x.status for x in list_ops_manager]

        if not (len(list(set(list_ops_manager_status))) == 1 and '0' in list_ops_manager_status):
            content_object.status = '4'
            content_object.save()
            task = content_object.serverhotupdatersynctask_set.all()
            task.update(**{'rsync_result': None})
            raise HotUpdateBlock('%s: 项目和地区已经被锁,进入待更新状态' % (content_object.title))
            # hot_update_log.logger.info('%s: 项目和地区已经被锁,进入待更新状态' % (content_object.title))
        else:
            # lock
            hot_update_log.logger.info('%s: 开始执行' % (content_object.title))
            update_status = {'status': '2'}
            list_ops_manager.update(**update_status)
            hot_update_log.logger.info('hot_server: %s-成功上锁' % (content_object.title))

            # 进行一次区服的数据校验（增加新服）
            revise_server_list(content_object)

            """区服数据校验后，重新更新子任务对应的区服数据"""
            update_server_list = json.loads(content_object.update_server_list)
            for update_server in update_server_list:
                game_server_id = update_server['gameserverid']
                game_server = GameServer.objects.get(pk=int(game_server_id))
                ops = game_server.host.opsmanager
                if ops:
                    """判断管理机对应的子任务是否已存在，是则更新字段，否则创建子任务"""
                    task = ServerHotUpdateRsyncTask.objects.filter(server_hot_update=content_object, ops=ops)
                    if task:
                        task_update_server_list = json.loads(task[0].update_server_list)
                        if update_server not in task_update_server_list:
                            task_update_server_list.append(update_server)
                        task_update_server_list = json.dumps(task_update_server_list)
                        task.update(**{"update_server_list": task_update_server_list})

            # 修改final_result最终结果为None
            content_object.final_result = None

            # 复制update_server_list到result_update_file_list
            result_update_file_list = content_object.update_server_list
            content_object.result_update_file_list = result_update_file_list
            content_object.save()
            hot_update_log.logger.info('hot_server: %s-复制数据成功' % (content_object.title))

            # 加载热更新区服列表到redis中
            load_to_redis(content_object)
            hot_update_log.logger.info('hot_server: %s-将数据load到redis成功' % (content_object.title))

            """
            2019.3修改，遍历热更新子任务，发送对应的更新区服数据到对应的运维管理机
            """
            for task in content_object.serverhotupdatersynctask_set.all():
                # 热更新后端数据
                update_server_list = format_hot_server_data(json.loads(task.update_server_list))

                # 获取运维管理机
                ops_manager = task.ops
                if not ops_manager.enable:
                    raise Exception('运维管理机状态已禁用: {}'.format(ops_manager.get_url()))

                url = ops_manager.get_url() + CLIENT_HOT
                token = ops_manager.token
                authorized_token = "Token " + token
                headers = {
                    'Accept': 'application/json',
                    'Authorization': authorized_token,
                    'Connection': 'keep-alive',
                }

                # 后端热更新需要post的数据
                hot_server_data = {}

                hot_server_data['uuid'] = content_object.uuid
                hot_server_data['update_type'] = 'hot_server'
                hot_server_data['update_server_list'] = update_server_list
                hot_server_data['version'] = content_object.server_version
                hot_server_data['hot_server_type'] = content_object.hot_server_type
                if content_object.erlang_cmd_list:
                    hot_server_data['erlang_cmd_list'] = content_object.erlang_cmd_list.split('\n')
                else:
                    hot_server_data['erlang_cmd_list'] = []

                if content_object.update_file_list:
                    hot_server_data['update_file_list'] = format_hot_update_file_list(json.loads(task.update_file_list),
                                                                                      'area_dir')
                else:
                    hot_server_data['update_file_list'] = []

                    # r = requests.post(url, headers=headers, json=hot_server_data, verify=False, timeout=30)
                s = Session()
                s.mount('https://', HTTPAdapter(max_retries=Retry(total=3, status_forcelist=[408])))
                r = s.post(url, headers=headers, json=hot_server_data, verify=False, timeout=10)
                if r.status_code == 200:
                    result = r.json()
                    if result.get('Accepted', False):
                        hot_update_log.logger.info('hot_server: %s-发送消息到管理机%s成功' % (content_object.title, ops_manager))
                    else:
                        hot_update_log.logger.error('hot_server: %s-发送消息到管理机%s失败' % (content_object.title, ops_manager))
                        raise Exception('%s-发送消息到管理机%s失败' % (content_object.title, ops_manager))
                else:
                    raise Exception('%s-发送消息到管理机%s失败: %s' % (content_object.title, ops_manager, str(r.status_code)))

    except OpsManager.DoesNotExist:
        msg = 'hot_server: 项目%s-地区%s没有找到运维管理机' % (content_object.project.project_name, content_object.area_name)
        hot_update_log.logger.error('hot_server: %s' % (msg))
        content_object.status = '2'
        content_object.save()
        task = content_object.serverhotupdatersynctask_set.all()
        task.update(**{'rsync_result': None})
        CMDB_ERROR = True
    except requests.exceptions.ConnectionError:
        content_object.status = '2'
        content_object.save()
        task = content_object.serverhotupdatersynctask_set.all()
        task.update(**{'rsync_result': None})
        CMDB_ERROR = True
        hot_update_log.logger.error('hot_server: %s: %s time out' % (content_object.title, url))
    except HotUpdateBlock as e:
        msg = str(e)
        hot_update_log.logger.error('hot_server: %s' % (msg))
        CMDB_ERROR = True
    except Exception as e:
        msg = 'hot_server: ' + str(e)
        hot_update_log.logger.error('hot_server: %s' % (msg))
        content_object.status = '2'
        content_object.save()
        task = content_object.serverhotupdatersynctask_set.all()
        task.update(**{'rsync_result': None})
        CMDB_ERROR = True
    finally:
        ws_notify()
        if CMDB_ERROR:
            # 通知所有相关人员本次更新失败
            all_user_objs = get_hot_update_all_related_user(content_object, project_ops_user=True)
            all_users = ','.join([x.first_name for x in all_user_objs])
            all_wx_users = '|'.join([x.first_name for x in all_user_objs])
            cmdb_hotupdate_qq_notify(all_users, content_object, False)
            cmdb_hotupdate_wx_notify(all_wx_users, content_object, False)
            to_list = [x.email for x in all_user_objs]
            cmdb_hotupdate_mail_notify(to_list, content_object, False)


def do_hot_update(content_object):
    """执行热更新函数
    """
    close_old_connections()
    uuid = content_object.uuid
    hot_update_log = HotUpdateLog(uuid)
    rsync_push_log = PushAPILog()
    # 添加调试打印
    # cdict = model_to_dict(content_object)
    # hot_update_log.logger.info("000000")
    # hot_update_log.logger.info(cdict)

    if isinstance(content_object, ClientHotUpdate):
        try:
            # cmdb上面的错误 用于cmdb出错以后发送邮件报警
            CMDB_ERROR = False

            # 所有任务的开始，状态必须从4(待更新)开始
            if content_object.status != '4':
                raise HotUpdateBlock('%s: 状态为%s,不能执行' % (content_object.title, content_object.status))

            """首先去检查lock项目和地区，如果lock失败，直接引发一个异常"""
            # list_ops_manager = OpsManager.objects.filter(project=content_object.project, area=area_name)
            # list_ops_manager_status = [x.status for x in list_ops_manager]
            """
            2019.3修改
            修改获取运维管理机的方法:
            通过content_object中关联的推送子任务表获取更新需要用到的运维管理机，
            及rsync推送时所需要用到的参数
            """
            status_list = []
            list_ops_manager_id = []
            for task in content_object.clienthotupdatersynctask_set.all():
                status_list.append(task.ops.status)
            for task in content_object.clienthotupdatersynctask_set.all():
                list_ops_manager_id.append(task.ops_id)
            """找到其他url相同的运维管理机，事实为同一台管理机，一起上锁"""
            all_list_ops_manager_id = []
            for ops_id in list_ops_manager_id:
                ops_obj = OpsManager.objects.get(pk=ops_id)
                url = ops_obj.url
                for x in OpsManager.objects.filter(url__icontains=url):
                    all_list_ops_manager_id.append(x.id)
            list_ops_manager = OpsManager.objects.filter(id__in=all_list_ops_manager_id)
            list_ops_manager_status_remark = [x.get_status_display() for x in list_ops_manager if
                                              x.get_status_display() != '空闲']
            lock_reason = ','.join(list_ops_manager_status_remark)

            if not (len(list(set(status_list))) == 1 and '0' in status_list):
                content_object.status = '4'
                content_object.save()
                raise HotUpdateBlock('%s: 项目和地区已经被锁,运维管理机正在 %s' % (content_object.title, lock_reason))

            project_name_en = content_object.project.project_name_en

            # 第二步同步rsync目录
            # 这里需要根据不同的项目
            # 来获取不同的推送方式
            if project_name_en in ('snsy', 'syjy', 'csxy', 'csxybt') or str(
                    content_object.project.get_client_hotupdate_template(tag=True)) in ('sy4',):
                content_object.status = '1'
                content_object.save()
                if PRODUCTION_ENV:
                    do_hot_client.delay(content_object.id)
                else:
                    do_test_hot_client.delay(content_object.id)
            else:
                # 第一步lock
                hot_update_log.logger.info('%s: 开始执行' % (content_object.title))
                update_status = {'status': '2'}
                list_ops_manager.update(**update_status)
                hot_update_log.logger.info('hot_client: %s-成功上锁' % (content_object.title))
                content_object.status = '1'
                content_object.save()

                # 第二步同步rsync目录
                # 这里需要根据不同的项目
                # 来获取不同的推送方式
                # 需要推送的热更新文件
                """
                2019.3修改
                如果需要更新的区服对应有多个运维管理机器，及对应多个对送路径和参数
                则需要触发多次rsync推送
                """
                """根据项目英文名字获取对应的celery任务名称"""

                map = ProjectCeleryQueueMap.objects.filter(
                    project__project_name_en=content_object.project.project_name_en, use=2)
                if map is None:
                    raise Exception('没有找到该游戏项目对应celery队列')
                else:
                    if PRODUCTION_ENV:
                        fun = map[0].celery_queue
                    else:
                        fun = 'file_push_test_8'

                """先把子任务的rsync结果改为None"""
                rsync_tasks = content_object.clienthotupdatersynctask_set.all()
                rsync_tasks.update(**{'rsync_result': None})
                """开始遍历rsync任务"""
                for rsync_task in content_object.clienthotupdatersynctask_set.all():
                    # 添加调试打印
                    # rsdict = model_to_dict(rsync_task)
                    # hot_update_log.logger.info("1111")
                    # hot_update_log.logger.info(rsdict)
                    # 配置推送rsync的信息
                    rsync_path = get_rsync_path(content_object, rsync_task)
                    update_file = json.loads(rsync_task.update_file_list)
                    update_file_list = [{"file_md5": x["file_md5"], "file_name": x["file_name"]} for x in update_file]
                    port = rsync_task.ops.rsync_port
                    pass_file = rsync_task.ops.rsync_pass_file
                    user = rsync_task.ops.rsync_user
                    ip = rsync_task.ops.rsync_ip
                    module = rsync_task.ops.rsync_module
                    content = json.loads(rsync_task.content)

                    """组装celery任务参数"""
                    push_info = {}
                    push_info['update_file_list'] = update_file_list
                    push_info['relative_path'] = rsync_path
                    push_info['version'] = content_object.client_version
                    push_info['port'] = int(port)
                    push_info['pass_file'] = pass_file
                    push_info['user'] = user
                    push_info['ip'] = ip
                    push_info['module'] = module
                    push_info['uuid'] = uuid
                    push_info['update_type'] = 'hot_client'
                    push_info['content_object_id'] = content_object.id
                    push_info['area_name'] = content_object.area_name
                    push_info['content'] = content
                    rsync_push_log.logger.info(push_info)

                    eval(fun).delay(project_name_en, **push_info)
                    hot_update_log.logger.info('开始rsync推送 %s' % rsync_task.ops.rsync_ip)

        except OpsManager.DoesNotExist:
            msg = 'hot_client: ops manager not found'
            hot_update_log.logger.error('%s' % (msg))
            content_object.status = '2'
            content_object.save()
            CMDB_ERROR = True
        except GameProject.DoesNotExist:
            msg = 'hot_client: game project not found'
            hot_update_log.logger.error('%s' % (msg))
            content_object.status = '2'
            content_object.save()
            CMDB_ERROR = True
        except Room.DoesNotExist:
            msg = 'hot_client: room not found'
            hot_update_log.logger.error('%s' % (msg))
            content_object.status = '2'
            content_object.save()
            CMDB_ERROR = True
        except HotUpdateBlock as e:
            msg = str(e)
            hot_update_log.logger.error('%s' % (msg))
            CMDB_ERROR = True
        except Exception as e:
            msg = str(e)
            hot_update_log.logger.error('%s' % (msg))
            content_object.status = '2'
            content_object.save()
            CMDB_ERROR = True
        finally:
            ws_notify()
            if CMDB_ERROR:
                # 通知所有相关人员本次更新失败
                all_user_objs = get_hot_update_all_related_user(content_object, project_ops_user=True)
                all_users = ','.join([x.first_name for x in all_user_objs])
                all_wx_users = '|'.join([x.first_name for x in all_user_objs])
                cmdb_hotupdate_qq_notify(all_users, content_object, False)
                cmdb_hotupdate_wx_notify(all_wx_users, content_object, False)
                to_list = [x.email for x in all_user_objs]
                cmdb_hotupdate_mail_notify(to_list, content_object, False)

    if isinstance(content_object, ServerHotUpdate):
        try:
            # cmdb上面的错误 用于cmdb出错以后发送邮件报警
            CMDB_ERROR = False
            uuid = content_object.uuid
            hot_update_log = HotUpdateLog(uuid)
            # 所有任务的开始，状态必须从4(待更新)开始
            if content_object.status != '4':
                raise HotUpdateBlock('%s: 状态为%s,不能执行' % (content_object.title, content_object.status))

            # 首先去检查lock项目和地区，如果lock失败，直接引发一个异常
            """2019.3修改，根据热更新子任务表获取运维管理机状态"""
            list_ops_manager_status = [x.ops.status for x in content_object.serverhotupdatersynctask_set.all()]
            list_ops_manager_id = [x.ops.id for x in content_object.serverhotupdatersynctask_set.all()]
            """找到其他url相同的运维管理机，事实为同一台管理机，一起上锁"""
            all_list_ops_manager_id = []
            for ops_id in list_ops_manager_id:
                ops_obj = OpsManager.objects.get(pk=ops_id)
                url = ops_obj.url
                for x in OpsManager.objects.filter(url__icontains=url):
                    all_list_ops_manager_id.append(x.id)
            list_ops_manager = OpsManager.objects.filter(id__in=all_list_ops_manager_id)
            list_ops_manager_status_remark = [x.get_status_display() for x in list_ops_manager if
                                              x.get_status_display() != '空闲']
            lock_reason = ','.join(list_ops_manager_status_remark)

            if not (len(list(set(list_ops_manager_status))) == 1 and '0' in list_ops_manager_status):
                content_object.status = '4'
                content_object.save()
                task = content_object.serverhotupdatersynctask_set.all()
                task.update(**{'rsync_result': None})
                raise HotUpdateBlock('%s: 项目和地区已经被锁,运维管理机正在 %s' % (content_object.title, lock_reason))

            content_object.status = '1'
            # 修改final_result最终结果为None
            content_object.final_result = None
            content_object.save()

            # 如果不需要更新文件，则直接执行热更新指令
            hot_server_type = content_object.hot_server_type
            if hot_server_type == '2':
                do_hot_server.delay(content_object.id)
            else:
                project_name_en = content_object.project.project_name_en

                # 第二步同步rsync目录
                # 这里需要根据不同的项目
                # 来获取不同的推送方式
                if project_name_en in ('csxy', 'csxybt') or str(
                        content_object.project.get_server_hotupdate_template(tag=True)) in ('sy4',):
                    content_object.status = '1'
                    content_object.save()
                    if PRODUCTION_ENV:
                        do_hot_server.delay(content_object.id)
                    else:
                        do_test_hot_server.delay(content_object.id)
                else:
                    # 上锁
                    hot_update_log.logger.info('%s: 开始执行' % (content_object.title))
                    update_status = {'status': '2'}
                    list_ops_manager.update(**update_status)
                    hot_update_log.logger.info('hot_server: %s-成功上锁' % (content_object.title))
                    content_object.status = '1'
                    content_object.save()

                    """2019.3修改，遍历热更新子任务表进行rsync"""

                    map = ProjectCeleryQueueMap.objects.filter(
                        project__project_name_en=content_object.project.project_name_en, use=2)
                    if map is None:
                        raise Exception('没有找到该游戏项目对应celery队列')
                    else:
                        if PRODUCTION_ENV:
                            fun = map[0].celery_queue
                        else:
                            fun = 'file_push_test_8'

                    """先把子任务的rsync结果改为None"""
                    rsync_tasks = content_object.serverhotupdatersynctask_set.all()
                    rsync_tasks.update(**{'rsync_result': None})
                    """开始遍历rsync任务"""
                    for rsync_task in content_object.serverhotupdatersynctask_set.all():
                        rsync_path = get_rsync_path(content_object, rsync_task)
                        # 添加调试打印
                        # rsdict = model_to_dict(rsync_task)
                        # hot_update_log.logger.info("2222")
                        # hot_update_log.logger.info(rsdict)
                        # hot_update_log.logger.info(rsync_path)

                        port = rsync_task.ops.rsync_port
                        pass_file = rsync_task.ops.rsync_pass_file
                        user = rsync_task.ops.rsync_user
                        ip = rsync_task.ops.rsync_ip
                        module = rsync_task.ops.rsync_module

                        # 要热更新的文件
                        update_file_list = json.loads(rsync_task.update_file_list)

                        push_info = {}
                        push_info['update_file_list'] = update_file_list
                        push_info['relative_path'] = rsync_path
                        push_info['version'] = content_object.server_version
                        push_info['port'] = int(port)
                        push_info['pass_file'] = pass_file
                        push_info['user'] = user
                        push_info['ip'] = ip
                        push_info['module'] = module
                        push_info['uuid'] = uuid
                        push_info['update_type'] = 'hot_server'
                        push_info['content_object_id'] = content_object.id
                        push_info['area_name'] = content_object.area_name
                        rsync_push_log.logger.info(push_info)

                        eval(fun).delay(project_name_en, **push_info)
                        hot_update_log.logger.info('开始rsync推送 %s' % rsync_task.ops.rsync_ip)

        except OpsManager.DoesNotExist:
            msg = 'hot_client: ops manager not found'
            hot_update_log.logger.error('%s' % (msg))
            content_object.status = '2'
            content_object.save()
            CMDB_ERROR = True
        except GameProject.DoesNotExist:
            msg = 'hot_client: game project not found'
            hot_update_log.logger.error('%s' % (msg))
            content_object.status = '2'
            content_object.save()
            CMDB_ERROR = True
        except Room.DoesNotExist:
            msg = 'hot_client: room not found'
            hot_update_log.logger.error('%s' % (msg))
            content_object.status = '2'
            content_object.save()
            CMDB_ERROR = True
        except HotUpdateBlock as e:
            msg = str(e)
            hot_update_log.logger.error('%s' % (msg))
            CMDB_ERROR = True
        except Exception as e:
            msg = str(e)
            hot_update_log.logger.error('%s' % (msg))
            content_object.status = '2'
            content_object.save()
            CMDB_ERROR = True
        finally:
            ws_notify()
            if CMDB_ERROR:
                # 通知所有相关人员本次更新失败
                all_user_objs = get_hot_update_all_related_user(content_object, project_ops_user=True)
                all_users = ','.join([x.first_name for x in all_user_objs])
                all_wx_users = '|'.join([x.first_name for x in all_user_objs])
                cmdb_hotupdate_qq_notify(all_users, content_object, False)
                cmdb_hotupdate_wx_notify(all_wx_users, content_object, False)
                to_list = [x.email for x in all_user_objs]
                cmdb_hotupdate_mail_notify(to_list, content_object, False)


def format_game_install(list_game_install_obj):
    """根据装服列表，格式化为根据每个运维管理机
    发送装服的列表过去
    [
        {'project': project1: 'area': 'area1', 'srv_num': 1},
        {'project': project1: 'area': 'area1', 'srv_num': 2},
        {'project': project2: 'area': 'area4', 'srv_num': 13},
    ]
    转化为
    {
        'ops1': [{装服记录1}, {装服记录2}]，
        'ops2': [{装服记录1}]
    }
    """
    format_data = defaultdict(list)

    for game_install_obj in list_game_install_obj:
        project = game_install_obj.project
        area = game_install_obj.area
        ops = OpsManager.objects.filter(project=project, room__area__chinese_name=area)
        urls = list(set([x.get_url() for x in ops]))
        if len(urls) != 1:
            raise Exception('{project}, {area}不能获取唯一的运维管理机'.format(project=project.project_name, area=area))
        format_data[ops[0]].append(game_install_obj)

    format_data.default_factory = None
    format_data = dict(format_data)

    return format_data


@app.task(ignore_result=True)
def do_game_install(list_game_install, request_user_id):
    """装服celery worker
    """
    close_old_connections()

    game_install_log = GameInstallLog()

    list_game_install = InstallGameServer.objects.filter(id__in=list_game_install)

    def run_game_install(ops, list_game_install_obj):
        """真正执行装服的地方"""
        authorized_token = 'Token ' + ops.token
        headers = {
            'Accept': 'application/json',
            'Authorization': authorized_token,
            'Connection': 'keep-alive',
            'Content-Type': 'application/json; charset=UTF-8',
        }

        success = False  # 是否发送请求成功
        msg = 'ok'

        try:
            # game_install_log.logger.info('start request')
            # game_install_log.logger.info(list_game_install_obj)
            request_url = ops.get_url() + 'game/install/'
            r = requests.post(
                request_url, headers=headers,
                json=json.dumps({
                    'data': [x.show_all(project_name_en=True, timestamp=True) for x in list_game_install_obj]
                }),
                verify=False, timeout=20)
            result = r.json()
            game_install_log.logger.info(result)
            if result.get('Accepted', False):
                game_install_log.logger.info('发送装服请求到管理机{}成功'.format(ops.get_url()))
                success = True
            else:
                game_install_log.logger.error('发送装服请求到管理机{}失败'.format(ops.get_url()))
        except requests.exceptions.ConnectionError:
            msg = '{} 连接超时'.format(ops.get_url())
            game_install_log.logger.error(msg)
        except Exception as e:
            msg = str(e)
            game_install_log.logger.error(msg)
        finally:
            for game_install in list_game_install_obj:
                if success:
                    game_install.status = 1
                else:
                    game_install.status = 3
                game_install.save()
                game_install_log.logger.info('当前状态是: %s' % (game_install.status,))
                InstallGameServerRecord.objects.create(OperationUser=User.objects.get(pk=request_user_id),
                                                       OperationType=0,
                                                       OperationResult=1,
                                                       InstallGameServer=game_install, remark=msg)
            else:
                game_install_log.logger.info('通知刷新装服状态')
                game_install_notify()

    try:
        format_data = format_game_install(list_game_install)
        # game_install_log.logger.info(format_data)
    except Exception as e:
        game_install_log.logger.error(str(e))
        return None

    with futures.ThreadPoolExecutor(max_workers=20) as executor:
        to_do_map = {}
        for ops, game_install_obj in format_data.items():
            future = executor.submit(run_game_install, ops, game_install_obj)
            to_do_map[future] = ops.get_url()

        game_install_log.logger.info('Current to_do_map list is %s' % (to_do_map,))

        done_iter = futures.as_completed(to_do_map)

        for future in done_iter:
            game_install_log.logger.info(future.result())


@app.task(ignore_result=True)
def do_game_uninstall(list_game_uninstall, request_user_id):
    """卸服celery worker
    """
    close_old_connections()

    game_uninstall_log = GameUnInstallLog()

    list_game_uninstall = InstallGameServer.objects.filter(id__in=list_game_uninstall)

    def run_game_uninstall(ops, list_game_uninstall_obj):
        """真正执行卸服的地方"""
        authorized_token = 'Token ' + ops.token
        headers = {
            'Accept': 'application/json',
            'Authorization': authorized_token,
            'Connection': 'keep-alive',
            'Content-Type': 'application/json; charset=UTF-8',
        }

        success = False  # 是否发送请求成功
        msg = 'ok'

        try:
            # game_install_log.logger.info('start request')
            # game_install_log.logger.info(list_game_install_obj)
            request_url = ops.get_url() + 'game/uninstall/'
            r = requests.post(
                request_url, headers=headers,
                json=[x.show_all(project_name_en=True) for x in list_game_uninstall_obj],
                verify=False, timeout=20)
            result = r.json()
            game_uninstall_log.logger.info(result)
            if result.get('Accepted', False):
                game_uninstall_log.logger.info('发送卸服请求到管理机{}成功'.format(ops.get_url()))
                success = True
            else:
                game_uninstall_log.logger.error('发送卸服请求到管理机{}失败'.format(ops.get_url()))
        except requests.exceptions.ConnectionError:
            msg = '{} 连接超时'.format(ops.get_url())
            game_uninstall_log.logger.error(msg)
        except Exception as e:
            msg = str(e)
            game_uninstall_log.logger.error(msg)
        finally:
            for game_uninstall in list_game_uninstall_obj:
                if success:
                    game_uninstall.status = 4
                else:
                    game_uninstall.status = 6
                game_uninstall.save()
                game_uninstall_log.logger.info('当前状态是: %s' % (game_uninstall.status,))
                InstallGameServerRecord.objects.create(OperationUser=User.objects.get(pk=request_user_id),
                                                       OperationType=4,
                                                       OperationResult=1,
                                                       InstallGameServer=game_uninstall, remark=msg)
            else:
                game_uninstall_log.logger.info('通知刷卸载服状态')
                game_install_notify()

    try:
        format_data = format_game_install(list_game_uninstall)
        # game_install_log.logger.info(format_data)
    except Exception as e:
        game_uninstall_log.logger.error(str(e))
        return None

    with futures.ThreadPoolExecutor(max_workers=20) as executor:
        to_do_map = {}
        for ops, game_uninstall_obj in format_data.items():
            future = executor.submit(run_game_uninstall, ops, game_uninstall_obj)
            to_do_map[future] = ops.get_url()

        game_uninstall_log.logger.info('Current to_do_map list is %s' % (to_do_map,))

        done_iter = futures.as_completed(to_do_map)

        for future in done_iter:
            game_uninstall_log.logger.info(future.result())


@app.task(ignore_result=False)
def testd():
    # print('from remote machine')
    pass


def md5Checksum(filePath):
    with open(filePath, 'rb') as fh:
        m = hashlib.md5()
        while True:
            data = fh.read(8192)
            if not data:
                break
            m.update(data)
        return m.hexdigest()


class RsyncLog(object):
    """热更新前后端log"""

    def __init__(self):
        # create logger
        self.logger = logging.getLogger('rsync-log')
        self.logger.setLevel(logging.DEBUG)

        if not self.logger.handlers:
            # create file handler and set level to debug
            fh = logging.FileHandler('/var/log/cmdb_rsync.log', 'a', encoding='UTF-8')
            fh.setLevel(logging.DEBUG)

            # create formatter
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

            # add formatter
            fh.setFormatter(formatter)

            # add fh to logger
            self.logger.addHandler(fh)


@app.task(ignore_result=True)
def file_push_8(project_name_en, **kwagrs):
    """通过rsync模块将本地要同步的文件同步到相应的地方
    为了谨慎起见，在通过的过程中，需要如果方法
    1 首先检测同步的文件是否存在
    2 删除本地不包含在update_file_list中的文件，然后同步整个目录

    update_file_list的格式是[{'file_name': 'xxx', 'file_md5': 'xxxx'}, {}]的格式

    relative_path是基于update_file_list的文件绝对路径的前缀
    比如update_file_list的一个文件是assets/1.txt
    relative_path为/data/hot_backup/hot_client/ssss/cn/fbb69580-5f0d-44dd-b6bd-1809dfd8ed85/003501000
    那么，完整的路径就是/data/hot_backup/hot_client/ssss/cn/fbb69580-5f0d-44dd-b6bd-1809dfd8ed85/003501000/assets/1.txt
    """

    msg = ''
    success = False

    log = RsyncLog()

    try:
        relative_path = kwagrs.get('relative_path', '')
        version = kwagrs.get('version', '')
        update_file_list = kwagrs.get('update_file_list', '')
        port = kwagrs.get('port', '')
        pass_file = kwagrs.get('pass_file', '')
        user = kwagrs.get('user', '')
        ip = kwagrs.get('ip', '')
        module = kwagrs.get('module', '')
        uuid = kwagrs.get('uuid', '')
        update_type = kwagrs.get('update_type', '')
        content_object_id = kwagrs.get('content_object_id', '')
        # 将本地的relative_path下面的所有文件转为list
        native_file_list = []

        if not os.path.isdir(relative_path):
            raise Exception('找不到要同步的目录:%s' % (relative_path))

        for root, dirs, files in os.walk(relative_path):
            for name in files:
                native_file_list.append(os.path.join(root, name))

        # 转化update_file_list的格式为list绝对路径
        relative_path_with_version = os.path.join(relative_path, version)
        update_file_list = [os.path.join(relative_path_with_version, x['file_name']) for x in update_file_list]

        # 循环本地的文件，如果该文件不在update_file_list当中，则删除
        for x in native_file_list:
            if x not in update_file_list:
                os.remove(x)

        # 循环要更新的文件，如果该文件不在本地，报错
        for x in update_file_list:
            if x not in native_file_list:
                raise Exception('%s文件没有找到' % (x))

        # 执行rsync的命令
        cmd = """rsync --port=%d -aqz  --password-file=%s \
                --delete %s %s@%s::%s/""" % (port, pass_file, relative_path, user, ip, module)
        log.logger.info('rsync命令:%s' % (cmd))
        result = os.system(cmd)
        if result == 0:
            success = True
            log.logger.info('%s:rsync传送文件成功' % (uuid))
        else:
            success = False
            msg = 'rsync传送文件失败'
    except Exception as e:
        msg = str(e)
        success = False
        log.logger.error('%s-%s' % (uuid, msg))
    finally:
        # 回调CMDB接口让cmdb执行热更新命令
        log.logger.info('%s开始回调cmdb接口' % (uuid))
        cmdb_callback(msg, success, update_type, content_object_id, uuid)


@app.task(ignore_result=True)
def file_push_cc(project_name_en, **kwagrs):
    """通过rsync模块将本地要同步的文件同步到相应的地方
    为了谨慎起见，在通过的过程中，需要如果方法
    1 首先检测同步的文件是否存在
    2 删除本地不包含在update_file_list中的文件，然后同步整个目录

    update_file_list的格式是[{'file_name': 'xxx', 'file_md5': 'xxxx'}, {}]的格式

    relative_path是基于update_file_list的文件绝对路径的前缀
    比如update_file_list的一个文件是assets/1.txt
    relative_path为/data/hot_backup/hot_client/ssss/cn/fbb69580-5f0d-44dd-b6bd-1809dfd8ed85/003501000
    那么，完整的路径就是/data/hot_backup/hot_client/ssss/cn/fbb69580-5f0d-44dd-b6bd-1809dfd8ed85/003501000/assets/1.txt
    """

    msg = ''
    success = False

    log = RsyncLog()

    try:
        relative_path = kwagrs.get('relative_path', '')
        version = kwagrs.get('version', '')
        update_file_list = kwagrs.get('update_file_list', '')
        port = kwagrs.get('port', '')
        pass_file = kwagrs.get('pass_file', '')
        user = kwagrs.get('user', '')
        ip = kwagrs.get('ip', '')
        module = kwagrs.get('module', '')
        uuid = kwagrs.get('uuid', '')
        update_type = kwagrs.get('update_type', '')
        content_object_id = kwagrs.get('content_object_id', '')
        # 将本地的relative_path下面的所有文件转为list
        native_file_list = []

        if not os.path.isdir(relative_path):
            raise Exception('找不到要同步的目录:%s' % (relative_path))

        for root, dirs, files in os.walk(relative_path):
            for name in files:
                native_file_list.append(os.path.join(root, name))

        # 转化update_file_list的格式为list绝对路径
        relative_path_with_version = os.path.join(relative_path, version)
        update_file_list = [os.path.join(relative_path_with_version, x['file_name']) for x in update_file_list]

        # 循环本地的文件，如果该文件不在update_file_list当中，则删除
        for x in native_file_list:
            if x not in update_file_list:
                os.remove(x)

        # 循环要更新的文件，如果该文件不在本地，报错
        for x in update_file_list:
            if x not in native_file_list:
                raise Exception('%s文件没有找到' % (x))

        # 执行rsync的命令
        cmd = """rsync --port=%d -aqz  --password-file=%s \
                --delete %s %s@%s::%s/""" % (port, pass_file, relative_path, user, ip, module)
        log.logger.info('rsync命令:%s' % (cmd))
        result = os.system(cmd)
        if result == 0:
            success = True
            log.logger.info('%s:rsync传送文件成功' % (uuid))
        else:
            success = False
            msg = 'rsync传送文件失败'
    except Exception as e:
        msg = str(e)
        success = False
        log.logger.error('%s-%s' % (uuid, msg))
    finally:
        # 回调CMDB接口让cmdb执行热更新命令
        log.logger.info('%s开始回调cmdb接口' % (uuid))
        cmdb_callback(msg, success, update_type, content_object_id, uuid)


@app.task(ignore_result=True)
def file_push_slqy3d_cn(project_name_en, **kwagrs):
    """通过rsync模块将本地要同步的文件同步到相应的地方
    为了谨慎起见，在通过的过程中，需要如果方法
    1 首先检测同步的文件是否存在
    2 删除本地不包含在update_file_list中的文件，然后同步整个目录

    update_file_list的格式是[{'file_name': 'xxx', 'file_md5': 'xxxx'}, {}]的格式

    relative_path是基于update_file_list的文件绝对路径的前缀
    比如update_file_list的一个文件是assets/1.txt
    relative_path为/data/hot_backup/hot_client/ssss/cn/fbb69580-5f0d-44dd-b6bd-1809dfd8ed85/003501000
    那么，完整的路径就是/data/hot_backup/hot_client/ssss/cn/fbb69580-5f0d-44dd-b6bd-1809dfd8ed85/003501000/assets/1.txt
    """

    msg = ''
    success = False

    log = RsyncLog()

    try:
        relative_path = kwagrs.get('relative_path', '')
        version = kwagrs.get('version', '')
        update_file_list = kwagrs.get('update_file_list', '')
        port = kwagrs.get('port', '')
        pass_file = kwagrs.get('pass_file', '')
        user = kwagrs.get('user', '')
        ip = kwagrs.get('ip', '')
        module = kwagrs.get('module', '')
        uuid = kwagrs.get('uuid', '')
        update_type = kwagrs.get('update_type', '')
        content_object_id = kwagrs.get('content_object_id', '')
        # 将本地的relative_path下面的所有文件转为list
        native_file_list = []

        if not os.path.isdir(relative_path):
            raise Exception('找不到要同步的目录:%s' % (relative_path))

        for root, dirs, files in os.walk(relative_path):
            for name in files:
                native_file_list.append(os.path.join(root, name))

        # 转化update_file_list的格式为list绝对路径
        relative_path_with_version = os.path.join(relative_path, version)
        update_file_list = [os.path.join(relative_path_with_version, x['file_name']) for x in update_file_list]

        # 循环本地的文件，如果该文件不在update_file_list当中，则删除
        for x in native_file_list:
            if x not in update_file_list:
                os.remove(x)

        # 循环要更新的文件，如果该文件不在本地，报错
        for x in update_file_list:
            if x not in native_file_list:
                raise Exception('%s文件没有找到' % (x))

        # 执行rsync的命令
        cmd = """rsync --port=%d -aqz  --password-file=%s \
                --delete %s %s@%s::%s/""" % (port, pass_file, relative_path, user, ip, module)
        log.logger.info('rsync命令:%s' % (cmd))
        result = os.system(cmd)
        if result == 0:
            success = True
            log.logger.info('%s:rsync传送文件成功' % (uuid))
        else:
            success = False
            msg = 'rsync传送文件失败'
    except Exception as e:
        msg = str(e)
        success = False
        log.logger.error('%s-%s' % (uuid, msg))
    finally:
        # 回调CMDB接口让cmdb执行热更新命令
        log.logger.info('%s开始回调cmdb接口' % (uuid))
        cmdb_callback(msg, success, update_type, content_object_id, uuid)


@app.task(ignore_result=True)
def file_push_cyh5s7(project_name_en, **kwagrs):
    """通过rsync模块将本地要同步的文件同步到相应的地方
    为了谨慎起见，在通过的过程中，需要如果方法
    1 首先检测同步的文件是否存在
    2 删除本地不包含在update_file_list中的文件，然后同步整个目录

    update_file_list的格式是[{'file_name': 'xxx', 'file_md5': 'xxxx'}, {}]的格式

    relative_path是基于update_file_list的文件绝对路径的前缀
    比如update_file_list的一个文件是assets/1.txt
    relative_path为/data/hot_backup/hot_client/ssss/cn/fbb69580-5f0d-44dd-b6bd-1809dfd8ed85/003501000
    那么，完整的路径就是/data/hot_backup/hot_client/ssss/cn/fbb69580-5f0d-44dd-b6bd-1809dfd8ed85/003501000/assets/1.txt
    """

    msg = ''
    success = False

    log = RsyncLog()

    try:
        relative_path = kwagrs.get('relative_path', '')
        version = kwagrs.get('version', '')
        update_file_list = kwagrs.get('update_file_list', '')
        port = kwagrs.get('port', '')
        pass_file = kwagrs.get('pass_file', '')
        user = kwagrs.get('user', '')
        ip = kwagrs.get('ip', '')
        module = kwagrs.get('module', '')
        uuid = kwagrs.get('uuid', '')
        update_type = kwagrs.get('update_type', '')
        content_object_id = kwagrs.get('content_object_id', '')
        # 将本地的relative_path下面的所有文件转为list
        native_file_list = []

        if not os.path.isdir(relative_path):
            raise Exception('找不到要同步的目录:%s' % (relative_path))

        for root, dirs, files in os.walk(relative_path):
            for name in files:
                native_file_list.append(os.path.join(root, name))

        # 转化update_file_list的格式为list绝对路径
        relative_path_with_version = os.path.join(relative_path, version)
        update_file_list = [os.path.join(relative_path_with_version, x['file_name']) for x in update_file_list]

        # 循环本地的文件，如果该文件不在update_file_list当中，则删除
        for x in native_file_list:
            if x not in update_file_list:
                os.remove(x)

        # 循环要更新的文件，如果该文件不在本地，报错
        for x in update_file_list:
            if x not in native_file_list:
                raise Exception('%s文件没有找到' % (x))

        # 执行rsync的命令
        cmd = """rsync --port=%d -aqz  --password-file=%s \
                --delete %s %s@%s::%s/""" % (port, pass_file, relative_path, user, ip, module)
        log.logger.info('rsync命令:%s' % (cmd))
        result = os.system(cmd)
        if result == 0:
            success = True
            log.logger.info('%s:rsync传送文件成功' % (uuid))
        else:
            success = False
            msg = 'rsync传送文件失败'
    except Exception as e:
        msg = str(e)
        success = False
        log.logger.error('%s-%s' % (uuid, msg))
    finally:
        # 回调CMDB接口让cmdb执行热更新命令
        log.logger.info('%s开始回调cmdb接口' % (uuid))
        cmdb_callback(msg, success, update_type, content_object_id, uuid)


def cmdb_callback(msg, success, update_type, content_object_id, uuid):
    try:
        log = RsyncLog()
        url = 'http://192.168.90.181:8090/api/RsyncOnFinishedCallBack/'
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Token 12312412513634675475686583568'
        }
        payload = {
            'msg': msg,
            'success': success,
            'update_type': update_type,
            'content_object_id': content_object_id,
            'uuid': uuid
        }

        requests.post(url, headers=headers, data=payload, timeout=15, verify=False)
    except Exception as e:
        log.logger.error('回调cmdb失败-%s' % (str(e)))


@app.task(ignore_result=False)
def file_pull_8(project_name_en, **kwagrs):
    """
    file_path表示要拉取目录的根路径，比如/data/version_update/client/x/cn
    uuid表示要保存的关于一个工单的文件目录的副本
    update_type表示前后端
    version表示要拉取的具体版本目录
    project_name_en表示副本的项目名
    """
    success = False
    msg = ''
    try:
        if project_name_en in ('snqxz', 'jyjh', 'ssss'):
            list_file = []
            BACKUP_FILE_DIR = '/data/hot_backup'

            # 检查必要的参数
            need_params = ('file_path uuid update_type version').split()
            for param in need_params:
                if param not in kwagrs:
                    raise Exception('%s: 获取文件没有%s 参数' % (project_name_en, param))

            # 获取必要的参数
            file_path = kwagrs.get('file_path')
            update_type = kwagrs.get('update_type')
            uuid = kwagrs.get('uuid')
            version = kwagrs.get('version')

            # 首先检测要copy的版本目录在不在
            if update_type == 'hot_client':
                hot_files = "hot_files"
                from_path = os.path.join(file_path, version, hot_files)
            elif update_type == 'hot_server':
                reloadfiles = 'reloadfiles'
                from_path = os.path.join(file_path, version, reloadfiles)
            else:
                raise Exception('未知的热更新类型')
            if os.path.isdir(from_path):
                area_name = os.path.basename(file_path)  # /data/version_update/client/x/cn ==> cn
                # 确定是否已经存在这个目录
                to_path = os.path.join(BACKUP_FILE_DIR, update_type, project_name_en, area_name, uuid, version)
                if os.path.isdir(to_path):
                    shutil.rmtree(to_path)
                shutil.copytree(from_path, to_path)

                # 遍历新的文件目录
                for root, dirs, files in os.walk(to_path):
                    for name in files:
                        file_path = root + '/' + name
                        file_md5 = md5Checksum(file_path)
                        relative_path = file_path[len(to_path) + 1:]
                        list_file.append({"file_name": relative_path, 'file_md5': file_md5})
                success = True
            else:
                success = False
                msg = '找不到该目录'
    except Exception as e:
        msg = str(e)
        success = False
    return (success, msg, list_file)


@app.task(ignore_result=False)
def file_pull_cc(project_name_en, **kwagrs):
    """
    file_path表示要拉取目录的根路径，比如/data/version_update/client/x/cn
    uuid表示要保存的关于一个工单的文件目录的副本
    update_type表示前后端
    version表示要拉取的具体版本目录
    project_name_en表示副本的项目名
    """
    success = False
    msg = ''
    try:
        if project_name_en in ('mjfz',):
            list_file = []
            BACKUP_FILE_DIR = '/data/hot_backup'

            # 检查必要的参数
            need_params = ('file_path uuid update_type version').split()
            for param in need_params:
                if param not in kwagrs:
                    raise Exception('%s: 获取文件没有%s 参数' % (project_name_en, param))

            # 获取必要的参数
            file_path = kwagrs.get('file_path')
            update_type = kwagrs.get('update_type')
            uuid = kwagrs.get('uuid')
            version = kwagrs.get('version')

            # 首先检测要copy的版本目录在不在
            if update_type == 'hot_client':
                hot_files = "hot_files"
                from_path = os.path.join(file_path, version, hot_files)
            elif update_type == 'hot_server':
                reloadfiles = 'reloadfiles'
                from_path = os.path.join(file_path, version, reloadfiles)
            else:
                raise Exception('未知的热更新类型')
            if os.path.isdir(from_path):
                area_name = os.path.basename(file_path)  # /data/version_update/client/x/cn ==> cn
                # 确定是否已经存在这个目录
                to_path = os.path.join(BACKUP_FILE_DIR, update_type, project_name_en, area_name, uuid, version)
                if os.path.isdir(to_path):
                    shutil.rmtree(to_path)
                else:
                    success = False
                    msg = '找不到备份目录'
                shutil.copytree(from_path, to_path)

                # 遍历新的文件目录
                for root, dirs, files in os.walk(to_path):
                    for name in files:
                        file_path = root + '/' + name
                        file_md5 = md5Checksum(file_path)
                        relative_path = file_path[len(to_path) + 1:]
                        list_file.append({"file_name": relative_path, 'file_md5': file_md5})
                success = True
            else:
                success = False
                msg = '找不到该目录'
    except Exception as e:
        msg = str(e)
        success = False
    return (success, msg, list_file)


@app.task(ignore_result=False)
def file_pull_slqy3d_cn(project_name_en, **kwagrs):
    """
    file_path表示要拉取目录的根路径，比如/data/version_update/client/x/cn
    uuid表示要保存的关于一个工单的文件目录的副本
    update_type表示前后端
    version表示要拉取的具体版本目录
    project_name_en表示副本的项目名
    """
    success = False
    msg = ''
    try:
        if project_name_en in ('slqy3d',):
            list_file = []
            BACKUP_FILE_DIR = '/data/hot_backup'

            # 检查必要的参数
            need_params = ('file_path uuid update_type version').split()
            for param in need_params:
                if param not in kwagrs:
                    raise Exception('%s: 获取文件没有%s 参数' % (project_name_en, param))

            # 获取必要的参数
            file_path = kwagrs.get('file_path')
            update_type = kwagrs.get('update_type')
            uuid = kwagrs.get('uuid')
            version = kwagrs.get('version')

            # 首先检测要copy的版本目录在不在
            if update_type == 'hot_client':
                hot_files = "hot_files"
                from_path = os.path.join(file_path, version, hot_files)
            elif update_type == 'hot_server':
                reloadfiles = 'reloadfiles'
                from_path = os.path.join(file_path, version, reloadfiles)
            else:
                raise Exception('未知的热更新类型')
            if os.path.isdir(from_path):
                area_name = os.path.basename(file_path)  # /data/version_update/client/x/cn ==> cn
                # 确定是否已经存在这个目录
                to_path = os.path.join(BACKUP_FILE_DIR, update_type, project_name_en, area_name, uuid, version)
                if os.path.isdir(to_path):
                    shutil.rmtree(to_path)
                else:
                    success = False
                    msg = '找不到备份目录'
                shutil.copytree(from_path, to_path)

                # 遍历新的文件目录
                for root, dirs, files in os.walk(to_path):
                    for name in files:
                        file_path = root + '/' + name
                        file_md5 = md5Checksum(file_path)
                        relative_path = file_path[len(to_path) + 1:]
                        list_file.append({"file_name": relative_path, 'file_md5': file_md5})
                success = True
            else:
                success = False
                msg = '找不到该目录'
    except Exception as e:
        msg = str(e)
        success = False
    return (success, msg, list_file)


@app.task(ignore_result=False)
def file_pull_cyh5s7(project_name_en, **kwagrs):
    """
    file_path表示要拉取目录的根路径，比如/data/version_update/client/x/cn
    uuid表示要保存的关于一个工单的文件目录的副本
    update_type表示前后端
    version表示要拉取的具体版本目录
    project_name_en表示副本的项目名
    """
    success = False
    msg = ''
    try:
        if project_name_en in ('cyh5s7',):
            list_file = []
            BACKUP_FILE_DIR = '/data/hot_backup'

            # 检查必要的参数
            need_params = ('file_path uuid update_type version').split()
            for param in need_params:
                if param not in kwagrs:
                    raise Exception('%s: 获取文件没有%s 参数' % (project_name_en, param))

            # 获取必要的参数
            file_path = kwagrs.get('file_path')
            update_type = kwagrs.get('update_type')
            uuid = kwagrs.get('uuid')
            version = kwagrs.get('version')

            # 首先检测要copy的版本目录在不在
            if update_type == 'hot_client':
                hot_files = "hot_files"
                from_path = os.path.join(file_path, version, hot_files)
            elif update_type == 'hot_server':
                reloadfiles = 'reloadfiles'
                from_path = os.path.join(file_path, version, reloadfiles)
            else:
                raise Exception('未知的热更新类型')
            if os.path.isdir(from_path):
                area_name = os.path.basename(file_path)  # /data/version_update/client/x/cn ==> cn
                # 确定是否已经存在这个目录
                to_path = os.path.join(BACKUP_FILE_DIR, update_type, project_name_en, area_name, uuid, version)
                if os.path.isdir(to_path):
                    shutil.rmtree(to_path)
                else:
                    success = False
                    msg = '找不到备份目录'
                shutil.copytree(from_path, to_path)

                # 遍历新的文件目录
                for root, dirs, files in os.walk(to_path):
                    for name in files:
                        file_path = root + '/' + name
                        file_md5 = md5Checksum(file_path)
                        relative_path = file_path[len(to_path) + 1:]
                        list_file.append({"file_name": relative_path, 'file_md5': file_md5})
                success = True
            else:
                success = False
                msg = '找不到该目录'
    except Exception as e:
        msg = str(e)
        success = False
    return (success, msg, list_file)


@app.task(ignore_result=True)
def file_push_15(project_name_en, **kwagrs):
    """通过rsync模块将本地要同步的文件同步到相应的地方
    为了谨慎起见，在通过的过程中，需要如果方法
    1 首先检测同步的文件是否存在
    2 删除本地不包含在update_file_list中的文件，然后同步整个目录

    update_file_list的格式是[{'file_name': 'xxx', 'file_md5': 'xxxx'}, {}]的格式

    relative_path是基于update_file_list的文件绝对路径的前缀
    比如update_file_list的一个文件是assets/1.txt
    relative_path为/data/hot_backup/hot_client/ssss/cn/fbb69580-5f0d-44dd-b6bd-1809dfd8ed85/003501000
    那么，完整的路径就是/data/hot_backup/hot_client/ssss/cn/fbb69580-5f0d-44dd-b6bd-1809dfd8ed85/003501000/assets/1.txt
    """

    msg = ''
    success = False

    log = RsyncLog()

    try:
        relative_path = kwagrs.get('relative_path', '')
        version = kwagrs.get('version', '')
        update_file_list = kwagrs.get('update_file_list', '')
        port = kwagrs.get('port', '')
        pass_file = kwagrs.get('pass_file', '')
        user = kwagrs.get('user', '')
        ip = kwagrs.get('ip', '')
        module = kwagrs.get('module', '')
        uuid = kwagrs.get('uuid', '')
        update_type = kwagrs.get('update_type', '')
        content_object_id = kwagrs.get('content_object_id', '')
        # 将本地的relative_path下面的所有文件转为list
        native_file_list = []

        if not os.path.isdir(relative_path):
            raise Exception('找不到要同步的目录:%s' % (relative_path))

        for root, dirs, files in os.walk(relative_path):
            for name in files:
                native_file_list.append(os.path.join(root, name))

        # 转化update_file_list的格式为list绝对路径
        relative_path_with_version = os.path.join(relative_path, version)
        update_file_list = [os.path.join(relative_path_with_version, x['file_name']) for x in update_file_list]

        # 循环本地的文件，如果该文件不在update_file_list当中，则删除
        for x in native_file_list:
            if x not in update_file_list:
                os.remove(x)

        # 循环要更新的文件，如果该文件不在本地，报错
        for x in update_file_list:
            if x not in native_file_list:
                raise Exception('%s文件没有找到' % (x))

        # 执行rsync的命令
        cmd = """rsync --port=%d -aqz  --password-file=%s \
                --delete %s %s@%s::%s/""" % (port, pass_file, relative_path, user, ip, module)
        log.logger.info('rsync命令:%s' % (cmd))
        result = os.system(cmd)
        if result == 0:
            success = True
            log.logger.info('%s:rsync传送文件成功' % (uuid))
        else:
            success = False
            msg = 'rsync传送文件失败'
    except Exception as e:
        msg = str(e)
        success = False
        log.logger.error('%s-%s' % (uuid, msg))
    finally:
        # 回调CMDB接口让cmdb执行热更新命令
        log.logger.info('%s开始回调cmdb接口' % (uuid))
        cmdb_callback(msg, success, update_type, content_object_id, uuid)


@app.task(ignore_result=False)
def file_pull_15(project_name_en, **kwagrs):
    """
    file_path表示要拉取目录的根路径，比如/data/version_update/client/x/cn
    uuid表示要保存的关于一个工单的文件目录的副本
    update_type表示前后端
    version表示要拉取的具体版本目录
    project_name_en表示副本的项目名
    """
    success = False
    msg = ''
    list_file = []

    BACKUP_FILE_DIR = '/data/hot_backup'
    try:
        relative_path = kwagrs.get('relative_path', '')
        version = kwagrs.get('version', '')
        update_file_list = kwagrs.get('update_file_list', '')
        file_path = kwagrs.get('file_path', '')
        port = kwagrs.get('port', '')
        pass_file = kwagrs.get('pass_file', '')
        user = kwagrs.get('user', '')
        ip = kwagrs.get('ip', '')
        module = kwagrs.get('module', '')
        uuid = kwagrs.get('uuid', '')
        update_type = kwagrs.get('update_type', '')
        content_object_id = kwagrs.get('content_object_id', '')
        # 首先检测要copy的版本目录在不在
        if update_type == 'hot_client':
            from_path = os.path.join(file_path, version)
        elif update_type == 'hot_server':
            reloadfiles = 'reloadfiles'
            from_path = os.path.join(file_path, version, reloadfiles)
        else:
            raise Exception('未知的热更新类型')
        if os.path.isdir(from_path):
            area_name = os.path.basename(file_path)  # /data/version_update/client/x/cn ==> cn
            # 确定是否已经存在这个目录
            to_path = os.path.join(BACKUP_FILE_DIR, update_type, project_name_en, area_name, uuid, version)
            if os.path.isdir(to_path):
                shutil.rmtree(to_path)
            shutil.copytree(from_path, to_path)

            # 遍历新的文件目录
            for root, dirs, files in os.walk(to_path):
                for name in files:
                    file_path = root + '/' + name
                    file_md5 = md5Checksum(file_path)
                    relative_path = file_path[len(to_path) + 1:]
                    list_file.append({"file_name": relative_path, 'file_md5': file_md5})
            success = True
        else:
            success = False
            msg = '找不到该目录'
    except Exception as e:
        msg = str(e)
        success = False
    return (success, msg, list_file)


@app.task()
def add_mac(user, macaddr, wifi_workflow_id, touser=None):
    """
    Cisco AP 增加绑定mac地址
    :param user: 用户名，拼音全拼
    :param macaddr: mac地址，格式04:52:f3:0f:d6:8f。冒号隔开
    :return: {'ret':True,'msg':'添加成功'}
    """
    apinfo = {'device_type': 'cisco_wlc',
              'ip': '172.16.199.200',
              'username': 'skynet',
              'password': 'skynet@2017swItch',
              'port': 22
              }
    try:
        # 重新连接数据库
        close_old_connections()

        wifi_workflow = Wifi.objects.get(pk=wifi_workflow_id)
        macaddr = macaddr.replace('-', ':')
        net_connect = ConnectHandler(**apinfo)
        net_connect.enable()
        cmd = 'config macfilter add {0} 7 vlan204 {1} '.format(macaddr, user)
        result = net_connect.send_command(cmd)
        result = result.strip()
        net_connect.disconnect()
        if not result:
            wifi_workflow.wifi_add_result = '添加成功'
            # 将工单处理状态设置为已处理
            wifi_workflow.status = 0
            wifi_workflow.save()
            if touser:
                send_weixin_message.delay(touser=touser, content='wifi: Cy-work添加mac地址成功：{}'.format(wifi_workflow.mac))
            return {'ret': True, 'msg': '添加成功'}
        else:
            if 'MAC filter already exists' in str(result):
                result = 'mac地址已存在'
                # 将工单处理状态设置为已处理
                wifi_workflow.status = 0
                wifi_workflow.save()
            wifi_workflow.wifi_add_result = '添加失败, ' + result
            wifi_workflow.save()
            if touser:
                send_weixin_message.delay(touser=touser, content='wifi: Cy-work添加mac地址失败：{}'.format(result))
            return {'ret': False, 'msg': '添加失败, ' + result}
    except Exception as e:
        try:
            net_connect.disconnect()
        except:
            pass
        if touser:
            send_weixin_message.delay(touser=touser, content='wifi: Cy-work添加mac地址失败：{}'.format(str(e)))
        return {'ret': False, 'msg': str(e)}


@app.task()
def send_weixin_message(content, touser='', toparty='', totag=''):
    """发送微信消息"""
    if MSG_CHANNEL == 0 or MSG_CHANNEL == 2:
        try:
            # 重新连接数据库
            close_old_connections()

            # 查询是否需要特殊转换
            touser = wechat_account_check(touser)
            if not PRODUCTION_ENV:
                touser = 'chenjiefeng'
            # 检查token是否可用
            token = check_valid_wx_token()
            if token is None:
                result = get_weixin_api_token()
                if result['success']:
                    token = result['data']
                else:
                    return {'success': False, 'msg': result['msg']}

            need_parm = {'touser': touser, 'toparty': toparty, 'totag': totag}
            data = {
                "msgtype": "text",
                "agentid": 1000004,
                "text": {
                    "content": content,
                },
                "safe": 0
            }
            for x in need_parm.keys():
                if need_parm[x] != '':
                    data[x] = need_parm[x]
            url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=' + token
            headers = {'Accept': 'application/json'}

            s = Session()
            s.mount('https://', HTTPAdapter(max_retries=Retry(total=5, status_forcelist=[408])))
            res = s.post(url, json=data, headers=headers, timeout=60, verify=False)
            if res.status_code == 200:
                r = res.json()
                print(r)
                if r['errcode'] == 0:
                    return {'success': True, 'msg': '{}: 发送企业微信消息成功: {}'.format(touser, content)}
                elif r['errcode'] == 40014:
                    wx_token = WXAccessToken.objects.filter(access_token=token)
                    wx_token.update(valid=0)
                    get_weixin_api_token()
                    send_weixin_message(content, touser)
                else:
                    return {'success': False, 'msg': '{}: 发送企业微信消息失败: {}-{}'.format(touser, content, r['errmsg'])}
            else:
                return {'success': False, 'msg': '{}: 发送企业微信消息失败: {}-{}'.format(touser, content, str(res))}
        except Exception as e:
            return {'success': False, 'msg': '{}: 发送企业微信消息失败: {}-{}'.format(touser, content, str(e))}


@app.task()
def execute_salt_task(task_id, user_id, telecom_ip_list):
    try:
        # 重新连接数据库
        close_old_connections()
        """执行saltstack任务"""
        salt_task = SaltTask.objects.get(pk=task_id)
        task_name = salt_task.name
        config_filename = salt_task.saltconfig_set.all()[0].filename
        push_path = salt_task.saltconfig_set.all()[0].push_path
        request_user = User.objects.get(pk=user_id)
        """开始执行salt任务"""
        start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ws_update_task_result(start_time + ' - 开始执行任务『' + task_name + '』，请耐心等待结果...')
        """初始化salt-api类"""
        salt = salt_init()
        """所需参数"""
        if PRODUCTION_ENV:
            client = telecom_ip_list
        else:
            # client = ['salt-minion']
            client = ['119.29.79.89']
        fun = 'state.apply'
        prefix = format_saltstack_configfile_path(push_path)
        suffix = config_filename.split('.')[0]
        if prefix:
            _params = prefix + '.' + suffix
        else:
            _params = suffix
        """执行命令"""
        result = salt.salt_command(client, fun, arg=_params, tgt_type='list')
        """获取每台主机单独的执行结果，并保存到数据库"""
        result_list = format_saltstack_execute_result(result)
        """返回celery结果"""
        result = json.dumps(result, indent=4, ensure_ascii=False)
        ws_update_task_result(result)
        time.sleep(1)
        """执行结束"""
        end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ws_update_task_result(end_time + ' - 执行任务『' + task_name + '』结束...\n\n')
        """记录执行记录机器明细"""
        execute_history = SaltTaskExecuteHistory.objects.create(salt_task=salt_task, run_targets=client,
                                                                execute_user=request_user,
                                                                execute_result=result)
        for x in result_list:
            host = Host.objects.get(telecom_ip=x['ip'])
            SaltExecuteHistoryDetail.objects.create(execute_history=execute_history, host=host, status=x['status'],
                                                    result=x['result'])
    except Exception as e:
        print(str(e))
    finally:
        return result


@app.task()
def refresh_txcloud_cdn(refresh_type, refresh_obj, record_id):
    # 重新连接数据库
    close_old_connections()
    """更新腾讯云刷新cdn记录"""
    record_obj = CDNRefreshRecord.objects.get(pk=record_id)
    cdn_api = record_obj.cdn_api
    secret_id = cdn_api.secret_id
    secret_key = cdn_api.secret_key
    res = QcloudCdnRefresh(refresh_type, refresh_obj, secret_id, secret_key)
    if res['success']:
        task_id = res['task_id']
        """更新操作刷新CDN的日志"""
        record_obj.task_id = task_id
        record_obj.result = 0
        record_obj.finish_time = datetime.now()
        record_obj.save()

        return {'success': True, 'msg': '提交成功，任务当前结果：' + record_obj.get_result_display()}
    else:
        """更新操作刷新CDN的日志"""
        record_obj.result = -1
        record_obj.auto_refresh = 0
        record_obj.remark = res['msg']
        record_obj.save()
        return {'success': False, 'msg': res['msg']}


@app.task()
def refresh_bscloud_cdn(refresh_type, refresh_obj, record_id):
    # 重新连接数据库
    close_old_connections()
    """更新白山云刷新cdn记录"""
    record_obj = CDNRefreshRecord.objects.get(pk=record_id)
    cdn_api = record_obj.cdn_api
    token = cdn_api.token
    res = BScloudRefresh(refresh_type, refresh_obj, token)
    if res['success']:
        task_id = res['task_id']
        """更新操作刷新CDN的日志"""
        record_obj.task_id = task_id
        record_obj.result = 0
        record_obj.finish_time = datetime.now()
        record_obj.save()
        # # 查询30次，每次间隔5秒，大于30次则推出循环
        # while True:
        #     time.sleep(5)
        #     res = BScloudRefreshResultQuery(task_id, token)
        #     if res['success']:
        #         record_obj.result = 1
        #         record_obj.finish_time = datetime.now()
        #         record_obj.save()
        #         break
        #     else:
        #         record_obj.auto_refresh = record_obj.auto_refresh + 1
        #         record_obj.save()
        #         if record_obj.auto_refresh > 30:
        #             break

        return {'success': True, 'msg': '提交成功，任务当前结果：' + record_obj.get_result_display()}
    else:
        """更新操作刷新CDN的日志"""
        record_obj.result = -1
        record_obj.auto_refresh = 0
        record_obj.remark = res['msg']
        record_obj.save()
        return {'success': False, 'msg': res['msg']}


@app.task()
def game_server_action_task(action_type, game_server_id_list, batch, user_id, source_ip=''):
    """区服管理操作"""

    try:
        # 重新连接数据库
        close_old_connections()

        with transaction.atomic():
            user = User.objects.get(pk=user_id)
            game_server = GameServer.objects.filter(id__in=game_server_id_list)

            ops_game_server_dict = format_game_server_action_data(game_server)
            print(ops_game_server_dict)

            """记录操作日志"""
            my_uuid = str(uuid.uuid1())
            for x in game_server:
                GameServerActionRecord.objects.create(game_server=x, operation_type=action_type,
                                                      operation_user=user, result=2, uuid=my_uuid,
                                                      old_status=x.srv_status, source_ip=source_ip)

            for ops_manager, srv_id_list in ops_game_server_dict.items():
                if not ops_manager:
                    raise Exception('区服: {}，没有找到运维管理机'.format(json.dumps(srv_id_list)))
                if not ops_manager.enable:
                    raise Exception('运维管理机已被禁用: {}'.format(ops_manager.get_url()))

                """运维管理及上锁"""
                url = ops_manager.url
                list_ops_manager = list(set([x for x in OpsManager.objects.filter(url__icontains=url)]))
                list_ops_manager_status = [x.status for x in list_ops_manager]
                list_ops_manager_status_remark = [x.get_status_display() for x in list_ops_manager if
                                                  x.get_status_display() != '空闲']
                lock_reason = ','.join(list_ops_manager_status_remark)

                if len(list(set(list_ops_manager_status))) == 1 and '0' in list_ops_manager_status:
                    for ops_manager in list_ops_manager:
                        if action_type == 'start':
                            ops_manager.status = '11'
                        elif action_type == 'stop':
                            ops_manager.status = '12'
                        elif action_type == 'restart':
                            ops_manager.status = '13'
                        elif action_type == 'clean':
                            ops_manager.status = '14'
                        ops_manager.save()
                else:
                    content = '运维管理机处于被锁状态，正在{}'.format(lock_reason)
                    raise Exception(content)

                """更新区服为中间状态"""
                part_of_game_server = GameServer.objects.filter(srv_id__in=srv_id_list)
                if action_type == 'start':
                    part_of_game_server.update(srv_status=8)
                elif action_type == 'stop':
                    part_of_game_server.update(srv_status=9)
                elif action_type == 'restart':
                    part_of_game_server.update(srv_status=6)
                elif action_type == 'clean':
                    part_of_game_server.update(srv_status=7)
                else:
                    raise Exception('未知的操作类型')

                """发送到运维管理机"""
                url = ops_manager.get_url() + 'hot/game_server/'
                data = {
                    "action_type": action_type,
                    "srv_id_list": srv_id_list,
                    'uuid': my_uuid,
                }
                authorized_token = "Token " + ops_manager.token
                headers = {
                    'Accept': 'application/json',
                    'Authorization': authorized_token,
                    'Connection': 'keep-alive',
                }
                s = Session()
                s.mount('https://', HTTPAdapter(max_retries=Retry(total=5, status_forcelist=[408])))
                if PRODUCTION_ENV:
                    r = s.post(url, headers=headers, json=data, verify=False, timeout=10)
                    if r.status_code == 200:
                        result = r.json()
                        if not result['Accepted']:
                            raise Exception('发送运维管理机失败 {}'.format(ops_manager.get_url()))
                    else:
                        raise Exception('发送运维管理机失败 {}: {}'.format(ops_manager.get_url(), str(r)))

                """通知前端页面刷新结果"""
                msg = '提交成功，操作完成后页面会自动刷新！也可以进入<a href="/myworkflows/game_server_action_record/">区服操作记录</a>查看实时结果'
                if batch:
                    msg = '批量' + msg
                ws_update_game_server_action(msg)
                ws_update_game_server_action_record('update_table')

            return {'success': True, 'action_type': action_type,
                    'game_server_list': json.dumps([x.srv_id for x in game_server])}

    except Exception as e:
        msg = str(e)
        """通知前端页面刷新结果"""
        ws_update_game_server_action(msg)
        return {'success': False, 'action_type': action_type,
                'game_server_list': json.dumps([x.srv_id for x in game_server]), 'msg': msg}


@app.task()
def do_game_server_off(uuid):
    """
    区服下线异步任务
    """
    success = True
    msg = 'ok'
    try:
        # 重新连接数据库
        close_old_connections()

        game_server_off = GameServerOff.objects.get(uuid=uuid)
        """找出对应运维管理机"""
        game_server = [x.game_server for x in game_server_off.gameserveroffdetail_set.all()]
        list_ops_manager = list(set([x.get_ops_manager() for x in game_server if x.get_ops_manager()]))
        if not list_ops_manager:
            raise Exception('没有找到区服对应的运维管理机')
        list_ops_manager_status = [x.status for x in list_ops_manager]
        list_ops_manager_status_remark = [x.get_status_display() for x in list_ops_manager if
                                          x.get_status_display() != '空闲']
        lock_reason = ','.join(list_ops_manager_status_remark)
        """找到其他url相同的运维管理机，事实为同一台管理机，一起上锁"""
        for ops_obj in list_ops_manager:
            url = ops_obj.url
            for x in OpsManager.objects.filter(url__icontains=url):
                if x not in list_ops_manager:
                    list_ops_manager.append(x)
        """运维管理机上锁"""
        if len(list(set(list_ops_manager_status))) == 1 and '0' in list_ops_manager_status:
            for ops_manager in list_ops_manager:
                ops_manager.status = '8'
                ops_manager.save()
                level = 'INFO'
                content = ops_manager.get_url() + '成功上锁'
                write_game_server_off_log(level, content, game_server_off)
        else:
            level = 'ERROR'
            content = '运维管理机处于被锁状态，正在 {}'.format(lock_reason)
            write_game_server_off_log(level, content, game_server_off)
            game_server_off.status = 1
            game_server_off.save(update_fields=['status'])
            raise Exception(content)

        """开始发送请求到运维管理机"""
        for gs in game_server:
            ops_manager = gs.get_ops_manager()
            if not ops_manager:
                raise Exception('区服: {}，没有找到运维管理机'.format(gs.__str__()))
            if not ops_manager.enable:
                raise Exception('运维管理机已被禁用: {}'.format(ops_manager.get_url()))

            if PRODUCTION_ENV:
                url = ops_manager.get_url() + 'recycle/closeServer/'
                token = ops_manager.token
            else:
                url = 'https://192.168.90.210/api/recycle/closeServer/'
                token = '12312412513634675475686583568'
            data = {
                'sid': gs.sid,
                'uuid': uuid,
            }
            authorized_token = "Token " + token
            headers = {
                'Accept': 'application/json',
                'Authorization': authorized_token,
                'Connection': 'keep-alive',
            }
            s = Session()
            s.mount('https://', HTTPAdapter(max_retries=Retry(total=5, status_forcelist=[408])))
            r = s.post(url, headers=headers, json=data, verify=False, timeout=10)
            if r.status_code == 200:
                result = r.json()
                if result['accepted']:
                    level = 'INFO'
                    content = '发送区服%s到运维管理机%s成功' % (gs.sid, ops_manager.get_url())
                    write_game_server_off_log(level, content, game_server_off)
                else:
                    content = '发送区服%s到运维管理机%s失败' % (gs.sid, ops_manager.get_url()) + str(r.status_code)
                    game_server_off.status = 4
                    game_server_off.save(update_fields=['status'])
                    raise Exception(content)
            else:
                content = '发送区服%s到运维管理机%s失败' % (gs.sid, ops_manager.get_url()) + str(r.status_code)
                game_server_off.status = 4
                game_server_off.save(update_fields=['status'])
                raise Exception(content)

    except GameServerOff.DoesNotExist:
        success = False
        msg = '找不到区服下线任务 - %s' % uuid
    except Exception as e:
        success = False
        msg = str(e)
        level = 'ERROR'
        write_game_server_off_log(level, msg, game_server_off)
    finally:
        if not success:
            """并记录日志，通知刷新"""
            ws_update_game_server_off_list()
            level = 'ERROR'
            content = '执行失败，请查看原因'
            write_game_server_off_log(level, content, game_server_off)
            """通知任务负责人"""
            # user_objs = game_server_off.get_related_user()
            user_objs = game_server_off.get_relate_role_user()
            qq_users = ','.join([x.first_name for x in user_objs])
            wx_users = '|'.join([x.first_name for x in user_objs])
            email_users = [x.email for x in user_objs]
            subject = '项目下架失败'
            content = '您所负责的项目下架计划 %s 失败，原因： %s，请登录cmdb查看' % (game_server_off.uuid, msg)
            send_qq.delay(qq_users, subject, subject, content, 'https://cmdb.cy666.com/')
            send_weixin_message.delay(touser=wx_users, content=content)
            send_mail.delay(email_users, subject, content)
        return {'success': success, 'msg': msg}


@app.task()
def do_host_migrate(uuid):
    """
    主机迁服异步任务
    """
    success = True
    msg = 'ok'
    try:
        # 重新连接数据库
        close_old_connections()

        host_compression = HostCompressionApply.objects.get(uuid=uuid)
        """找出对应运维管理机"""
        host_ip_list = [x.ip for x in host_compression.hostcompressiondetail_set.all()]
        host_list = Host.objects.filter(telecom_ip__in=host_ip_list)
        list_ops_manager = list(set([x.opsmanager for x in host_list if x.opsmanager]))
        if not list_ops_manager:
            raise Exception('没有找到主机对应的运维管理机')
        list_ops_manager_status = [x.status for x in list_ops_manager]
        list_ops_manager_status_remark = [x.get_status_display() for x in list_ops_manager if
                                          x.get_status_display() != '空闲']
        lock_reason = ','.join(list_ops_manager_status_remark)
        """找到其他url相同的运维管理机，事实为同一台管理机，一起上锁"""
        for ops_obj in list_ops_manager:
            url = ops_obj.url
            for x in OpsManager.objects.filter(url__icontains=url):
                if x not in list_ops_manager:
                    list_ops_manager.append(x)
        """运维管理机上锁"""
        if len(list(set(list_ops_manager_status))) == 1 and '0' in list_ops_manager_status:
            for ops_manager in list_ops_manager:
                ops_manager.status = '9'
                ops_manager.save()
                level = 'INFO'
                content = ops_manager.get_url() + '成功上锁'
                write_host_compression_log(level, content, host_compression)
        else:
            level = 'ERROR'
            content = '运维管理机处于被锁状态，正在 {}'.format(lock_reason)
            write_host_compression_log(level, content, host_compression)
            host_compression.action_status = 1
            host_compression.save(update_fields=['action_status'])
            raise Exception(content)

        """开始发送请求到运维管理机"""
        for host in host_list:
            ops_manager = host.opsmanager
            if not ops_manager:
                raise Exception('主机: {}，没有设置运维管理机'.format(host.telecom_ip))
            if not ops_manager.enable:
                raise Exception('运维管理机已被禁用: {}'.format(ops_manager.get_url()))
            sid_list = host.get_sid_list()
            if not sid_list:
                host_compression.action_status = 4
                host_compression.save(update_fields=['action_status'])
                level = 'INFO'
                content = '该主机%s已没有任何区服' % host.telecom_ip
                write_host_compression_log(level, content, host_compression)
                continue

            for sid in sid_list:
                if PRODUCTION_ENV:
                    url = ops_manager.get_url() + 'recycle/migrateServer/'
                    token = ops_manager.token
                else:
                    url = 'https://192.168.90.210/api/recycle/migrateServer/'
                    token = '12312412513634675475686583568'
                data = {
                    'sid': sid,
                    'uuid': uuid,
                }
                authorized_token = "Token " + token
                headers = {
                    'Accept': 'application/json',
                    'Authorization': authorized_token,
                    'Connection': 'keep-alive',
                }
                s = Session()
                s.mount('https://', HTTPAdapter(max_retries=Retry(total=5, status_forcelist=[408])))
                r = s.post(url, headers=headers, json=data, verify=False, timeout=10)
                if r.status_code == 200:
                    result = r.json()
                    if result['accepted']:
                        level = 'INFO'
                        content = '发送区服%s到运维管理机%s成功' % (sid, ops_manager.get_url())
                        write_host_compression_log(level, content, host_compression)
                    else:
                        content = '发送区服%s到运维管理机%s失败' % (sid, ops_manager.get_url()) + str(r.status_code)
                        host_compression.action_status = 4
                        host_compression.save(update_fields=['action_status'])
                        raise Exception(content)
                else:
                    content = '发送区服%s到运维管理机%s失败' % (sid, ops_manager.get_url()) + str(r.status_code)
                    host_compression.action_status = 4
                    host_compression.save(update_fields=['action_status'])
                    raise Exception(content)

    except HostCompressionApply.DoesNotExist:
        success = False
        msg = '找不到该主机迁服任务 - %s' % uuid
    except Exception as e:
        success = False
        msg = str(e)
        level = 'ERROR'
        write_host_compression_log(level, msg, host_compression)
    finally:
        if not success:
            """并记录日志，通知刷新"""
            ws_update_host_compression_list()
            level = 'ERROR'
            content = '迁服失败，请查看原因'
            write_host_compression_log(level, content, host_compression)
            """通知任务负责人"""
            user_objs = host_compression.ops
            qq_users = user_objs.first_name
            wx_users = user_objs.first_name
            email_users = [user_objs.email]
            subject = '主机迁服失败'
            content = '主机迁服 %s 失败，请登录cmdb查看原因' % host_compression.title
            send_qq.delay(qq_users, subject, subject, content, 'https://cmdb.cy666.com/')
            send_weixin_message.delay(touser=wx_users, content=content)
            send_mail.delay(email_users, subject, content)
        return {'success': success, 'msg': msg}


@app.task()
def do_host_recover(uuid):
    """
    主机回收异步任务
    """
    success = True
    msg = 'ok'
    try:
        # 重新连接数据库
        close_old_connections()

        host_compression = HostCompressionApply.objects.get(uuid=uuid)
        """找出对应运维管理机"""
        host_ip_list = [x.ip for x in host_compression.hostcompressiondetail_set.all()]
        host_list = Host.objects.filter(telecom_ip__in=host_ip_list)
        list_ops_manager = list(set([x.opsmanager for x in host_list if x.opsmanager]))
        if not list_ops_manager:
            raise Exception('没有找到主机对应的运维管理机')
        list_ops_manager_status = [x.status for x in list_ops_manager]
        list_ops_manager_status_remark = [x.get_status_display() for x in list_ops_manager if
                                          x.get_status_display() != '空闲']
        lock_reason = ','.join(list_ops_manager_status_remark)
        """找到其他url相同的运维管理机，事实为同一台管理机，一起上锁"""
        for ops_obj in list_ops_manager:
            url = ops_obj.url
            for x in OpsManager.objects.filter(url__icontains=url):
                if x not in list_ops_manager:
                    list_ops_manager.append(x)
        """运维管理机上锁"""
        if len(list(set(list_ops_manager_status))) == 1 and '0' in list_ops_manager_status:
            for ops_manager in list_ops_manager:
                ops_manager.status = '9'
                ops_manager.save()
                level = 'INFO'
                content = ops_manager.get_url() + '成功上锁'
                write_host_compression_log(level, content, host_compression)
        else:
            level = 'ERROR'
            content = '运维管理机处于被锁状态，正在 {}'.format(lock_reason)
            write_host_compression_log(level, content, host_compression)
            host_compression.recover_status = 1
            host_compression.save(update_fields=['recover_status'])
            raise Exception(content)

        """开始发送请求到运维管理机"""
        for host in host_list:
            ops_manager = host.opsmanager
            if not ops_manager:
                raise Exception('主机: {}，没有设置运维管理机'.format(host.telecom_ip))
            if not ops_manager.enable:
                raise Exception('运维管理机已被禁用: {}'.format(ops_manager.get_url()))
            if PRODUCTION_ENV:
                url = ops_manager.get_url() + 'recycle/recycleHost/'
                token = ops_manager.token
            else:
                url = 'https://192.168.90.210/api/recycle/recycleHost/'
                token = '12312412513634675475686583568'
            data = {
                'ip': host.telecom_ip,
                'uuid': uuid,
            }
            authorized_token = "Token " + token
            headers = {
                'Accept': 'application/json',
                'Authorization': authorized_token,
                'Connection': 'keep-alive',
            }
            s = Session()
            s.mount('https://', HTTPAdapter(max_retries=Retry(total=5, status_forcelist=[408])))
            r = s.post(url, headers=headers, json=data, verify=False, timeout=10)
            if r.status_code == 200:
                result = r.json()
                if result['accepted']:
                    level = 'INFO'
                    content = '发送主机%s到运维管理机%s成功' % (host.telecom_ip, ops_manager.get_url())
                    write_host_compression_log(level, content, host_compression)
                else:
                    content = '发送主机%s到运维管理机%s失败' % (host.telecom_ip, ops_manager.get_url()) + str(r.status_code)
                    host_compression.recover_status = 4
                    host_compression.save(update_fields=['recover_status'])
                    raise Exception(content)
            else:
                content = '发送主机%s到运维管理机%s失败' % (host.telecom_ip, ops_manager.get_url()) + str(r.status_code)
                host_compression.recover_status = 4
                host_compression.save(update_fields=['recover_status'])
                raise Exception(content)

    except GameServerOff.DoesNotExist:
        success = False
        msg = '找不到该主机回收任务 - %s' % uuid
    except Exception as e:
        success = False
        msg = str(e)
        level = 'ERROR'
        write_host_compression_log(level, msg, host_compression)
    finally:
        if not success:
            """并记录日志，通知刷新"""
            ws_update_host_compression_list()
            level = 'ERROR'
            content = '回收失败，请查看原因'
            write_host_compression_log(level, content, host_compression)
            """通知任务负责人"""
            user_objs = host_compression.ops
            qq_users = user_objs.first_name
            wx_users = user_objs.first_name
            email_users = [user_objs.email]
            subject = '主机回收失败'
            content = '主机回收 %s 失败，请登录cmdb查看原因' % host_compression.title
            send_qq.delay(qq_users, subject, subject, content, 'https://cmdb.cy666.com/')
            send_weixin_message.delay(touser=wx_users, content=content)
            send_mail.delay(email_users, subject, content)
        return {'success': success, 'msg': msg}


@app.task()
def cancel_desired_user_workflow_apply(user_id):
    # 重新连接数据库
    close_old_connections()

    """取消离职人员未完成审批的工单，走本地worker"""
    user = User.objects.get(pk=user_id)
    wse_list = get_user_workflow_apply(user)
    print('取消工单：', wse_list)
    for wse in wse_list:
        success, msg = cancel_workflow_apply(wse.id)
        print(success, msg)


@app.task(ignore_result=False)
def file_pull_23(project_name_en, **kwagrs):
    """原力官网机器，拉取更新列表函数"""
    pass


@app.task(ignore_result=True)
def file_push_23(project_name_en, **kwagrs):
    """原力官网机器，推送更新列表函数"""
    pass


@app.task()
def do_modify_srv_open_time(uuid):
    success = True
    msg = '发送运维管理机成功'
    try:
        # 重新连接数据库
        close_old_connections()

        modify_schedule = ModifyOpenSrvSchedule.objects.get(uuid=uuid)
        modify_schedule.status = 2
        modify_schedule.save(update_fields=['status'])
        ws_modify_srv_open_time_schedule_list()
        level = 'INFO'
        content = '开始执行'
        write_modify_srv_open_time_schedule_log(level, content, modify_schedule)

        """找出对应运维管理机"""
        game_server_list = [x.game_server for x in modify_schedule.modifyopensrvscheduledetail_set.all()]
        list_ops_manager = list(set([x.get_ops_manager() for x in game_server_list if x.get_ops_manager()]))
        if not list_ops_manager:
            raise Exception('没有找到区服对应的运维管理机')
        list_ops_manager_status = [x.status for x in list_ops_manager]
        list_ops_manager_status_remark = [x.get_status_display() for x in list_ops_manager if
                                          x.get_status_display() != '空闲']
        lock_reason = ','.join(list_ops_manager_status_remark)
        """找到其他url相同的运维管理机，事实为同一台管理机，一起上锁"""
        for ops_obj in list_ops_manager:
            url = ops_obj.url
            for x in OpsManager.objects.filter(url__icontains=url):
                if x not in list_ops_manager:
                    list_ops_manager.append(x)
        """运维管理机上锁"""
        if len(list(set(list_ops_manager_status))) == 1 and '0' in list_ops_manager_status:
            for ops_manager in list_ops_manager:
                ops_manager.status = '10'
                ops_manager.save()
                level = 'INFO'
                content = ops_manager.get_url() + '成功上锁'
                write_modify_srv_open_time_schedule_log(level, content, modify_schedule)
        else:
            level = 'ERROR'
            content = '运维管理机处于被锁状态，正在 {}'.format(lock_reason)
            write_modify_srv_open_time_schedule_log(level, content, modify_schedule)
            modify_schedule.status = 1
            modify_schedule.save(update_fields=['status'])
            raise Exception(content)

        """开始发送运维管理机"""
        for gs in game_server_list:
            ops_manager = gs.get_ops_manager()
            if not ops_manager:
                raise Exception('区服: {}，没有找到运维管理机'.format(gs.__str__()))
            if not ops_manager.enable:
                raise Exception('运维管理机已被禁用: {}'.format(ops_manager.get_url()))

            url = ops_manager.get_url() + 'hot/game_server/'
            token = ops_manager.token
            data = {
                'project': gs.project.project_name_en,
                'area': gs.host.belongs_to_room.area.short_name,
                'sid': gs.sid,
                'uuid': uuid,
                'open_time': int(time.mktime(time.strptime(str(modify_schedule.open_time), '%Y-%m-%d %H:%M:%S'))),
                'action_type': 'optime',
            }
            authorized_token = "Token " + token
            headers = {
                'Accept': 'application/json',
                'Authorization': authorized_token,
                'Connection': 'keep-alive',
            }
            s = Session()
            s.mount('https://', HTTPAdapter(max_retries=Retry(total=5, status_forcelist=[408])))
            if PRODUCTION_ENV:
                r = s.post(url, headers=headers, json=data, verify=False, timeout=10)
                if r.status_code == 200:
                    result = r.json()
                    if result['accepted']:
                        level = 'INFO'
                        content = '发送区服%s到运维管理机%s成功' % (gs.sid, ops_manager.get_url())
                        write_modify_srv_open_time_schedule_log(level, content, modify_schedule)
                    else:
                        content = '发送区服%s到运维管理机%s失败:' % (gs.sid, ops_manager.get_url()) + str(r.status_code)
                        modify_schedule.status = 4
                        modify_schedule.save(update_fields=['status'])
                        raise Exception(content)
                else:
                    content = '发送区服%s到运维管理机%s失败:' % (gs.sid, ops_manager.get_url()) + str(r.status_code)
                    modify_schedule.status = 4
                    modify_schedule.save(update_fields=['status'])
                    raise Exception(content)
            else:
                level = 'INFO'
                content = '发送区服%s到运维管理机%s成功' % (gs.sid, ops_manager.get_url())
                write_modify_srv_open_time_schedule_log(level, content, modify_schedule)

    except ModifyOpenSrvSchedule.DoesNotExist:
        success = False
        msg = '修改开服时间计划不存在:%s' % uuid
    except Exception as e:
        success = False
        msg = str(e)
    finally:
        if not success:
            """记录日志，通知刷新"""
            ws_modify_srv_open_time_schedule_list()
            level = 'ERROR'
            content = '执行失败，请登录cmdb查看原因: %s' % msg
            write_modify_srv_open_time_schedule_log(level, content, modify_schedule)
            """通知任务负责人"""
            user_objs = modify_schedule.get_relate_role_user()
            qq_users = ','.join([x.first_name for x in user_objs])
            wx_users = '|'.join([x.first_name for x in user_objs])
            email_users = [x.email for x in user_objs]
            subject = '修改开服时间失败'
            content = '您所负责的修改开服时间任务 %s 失败，原因： %s，请登录cmdb查看' % (modify_schedule.uuid, msg)
            send_qq.delay(qq_users, subject, subject, content, 'https://cmdb.cy666.com/')
            send_weixin_message.delay(touser=wx_users, content=content)
            send_mail.delay(email_users, subject, content)
        return success, msg


@app.task()
def send_task_card_to_wx_user(touser, data):
    log = SendWxTaskCardLog()
    success = True
    msg = 'ok'
    try:
        # 重新连接数据库
        close_old_connections()

        """发送任务卡片给微信用户"""
        touser = wechat_account_check(touser)
        if not PRODUCTION_ENV:
            touser = 'chenjiefeng'

        token = check_valid_wx_token()
        if token is None:
            result = get_weixin_api_token()
            if result['success']:
                token = result['data']
            else:
                raise Exception(result['msg'])

        data = data
        url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=' + token
        headers = {'Accept': 'application/json'}

        """发送任务卡片内容"""
        log.logger.info('发送任务卡片的内容: {}'.format(json.dumps(data)))

        res = requests.post(url, json=data, headers=headers, timeout=60, verify=False)
        if res.status_code == 200:
            r = res.json()
            log.logger.info(r)
            if r['errcode'] == 0:
                msg = '{}: 发送企业微信任务卡片成功，task_id：{}，内容：{}'.format(touser, data['taskcard']['task_id'],
                                                                 data['taskcard']['description'])
                log.logger.info(msg)
                if r.get('invaliduser', None):
                    """如果发送任务卡片失败，则发送微信消息提醒登录网页进行审批"""
                    log.logger.error('发送企业微信任务卡片失败的用户：' + r.get('invaliduser'))
                    data = get_wx_notify()
                    send_weixin_message.delay(touser=touser, content=data)
            elif r['errcode'] == 40014:
                wx_token = WXAccessToken.objects.filter(access_token=token)
                wx_token.update(valid=0)
                """如果token失效，则重新获取token再次发送任务卡片"""
                get_weixin_api_token()
                send_task_card_to_wx_user(touser, data)
            else:
                success = False
                raise Exception(touser + ': 发送企业微信任务卡片失败' + r['errmsg'])
        else:
            success = False
            raise Exception(touser + ': 发送企业微信任务卡片失败' + str(res))
    except Exception as e:
        success = False
        msg = '{}：发送企业微信任务卡片失败，内容：{}，原因：{}'.format(touser, data['taskcard']['description'], str(e))
        log.logger.error(msg)
        """如果发送任务卡片失败，则发送微信消息提醒登录网页进行审批"""
        data = get_wx_notify()
        send_weixin_message.delay(touser=touser, content=data)
    finally:
        return {'success': success, 'msg': msg}


def cmp_tuple(tuple1, tuple2):
    """
    对比两个元组中的元素，
    如果所有元素都相同（不分先后顺序），则返回True，
    如果存在差异，则返回False，并列出差异元素
    """
    t1 = tuple(sorted(list(tuple1), reverse=False))
    t2 = tuple(sorted(list(tuple2), reverse=False))
    eq = operator.eq(t1, t2)
    if eq:
        return True, ''
    else:
        s1 = set()
        for t in t1:
            if t not in t2:
                s1.add(t)
        if s1:
            s1 = ','.join(s1)
            msg1 = '减少IP段：{}'.format(s1)
        else:
            msg1 = ''
        s2 = set()
        for t in t2:
            if t not in t1:
                s2.add(t)
        if s2:
            s2 = ','.join(s2)
            msg2 = '新增IP段：{}'.format(s2)
        else:
            msg2 = ''
        if msg1 or msg2:
            return False, msg1 + ',   ' + msg2


@app.task()
def wx_whitelist_task():
    """检测微信回调服务器IP定时任务"""
    success = True
    msg = 'ok'
    try:
        # 重新连接数据库
        close_old_connections()

        token = check_valid_wx_token()
        if token is None:
            result = get_weixin_api_token()
            if result['success']:
                token = result['data']
            else:
                return {'success': False, 'msg': result['msg']}

        url = 'https://qyapi.weixin.qq.com/cgi-bin/getcallbackip?access_token=' + token

        r = requests.get(url)
        if r.status_code == 200:
            res = r.json()
            remote = tuple(res['ip_list'])
            """对比IP列表"""
            local = wx_whitelist_ip
            success, msg = cmp_tuple(local, remote)
            if not success:
                config = SpecialUserParamConfig.objects.get(param='WX_WHITELIST_ADMINISTRATOR')
                touser = '|'.join([u.first_name for u in config.user.all()])
                content = '微信服务器白名单IP发生变化！ {}'.format(msg)
                send_weixin_message.delay(touser=touser, content=content)
                to_list = [u.first_name for u in config.user.all()]
                subject = '微信服务器白名单IP发生变化'
                send_mail.delay(to_list, subject, content)
        else:
            raise Exception(str(r.status_code))
    except SpecialUserParamConfig.DoesNotExist:
        success = False
        msg = '没有配置微信服务器白名单管理员参数'
    except Exception as e:
        success = False
        msg = str(e)
    finally:
        return {'success': success, 'msg': msg}


@app.task()
def do_game_server_migrate(game_server_id, user_id):
    """
    单个区服迁服异步任务
    """
    success = True
    msg = 'ok'
    try:
        # 重新连接数据库
        close_old_connections()

        with transaction.atomic():
            game_server = GameServer.objects.get(id=game_server_id)
            user = User.objects.get(pk=user_id)
            """创建迁服记录"""
            myuuid = str(uuid.uuid1()) + '-migrate'
            GameServerActionRecord.objects.create(game_server=game_server, operation_type='migrate',
                                                  operation_user=user, uuid=myuuid, old_status=game_server.srv_status)
            game_server.srv_status = 10
            game_server.save(update_fields=['srv_status'])
            """找出对应运维管理机"""
            ops_manager = game_server.get_ops_manager()
            if not ops_manager:
                raise Exception('没有找到主机对应的运维管理机')
            ops_manager_status = ops_manager.status
            lock_reason = ops_manager.get_status_display()
            """找到其他url相同的运维管理机，事实为同一台管理机，一起上锁"""
            list_ops_manager = set()
            url = ops_manager.url
            for x in OpsManager.objects.filter(url__icontains=url):
                list_ops_manager.add(x)
            list_ops_manager = list(list_ops_manager)
            """运维管理机上锁"""
            if ops_manager_status == '0':
                for ops_manager in list_ops_manager:
                    ops_manager.status = '15'
                    ops_manager.save()
            else:
                content = '运维管理机处于被锁状态，正在 {}'.format(lock_reason)
                raise Exception(content)

            """开始发送请求到运维管理机"""
            sid = game_server.sid
            if not sid:
                raise Exception('该区服没有回调sid，请先回调！')
            if PRODUCTION_ENV:
                url = ops_manager.get_url() + 'recycle/migrateServer/'
                token = ops_manager.token
            else:
                url = 'https://192.168.90.210/api/recycle/migrateServer/'
                token = '12312412513634675475686583568'
            data = {
                'sid': sid,
                'uuid': myuuid,
            }
            authorized_token = "Token " + token
            headers = {
                'Accept': 'application/json',
                'Authorization': authorized_token,
                'Connection': 'keep-alive',
            }
            s = Session()
            s.mount('https://', HTTPAdapter(max_retries=Retry(total=5, status_forcelist=[408])))
            r = s.post(url, headers=headers, json=data, verify=False, timeout=10)
            if r.status_code == 200:
                result = r.json()
                if result['accepted']:
                    msg = '发送区服%s到运维管理机%s成功' % (sid, ops_manager.get_url())
                else:
                    content = '发送区服%s到运维管理机%s失败' % (sid, ops_manager.get_url()) + str(r.status_code)
                    raise Exception(content)
            else:
                content = '发送区服%s到运维管理机%s失败' % (sid, ops_manager.get_url()) + str(r.status_code)
                raise Exception(content)
            content = '发送区服%s到运维管理机%s成功' % (sid, ops_manager.get_url())
            ws_update_game_server_action(content)
            ws_update_game_server_action_record('update_table')

    except Exception as e:
        success = False
        msg = str(e)
        ws_update_game_server_action(msg)
    finally:
        return {'success': success, 'msg': msg}


@app.task()
def install_salt_minion(telecom_ip_list):
    """
    主机初始化步骤 1：安装salt-minion客户端
    给运维管理机发送主机salt-minion的异步请求
    """
    success = True
    msg = 'ok'
    try:
        # 重新连接数据库
        close_old_connections()

        # 先test.ping测试是否通，不通则继续发送安装请求，通则直接进入步骤3：初始化主机,更新安装状态为成功
        for ip in telecom_ip_list:
            ping_success, msg = saltstack_test_ping(ip)
            if ping_success:
                saltstack_host_initialize.delay(ip)
                host_initialize = HostInitialize.objects.get(telecom_ip=ip)
                host_initialize.install_status = 2
                host_initialize.save(update_fields=['install_status'])
                ws_update_host_initialize_list()
                write_host_initialize_log('INFO', 'test.ping测试通过，直接进入【步骤3】', host_initialize)
                write_host_initialize_log('INFO', '【步骤3】-【开始】-【执行初始化初始化】', host_initialize)
                telecom_ip_list.remove(ip)
        # 如果telecom_ip_list还有IP，则开始发送安装客户端请求
        if telecom_ip_list:
            host_initialize = HostInitialize.objects.filter(telecom_ip__in=telecom_ip_list)
            url = 'https://119.29.79.89/api/install/installagent/'
            token = '12312412513634675475686583568'
            minion_list = []
            for i in host_initialize:
                minion_list.append({
                    'minion_ip': i.telecom_ip,
                    'user': i.sshuser,
                    'password': i.password,
                    'port': i.sshport,
                    'master_ip': i.syndic_ip,
                    'iname': i.project.project_name_en,
                    'gtype': i.business.business_name,
                    'jf': i.room.room_name_en,
                    'area': i.room.area.short_name,
                })
            data = {
                'uuid': str(uuid.uuid1()),
                "minion_list": minion_list
            }
            authorized_token = "Token " + token
            headers = {
                'Accept': 'application/json',
                'Authorization': authorized_token,
                'Connection': 'keep-alive',
            }
            s = Session()
            s.mount('https://', HTTPAdapter(max_retries=Retry(total=5, status_forcelist=[408])))
            r = s.post(url, headers=headers, json=data, verify=False, timeout=10)
            if r.status_code == 200:
                result = r.json()
                print(result)
                if result['Accepted']:
                    msg = '发送安装salt-minion请求成功'
                    for i in host_initialize:
                        write_host_initialize_log('INFO', msg, i)
                else:
                    msg = '发送安装salt-minion请求失败: {}'.format(str(r.status_code))
                    raise Exception(msg)
            else:
                msg = '发送安装salt-minion请求失败: {}'.format(str(r.status_code))
                raise Exception(msg)

    except Exception as e:
        success = False
        msg = str(e)
        # 更新失败结果
        host_initialize = HostInitialize.objects.filter(telecom_ip__in=telecom_ip_list)
        host_initialize.update(**{'install_status': 3, 'install_remark': msg})
        for i in host_initialize:
            write_host_initialize_log('ERROR', msg, i)
            # 发送邮件/QQ/微信消息
            to_list = [host_initialize.add_user.email]
            first_name = host_initialize.add_user.first_name
            subject = '主机初始化结果-{}'.format(i.telecom_ip)
            content = '主机初始化【步骤1】-【安装salt-minion】失败，IP: {}，请登录cmdb查看详细日志！'.format(i.telecom_ip)
            if to_list:
                send_mail.delay(to_list, subject, content)
            send_qq.delay(first_name, subject, subject, content, '')
            send_weixin_message.delay(touser=first_name, content=content)
    finally:
        return {'success': success, 'msg': msg}


@app.task()
def saltstack_test_ping_tasks(telecom_ip, host_initialize_id):
    """
    主机初始化步骤 2：测试salt-minion客户端连通性异步任务
    - 测试主机salt-minion的连通性
    - 如果失败则过60秒再尝试，循环3次都失败则不再尝试
    - 如果3次内成功，则返回成功
    """
    try:
        # 重新连接数据库
        close_old_connections()

        time.sleep(5)
        host_initialize = HostInitialize.objects.get(pk=host_initialize_id)
        i = 1
        while i < 4:
            result, msg = saltstack_test_ping(telecom_ip)
            if result:
                host_initialize.install_status = 2
                host_initialize.save(update_fields=['install_status'])
                ws_update_host_initialize_list()
                log = '第{}次 {}'.format(i, msg)
                write_host_initialize_log('INFO', log, host_initialize)
                print(log)
                # 开始执行主机初始化异步任务
                host_initialize.initialize_status = 1
                host_initialize.save(update_fields=['initialize_status'])
                ws_update_host_initialize_list()
                write_host_initialize_log('INFO', '【步骤3】-【开始】-【执行初始化模块】', host_initialize)
                saltstack_host_initialize.delay(telecom_ip)
                return
            else:
                if i < 3:
                    log = '第{}次 {}{}'.format(i, msg, '，等待60秒后再尝试......')
                else:
                    log = '第{}次 {}{}'.format(i, msg, '，退出')
                write_host_initialize_log('ERROR', log, host_initialize)
                print(log)

            i += 1
            if i > 3:
                break
            time.sleep(60)

        host_initialize.install_status = 3
        host_initialize.save(update_fields=['install_status'])
        ws_update_host_initialize_list()
        # 发送邮件/QQ/微信消息
        to_list = [host_initialize.add_user.email]
        first_name = host_initialize.add_user.first_name
        subject = '主机初始化结果-{}'.format(host_initialize.telecom_ip)
        content = '主机初始化【步骤2】-【test.ping测试】失败，IP: {}，请登录cmdb查看详细日志！'.format(host_initialize.telecom_ip)
        if to_list:
            send_mail.delay(to_list, subject, content)
        send_qq.delay(first_name, subject, subject, content, '')
        send_weixin_message.delay(touser=first_name, content=content)
        return
    except Exception as e:
        print(str(e))


@app.task()
def saltstack_host_initialize(telecom_ip):
    """
    主机初始化步骤 3：调用salt-api执行主机初始化
    """
    level = "INFO"
    try:
        # 重新连接数据库
        close_old_connections()

        host_initialize = HostInitialize.objects.get(telecom_ip=telecom_ip)
        salt = salt_init()
        client = [telecom_ip]
        fun = 'state.sls'
        arg = 'start_init'
        # 执行异步命令
        job_id = salt.salt_async_command(client, fun, arg=arg, tgt_type='list')
        print('主机初始化步骤3: saltstack异步任务id: {}'.format(job_id))
        write_host_initialize_log(level, '发送主机初始化请求成功，请耐心等待返回...', host_initialize)
        # 每隔2秒获取一次结果，600s后认为任务超时
        time.sleep(2)
        start_time = int(time.time())
        while not salt.look_jid(job_id):
            time.sleep(2)
            now = int(time.time())
            if now - start_time > 1200:
                raise Exception('主机初始化超时')
        # 格式化任务输出结果
        result = salt.look_jid(job_id)
        print(json.dumps(result, indent=4, ensure_ascii=False))
        success, result = format_saltstack_host_initialize_result(result, telecom_ip)
        result = json.dumps(result, indent=4, ensure_ascii=False)
        if success:
            write_host_initialize_log(level, result, host_initialize)
            if 'false' in result:
                host_initialize.initialize_status = 3
                host_initialize.save(update_fields=['initialize_status'])
                ws_update_host_initialize_list()
                # 发送邮件/QQ/微信消息
                to_list = [host_initialize.add_user.email]
                first_name = host_initialize.add_user.first_name
                subject = '主机初始化结果-{}'.format(host_initialize.telecom_ip)
                content = '主机初始化【步骤3】-【执行初始化模块】失败，IP: {}，请登录cmdb查看详细日志！'.format(host_initialize.telecom_ip)
                if to_list:
                    send_mail.delay(to_list, subject, content)
                send_qq.delay(first_name, subject, subject, content, '')
                send_weixin_message.delay(touser=first_name, content=content)
            else:
                # 开始执行主机环境测试
                write_host_initialize_log('INFO', '【步骤4】-【开始】-【执行主机环境测试】', host_initialize)
                saltstack_host_check.delay(telecom_ip)
        else:
            level = 'ERROR'
            host_initialize.initialize_status = 3
            host_initialize.save(update_fields=['initialize_status'])
            ws_update_host_initialize_list()
            write_host_initialize_log(level, result, host_initialize)
            # 发送邮件/QQ/微信消息
            to_list = [host_initialize.add_user.email]
            first_name = host_initialize.add_user.first_name
            subject = '主机初始化结果-{}'.format(host_initialize.telecom_ip)
            content = '主机初始化【步骤3】-【执行初始化模块】失败，IP: {}，请登录cmdb查看详细日志！'.format(host_initialize.telecom_ip)
            if to_list:
                send_mail.delay(to_list, subject, content)
            send_qq.delay(first_name, subject, subject, content, '')
            send_weixin_message.delay(touser=first_name, content=content)

    except Exception as e:
        result = str(e)
        level = 'ERROR'
        write_host_initialize_log(level, result, host_initialize)
        # 发送邮件/QQ/微信消息
        to_list = [host_initialize.add_user.email]
        first_name = host_initialize.add_user.first_name
        subject = '主机初始化结果-{}'.format(host_initialize.telecom_ip)
        content = '主机初始化【步骤3】-【执行初始化模块】失败，IP: {}，请登录cmdb查看详细日志！'.format(host_initialize.telecom_ip)
        if to_list:
            send_mail.delay(to_list, subject, content)
        send_qq.delay(first_name, subject, subject, content, '')
        send_weixin_message.delay(touser=first_name, content=content)


@app.task()
def saltstack_host_check(telecom_ip):
    """
    主机初始化步骤 4： 主机环境测试
    """
    level = "INFO"
    try:
        # 重新连接数据库
        close_old_connections()

        host_initialize = HostInitialize.objects.get(telecom_ip=telecom_ip)
        salt = salt_init()
        client = [telecom_ip]
        fun = 'state.sls'
        arg = 'check_host'
        # 执行异步命令
        job_id = salt.salt_async_command(client, fun, arg=arg, tgt_type='list')
        write_host_initialize_log(level, '发送主机环境测试请求成功，请耐心等待返回...', host_initialize)
        print('主机初始化步骤4: saltstack异步任务id: {}'.format(job_id))
        # 每隔2秒获取一次结果，30s后认为任务超时
        time.sleep(2)
        start_time = int(time.time())
        while not salt.look_jid(job_id):
            time.sleep(2)
            now = int(time.time())
            if now - start_time > 30:
                raise Exception('主机环境测试超时')
        # 格式化任务输出结果
        result = salt.look_jid(job_id)
        print(json.dumps(result, indent=4, ensure_ascii=False))
        success, result = format_saltstack_host_check_result(result, telecom_ip)
        if success:
            error_flag = False
            stdout_list = result
            for std in stdout_list:
                if 'ERROR' in std:
                    error_flag = True
                    write_host_initialize_log('ERROR', std, host_initialize)
                else:
                    write_host_initialize_log(level, std, host_initialize)
            if error_flag:
                host_initialize.initialize_status = 3
                # 发送邮件/QQ/微信消息
                to_list = [host_initialize.add_user.email]
                first_name = host_initialize.add_user.first_name
                subject = '主机初始化结果-{}'.format(host_initialize.telecom_ip)
                content = '主机初始化【步骤4】-【主机环境测试】失败，IP: {}，请登录cmdb查看详细日志！'.format(host_initialize.telecom_ip)
                if to_list:
                    send_mail.delay(to_list, subject, content)
                send_qq.delay(first_name, subject, subject, content, '')
                send_weixin_message.delay(touser=first_name, content=content)
            else:
                host_initialize.initialize_status = 2
                # 发送重启主机异步任务
                write_host_initialize_log('INFO', '【步骤5】-【开始】-【重启主机】', host_initialize)
                saltstack_host_reboot.delay(telecom_ip)
            host_initialize.save(update_fields=['initialize_status'])
            ws_update_host_initialize_list()
        else:
            level = 'ERROR'
            host_initialize.initialize_status = 3
            host_initialize.save(update_fields=['initialize_status'])
            ws_update_host_initialize_list()
            write_host_initialize_log(level, json.dumps(result, indent=4, ensure_ascii=False), host_initialize)

    except Exception as e:
        result = str(e)
        level = 'ERROR'
        write_host_initialize_log(level, result, host_initialize)
        # 发送邮件/QQ/微信消息
        to_list = [host_initialize.add_user.email]
        first_name = host_initialize.add_user.first_name
        subject = '主机初始化结果-{}'.format(host_initialize.telecom_ip)
        content = '主机初始化【步骤4】-【主机环境测试】失败，IP: {}，请登录cmdb查看详细日志！'.format(host_initialize.telecom_ip)
        if to_list:
            send_mail.delay(to_list, subject, content)
        send_qq.delay(first_name, subject, subject, content, '')
        send_weixin_message.delay(touser=first_name, content=content)


@app.task()
def saltstack_host_reboot(telecom_ip):
    """
    主机初始化步骤 5： 重启主机
    """
    level = "INFO"
    try:
        # 重新连接数据库
        close_old_connections()

        host_initialize = HostInitialize.objects.get(telecom_ip=telecom_ip)
        salt = salt_init()
        client = [telecom_ip]
        fun = 'cmd.run'
        arg = 'reboot'
        # 执行异步命令
        job_id = salt.salt_async_command(client, fun, arg=arg, tgt_type='list')
        print('主机初始化步骤5: saltstack异步任务id: {}'.format(job_id))
        host_initialize.reboot_status = 1
        host_initialize.save(update_fields=['reboot_status'])
        ws_update_host_initialize_list()
        # 每隔2秒获取一次结果，10s后认为任务超时
        time.sleep(1)
        start_time = int(time.time())
        while not salt.look_jid(job_id):
            time.sleep(2)
            now = int(time.time())
            if now - start_time > 120:
                raise Exception('发送重启主机请求失败')
        # 格式化任务输出结果
        result = salt.look_jid(job_id)
        if result:
            print('发送重启主机请求成功: ', json.dumps(result, indent=4, ensure_ascii=False))
            write_host_initialize_log(level, '发送重启主机请求成功，请耐心等待...', host_initialize)
            time.sleep(10)
            write_host_initialize_log(level, '开始执行test.ping测试', host_initialize)
            success, msg = saltstack_test_ping(telecom_ip)
            # 每隔2秒test.ping，180s后认为任务超时
            i = 1
            while not success:
                write_host_initialize_log(level, '第{}次 test.ping测试失败，2秒后再尝试...'.format(i), host_initialize)
                i += 1
                time.sleep(2)
                now = int(time.time())
                if now - start_time > 300:
                    raise Exception('主机重启超时，请检查原因')
                success, msg = saltstack_test_ping(telecom_ip)

            write_host_initialize_log(level, 'test.ping测试通过，主机重启成功', host_initialize)
            host_initialize.reboot_status = 2
            host_initialize.save(update_fields=['reboot_status'])
            ws_update_host_initialize_list()
            # 发送主机入库异步任务
            write_host_initialize_log('INFO', '【步骤6】-【开始】-【主机入库】', host_initialize)
            saltstack_host_import.delay(telecom_ip)
        else:
            print('发送重启主机请求失败')
            host_initialize.reboot_status = 3
            host_initialize.save(update_fields=['reboot_status'])
            ws_update_host_initialize_list()
            # 发送邮件/QQ/微信消息
            to_list = [host_initialize.add_user.email]
            first_name = host_initialize.add_user.first_name
            subject = '主机初始化结果-{}'.format(host_initialize.telecom_ip)
            content = '主机初始化【步骤5】-【重启主机】失败，IP: {}，请登录cmdb查看详细日志！'.format(host_initialize.telecom_ip)
            if to_list:
                send_mail.delay(to_list, subject, content)
            send_qq.delay(first_name, subject, subject, content, '')
            send_weixin_message.delay(touser=first_name, content=content)

    except Exception as e:
        result = str(e)
        print(result)
        level = 'ERROR'
        host_initialize.reboot_status = 3
        host_initialize.save(update_fields=['reboot_status'])
        ws_update_host_initialize_list()
        write_host_initialize_log(level, result, host_initialize)
        # 发送邮件/QQ/微信消息
        to_list = [host_initialize.add_user.email]
        first_name = host_initialize.add_user.first_name
        subject = '主机初始化结果-{}'.format(host_initialize.telecom_ip)
        content = '主机初始化【步骤5】-【重启主机】失败，IP: {}，请登录cmdb查看详细日志！'.format(host_initialize.telecom_ip)
        if to_list:
            send_mail.delay(to_list, subject, content)
        send_qq.delay(first_name, subject, subject, content, '')
        send_weixin_message.delay(touser=first_name, content=content)


@app.task()
def saltstack_host_import(telecom_ip):
    """主机初始化步骤 6： 机器入库"""
    level = "INFO"
    try:
        # 重新连接数据库
        close_old_connections()

        host_init = HostInitialize.objects.get(telecom_ip=telecom_ip)
        ops_obj = OpsManager.objects.filter(project=host_init.project, room=host_init.room)
        if not ops_obj:
            host_init.import_status = 0
            host_init.save(update_fields=['import_status'])
            ws_update_host_initialize_list()
            write_host_initialize_log(level, '还没有关联的运维管理机，请手动入库', host_init)
            return
        ops_obj = ops_obj[0]
        url = ops_obj.get_url() + 'interface/add_host/'
        data = {
            'data': [{
                'game_type': host_init.business.business_name,
                'ip': host_init.telecom_ip,
                'mask': host_init.room.room_name_en
            }]
        }
        ops_api_obj = OpsManagerAPI(url=url, token=ops_obj.token, json=json.dumps(data))
        success, msg = ops_api_obj.post()
        if success:
            host_init.import_status = 2
            host_init.save(update_fields=['import_status'])
            ws_update_host_initialize_list()
            write_host_initialize_log(level, '{} 入库成功'.format(host_init.telecom_ip), host_init)
        else:
            raise Exception(msg)

    except HostInitialize.DoesNotExist:
        msg = '主机初始化记录不存在'
        print(msg)
    except Exception as e:
        level = "ERROR"
        msg = str(e)
        host_init.import_status = 3
        host_init.save(update_fields=['import_status'])
        ws_update_host_initialize_list()
        write_host_initialize_log(level, '{} 入库失败: {}'.format(host_init.telecom_ip, msg), host_init)
        # 发送邮件/QQ/微信消息
        to_list = [host_init.add_user.email]
        first_name = host_init.add_user.first_name
        subject = '主机初始化结果-{}'.format(host_init.telecom_ip)
        content = '主机初始化【步骤6】-【主机入库】失败，IP: {}，请登录cmdb查看详细日志！'.format(host_init.telecom_ip)
        if to_list:
            send_mail.delay(to_list, subject, content)
        send_qq.delay(first_name, subject, subject, content, '')
        send_weixin_message.delay(touser=first_name, content=content)


@app.task()
def cmdb_tasks_timeout_check():
    """
    检查超时任务
    每隔10分钟找出所有正在执行的任务
    如果当前时间比任务开始时间大于60分钟，则通知相关人员任务超时
    目前检测的任务有：
    1. 区服下架计划
    2. 主机迁服
    3. 主机回收
    4. 区服管理操作（开服/关服/重启/清档/迁服）
    """
    try:
        # 重新连接数据库
        close_old_connections()

        cmdb_timeout_tasks = []
        _DEFAULT_INTERVAL = 60
        _TIMEOUT_POINT = datetime.now() + timedelta(minutes=-_DEFAULT_INTERVAL)

        # 区服下架任务超时检查
        off_schedules = GameServerOff.objects.filter(status=2, off_time__lt=_TIMEOUT_POINT)
        cmdb_timeout_tasks.extend([task for task in off_schedules])
        # 主机迁服任务超时检查
        host_migrate = HostCompressionApply.objects.filter(action_status=2, action_time__lt=_TIMEOUT_POINT)
        cmdb_timeout_tasks.extend([task for task in host_migrate])
        # 主机回收任务超时检查
        host_recover = HostCompressionApply.objects.filter(recover_status=2, recover_time__lt=_TIMEOUT_POINT)
        cmdb_timeout_tasks.extend([task for task in host_recover])
        # 区服管理操作任务超时检查
        srv_action_record = GameServerActionRecord.objects.filter(result=2, operation_time__lt=_TIMEOUT_POINT)
        cmdb_timeout_tasks.extend([task for task in srv_action_record])

        for task in cmdb_timeout_tasks:
            if isinstance(task, GameServerOff):
                print('区服下架任务超时: {}'.format(task.uuid))
                subject = '区服下架任务超时'
                content = '区服下架任务执行时间超过1个小时，uuid: {}，请登录cmdb查看详情'.format(task.uuid)
            elif isinstance(task, HostCompressionApply) and task.action_status == 2:
                print('主机迁服任务超时: {}'.format(task.uuid))
                subject = '主机迁服任务超时'
                content = '主机迁服任务执行时间超过1个小时，uuid: {}，请登录cmdb查看详情'.format(task.uuid)
            elif isinstance(task, HostCompressionApply) and task.recover_status == 2:
                print('主机回收任务超时: {}'.format(task.uuid))
                subject = '主机回收任务超时'
                content = '主机回收任务执行时间超过1个小时，uuid: {}，请登录cmdb查看详情'.format(task.uuid)
            elif isinstance(task, GameServerActionRecord):
                action_type = task.get_operation_type_chinese_word()
                print('区服{}操作超时: {}'.format(action_type, task.uuid))
                subject = '区服管理操作超时'
                content = '区服管理操作执行时间超过1个小时，uuid: {}，请登录cmdb查看详情'.format(task.uuid)
            else:
                raise Exception('未知的任务类型')

            # 邮件通知
            to_list = [u.first_name for u in task.get_relate_role_user()]
            send_mail.delay(to_list, subject, content)
            # 都要发送qq弹框提醒
            users = ','.join([u.first_name for u in task.get_relate_role_user()])
            send_qq.delay(users, subject, subject, content, '')
            # 发送wx弹框提醒
            wx_users = '|'.join([u.first_name for u in task.get_relate_role_user()])
            send_weixin_message.delay(touser=wx_users, content=content)

    except Exception as e:
        print('检测cmdb超时任务失败: {}'.format(str(e)))


class OpsManagerAPI(object):
    """
    发送运维管理机API接口
    """

    def __init__(self, url, token, data=None, json=None):
        self.headers = {
            'Accept': 'application/json',
            'Authorization': 'Token {}'.format(token)
        }
        self.url = url
        self.data = data
        self.json = json

    def post(self):
        s = Session()
        s.mount('https://', HTTPAdapter(max_retries=Retry(total=5, status_forcelist=[408])))
        if self.json:
            r = s.post(self.url, headers=self.headers, json=self.json, timeout=30, verify=False)
        else:
            r = s.post(self.url, headers=self.headers, data=self.data, timeout=30, verify=False)
        if r.status_code == 200:
            result = r.json()
            if result['Accepted']:
                return True, 'ok'
        else:
            return False, str(r)


@app.task()
def do_game_server_merge(data, uuid, type=1):
    """
    发送合服计划到运维管理机的异步任务
    data参数:
    '[
        {"main_srv": "1", "slave_srv": "3,4,5", "group_id": 1, "merge_time": "1234567890", "project": "ssss"},
        {"main_srv": "2", "slave_srv": "6,7,8", "group_id": 2, "merge_time": "1234567123", "project": "ssss"},
        ...
    ]'
    type: 1-合服  2-回滚合服
    """
    success = True
    msg = 'ok'
    try:
        # 重新连接数据库
        close_old_connections()

        data = json.loads(data)
        opsmanager_dict = dict()
        # 将data数据根据发往不同的运维管理机进行划分
        for d in data:
            main_srv = GameServer.objects.filter(sid=d['main_srv'], project__project_name_en=d['project'])
            obj = GameServerMergeSchedule.objects.get(uuid=uuid, main_srv=d['main_srv'])
            # 更新该合服记录为发送失败，原因是sid匹配不到区服
            if not main_srv:
                obj.status = 2
                obj.remark = '匹配区服失败，sid: {}'.format(d['main_srv'])
                obj.save()
                continue
            ops_manager = main_srv[0].get_ops_manager()
            # 更新该合服记录为发送失败，原因是区服找不到对应的运维管理机
            if not ops_manager:
                obj.status = 2
                obj.remark = '区服找不到运维管理机，{}'.format(d['main_srv'])
                obj.save()
                continue
            if ops_manager in opsmanager_dict:
                opsmanager_dict[ops_manager].append(d)
            else:
                opsmanager_dict[ops_manager] = [d]

        # 发送到对应的运维管理机
        for ops, data in opsmanager_dict.items():
            if type == 1:
                url = ops.get_url() + 'merge/mergeserver/'
            else:
                url = ops.get_url() + 'merge/archiveserver/'
            data = {'data': data}
            print(data)
            ops_api_obj = OpsManagerAPI(url=url, token=ops.token, json=data)
            success, msg = ops_api_obj.post()
            main_srv_list = [x['main_srv'] for x in data['data']]
            obj = GameServerMergeSchedule.objects.filter(uuid=uuid, main_srv__in=main_srv_list)
            if success:
                if type == 1:
                    obj.update(**{'status': 1})
                else:
                    obj.update(**{'status': 3})
            else:
                if type == 1:
                    obj.update(**{'status': 2, 'remark': msg})
                else:
                    obj.update(**{'status': 4, 'remark': msg})

    except Exception as e:
        success = False
        msg = str(e)
    finally:
        return {'success': success, 'msg': msg}


@app.task()
def do_query_txserver_status(instance_set, secret_id, secret_key, cloud_account, region_code):
    """购买腾讯云服务器后，循环查询机器状态异步任务"""
    success = True
    msg = 'ok'
    log = PurchaseCloudServerLog()
    try:
        # 重新连接数据库
        close_old_connections()

        # 查询实例状态，直到状态为运行中
        action = "DescribeInstances"
        params = {"Filters": [{"Name": "instance-id", "Values": instance_set}]}
        obj = TXCloudTC3(secret_id, secret_key, region=region_code,
                         action=action, params=params)
        # 循环查询五分钟，直到签名过期，如果期间查询到实例状态为运行中，则更新主机外网IP，否则跳出循环
        n = 0
        while True:
            time.sleep(5)
            success, msg = obj.python_request()
            n += 1
            if not success:
                if n > 10:
                    raise TxCloudError(msg)
                continue
            for i in msg:
                host_init_obj = HostInitialize.objects.filter(instance_id=i['instance_id'])
                host_init_obj.update(**{'instance_state': i['instance_state']})
                ws_update_host_initialize_list()
                if i['instance_state'] == 'PENDING':
                    print('服务器创建中，实例ID：{}'.format(i['instance_id']))
                if i['instance_state'] == 'LAUNCH_FAILED':
                    raise Exception('腾讯云服务器创建失败，请登录腾讯云后台查询详情，实例ID：{}'.format(i['instance_id']))
                if i['instance_state'] == 'RUNNING':
                    host_init_obj.update(**{'telecom_ip': i['public_ip']})
                    ws_update_host_initialize_list()
                    instance_set.remove(i['instance_id'])
                    # 发送购买成功邮件通知服务器管理员
                    to_list = host_init_obj[0].project.get_relate_role_user_email_list()
                    subject = 'cmdb购买腾讯云服务器成功'
                    content = make_purchase_tx_server_email(i['public_ip'], host_init_obj[0], cloud_account)
                    send_mail.delay(to_list, subject, content)
                    # 开始安装salt-minion客户端
                    if PRODUCTION_ENV:
                        host_init_obj.update(**{'install_status': 1})
                        ws_update_host_initialize_list()
                        log_message = '{} - 开始执行主机初始化任务'.format('cmdb')
                        for h in host_init_obj:
                            write_host_initialize_log('INFO', log_message, h)
                            write_host_initialize_log('INFO', '【步骤1】-【开始】-【安装salt-minion】', h)
                            """发送安装salt-minion异步任务"""
                            install_salt_minion.delay([h.telecom_ip])

                log.logger.info('查询腾讯云服务器状态成功，当前状态: {}'.format(i['instance_state']))
            if not instance_set:
                break
    except TxCloudError as e:
        success = False
        msg = '调用腾讯云接口失败: {}'.format(str(e))
        log.logger.error(msg)
    except Exception as e:
        success = False
        msg = str(e)
        log.logger.error('查询腾讯云服务器状态失败: {}'.format(msg))
    finally:
        return {'success': success, 'msg': msg}


@app.task()
def version_update_task(version_update_id, version_update_type):
    """版本更新单异步任务"""
    success = True
    msg = 'ok'
    log = VersionUpdateLog()
    # 重新连接数据库(上级调用方法使用了事务，所以不能清理数据库连接)
    # close_old_connections()

    try:
        version_update = VersionUpdate.objects.get(pk=version_update_id)
        if not version_update.uuid:
            v_uuid = str(uuid.uuid1())
            version_update.uuid = v_uuid
            version_update.save(update_fields=['uuid'])
        else:
            v_uuid = version_update.uuid
        # 检查后端版本号目录
        if PRODUCTION_ENV:
            if version_update_type == 'server' or version_update_type == 'all':
                success, msg = version_update_check_push_dir_util('server', version_update.server_version,
                                                                  version_update.project, version_update.area)
                if not success:
                    touser = '|'.join([user.first_name for user in version_update.project.get_relate_role_user()])
                    send_weixin_message(touser=touser, content='版本更新单： {}，{}'.format(version_update.title, msg))
                    raise Exception(v_uuid + '-' + msg)
            # 检查前端版本号目录
            if (version_update_type == 'client' or version_update_type == 'all') and version_update.client_content:
                for update_client_item in json.loads(version_update.client_content):
                    success, msg = version_update_check_push_dir_util('client', update_client_item['version'],
                                                                      version_update.project, version_update.area)
                    if not success:
                        touser = '|'.join([user.first_name for user in version_update.project.get_relate_role_user()])
                        send_weixin_message(touser=touser, content='版本更新单： {}，{}'.format(version_update.title, msg))
                        raise Exception(v_uuid + '-' + msg)

        area = version_update.area
        project = version_update.project
        ops = OpsManager.objects.filter(room__area=area, project=project)
        if not ops:
            raise Exception(v_uuid + '-' + '找不到运维管理机')
        ops = ops[0]
        url = ops.get_url() + 'update/version_update/'
        srv_list = version_update.get_srv_id_list()
        erl_command = [x for x in map(lambda x: x.strip(), version_update.server_erlang.split('\n'))
                       if x is not None and x != '']
        post_data = {
            'uuid': v_uuid,
            'update_type': version_update_type,
            'data': {
                "server": {
                    "srv_list": srv_list,
                    "update_version": version_update.server_version,
                    "update_time": str(version_update.start_time)[:19],
                    "ask_reset": version_update.get_ask_reset_display(),
                    "erl_command": erl_command,
                },
                "client": json.loads(version_update.client_content),
            }
        }
        log.logger.info(v_uuid + '-' + json.dumps(post_data))
        ops_api_obj = OpsManagerAPI(url=url, token=ops.token, json=json.dumps(post_data))
        if PRODUCTION_ENV:
            success, msg = ops_api_obj.post()
            if success:
                version_update.status = 0
            else:
                version_update.status = 1
        else:
            version_update.status = 0
            version_update.save(update_fields=['status'])

    except VersionUpdate.DoesNotExist:
        success = False
        msg = '版本更新单不存在'
        log.logger.error(msg)
    except Exception as e:
        success = False
        msg = str(e)
        log.logger.error(msg)
        version_update.status = 1
        version_update.save(update_fields=['status'])
    finally:
        return {'success': success, 'msg': msg}


@app.task()
def query_mysql_info(region, secret_id, secret_key, cloud_account, InstanceIds=None, notice=True):
    """查询数据库实例信息"""
    success = True
    msg = 'ok'
    try:
        # 重新连接数据库
        close_old_connections()

        action = 'DescribeDBInstances'
        version = '2017-03-20'
        host = 'cdb.tencentcloudapi.com'
        service = 'cdb'
        if InstanceIds:
            obj = TXCloudTC3(secret_id, secret_key, version=version, region=region,
                             action=action, params={'InstanceIds': InstanceIds}, host=host, service=service)
        else:
            obj = TXCloudTC3(secret_id, secret_key, version=version, region=region,
                             action=action, host=host, service=service)
        # 循环查询实例状态，在五分钟内（签名未过期）
        while True:
            time.sleep(1)
            success, data = obj.python_request()
            # 如果调用API不成功，退出循环
            if not success:
                break

            # 开始遍历结果
            for instance in data:
                if instance['Status'] == 1 and instance['TaskStatus'] == 0 and instance['InitFlag'] == 1:
                    print('实例ID：' + instance['InstanceId'] + '状态运行中，任务状态为空闲，已初始化')
                    mysql_obj = MysqlInstance.objects.filter(instance_id=instance['InstanceId'])
                    if mysql_obj:
                        mysql_obj = mysql_obj[0]
                    else:
                        continue
                    if instance['WanStatus'] == 1:
                        mysql_obj.host = instance.get('WanDomain', '')
                        mysql_obj.port = instance.get('WanPort', '')
                        mysql_obj.open_wan = 1
                    else:
                        mysql_obj.host = instance.get('Vip', '')
                        mysql_obj.port = instance.get('Vport', '')

                    mysql_obj.status = 1
                    mysql_obj.save()

                    # websocket 刷新列表
                    ws_update_mysql_list()

                    if notice:
                        # 发送邮件通知
                        to_list = mysql_obj.project.get_relate_role_user_email_list()
                        subject = 'cmdb购买腾讯云数据库成功'
                        email_content = make_purchase_tx_mysql_email(mysql_obj, cloud_account)
                        send_mail(to_list, subject, email_content)

            # 如果全部实例状态是运行中，则退出循环
            if len(data) == len([instance for instance in data if
                                 instance['Status'] == 1 and instance['TaskStatus'] == 0 and instance[
                                     'InitFlag'] == 1]):
                break

    except Exception as e:
        success = False
        msg = str(e)
    finally:
        return success, msg


@app.task()
def query_txcloud_async_result(region, secret_id, secret_key, cloud_account, instance_id, async_request_id):
    """
    查询k开通腾讯云mysql外网访问结果
    1. 根据任务id查询异步任务结果
    2. 查询实例外网访问域名与端口，并更新cmdb
    """
    success = True
    data = 'ok'
    try:
        # 重新连接数据库
        close_old_connections()

        action = 'DescribeAsyncRequestInfo'
        version = '2017-03-20'
        host = 'cdb.tencentcloudapi.com'
        service = 'cdb'
        params = {
            'AsyncRequestId': async_request_id,
        }
        obj = TXCloudTC3(secret_id, secret_key, version=version, region=region,
                         action=action, params=params, host=host, service=service)
        while True:
            success, data = obj.python_request()
            if not success:
                raise Exception('查询异步任务失败: {}'.format(data))
            result = data['status']
            if result == 'SUCCESS':
                print('实例ID： {}，开通外网访问成功'.format(instance_id))
                # 查询数据库实例信息并更新外网访问域名和端口
                query_mysql_info(region, secret_id, secret_key, cloud_account, InstanceIds=[instance_id], notice=False)
                # 刷新列表
                ws_update_mysql_list()
                # 退出循环
                break

            time.sleep(1)

    except Exception as e:
        success = False
        data = str(e)
    finally:
        return success, data


@app.task()
def compare_txcloud_server_config():
    """
    调用腾讯云接口查询服务器配置，与cmdb记录的进行对比，如果不一致则更新cmdb，并发送微信消息
    """
    for tx_account in TecentCloudAccount.objects.all():
        secret_id = tx_account.secret_id
        secret_key = tx_account.secret_key
        region = "ap-guangzhou"
        action = "DescribeInstances"

        obj = TXCloudTC3(secret_id, secret_key, region, action)
        success, result = obj.python_request()

        if not success:
            continue

        for instance in result:
            public_ip = instance['public_ip']
            private_ip = instance['private_ip']
            cpu = instance['cpu']
            memory = instance['memory']
            host = Host.objects.select_related('belongs_to_game_project').filter(
                Q(telecom_ip=public_ip) | Q(internal_ip=private_ip))

            if not host:
                continue

            host = host[0]
            if str(host.cpu_num) != str(cpu) or abs(
                    float(re.sub(r'([a-zA-Z]+)', '', str(host.ram))) - float(memory)) > 1:
                # 发送核实提示
                # touser = '|'.join([u.first_name for u in host.belongs_to_game_project.get_relate_role_user()])
                # content = 'cmdb主机配置与腾讯云(帐号: {})不符合，请核实！\n主机{}\ncpu核数: {}(cmdb); {}(腾讯云)\n内存: {}(cmdb); {}(腾讯云)'.format(
                #     tx_account.remark, host.get_host_ip(), host.cpu_num, cpu, host.ram, memory)
                # send_weixin_message(touser=touser, content=content)

                # 记录修改前的值
                old_host = host.show_all()
                old_host.pop('area')

                # 更新cmdb数据
                host.cpu_num = cpu
                host.ram = memory
                host.save(update_fields=['cpu_num', 'ram'])

                # 记录所有字段之后值
                new_host = host.show_all()
                new_host.pop('area')

                # 找出差异字段，并记录操作日志
                alert_fields_list = []
                for k, v in new_host.items():
                    if v != old_host[k]:
                        alert_fields_list.append(k)
                for x in alert_fields_list:
                    alter_field = Host._meta.get_field(x).help_text
                    HostHistoryRecord.objects.create(host=host, type=2,
                                                     alter_field=alter_field,
                                                     old_content=old_host[x], new_content=new_host[x],
                                                     source_ip='127.0.0.1')


@app.task()
def send_weixin_rebot(url, content):
    success = True
    msg = '发送微信机器人成功'
    try:
        headers = {
            'Accept': 'application/json',
            'Connection': 'keep-alive',
        }
        data = {
            "msgtype": "markdown",
            "markdown": {"content": content}
        }
        s = Session()
        s.mount('https://', HTTPAdapter(max_retries=Retry(total=3, status_forcelist=[408])))
        r = s.post(url, headers=headers, json=data, verify=False, timeout=10)
        if r.status_code == 200:
            result = r.json()
            if result.get('errcode', '') != 0:
                raise Exception(result.get('errmsg', ''))
        else:
            raise Exception(str(r))
    except Exception as e:
        success = False
        msg = str(e)
    finally:
        return success, msg


@app.task()
def get_salt_minion():
    """获取所有salt节点"""
    url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=70753472-e00c-42b5-9ffe-0634d8728dc3'
    salt = salt_init()
    client = '*'
    fun = 'test.ping'
    minion_status_dict = salt.salt_command(client, fun, tgt_type='glob')
    minion_list = list(set(minion_status_dict.keys()))
    minion_list = [m.split('_')[-1] for m in minion_list]
    no_warehousing_host_list = []
    offline_host_list = []

    for minion in minion_list:
        host = Host.objects.filter(Q(telecom_ip=minion) | Q(internal_ip=minion) | Q(unicom_ip=minion))
        if not host:
            no_warehousing_host_list.append(minion)

    if no_warehousing_host_list:
        # 每次发送最多200个IP，防止content超过最大长度4096字节被截断
        max_count = 200
        for i in range(0, len(no_warehousing_host_list), max_count):
            sub_list = no_warehousing_host_list[i:i + max_count]
            content = '# SaltStack检查 \n以下<font color=\"warning\">salt minion</font>未入库cmdb，请相关同事注意！\n' + \
                '>minion IP：<font color=\"comment\">{}</font>'.format(', '.join(sub_list))
            send_weixin_rebot(url, content)

    for minion, status in minion_status_dict.items():
        if not status:
            offline_host_list.append(minion)

    if offline_host_list:
        # 每次发送最多200个IP，防止content超过最大长度4096字节被截断
        max_count = 200
        for i in range(0, len(offline_host_list), max_count):
            sub_list = offline_host_list[i:i + max_count]
            content = '# SaltStack检查 \n<font color=\"warning\">salt master test ping</font>以下<font color=\"warning\">salt minion</font>失败，请相关同事注意！\n' + \
                '>minion IP：<font color=\"comment\">{}</font>'.format(', '.join(sub_list))
            send_weixin_rebot(url, content)
