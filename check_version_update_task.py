import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cmdb.settings")
import django
import datetime

django.setup()
from cmdb.settings import NEW_VERSION_UPDATE
from myworkflows.models import VersionUpdate
from tasks import version_update_task
from cmdb.logs import VersionUpdateLog


def check_version_update_task():
    """
    找出符合以下条件的版本更新单，并发送版本更新请求：
    1.NEW_VERSION_UPDATE=True
    2.本本更新单new_edition字段为True
    3.版本更新单所属项目设置为自动版本更新
    4.web已挂维护
    5.当前时间在更新指定时间范围内
    6.对应工单已审批完成
    7.版本更新单状态为未处理
    """
    log = VersionUpdateLog()
    try:
        if not NEW_VERSION_UPDATE:
            return
        now = datetime.datetime.now()
        version_update = VersionUpdate.objects.select_related('project').filter(new_edition=True,
                                                                                project__auto_version_update=True,
                                                                                is_maintenance=True,
                                                                                start_time__lte=now, end_time__gte=now,
                                                                                status=2)
        for v in version_update:
            if v.workflows.last().state.name == '完成':
                log.logger.info('计划任务开始执行版本更新：#{}'.format(v.title))
                version_update_task(v.id, 'all')

    except Exception as e:
        print(str(e))


if __name__ == '__main__':
    check_version_update_task()
