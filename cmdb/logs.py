# -*- encoding: utf-8 -*-

"""CMDB的log模块

分为cmdb_runtime和mail_log
用于记录不同的log
"""

import logging
import os

from logging.handlers import RotatingFileHandler


class RuntimeLog(object):
    """主要记录一些运行时候的log"""
    pass


class HotUpdateTimeOutLog(object):
    """热更新检测超时的log"""

    def __init__(self):
        # create logger
        self.logger = logging.getLogger('hotupdate_timeout_log')
        self.logger.setLevel(logging.DEBUG)

        if not self.logger.handlers:

            # create file handler and set level to debug
            fh = RotatingFileHandler('/var/log/cmdb_hotupdate_timeout.log', maxBytes=1000 * 1000 * 10, backupCount=5, encoding='UTF-8')
            fh.setLevel(logging.DEBUG)

            # create formatter
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

            # add formatter
            fh.setFormatter(formatter)

            # add fh to logger
            self.logger.addHandler(fh)


class MailLog(object):
    """发送邮件的log"""

    def __init__(self):
        # create logger
        self.logger = logging.getLogger('mail_log')
        self.logger.setLevel(logging.DEBUG)

        if not self.logger.handlers:

            # create file handler and set level to debug
            fh = RotatingFileHandler('/var/log/cmdb_mail.log', maxBytes=1000 * 1000 * 10, backupCount=5, encoding='UTF-8')
            fh.setLevel(logging.DEBUG)

            # create formatter
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

            # add formatter
            fh.setFormatter(formatter)

            # add fh to logger
            self.logger.addHandler(fh)


class SendQQLog(object):
    """发送qq弹窗的log"""

    def __init__(self):
        # create logger
        self.logger = logging.getLogger('sqq_log')
        self.logger.setLevel(logging.DEBUG)

        if not self.logger.handlers:

            # create file handler and set level to debug
            fh = RotatingFileHandler('/var/log/cmdb_sqq.log', maxBytes=1000 * 1000 * 10, backupCount=5, encoding='UTF-8')
            fh.setLevel(logging.DEBUG)

            # create formatter
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

            # add formatter
            fh.setFormatter(formatter)

            # add fh to logger
            self.logger.addHandler(fh)


class MailReceivLog(object):
    """收取邮件的log"""

    def __init__(self):
        # create logger
        self.logger = logging.getLogger('mail_receive_log')
        self.logger.setLevel(logging.DEBUG)

        if not self.logger.handlers:

            # create file handler and set level to debug
            fh = RotatingFileHandler('/var/log/cmdb_mail_receive.log', maxBytes=1000 * 1000 * 10, backupCount=5, encoding='UTF-8')
            fh.setLevel(logging.DEBUG)

            # create formatter
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

            # add formatter
            fh.setFormatter(formatter)

            # add fh to logger
            self.logger.addHandler(fh)


class SVNLog(object):
    """svn操作的log"""

    def __init__(self):
        # create logger
        self.logger = logging.getLogger('svn_log')
        self.logger.setLevel(logging.DEBUG)

        if not self.logger.handlers:

            # create file handler and set level to debug
            fh = RotatingFileHandler('/var/log/cmdb_svn.log', maxBytes=1000 * 1000 * 10, backupCount=5, encoding='UTF-8')
            fh.setLevel(logging.DEBUG)

            # create formatter
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

            # add formatter
            fh.setFormatter(formatter)

            # add fh to logger
            self.logger.addHandler(fh)


class SerPerLog(object):
    """服务器权限的log"""

    def __init__(self):
        # create logger
        self.logger = logging.getLogger('serper_log')
        self.logger.setLevel(logging.DEBUG)

        if not self.logger.handlers:
            # create file handler and set level to debug
            fh = RotatingFileHandler('/var/log/cmdb_serper.log', maxBytes=1000 * 1000 * 10, backupCount=5, encoding='UTF-8')
            fh.setLevel(logging.DEBUG)

            # create formatter
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

            # add formatter
            fh.setFormatter(formatter)

            # add fh to logger
            self.logger.addHandler(fh)


class SHostLog(object):
    """定期修改服务器权限和用户关系的log"""

    def __init__(self):
        # create logger
        self.logger = logging.getLogger('shost_log')
        self.logger.setLevel(logging.DEBUG)

        if not self.logger.handlers:
            # create file handler and set level to debug
            fh = RotatingFileHandler('/var/log/cmdb_shost.log', maxBytes=1000 * 1000 * 10, backupCount=5, encoding='UTF-8')
            fh.setLevel(logging.DEBUG)

            # create formatter
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

            # add formatter
            fh.setFormatter(formatter)

            # add fh to logger
            self.logger.addHandler(fh)


class HotUpdateLog(object):
    """热更新前后端log"""

    def __init__(self, uuid):
        # create logger
        self.logger = logging.getLogger(uuid)
        self.logger.setLevel(logging.DEBUG)

        if not self.logger.handlers:

            # create file handler and set level to debug
            logpath = os.path.join('/var/log/cmdb_hotupdate', uuid)
            fh = logging.FileHandler(logpath, 'a', encoding='UTF-8')
            fh.setLevel(logging.DEBUG)

            # create formatter
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

            # add formatter
            fh.setFormatter(formatter)

            # add fh to logger
            self.logger.addHandler(fh)


class PushAPILog(object):
    """运维管理机给cmdb上锁记录的log"""

    def __init__(self):
        # create logger
        self.logger = logging.getLogger('push_api_log')
        self.logger.setLevel(logging.DEBUG)

        if not self.logger.handlers:

            # create file handler and set level to debug
            fh = RotatingFileHandler('/var/log/cmdb_push_api.log', maxBytes=1000 * 1000 * 10, backupCount=5, encoding='UTF-8')
            fh.setLevel(logging.DEBUG)

            # create formatter
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

            # add formatter
            fh.setFormatter(formatter)

            # add fh to logger
            self.logger.addHandler(fh)


class CleanUserLog(object):
    """离职清理用户的log"""

    def __init__(self):
        # create logger
        self.logger = logging.getLogger('clean_user_log')
        self.logger.setLevel(logging.DEBUG)

        if not self.logger.handlers:
            # create file handler and set level to debug
            fh = RotatingFileHandler('/var/log/clean_user_log.log', maxBytes=1000 * 1000 * 10, backupCount=5, encoding='UTF-8')
            fh.setLevel(logging.DEBUG)

            # create formatter
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

            # add formatter
            fh.setFormatter(formatter)

            # add fh to logger
            self.logger.addHandler(fh)


class CleanProjectServer(object):
    """根据项目清除服务器权限"""

    def __init__(self):
        # create logger
        self.logger = logging.getLogger('clean_project_server_log')
        self.logger.setLevel(logging.DEBUG)

        if not self.logger.handlers:
            # create file handler and set level to debug
            fh = RotatingFileHandler('/var/log/cmdb_clean_project_serper.log', maxBytes=1000 * 1000 * 10, backupCount=5, encoding='UTF-8')
            fh.setLevel(logging.DEBUG)

            # create formatter
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

            # add formatter
            fh.setFormatter(formatter)

            # add fh to logger
            self.logger.addHandler(fh)


class MysqlPermissionLog(object):
    """添加mysql权限日志"""

    def __init__(self):
        # create logger
        self.logger = logging.getLogger('mysq_permission_log')
        self.logger.setLevel(logging.DEBUG)

        if not self.logger.handlers:

            # create file handler and set level to debug
            # fh = logging.FileHandler('/var/log/cmdb_update_loop.log', 'a', encoding='UTF-8')
            # fh.setLevel(logging.DEBUG)

            # create formatter
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

            # add formatter
            # fh.setFormatter(formatter)

            # create handler
            rh = RotatingFileHandler('/var/log/cmdb_mysq_permission.log', maxBytes=1000 * 1000 * 10, backupCount=5, encoding='UTF-8')
            rh.setLevel(logging.DEBUG)
            rh.setFormatter(formatter)

            # add fh to logger
            # self.logger.addHandler(fh)
            self.logger.addHandler(rh)


class WebApiLog(object):
    """web调用api的log
    装服计划从web调用到cmdb
    """

    def __init__(self):
        # create logger
        self.logger = logging.getLogger('web_api_log')
        self.logger.setLevel(logging.DEBUG)

        if not self.logger.handlers:

            # create file handler and set level to debug
            # fh = logging.FileHandler('/var/log/cmdb_update_loop.log', 'a', encoding='UTF-8')
            # fh.setLevel(logging.DEBUG)

            # create formatter
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

            # add formatter
            # fh.setFormatter(formatter)

            # create handler
            rh = RotatingFileHandler('/var/log/cmdb_web_api.log', maxBytes=1000 * 1000 * 10, backupCount=5, encoding='UTF-8')
            rh.setLevel(logging.DEBUG)
            rh.setFormatter(formatter)

            # add fh to logger
            # self.logger.addHandler(fh)
            self.logger.addHandler(rh)


class GameInstallLog(object):
    """安装游戏服的log
    """

    def __init__(self):
        # create logger
        self.logger = logging.getLogger('game_install_log')
        self.logger.setLevel(logging.DEBUG)

        if not self.logger.handlers:

            # create file handler and set level to debug
            # fh = logging.FileHandler('/var/log/cmdb_update_loop.log', 'a', encoding='UTF-8')
            # fh.setLevel(logging.DEBUG)

            # create formatter
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

            # add formatter
            # fh.setFormatter(formatter)

            # create handler
            rh = RotatingFileHandler('/var/log/game_install.log', maxBytes=1000 * 1000 * 10, backupCount=5, encoding='UTF-8')
            rh.setLevel(logging.DEBUG)
            rh.setFormatter(formatter)

            # add fh to logger
            # self.logger.addHandler(fh)
            self.logger.addHandler(rh)


class GameUnInstallLog(object):
    """卸载游戏服的log
    """

    def __init__(self):
        # create logger
        self.logger = logging.getLogger('game_uninstall_log')
        self.logger.setLevel(logging.DEBUG)

        if not self.logger.handlers:

            # create file handler and set level to debug
            # fh = logging.FileHandler('/var/log/cmdb_update_loop.log', 'a', encoding='UTF-8')
            # fh.setLevel(logging.DEBUG)

            # create formatter
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

            # add formatter
            # fh.setFormatter(formatter)

            # create handler
            rh = RotatingFileHandler('/var/log/game_uninstall.log', maxBytes=1000 * 1000 * 10, backupCount=5, encoding='UTF-8')
            rh.setLevel(logging.DEBUG)
            rh.setFormatter(formatter)

            # add fh to logger
            # self.logger.addHandler(fh)
            self.logger.addHandler(rh)


class AddEntEmailAccountLog(object):
    """创建企业邮箱帐号的log
    """

    def __init__(self):
        # create logger
        self.logger = logging.getLogger('add_ent_email_account_log')
        self.logger.setLevel(logging.DEBUG)

        if not self.logger.handlers:

            # create file handler and set level to debug
            # fh = logging.FileHandler('/var/log/cmdb_update_loop.log', 'a', encoding='UTF-8')
            # fh.setLevel(logging.DEBUG)

            # create formatter
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

            # add formatter
            # fh.setFormatter(formatter)

            # create handler
            rh = RotatingFileHandler('/var/log/ent_email_account.log', maxBytes=1000 * 1000 * 10, backupCount=5, encoding='UTF-8')
            rh.setLevel(logging.DEBUG)
            rh.setFormatter(formatter)

            # add fh to logger
            # self.logger.addHandler(fh)
            self.logger.addHandler(rh)


class AddEntQQAccountLog(object):
    """创建企业QQ帐号的log
    """

    def __init__(self):
        # create logger
        self.logger = logging.getLogger('add_ent_qq_account_log')
        self.logger.setLevel(logging.DEBUG)

        if not self.logger.handlers:

            # create file handler and set level to debug
            # fh = logging.FileHandler('/var/log/cmdb_update_loop.log', 'a', encoding='UTF-8')
            # fh.setLevel(logging.DEBUG)

            # create formatter
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

            # add formatter
            # fh.setFormatter(formatter)

            # create handler
            rh = RotatingFileHandler('/var/log/ent_qq_account.log', maxBytes=1000 * 1000 * 10, backupCount=5, encoding='UTF-8')
            rh.setLevel(logging.DEBUG)
            rh.setFormatter(formatter)

            # add fh to logger
            # self.logger.addHandler(fh)
            self.logger.addHandler(rh)


class RsyncLog(object):
    """推送salt配置文件log"""

    def __init__(self):
        # create logger
        self.logger = logging.getLogger('salt-rsync-log')
        self.logger.setLevel(logging.DEBUG)

        if not self.logger.handlers:
            # create file handler and set level to debug
            fh = RotatingFileHandler('/var/log/salt_rsync.log', maxBytes=1000 * 1000 * 10, backupCount=5, encoding='UTF-8')
            fh.setLevel(logging.DEBUG)

            # create formatter
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

            # add formatter
            fh.setFormatter(formatter)

            # add fh to logger
            self.logger.addHandler(fh)


class SyncCeleryWorkerLog(object):
    """定时同步celery worker状态log"""

    def __init__(self):
        # create logger
        self.logger = logging.getLogger('sync-celery-worker-log')
        self.logger.setLevel(logging.DEBUG)

        if not self.logger.handlers:
            # create file handler and set level to debug
            fh = RotatingFileHandler('/var/log/sync_celery_worker_status.log', maxBytes=1000 * 1000 * 10, backupCount=5, encoding='UTF-8')
            fh.setLevel(logging.DEBUG)

            # create formatter
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

            # add formatter
            fh.setFormatter(formatter)

            # add fh to logger
            self.logger.addHandler(fh)


class OpenVPNLog(object):
    """openVPN的log"""

    def __init__(self):
        # create logger
        self.logger = logging.getLogger('cmdb-openvpn-log')
        self.logger.setLevel(logging.DEBUG)

        if not self.logger.handlers:
            # create file handler and set level to debug
            fh = RotatingFileHandler('/var/log/cmdb_openvpn.log', maxBytes=1000 * 1000 * 10, backupCount=5, encoding='UTF-8')
            fh.setLevel(logging.DEBUG)

            # create formatter
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

            # add formatter
            fh.setFormatter(formatter)

            # add fh to logger
            self.logger.addHandler(fh)


class PullFileLog(object):
    """获取更新文件列表的log"""

    def __init__(self):
        # create logger
        self.logger = logging.getLogger('cmdb-pull-file-log')
        self.logger.setLevel(logging.DEBUG)

        if not self.logger.handlers:
            # create file handler and set level to debug
            fh = RotatingFileHandler('/var/log/cmdb_pull_file.log', maxBytes=1000 * 1000 * 10, backupCount=5, encoding='UTF-8')
            fh.setLevel(logging.DEBUG)

            # create formatter
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

            # add formatter
            fh.setFormatter(formatter)

            # add fh to logger
            self.logger.addHandler(fh)


class GameServerOffLog(object):
    """区服下线计划执行的log"""

    def __init__(self):
        # create logger
        self.logger = logging.getLogger('game-server-off-log')
        self.logger.setLevel(logging.DEBUG)

        if not self.logger.handlers:
            # create file handler and set level to debug
            fh = RotatingFileHandler('/var/log/cmdb_game_server_off.log', maxBytes=1000 * 1000 * 10, backupCount=5, encoding='UTF-8')
            fh.setLevel(logging.DEBUG)

            # create formatter
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

            # add formatter
            fh.setFormatter(formatter)

            # add fh to logger
            self.logger.addHandler(fh)


class WorkflowApproveLog(object):
    """工单审批的log"""

    def __init__(self):
        # create logger
        self.logger = logging.getLogger('workflow-approve-log')
        self.logger.setLevel(logging.DEBUG)

        if not self.logger.handlers:
            # create file handler and set level to debug
            fh = RotatingFileHandler('/var/log/cmdb_workflow_approve.log', maxBytes=1000 * 1000 * 10, backupCount=5, encoding='UTF-8')
            fh.setLevel(logging.DEBUG)

            # create formatter
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

            # add formatter
            fh.setFormatter(formatter)

            # add fh to logger
            self.logger.addHandler(fh)


class APIUserLog(object):
    """通过API接口新增用户/确认入职/删除用户的log"""

    def __init__(self):
        # create logger
        self.logger = logging.getLogger('api-user-log')
        self.logger.setLevel(logging.DEBUG)

        if not self.logger.handlers:
            # create file handler and set level to debug
            fh = RotatingFileHandler('/var/log/cmdb_api_user.log', maxBytes=1000 * 1000 * 10, backupCount=5, encoding='UTF-8')
            fh.setLevel(logging.DEBUG)

            # create formatter
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

            # add formatter
            fh.setFormatter(formatter)

            # add fh to logger
            self.logger.addHandler(fh)


class WXMsgReceiveLog(object):
    """微信信息回调的log"""

    def __init__(self):
        # create logger
        self.logger = logging.getLogger('wechat-callback-log')
        self.logger.setLevel(logging.DEBUG)

        if not self.logger.handlers:
            # create file handler and set level to debug
            fh = RotatingFileHandler('/var/log/wechat_callback.log', maxBytes=1000 * 1000 * 10, backupCount=5, encoding='UTF-8')
            fh.setLevel(logging.DEBUG)

            # create formatter
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

            # add formatter
            fh.setFormatter(formatter)

            # add fh to logger
            self.logger.addHandler(fh)


class SendWxTaskCardLog(object):
    """发送微信任务卡片的log"""

    def __init__(self):
        # create logger
        self.logger = logging.getLogger('wechat-taskcard-log')
        self.logger.setLevel(logging.DEBUG)

        if not self.logger.handlers:
            # create file handler and set level to debug
            fh = RotatingFileHandler('/var/log/wechat_taskcard.log', maxBytes=1000 * 1000 * 10, backupCount=5, encoding='UTF-8')
            fh.setLevel(logging.DEBUG)

            # create formatter
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

            # add formatter
            fh.setFormatter(formatter)

            # add fh to logger
            self.logger.addHandler(fh)


class GameSeverMergeAPILog(object):
    """接收web发送合服计划API的log"""

    def __init__(self):
        # create logger
        self.logger = logging.getLogger('srv-merge-api-log')
        self.logger.setLevel(logging.DEBUG)

        if not self.logger.handlers:
            # create file handler and set level to debug
            fh = RotatingFileHandler('/var/log/cmdb_srv_merge_api.log', maxBytes=1000 * 1000 * 10, backupCount=5, encoding='UTF-8')
            fh.setLevel(logging.DEBUG)

            # create formatter
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

            # add formatter
            fh.setFormatter(formatter)

            # add fh to logger
            self.logger.addHandler(fh)


class JenkinsLoginLog(object):
    """模拟登录jenkins的log"""

    def __init__(self):
        # create logger
        self.logger = logging.getLogger('jenkins-login-log')
        self.logger.setLevel(logging.DEBUG)

        if not self.logger.handlers:
            # create file handler and set level to debug
            fh = RotatingFileHandler('/var/log/cmdb_login_jenkins.log', maxBytes=1000 * 1000 * 10, backupCount=5, encoding='UTF-8')
            fh.setLevel(logging.DEBUG)

            # create formatter
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

            # add formatter
            fh.setFormatter(formatter)

            # add fh to logger
            self.logger.addHandler(fh)


class PurchaseCloudServerLog(object):
    """购买云服务器的log"""

    def __init__(self):
        # create logger
        self.logger = logging.getLogger('purchase-cloudserver-log')
        self.logger.setLevel(logging.DEBUG)

        if not self.logger.handlers:
            # create file handler and set level to debug
            fh = RotatingFileHandler('/var/log/cmdb_purchase_cloudserver.log', maxBytes=1000 * 1000 * 10, backupCount=5, encoding='UTF-8')
            fh.setLevel(logging.DEBUG)

            # create formatter
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

            # add formatter
            fh.setFormatter(formatter)

            # add fh to logger
            self.logger.addHandler(fh)


class VersionUpdateLog(object):
    """发送版本更新请求的log"""

    def __init__(self):
        # create logger
        self.logger = logging.getLogger('cmdb-version-update-log')
        self.logger.setLevel(logging.DEBUG)

        if not self.logger.handlers:
            # create file handler and set level to debug
            fh = RotatingFileHandler('/var/log/cmdb_version_update.log', 'a', maxBytes=1000 * 1000 * 10, backupCount=5, encoding='UTF-8')
            fh.setLevel(logging.DEBUG)

            # create formatter
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

            # add formatter
            fh.setFormatter(formatter)

            # add fh to logger
            self.logger.addHandler(fh)


class RecvWebMaintenanceLog(object):
    """接收web挂维护信息的log"""

    def __init__(self):
        # create logger
        self.logger = logging.getLogger('cmdb-maintenance-log')
        self.logger.setLevel(logging.DEBUG)

        if not self.logger.handlers:
            # create file handler and set level to debug
            fh = RotatingFileHandler('/var/log/cmdb_maintenance.log', 'a', maxBytes=1000 * 1000 * 10, backupCount=5, encoding='UTF-8')
            fh.setLevel(logging.DEBUG)

            # create formatter
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

            # add formatter
            fh.setFormatter(formatter)

            # add fh to logger
            self.logger.addHandler(fh)


class DebugTempLog(object):
    """调试临时记录的log"""

    def __init__(self):
        # create logger
        self.logger = logging.getLogger('cmdb-debug-log')
        self.logger.setLevel(logging.DEBUG)

        if not self.logger.handlers:
            # create file handler and set level to debug
            fh = RotatingFileHandler('/var/log/cmdb_debug.log', 'a', maxBytes=1000 * 1000 * 10, backupCount=5, encoding='UTF-8')
            fh.setLevel(logging.DEBUG)

            # create formatter
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

            # add formatter
            fh.setFormatter(formatter)

            # add fh to logger
            self.logger.addHandler(fh)
