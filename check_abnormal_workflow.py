import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cmdb.settings")
import django
django.setup()
from myworkflows.models import WorkflowStateEvent
from django.db.models import Count
from tasks import send_weixin_message


def check_abnormal_workflow():
    """找出异常状态的工单流程，并发送微信信息"""
    objs = WorkflowStateEvent.objects.values('object_id', 'creator_id', 'title').filter(is_current=True).annotate(
        is_current=Count('is_current')).filter(is_current__gt=1)
    for o in objs:
        o['is_current'] = True
        wse = WorkflowStateEvent.objects.filter(**o).order_by('id')
        wse = sorted(wse, key=lambda x: x.id)[:-1]
        for w in wse:
            if w.is_current and w.state.name != '完成':
                send_weixin_message(touser='chenjiefeng',
                                    content='工单流程审批异常 wse id: {}, title: {}'.format(w.id, w.title))
                # w.is_current = False
                # w.save()

    return objs


if __name__ == '__main__':
    check_abnormal_workflow()
