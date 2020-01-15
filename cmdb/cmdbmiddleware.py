# -*- encoding: utf-8 -*-

from django.shortcuts import redirect, render_to_response
from django.conf import settings
from urllib.parse import unquote,quote


# from users.models import Users

class LocalLoginRequiredMiddleware(object):
    """Middleware that requires user login
       accross the whole website
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        if (not request.user.is_authenticated() and 'login' not in request.path and
                'user_register' not in request.path and
                'forget_password' not in request.path and
                'error_version' not in request.path and
                'reset_password' not in request.path and not str(request.path_info).startswith('/api')):
            if request.path not in [
                '/assets/list_register_group/', '/assets/list_project_group/', '/assets/list_game_project/'
            ]:
                next_path = request.get_full_path()
                next_path = quote(next_path)
                return redirect('%s?next=%s' % (settings.LOGIN_URL, next_path))

        response = self.get_response(request)

        # 强制修改初始密码
        if request.user.is_authenticated():
            if request.user.check_password('redhat'):
                if 'new_passwd' not in request.path:
                    if 'user_logout' not in request.path:
                        return redirect('/users/new_passwd/')

        # 判断是否维护
        if settings.MAINTENANCE:
            return render_to_response('maintenance.html')

        return response

    """
    def process_request(self, request):
        error = ("The LoginRequiredMiddleware requires authentication "
                 "middleware to be installed. Edit your MIDDLEWARE_CLASSES "
                 "setting to insert 'django.contrib.auth.middleware.AuthenticationMiddleware"
                 )

        #assert hasattr(request, 'user'), error

        if not request.user.is_authenticated() and 'login' not in request.path:
            return HttpResponseRedirect(settings.LOGIN_URL)
    """
