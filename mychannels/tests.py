from django.test import TestCase

# Create your tests here.

import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'cmdb.settings'

import django

django.setup()
from channels import Channel


def ws_update_task_result(update_msg):
    """刷新salt任务执行结果
    """
    msg = {"message": update_msg, 'group_name': 'salt_task'}
    Channel('update_execute_salt_task').send(msg)


ws_update_task_result('test')