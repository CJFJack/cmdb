import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cmdb.settings")
import django
django.setup()
from ops.models import GameServerOff
from ops.utils import write_game_server_off_log
from ops.utils import ws_update_game_server_off_list
from tasks import do_game_server_off
from datetime import datetime


def check_game_server_task():
    """找出下架状态为未执行，且执行时间小于当前时间的区服下架申请单，发送区服下架任务"""
    now = datetime.now()
    apply_list = GameServerOff.objects.filter(status=1).order_by('off_time')
    for apply in apply_list:
        if apply.get_related_project_name_en() in ('ssss', 'snqxz'):
            apply.status = 5
            apply.save()
        else:
            if apply.off_time < now:
                apply.status = 2
                apply.save(update_fields=['status'])
                ws_update_game_server_off_list()
                do_game_server_off.delay(apply.uuid)
                write_game_server_off_log('INFO', 'cmdb定时计划执行项目下架任务', apply)


if __name__ == '__main__':
    check_game_server_task()
