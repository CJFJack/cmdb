# -*- coding: utf-8 -*-

# from collections import defaultdict

# Create your views here.

from rest_framework.views import APIView
from django.http import JsonResponse

from assets.models import GameProject


class ProjectSvn(APIView):
    """获取项目的svn信息
    返回的数据格式如下:
    {
        "项目英文名1": {"项目负责人邮件1", "svn_repo1"},
        "项目英文名2": {"项目负责人邮件2", "svn_repo2"},
    }
    """

    def get(self, request, format=None):
        resp = 0
        reason = ''
        project_svn = {}
        try:
            all_project = GameProject.objects.all()
            for p in all_project:
                project_name = p.project_name
                svn_repo = p.svn_repo
                leader_email = p.leader.email if p.leader else ''
                if svn_repo:
                    project_svn[project_name] = {}
                    project_svn[project_name][leader_email] = svn_repo
            reason = project_svn
        except Exception as e:
            reason = str(e)
            resp = 1
        return JsonResponse({'reason': reason, 'resp': resp})
