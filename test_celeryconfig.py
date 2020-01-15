# -*- encoding: utf-8 -*-
from cmdb.settings import REDIS_URL
from cmdb.settings import REDIS_BACKEND_URL

CELERY_TIMEZONE = 'Asia/Shanghai'

# BROKER_URL = 'amqp://localhost//'
BROKER_URL = REDIS_URL
CELERY_IMPORTS = ('test_tasks',)

CELERY_RESULT_BACKEND = REDIS_BACKEND_URL
CELERY_RESULT_PERSISTENT = True
CELERY_TASK_RESULT_EXPIRES = None

CELERY_DEFAULT_QUEUE = 'default'
CELERY_QUEUES = {
    'default': {
        'binding_key': 'task.#',
    },
    'test': {
        'binding_key': 'test.#',
    },
    'file_pull_test_8': {
        'binding_key': 'file_pull_test_8.#',
    },
    'file_push_test_8': {
        'binding_key': 'file_push_test_8.#',
    },
    'file_pull_test_15': {
        'binding_key': 'file_pull_test_15.#',
    },
    'file_push_test_15': {
        'binding_key': 'file_push_test_15.#',
    },
    'do_test_hot_update': {
        'binding_key': 'do_test_hot_update.#',
    },
}
CELERY_DEFAULT_EXCHANGE = 'tasks'
CELERY_DEFAULT_EXCHANGE_TYPE = 'topic'
CELERY_DEFAULT_ROUTING_KEY = 'task.default'
CELERY_ROUTES = {
    'test_tasks.test': {
        'queue': 'test',
        'routing_key': 'test.a_qq'
    },
    'test_tasks.file_pull_test_8': {
        'queue': 'file_pull_test_8',
        'routing_key': 'file_pull_test_8.a_file_pull_test_8'
    },
    'test_tasks.file_push_test_8': {
        'queue': 'file_push_test_8',
        'routing_key': 'file_push_test_8.a_file_push_test_8'
    },
    'test_tasks.file_pull_test_15': {
        'queue': 'file_pull_test_15',
        'routing_key': 'file_pull_test_15.a_file_pull_test_15'
    },
    'test_tasks.file_push_test_15': {
        'queue': 'file_push_test_15',
        'routing_key': 'file_push_test_15.a_file_push_test_15'
    },
    'test_tasks.do_test_hot_client': {
        'queue': 'do_test_hot_update',
        'routing_key': 'do_test_hot_update.test_hot_client'
    },
    'test_tasks.do_test_hot_server': {
        'queue': 'do_test_hot_update',
        'routing_key': 'do_test_hot_update.test_hot_server'
    },
}
