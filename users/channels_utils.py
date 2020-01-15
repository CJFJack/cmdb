# -*- encoding: utf-8 -*-

"""Using django channles!
"""

from channels import Channel

from users.models import *


def ws_notify_clean_user(user_id):
    """根据用户id通知相应的客户端来
    刷新清除数据的结果展示
    """

    user = User.objects.get(id=user_id)
    ucs = UserClearStatus.objects.get(profile=user.profile)
    process_info = ucs.show_process_info()

    msg = {"message": "update_msg", "user_id": user_id, "process_info": process_info}
    Channel("update_clean_user").send(msg)
