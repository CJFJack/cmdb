"""调用qq提醒
"""

from tasks import send_qq


def hot_update_qq_notify(all_users, content_obj, finish_ok):
    """热更新完成后调用这个函数
    告知工单发起人，节点审批人和额外
    通知的人本次更新结果
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
