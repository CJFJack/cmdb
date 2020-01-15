"""调用邮件提醒
"""

from tasks import send_mail
from myworkflows.models import ServerHotUpdate


def hot_update_mail_notify(to_list, content_obj, finish_ok):
    """热更新完成后调用这个函数
    告知工单发起人，节点审批人和额外
    通知的人本次更新结果
    """

    if isinstance(content_obj, ServerHotUpdate):
        update_type = '后端热更新#'
    else:
        update_type = '前端热更新#'

    if finish_ok:
        subject = update_type + content_obj.title + '#热更新成功'
        content = '热更新: ' + content_obj.title + ' 更新成功.'
    else:
        subject = update_type + content_obj.title + '#热更新失败'
        content = '热更新: ' + content_obj.title + ' 更新失败, 请联系运维负责人处理'

    send_mail.delay(to_list, subject, content)


def rsync_failed_mail_notify(content_obj):
    """rsync推送失败后发送邮件
    """
    project = content_obj.project
    title = content_obj.title
    area_name = content_obj.area_name
    to_list = [x.email for x in project.related_user.all()]
    subject = '热更新{}rsync推送失败'.format(content_obj.area_name)
    content = '热更新: {} 项目:{} 地区:{} rsync推送失败'.format(title, project.project_name, area_name)
    send_mail.delay(to_list, subject, content)
