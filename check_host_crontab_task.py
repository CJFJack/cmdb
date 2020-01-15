import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cmdb.settings")
import django
django.setup()
from myworkflows.models import HostCompressionApply
from myworkflows.utils import write_host_compression_log
from myworkflows.utils import ws_update_host_compression_list
from tasks import do_host_migrate
from tasks import do_host_recover
from datetime import datetime


def check_host_migrate_task():
    """找出迁服状态为未迁服，且迁服时间小于当前时间的主机迁服回收申请单，发送异步迁服任务"""
    now = datetime.now()
    apply_list = HostCompressionApply.objects.filter(action_status=1, type=2).order_by('action_time')
    for apply in apply_list:
        if apply.action_time < now < apply.action_deadline:
            apply.action_status = 2
            apply.save(update_fields=['action_status'])
            ws_update_host_compression_list()
            do_host_migrate.delay(apply.uuid)
            write_host_compression_log('INFO', 'cmdb定时计划执行迁服任务', apply)


def check_host_recover_task():
    """找出回收状态为未迁服，且回收时间小于当前时间的主机迁服回收申请单，发送异步回收任务"""
    now = datetime.now()
    apply_list = HostCompressionApply.objects.filter(recover_status=1).order_by('recover_time')
    for apply in apply_list:
        if apply.recover_time < now < apply.recover_deadline:
            apply.recover_status = 2
            apply.save(update_fields=['recover_status'])
            ws_update_host_compression_list()
            do_host_recover.delay(apply.uuid)
            write_host_compression_log('INFO', 'cmdb定时计划执行回收任务', apply)


if __name__ == '__main__':
    check_host_migrate_task()
    check_host_recover_task()
