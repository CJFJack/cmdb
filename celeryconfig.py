# -*- encoding: utf-8 -*-

from cmdb.settings import REDIS_URL
from cmdb.settings import REDIS_BACKEND_URL

CELERY_TIMEZONE = 'Asia/Shanghai'

# BROKER_URL = 'amqp://localhost//'
# BROKER_URL = 'redis://localhost:6379/0'
BROKER_URL = REDIS_URL
CELERY_IMPORTS = ('tasks',)

CELERY_RESULT_BACKEND = REDIS_BACKEND_URL
CELERY_RESULT_PERSISTENT = True
CELERY_TASK_RESULT_EXPIRES = None

# Worker在执行n个任务杀掉子进程再启动新的子进程，可以防止内存泄露
# CELERYD_MAX_TASKS_PER_CHILD = 30

CELERY_DEFAULT_QUEUE = 'default'
CELERY_QUEUES = {
    'default': {
        'binding_key': 'task.#',
    },
    'send_mail': {
        'binding_key': 'send_mail.#',
    },
    'send_qq': {
        'binding_key': 'send_qq.#',
    },
    'recieve_mail': {
        'binding_key': 'recieve_mail.#',
    },
    'workflow_add_server_permission': {
        'binding_key': 'workflow_add_server_permission.#',
    },
    'set_user_host': {
        'binding_key': 'set_user_host.#',
    },
    'add_svn_workflow': {
        'binding_key': 'add_svn_workflow.#',
    },
    'do_hot_update': {
        'binding_key': 'do_hot_update.#',
    },
    'do_game_server': {
        'binding_key': 'do_game_server.#',
    },
    'file_pull_8': {
        'binding_key': 'file_pull_8.#',
    },
    'file_push_8': {
        'binding_key': 'file_push_8.#',
    },
    'file_pull_15': {
        'binding_key': 'file_pull_15.#',
    },
    'file_push_15': {
        'binding_key': 'file_push_15.#',
    },
    'file_pull_cc': {
        'binding_key': 'file_pull_cc.#',
    },
    'file_push_cc': {
        'binding_key': 'file_push_cc.#',
    },
    'clean_project_serper': {
        'binding_key': 'clean_project_serper.#',
    },
    'hotupdate_timeout': {
        'binding_key': 'hotupdate_timeout.#',
    },
    'add_mysql_permission': {
        'binding_key': 'add_mysql_permission.#',
    },
    'remove_mysql_permission': {
        'binding_key': 'remove_mysql_permission.#',
    },
    'add_qq_user': {
        'binding_key': 'add_qq_user.#',
    },
    'add_email_account': {
        'binding_key': 'add_email_account.#',
    },
    'add_mac': {
        'binding_key': 'add_mac.#',
    },
    'send_weixin_message': {
        'binding_key': 'send_weixin_message.#',
    },
    'execute_salt_task': {
        'binding_key': 'execute_salt_task.#',
    },
    'file_pull_slqy3d_cn': {
        'binding_key': 'file_pull_slqy3d_cn.#',
    },
    'file_push_slqy3d_cn': {
        'binding_key': 'file_push_slqy3d_cn.#',
    },
    'file_pull_cyh5s7': {
        'binding_key': 'file_pull_cyh5s7.#',
    },
    'file_push_cyh5s7': {
        'binding_key': 'file_push_cyh5s7.#',
    },
    'refresh_cdn': {
        'binding_key': 'refresh_cdn.#',
    },
    'game_server_action_task': {
        'binding_key': 'game_server_action_task.#',
    },
    'do_game_server_off': {
        'binding_key': 'do_game_server_off.#',
    },
    'do_host_migrate': {
        'binding_key': 'do_host_migrate.#',
    },
    'do_host_recover': {
        'binding_key': 'do_host_recover.#',
    },
    'cancel_desired_user_workflow_apply': {
        'binding_key': 'cancel_desired_user_workflow_apply.#',
    },
    'file_pull_23': {
        'binding_key': 'file_pull_23.#',
    },
    'file_push_23': {
        'binding_key': 'file_push_23.#',
    },
    'do_modify_srv_open_time': {
        'binding_key': 'do_modify_srv_open_time.#',
    },
    'send_task_card_to_wx_user': {
        'binding_key': 'send_task_card_to_wx_user.#',
    },
    'do_game_server_migrate': {
        'binding_key': 'do_game_server_migrate.#',
    },
    'install_salt_minion': {
        'binding_key': 'install_salt_minion.#',
    },
    'saltstack_test_ping_tasks': {
        'binding_key': 'saltstack_test_ping_tasks.#',
    },
    'saltstack_host_initialize': {
        'binding_key': 'saltstack_host_initialize.#',
    },
    'saltstack_host_check': {
        'binding_key': 'saltstack_host_check.#',
    },
    'saltstack_host_reboot': {
        'binding_key': 'saltstack_host_reboot.#',
    },
    'version_update_task': {
        'binding_key': 'version_update_task.#',
    },
    'txcloud_api': {
        'binding_key': 'txcloud_api.#',
    },
    'saltstack_host_import': {
        'binding_key': 'saltstack_host_import.#',
    },
}
CELERY_DEFAULT_EXCHANGE = 'tasks'
CELERY_DEFAULT_EXCHANGE_TYPE = 'topic'
CELERY_DEFAULT_ROUTING_KEY = 'task.default'
CELERY_ROUTES = {
    'tasks.send_mail': {
        'queue': 'send_mail',
        'routing_key': 'send_mail.a_mail'
    },
    'tasks.send_qq': {
        'queue': 'send_qq',
        'routing_key': 'send_qq.a_qq'
    },
    'tasks.recieve_mail': {
        'queue': 'recieve_mail',
        'routing_key': 'recieve_mail.a_mail'
    },
    'tasks.workflow_add_server_permission': {
        'queue': 'workflow_add_server_permission',
        'routing_key': 'workflow_add_server_permission.a_server_permission'
    },
    'tasks.set_user_host': {
        'queue': 'set_user_host',
        'routing_key': 'set_user_host.a_set_user_host'
    },
    'tasks.add_svn_workflow': {
        'queue': 'add_svn_workflow',
        'routing_key': 'add_svn_workflow.a_set_user_host'
    },
    'tasks.hotupdate': {
        'queue': 'send_mail',
        'routing_key': 'send_mail.a_mail'
    },
    'tasks.do_hot_client': {
        'queue': 'do_hot_update',
        'routing_key': 'do_hot_update.hot_client'
    },
    'tasks.do_hot_server': {
        'queue': 'do_hot_update',
        'routing_key': 'do_hot_update.hot_server'
    },
    'tasks.do_game_install': {
        'queue': 'game_server_action_task',
        'routing_key': 'game_server_action_task.do_game_install'
    },
    'tasks.do_game_uninstall': {
        'queue': 'game_server_action_task',
        'routing_key': 'game_server_action_task.do_game_uninstall'
    },
    'tasks.file_pull_8': {
        'queue': 'file_pull_8',
        'routing_key': 'file_pull_8.a_file_pull_8'
    },
    'tasks.file_push_8': {
        'queue': 'file_push_8',
        'routing_key': 'file_push_8.a_file_push_8'
    },
    'tasks.file_pull_15': {
        'queue': 'file_pull_15',
        'routing_key': 'file_pull_15.a_file_pull_8'
    },
    'tasks.file_push_15': {
        'queue': 'file_push_15',
        'routing_key': 'file_push_15.a_file_push_8'
    },
    'tasks.file_pull_cc': {
        'queue': 'file_pull_cc',
        'routing_key': 'file_pull_cc.a_file_pull_cc'
    },
    'tasks.file_push_cc': {
        'queue': 'file_push_cc',
        'routing_key': 'file_push_cc.a_file_push_cc'
    },
    'tasks.clean_project_serper': {
        'queue': 'clean_project_serper',
        'routing_key': 'clean_project_serper.a_clean_project_serper'
    },
    'tasks.clean_svn_workflow': {
        'queue': 'add_svn_workflow',
        'routing_key': 'add_svn_workflow.clean_svn_workflow'
    },
    'tasks.hotupdate_timeout': {
        'queue': 'hotupdate_timeout',
        'routing_key': 'hotupdate_timeout.a_hotupdate_timeout'
    },
    'tasks.add_mysql_permission': {
        'queue': 'add_mysql_permission',
        'routing_key': 'add_mysql_permission.a_add_mysql_permission'
    },
    'tasks.remove_mysql_permission': {
        'queue': 'remove_mysql_permission',
        'routing_key': 'remove_mysql_permission.a_remove_mysql_permission'
    },
    'tasks.add_qq_user': {
        'queue': 'add_qq_user',
        'routing_key': 'add_qq_user.a_add_qq_user'
    },
    'tasks.add_email_account': {
        'queue': 'add_email_account',
        'routing_key': 'add_email_account.a_add_email_account'
    },
    'tasks.add_mac': {
        'queue': 'add_mac',
        'routing_key': 'add_mac.a_add_mac'
    },
    'tasks.send_weixin_message': {
        'queue': 'send_weixin_message',
        'routing_key': 'send_weixin_message.a_send_weixin_message'
    },
    'tasks.execute_salt_task': {
        'queue': 'execute_salt_task',
        'routing_key': 'execute_salt_task.a_execute_salt_task'
    },
    'tasks.file_pull_slqy3d_cn': {
        'queue': 'file_pull_slqy3d_cn',
        'routing_key': 'file_pull_slqy3d.a_file_pull_slqy3d_cn'
    },
    'tasks.file_push_slqy3d_cn': {
        'queue': 'file_push_slqy3d_cn',
        'routing_key': 'file_push_slqy3d_cn.a_file_push_slqy3d_cn'
    },
    'tasks.file_pull_cyh5s7': {
        'queue': 'file_pull_cyh5s7',
        'routing_key': 'file_pull_cyh5s7.a_file_pull_cyh5s7'
    },
    'tasks.file_push_cyh5s7': {
        'queue': 'file_push_cyh5s7',
        'routing_key': 'file_push_cyh5s7.a_file_push_cyh5s7'
    },
    'tasks.refresh_txcloud_cdn': {
        'queue': 'refresh_cdn',
        'routing_key': 'refresh_cdn.a_refresh_txcloud_cdn'
    },
    'tasks.refresh_bscloud_cdn': {
        'queue': 'refresh_cdn',
        'routing_key': 'refresh_cdn.a_refresh_bscloud_cdn'
    },
    'tasks.game_server_action_task': {
        'queue': 'game_server_action_task',
        'routing_key': 'game_server_action_task.a_game_server_action_task'
    },
    'tasks.do_game_server_off': {
        'queue': 'game_server_action_task',
        'routing_key': 'game_server_action_task.a_do_game_server_off'
    },
    'tasks.do_host_migrate': {
        'queue': 'do_host_migrate',
        'routing_key': 'do_host_migrate.a_do_host_migrate'
    },
    'tasks.do_host_recover': {
        'queue': 'do_host_recover',
        'routing_key': 'do_host_recover.a_do_host_recover'
    },
    'tasks.cancel_desired_user_workflow_apply': {
        'queue': 'cancel_desired_user_workflow_apply',
        'routing_key': 'cancel_desired_user_workflow_apply.a_cancel_desired_user_workflow_apply'
    },
    'tasks.file_pull_23': {
        'queue': 'file_pull_23',
        'routing_key': 'file_pull_23.a_file_pull_23'
    },
    'tasks.file_push_23': {
        'queue': 'file_push_23',
        'routing_key': 'file_push_23.a_file_push_23'
    },
    'tasks.do_modify_srv_open_time': {
        'queue': 'game_server_action_task',
        'routing_key': 'game_server_action_task.a_do_modify_srv_open_time'
    },
    'tasks.send_task_card_to_wx_user': {
        'queue': 'send_task_card_to_wx_user',
        'routing_key': 'send_task_card_to_wx_user.a_send_task_card_to_wx_user'
    },
    'tasks.do_game_server_migrate': {
        'queue': 'game_server_action_task',
        'routing_key': 'game_server_action_task.a_do_game_server_migrate'
    },
    'tasks.install_salt_minion': {
        'queue': 'install_salt_minion',
        'routing_key': 'install_salt_minion.a_install_salt_minion'
    },
    'tasks.saltstack_test_ping_tasks': {
        'queue': 'saltstack_test_ping_tasks',
        'routing_key': 'saltstack_test_ping_tasks.a_saltstack_test_ping_tasks'
    },
    'tasks.saltstack_host_initialize': {
        'queue': 'saltstack_host_initialize',
        'routing_key': 'saltstack_host_initialize.a_saltstack_host_initialize'
    },
    'tasks.saltstack_host_check': {
        'queue': 'saltstack_host_check',
        'routing_key': 'saltstack_host_check.a_saltstack_host_check'
    },
    'tasks.saltstack_host_reboot': {
        'queue': 'saltstack_host_reboot',
        'routing_key': 'saltstack_host_reboot.a_saltstack_host_reboot'
    },
    'tasks.cmdb_tasks_timeout_check': {
        'queue': 'hotupdate_timeout',
        'routing_key': 'hotupdate_timeout.cmdb_tasks_timeout_check'
    },
    'tasks.do_game_server_merge': {
        'queue': 'game_server_action_task',
        'routing_key': 'game_server_action_task.do_game_server_merge'
    },
    'tasks.do_query_txserver_status': {
        'queue': 'txcloud_api',
        'routing_key': 'txcloud_api.do_query_txserver_status'
    },
    'tasks.version_update_task': {
        'queue': 'version_update_task',
        'routing_key': 'version_update_task.do_version_update_task'
    },
    'tasks.query_mysql_info': {
        'queue': 'txcloud_api',
        'routing_key': 'txcloud_api.query_mysql_info'
    },
    'tasks.query_txcloud_async_result': {
        'queue': 'txcloud_api',
        'routing_key': 'txcloud_api.query_txcloud_async_result'
    },
    'tasks.wx_whitelist_task': {
        'queue': 'txcloud_api',
        'routing_key': 'txcloud_api.wx_whitelist_task'
    },
    'tasks.saltstack_host_import': {
        'queue': 'saltstack_host_import',
        'routing_key': 'saltstack_host_import.a_saltstack_host_import'
    },
    'tasks.get_salt_minion': {
        'queue': 'execute_salt_task',
        'routing_key': 'execute_salt_task.a_get_salt_minion'
    },
}

from datetime import timedelta
from celery.schedules import crontab

CELERYBEAT_SCHEDULE = {
    'recieve_mail': {
        'task': 'tasks.recieve_mail',
        'schedule': timedelta(seconds=60),
    },
    'set_user_host': {
        'task': 'tasks.set_user_host',
        'schedule': crontab(minute=0, hour='*/4'),
    },
    'hotupdate_timeout': {
        'task': 'tasks.hotupdate_timeout',
        'schedule': timedelta(seconds=600),
    },
    'wx_whitelist_task': {
        'task': 'tasks.wx_whitelist_task',
        'schedule': crontab(day_of_week=1),
    },
    'cmdb_tasks_timeout_check': {
        'task': 'tasks.cmdb_tasks_timeout_check',
        'schedule': timedelta(seconds=600),
    },
    'get_salt_minion': {
        'task': 'tasks.get_salt_minion',
        'schedule': crontab(minute=0, hour=1, day_of_week='1-5'),
    },
}
