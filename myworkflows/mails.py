# -*- encoding: utf-8 -*-

""" 发送邮件给相应的流程负责人
    如果可以的话，可以集成到cmdb的流程中
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import imapy
from imapy.query_builder import Q

import re

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cmdb.settings")

import django
django.setup()

from myworkflows.models import WorkflowStateEvent
from myworkflows.utils import do_transition, get_state_user, make_email_notify


from django.contrib.auth.models import User

from cmdb.logs import MailLog

ml = MailLog()

from django.db import connections


def close_old_connections():
    for conn in connections.all():
        conn.close_if_unusable_or_obsolete()


class SendEmail(object):

    def __init__(self, to_list, subject, content):
        self._host = 'smtp.exmail.qq.com'
        self._port = 465
        self._user = 'devopsteam@forcegames.cn'
        self._passwd = 'Khgey@520199'
        self.to_list = to_list
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

        box = imapy.connect(
            host=self._host,
            port=self._port,
            username=self._username,
            password=self._password,
            ssl=True,
        )

        q = Q()

        emails = box.folder('INBOX').emails(
            q.unseen()
        )[0:count]

        emails = list(reversed(emails))

        p = re.compile(r'.*#工单流程')

        for mail in emails:
            try:
                # 重新连接数据库
                close_old_connections()

                subject = mail['subject']
                from_email = mail['from_email']
                user = User.objects.get(email=from_email)
                username = user.username
                # 如果匹配到的是工单流程的主题的邮件，则需要处理
                # 如果不是，这里就标记为已读
                if p.match(subject):
                    user = User.objects.get(username=username)
                    wse = subject.split("#")[3].split('=')[1]    # 'Re:#工单流程#剑雨后端SVN申请#wse=92' ==> 92
                    wse = WorkflowStateEvent.objects.get(id=int(wse))
                    reply = mail['text'][0]['text']
                    if reply.startswith('yes'):
                        transition = wse.state.transition.get(condition='同意')
                        ml.logger.info('%s: %s: 同意处理' % (subject, username))

                        msg, success, new_wse = do_transition(wse, transition, user)

                        to_list = [
                            x.email for x in get_state_user(transition.destination, obj=new_wse.content_object) if x.email
                        ]

                        if to_list:
                            subject, content = make_email_notify(True)
                            send_mail.delay(to_list, subject, content)
                        ml.logger.info('%s: %s: 处理结果:%s %s' % (subject, username, msg, success))
                    elif reply.startswith('no'):
                        transition = wse.state.transition.get(condition='拒绝')
                        ml.logger.info('%s: %s: 拒绝处理' % (subject, username))
                        msg, success, new_wse = do_transition(wse, transition, user)

                        to_list = [new_wse.creator.email]
                        subject, content = make_email_notify(False)
                        send_mail.delay(to_list, subject, content)

                        ml.logger.info('%s: %s: 处理结果:%s %s' % (subject, username, msg, success))
                    else:
                        ml.logger.warn('%s: %s: 没有匹配到指令' % (subject, username))
                else:
                    ml.logger.warn('%s: %s: 没有匹配到主题' % (subject, username))
            except Exception as e:
                ml.logger.error('%s: %s: %s' % (from_email, subject, str(e)))
            finally:
                # 主题邮件全部标记为已读
                mail.mark('Seen')
        box.logout()




