# -*- encoding: utf-8 -*-

"""用户角色模块
"""

from django.contrib.auth.models import Group


def is_group_leader(user):
    """判断用户是否为部门负责人
    """

    for g in Group.objects.all():
        if g.groupprofile.group_leader.id == user.id:
            return True
    else:
        return False
