import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cmdb.settings")
import django
django.setup()
from myworkflows.utils import get_celery_worker_status
from myworkflows.models import CeleryWorkerStatus, CeleryReceiveNoticeUser
from tasks import send_mail, send_weixin_message, send_qq
from cmdb.logs import SyncCeleryWorkerLog

log = SyncCeleryWorkerLog()


def sync_running_worker():
    """同步正在运行的worker"""
    success = True
    msg = '同步成功'
    try:
        result = get_celery_worker_status()
        users = [x.receive_user for x in CeleryReceiveNoticeUser.objects.all()]
        wx_touser = '|'.join([x.first_name for x in users])
        qq_user = ','.join([x.first_name for x in users])
        to_list = [x.email for x in users]
        if 'ERROR_KEY' in result.keys():
            success = False
            msg = '同步失败' + result['ERROR_KEY']
            log.logger.info(msg)
        else:
            celery_dict = {}

            for k, v in result.items():
                total = result[k]['total']
                if total:
                    celery_dict[k] = {'total': list(result[k]['total'].values())[0]}
                else:
                    celery_dict[k] = {'total': 0}
            running_worker_list = [x for x in result.keys()]
            db_workers_list = [x.celery_hostname for x in CeleryWorkerStatus.objects.all()]
            # 遍历本地数据库的在线worker列表，跟确定在线的worker列表对比
            for worker in db_workers_list:
                if worker not in running_worker_list:
                    obj = CeleryWorkerStatus.objects.get(celery_hostname=worker)
                    obj.status = 0
                    obj.off_count += 1
                    obj.save()
                    # 发送worker离线消息，判断告警次数是否为6的倍数或等于3，是则发送告警
                    if obj.off_count % 6 == 0 or obj.off_count == 3:
                        content = worker + '离线'
                        log.logger.info(content)
                        send_mail(to_list, content, content)
                        send_weixin_message(touser=wx_touser, content=content)
                        send_qq(qq_user, 'worker离线', 'worker离线', content, '')
                else:
                    obj = CeleryWorkerStatus.objects.get(celery_hostname=worker)
                    obj.total = celery_dict[worker]['total']
                    if obj.status == 0:
                        # 发送worker上线消息
                        if obj.off_count >= 3:
                            content = worker + '恢复'
                            log.logger.info(content)
                            send_mail(to_list, content, content)
                            send_weixin_message(touser=wx_touser, content=content)
                            send_qq(qq_user, 'worker恢复', 'worker恢复', content, '')

                        obj.status = 1
                        obj.off_count = 0

                    obj.save()
            # 遍历确定在线的worker列表，跟对比数据库在线worker列表对比
            for worker in running_worker_list:
                if worker not in db_workers_list:
                    CeleryWorkerStatus.objects.create(celery_hostname=worker, total=celery_dict[worker]['total'])
                    log.logger.info('增加监控' + worker)

    except Exception as e:
        success = False
        log.logger.info(str(e))
        msg = str(e)

    finally:
        return {'success': success, 'msg': msg}


if __name__ == '__main__':
    sync_running_worker()
