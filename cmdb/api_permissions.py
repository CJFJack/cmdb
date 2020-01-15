"""API的自定义权限class
by yanwenchi
2018.4.4 V1
"""

from django.contrib.auth.models import User

from rest_framework.permissions import BasePermission


class ApiPermission(BasePermission):
    """ApiPermission, 检查一个token关联的用户
    是否具有某些权限

    APIView需要有_api_perms的属性:
    type: list
    eg: ['api_hotupdate_callback']

    管理员用户具有超级权限，不受权限系统的控制
    """

    message = '权限拒绝'

    def has_perms(self, user, list_perm):
        """list_perm是否在user的所有权限中"""

        user_perms = User.objects.get(id=user.id).get_all_permissions()
        for perm in list_perm:
            if perm in user_perms:
                return True
        return False

    def get_module_perms(self, view):
        """返回view的api_perms的属性"""
        return ['users.' + x for x in view._api_perms]

    def has_permission(self, request, view):
        """这里是真正检查是否具有权限的地方

        override this method !!!

        如果有权限，返回True,不然，返回False

        管理员权限不受控制
        """

        if request.user.is_superuser:
            return True

        assert hasattr(view, '_ignore_perm') and isinstance(view._ignore_perm, bool), (
            '需要在APIView中配置_ignore_perm的属性并且为bool类型'
        )

        if view._ignore_perm:
            return True

        assert hasattr(view, '_api_perms') and isinstance(view._api_perms, list), (
            '需要在APIView中配置_api_perms的属性并且为list类型'
        )

        return self.has_perms(request.user, self.get_module_perms(view))


def api_permission(*, api_perms=[], ignore_perm=False):
    """装饰器函数
    用来装饰APIView，指定某个api有哪些权限

    api_perms是django permission的list集合
    如果想要忽略某个api的权限，设置ignore_perm=True

    用法:
    在api的app的views.py中，装饰class
    @api_permission(api_perms=['view_host', 'view_room'])
    class CleanUserCallBack(APIView):
        ...

    如果你想忽略掉某个api的权限
    @api_permission(ignore_perms=True)
    class CleanUserCallBack(APIView):
        ...
    """

    def _decorate(cls):
        cls._api_perms = api_perms
        cls._ignore_perm = ignore_perm
        return cls
    return _decorate
