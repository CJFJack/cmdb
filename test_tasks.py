# -*- encoding: utf-8 -*-

from celery import Celery

app = Celery()

import test_celeryconfig

app.config_from_object(test_celeryconfig)

# from myworkflows.mails import SendEmail
# from myworkflows.mails import RecieveMail

import shutil
import os
import json

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cmdb.settings")
import django

django.setup()
import hashlib
import logging
import subprocess
import requests
from requests.packages.urllib3.util import Retry
from requests.adapters import HTTPAdapter
from requests import Session
from myworkflows.exceptions import HotUpdateBlock
from myworkflows.models import *
from myworkflows.utils import *
from myworkflows.hot_server_utils import revise_server_list
from myworkflows.config import CLIENT_HOT


class RsyncLog(object):
    """热更新前后端log"""

    def __init__(self):
        # create logger
        self.logger = logging.getLogger('rsync-log')
        self.logger.setLevel(logging.DEBUG)

        if not self.logger.handlers:
            # create file handler and set level to debug
            fh = logging.FileHandler('/var/log/cmdb_rsync_test.log', 'a', encoding='UTF-8')
            fh.setLevel(logging.DEBUG)

            # create formatter
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

            # add formatter
            fh.setFormatter(formatter)

            # add fh to logger
            self.logger.addHandler(fh)


class _AttributeString(str):
    @property
    def stdout(self):
        return str(self)


def local(cmd, capture=True, shell=None):
    try:
        out_stream = subprocess.PIPE
        err_stream = subprocess.PIPE
        p = subprocess.Popen(cmd, shell=True, stdout=out_stream, stderr=err_stream, executable=shell)
        (stdout, stderr) = p.communicate()

        out = _AttributeString(stdout.strip().decode('utf-8') if stdout else "")
        err = _AttributeString(stderr.strip().decode('utf-8') if stderr else "")

        out.cmd = cmd
        out.failed = False
        out.return_code = p.returncode
        out.stderr = err or out
        if out.return_code != 0:
            out.failed = True
        out.succeeded = not out.failed

        return out
    except:
        out = _AttributeString("do %s is error" % cmd)
        out.failed = True
        out.succeeded = not out.failed
        return out


@app.task()
def test():
    print('send')
    return 'send'


def md5Checksum(filePath):
    with open(filePath, 'rb') as fh:
        m = hashlib.md5()
        while True:
            data = fh.read(8192)
            if not data:
                break
            m.update(data)
        return m.hexdigest()


@app.task(ignore_result=False)
def file_pull_test_8(project_name_en, **kwagrs):
    """
    file_path表示要拉取目录的根路径，比如/data/version_update/client/x/cn
    uuid表示要保存的关于一个工单的文件目录的副本
    update_type表示前后端
    version表示要拉取的具体版本目录
    project_name_en表示副本的项目名

    原来的参数是
    file_path, uuid, update_type, version
    """
    success = False
    msg = ''
    try:
        if project_name_en in ('csxy'):
            list_file = []
            BACKUP_FILE_DIR = '/data/hot_backup'

            # 检查必要的参数
            need_params = ('area_name_en version').split()
            for param in need_params:
                if param not in kwagrs:
                    raise Exception('%s: 获取文件没有%s 参数' % (project_name_en, param))

            # 获取必要的参数
            area_name_en = kwagrs.get('area_name_en')
            version = kwagrs.get('version')
            file_path = kwagrs.get('file_path')
            update_type = kwagrs.get('update_type')
            uuid = kwagrs.get('uuid')

            # 首先检测要copy的版本目录在不在
            from_path = os.path.join(area_name_en, version)

            if os.path.isdir(from_path):
                area_name = os.path.basename(file_path)  # /data/version_update/client/x/cn ==> cn
                # 确定是否已经存在这个目录
                to_path = os.path.join(BACKUP_FILE_DIR, update_type, project_name_en, area_name, uuid, version)
                if os.path.isdir(to_path):
                    shutil.rmtree(to_path)
                shutil.copytree(from_path, to_path)

                # 遍历新的文件目录
                for root, dirs, files in os.walk(to_path):
                    for name in files:
                        file_path = root + '/' + name
                        file_md5 = md5Checksum(file_path)
                        relative_path = file_path[len(to_path) + 1:]
                        file_mtime = os.stat(file_path).st_mtime
                        file_mtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(file_mtime))
                        list_file.append({"file_name": relative_path, 'file_md5': file_md5, 'file_mtime': file_mtime})
                success = True
            else:
                success = False
                msg = '找不到该目录' + from_path

        else:
            list_file = []
            BACKUP_FILE_DIR = '/data/hot_backup'

            # 检查必要的参数
            need_params = ('file_path uuid update_type version').split()
            for param in need_params:
                if param not in kwagrs:
                    raise Exception('%s: 获取文件没有%s 参数' % (project_name_en, param))

            # 获取必要的参数
            file_path = kwagrs.get('file_path')
            update_type = kwagrs.get('update_type')
            uuid = kwagrs.get('uuid')
            version = kwagrs.get('version')
            if type(version).__name__ == 'list':
                version_list = version
            elif type(version).__name__ == 'str':
                version_list = []
                version_list.append(version)
            else:
                raise Exception('未知的版本号类型')

            for version in version_list:
                file_path = kwagrs.get('file_path')
                # 首先检测要copy的版本目录在不在
                if update_type == 'hot_client':
                    hot_files = "hot_files"
                    from_path = os.path.join(file_path, version, hot_files)
                elif update_type == 'hot_server':
                    reloadfiles = 'reloadfiles'
                    from_path = os.path.join(file_path, version, reloadfiles)
                else:
                    raise Exception('未知的热更新类型')
                if os.path.isdir(from_path):
                    area_name = os.path.basename(file_path)  # /data/version_update/client/x/cn ==> cn

                    # 确定是否已经存在这个目录
                    to_path = os.path.join(BACKUP_FILE_DIR, update_type, project_name_en, area_name, uuid, version)
                    if os.path.isdir(to_path):
                        shutil.rmtree(to_path)
                    shutil.copytree(from_path, to_path)

                    # 遍历新的文件目录
                    for root, dirs, files in os.walk(to_path):
                        for name in files:
                            file_path = root + '/' + name
                            file_md5 = md5Checksum(file_path)
                            relative_path = file_path[len(to_path) + 1:]
                            file_mtime = os.stat(file_path).st_mtime
                            file_mtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(file_mtime))
                            list_file.append({"version": version, "file_name": relative_path, 'file_md5': file_md5, 'file_mtime': file_mtime})
                    success = True
                else:
                    raise Exception('找不到该目录' + from_path)

    except Exception as e:
        msg = str(e)
        success = False
    return (success, msg, list_file)


@app.task(ignore_result=True)
def file_push_test_8(project_name_en, **kwagrs):
    """通过rsync模块将本地要同步的文件同步到相应的地方
    为了谨慎起见，在通过的过程中，需要如果方法
    1 首先检测同步的文件是否存在
    2 删除本地不包含在update_file_list中的文件，然后同步整个目录

    update_file_list的格式是[{'file_name': 'xxx', 'file_md5': 'xxxx'}, {}]的格式

    relative_path 是基于update_file_list的文件绝对路径的前缀
    比如update_file_list的一个文件是assets/1.txt
    relative_path为/data/hot_backup/hot_client/ssss/cn/fbb69580-5f0d-44dd-b6bd-1809dfd8ed85/003501000
    那么，完整的路径就是/data/hot_backup/hot_client/ssss/cn/fbb69580-5f0d-44dd-b6bd-1809dfd8ed85/003501000/assets/1.txt
    原来的参数是
    update_file_list, relative_path, version, port, pass_file, user, ip, module, uuid, update_type, content_object_id
    """

    msg = ''
    success = False

    log = RsyncLog()

    try:
        # 将本地的relative_path下面的所有文件转为list
        native_file_list = []

        # 检查必要的参数
        need_params = ('update_file_list relative_path version port pass_file '
                       'user ip module uuid update_type content_object_id').split()

        for param in need_params:
            if param not in kwagrs:
                raise Exception('%s: 获取文件没有%s 参数' % (project_name_en, param))

        # 获取必要的参数
        update_file_list = kwagrs.get('update_file_list')
        relative_path = kwagrs.get('relative_path')
        version = kwagrs.get('version')
        port = kwagrs.get('port')
        pass_file = kwagrs.get('pass_file')
        user = kwagrs.get('user')
        ip = kwagrs.get('ip')
        module = kwagrs.get('module')
        uuid = kwagrs.get('uuid')
        update_type = kwagrs.get('update_type')
        content_object_id = kwagrs.get('content_object_id')

        if not os.path.isdir(relative_path):
            raise Exception('找不到要同步的目录:%s' % (relative_path))

        for root, dirs, files in os.walk(relative_path):
            for name in files:
                native_file_list.append(os.path.join(root, name))

        # 转化update_file_list的格式为list绝对路径
        relative_path_with_version = os.path.join(relative_path, version)
        update_file_list = [os.path.join(relative_path_with_version, x['file_name']) for x in update_file_list]

        # 循环本地的文件，如果该文件不在update_file_list当中，则删除
        for x in native_file_list:
            if x not in update_file_list:
                os.remove(x)

        # 循环要更新的文件，如果该文件不在本地，报错
        for x in update_file_list:
            if x not in native_file_list:
                raise Exception('%s文件没有找到' % (x))

        # 执行rsync的命令
        cmd = """rsync --port=%d -aqz  --password-file=%s \
                --delete %s %s@%s::%s/""" % (port, pass_file, relative_path, user, ip, module)
        log.logger.info('rsync命令:%s' % (cmd))
        # result = os.system(cmd)
        result = local(cmd)
        result.succeeded = True
        # if result == 0:
        if result.succeeded:
            success = True
            log.logger.info('%s:rsync传送文件成功' % (uuid))
        else:
            success = False
            # msg = 'rsync传送文件失败'
            msg = result.stderr or result.stdout

    except Exception as e:
        msg = str(e)
        success = False
        log.logger.error('%s-%s' % (uuid, msg))
    finally:
        # 回调CMDB接口让cmdb执行热更新命令
        log.logger.info('%s开始回调cmdb接口' % (uuid))
        cmdb_callback(msg, success, update_type, content_object_id, uuid, ip)


@app.task(ignore_result=False)
def file_pull_test_15(project_name_en, **kwagrs):
    """
    file_path表示要拉取目录的根路径，比如/data/version_update/client/x/cn
    uuid表示要保存的关于一个工单的文件目录的副本
    update_type表示前后端
    version表示要拉取的具体版本目录
    project_name_en表示副本的项目名

    原来的参数是
    file_path, uuid, update_type, version
    """
    success = False
    msg = ''
    try:
        if project_name_en in ('snqxz', 'jyjh'):
            list_file = []
            BACKUP_FILE_DIR = '/data/hot_backup'

            # 检查必要的参数
            need_params = ('file_path uuid update_type version').split()
            for param in need_params:
                if param not in kwagrs:
                    raise Exception('%s: 获取文件没有%s 参数' % (project_name_en, param))

            # 获取必要的参数
            file_path = kwagrs.get('file_path')
            update_type = kwagrs.get('update_type')
            uuid = kwagrs.get('uuid')
            version = kwagrs.get('version')

            # 首先检测要copy的版本目录在不在
            if update_type == 'hot_client':
                hot_files = "hot_files"
                from_path = os.path.join(file_path, version, hot_files)
            elif update_type == 'hot_server':
                reloadfiles = 'reloadfiles'
                from_path = os.path.join(file_path, version, reloadfiles)
            else:
                raise Exception('未知的热更新类型')
            if os.path.isdir(from_path):
                area_name = os.path.basename(file_path)  # /data/version_update/client/x/cn ==> cn
                # 确定是否已经存在这个目录
                to_path = os.path.join(BACKUP_FILE_DIR, update_type, project_name_en, area_name, uuid, version)
                if os.path.isdir(to_path):
                    shutil.rmtree(to_path)
                shutil.copytree(from_path, to_path)

                # 遍历新的文件目录
                for root, dirs, files in os.walk(to_path):
                    for name in files:
                        file_path = root + '/' + name
                        file_md5 = md5Checksum(file_path)
                        relative_path = file_path[len(to_path) + 1:]
                        list_file.append({"file_name": relative_path, 'file_md5': file_md5})
                success = True
            else:
                success = False
                msg = '找不到该目录'
    except Exception as e:
        msg = str(e)
        success = False
    return (success, msg, list_file)


@app.task(ignore_result=False)
def file_pull_test_cc(project_name_en, **kwagrs):
    """
    file_path表示要拉取目录的根路径，比如/data/version_update/client/x/cn
    uuid表示要保存的关于一个工单的文件目录的副本
    update_type表示前后端
    version表示要拉取的具体版本目录
    project_name_en表示副本的项目名

    原来的参数是
    file_path, uuid, update_type, version
    """
    success = False
    msg = ''
    try:
        if project_name_en in ('mjfz',):
            list_file = []
            BACKUP_FILE_DIR = '/data/hot_backup'

            # 检查必要的参数
            need_params = ('file_path uuid update_type version').split()
            for param in need_params:
                if param not in kwagrs:
                    raise Exception('%s: 获取文件没有%s 参数' % (project_name_en, param))

            # 获取必要的参数
            file_path = kwagrs.get('file_path')
            update_type = kwagrs.get('update_type')
            uuid = kwagrs.get('uuid')
            version = kwagrs.get('version')

            # 首先检测要copy的版本目录在不在
            if update_type == 'hot_client':
                hot_files = "hot_files"
                from_path = os.path.join(file_path, version, hot_files)
            elif update_type == 'hot_server':
                reloadfiles = 'reloadfiles'
                from_path = os.path.join(file_path, version, reloadfiles)
            else:
                raise Exception('未知的热更新类型')
            if os.path.isdir(from_path):
                area_name = os.path.basename(file_path)  # /data/version_update/client/x/cn ==> cn
                # 确定是否已经存在这个目录
                to_path = os.path.join(BACKUP_FILE_DIR, update_type, project_name_en, area_name, uuid, version)
                if os.path.isdir(to_path):
                    shutil.rmtree(to_path)
                shutil.copytree(from_path, to_path)

                # 遍历新的文件目录
                for root, dirs, files in os.walk(to_path):
                    for name in files:
                        file_path = root + '/' + name
                        file_md5 = md5Checksum(file_path)
                        relative_path = file_path[len(to_path) + 1:]
                        list_file.append({"file_name": relative_path, 'file_md5': file_md5})
                success = True
            else:
                success = False
                msg = '找不到该目录'
    except Exception as e:
        msg = str(e)
        success = False
    return (success, msg, list_file)


@app.task(ignore_result=False)
def file_pull_test_slqy3d_cn(project_name_en, **kwagrs):
    """
    file_path表示要拉取目录的根路径，比如/data/version_update/client/x/cn
    uuid表示要保存的关于一个工单的文件目录的副本
    update_type表示前后端
    version表示要拉取的具体版本目录
    project_name_en表示副本的项目名

    原来的参数是
    file_path, uuid, update_type, version
    """
    success = False
    msg = ''
    try:
        if project_name_en in ('mjfz',):
            list_file = []
            BACKUP_FILE_DIR = '/data/hot_backup'

            # 检查必要的参数
            need_params = ('file_path uuid update_type version').split()
            for param in need_params:
                if param not in kwagrs:
                    raise Exception('%s: 获取文件没有%s 参数' % (project_name_en, param))

            # 获取必要的参数
            file_path = kwagrs.get('file_path')
            update_type = kwagrs.get('update_type')
            uuid = kwagrs.get('uuid')
            version = kwagrs.get('version')

            # 首先检测要copy的版本目录在不在
            if update_type == 'hot_client':
                hot_files = "hot_files"
                from_path = os.path.join(file_path, version, hot_files)
            elif update_type == 'hot_server':
                reloadfiles = 'reloadfiles'
                from_path = os.path.join(file_path, version, reloadfiles)
            else:
                raise Exception('未知的热更新类型')
            if os.path.isdir(from_path):
                area_name = os.path.basename(file_path)  # /data/version_update/client/x/cn ==> cn
                # 确定是否已经存在这个目录
                to_path = os.path.join(BACKUP_FILE_DIR, update_type, project_name_en, area_name, uuid, version)
                if os.path.isdir(to_path):
                    shutil.rmtree(to_path)
                shutil.copytree(from_path, to_path)

                # 遍历新的文件目录
                for root, dirs, files in os.walk(to_path):
                    for name in files:
                        file_path = root + '/' + name
                        file_md5 = md5Checksum(file_path)
                        relative_path = file_path[len(to_path) + 1:]
                        list_file.append({"file_name": relative_path, 'file_md5': file_md5})
                success = True
            else:
                success = False
                msg = '找不到该目录'
    except Exception as e:
        msg = str(e)
        success = False
    return (success, msg, list_file)


@app.task(ignore_result=True)
def file_push_test_15(project_name_en, **kwagrs):
    """通过rsync模块将本地要同步的文件同步到相应的地方
    为了谨慎起见，在通过的过程中，需要如果方法
    1 首先检测同步的文件是否存在
    2 删除本地不包含在update_file_list中的文件，然后同步整个目录

    update_file_list的格式是[{'file_name': 'xxx', 'file_md5': 'xxxx'}, {}]的格式

    relative_path 是基于update_file_list的文件绝对路径的前缀
    比如update_file_list的一个文件是assets/1.txt
    relative_path为/data/hot_backup/hot_client/ssss/cn/fbb69580-5f0d-44dd-b6bd-1809dfd8ed85/003501000
    那么，完整的路径就是/data/hot_backup/hot_client/ssss/cn/fbb69580-5f0d-44dd-b6bd-1809dfd8ed85/003501000/assets/1.txt
    原来的参数是
    update_file_list, relative_path, version, port, pass_file, user, ip, module, uuid, update_type, content_object_id
    """

    msg = ''
    success = False

    log = RsyncLog()

    try:
        # 这里根据不同的项目来做推送方式
        if project_name_en in ('snqxz', 'jyjh'):
            # 将本地的relative_path下面的所有文件转为list
            native_file_list = []

            # 检查必要的参数
            need_params = ('update_file_list relative_path version port pass_file '
                           'user ip module uuid update_type content_object_id').split()

            for param in need_params:
                if param not in kwagrs:
                    raise Exception('%s: 获取文件没有%s 参数' % (project_name_en, param))

            # 获取必要的参数
            update_file_list = kwagrs.get('update_file_list')
            relative_path = kwagrs.get('relative_path')
            version = kwagrs.get('version')
            port = kwagrs.get('port')
            pass_file = kwagrs.get('pass_file')
            user = kwagrs.get('user')
            ip = kwagrs.get('ip')
            module = kwagrs.get('module')
            uuid = kwagrs.get('uuid')
            update_type = kwagrs.get('update_type')
            content_object_id = kwagrs.get('content_object_id')

            if not os.path.isdir(relative_path):
                raise Exception('找不到要同步的目录:%s' % (relative_path))

            for root, dirs, files in os.walk(relative_path):
                for name in files:
                    native_file_list.append(os.path.join(root, name))

            # 转化update_file_list的格式为list绝对路径
            relative_path_with_version = os.path.join(relative_path, version)
            update_file_list = [os.path.join(relative_path_with_version, x['file_name']) for x in update_file_list]

            # 循环本地的文件，如果该文件不在update_file_list当中，则删除
            for x in native_file_list:
                if x not in update_file_list:
                    os.remove(x)

            # 循环要更新的文件，如果该文件不在本地，报错
            for x in update_file_list:
                if x not in native_file_list:
                    raise Exception('%s文件没有找到' % (x))

            # 执行rsync的命令
            cmd = """rsync --port=%d -aqz  --password-file=%s \
                    --delete %s %s@%s::%s/""" % (port, pass_file, relative_path, user, ip, module)
            log.logger.info('rsync命令:%s' % (cmd))
            # result = os.system(cmd)
            result = local(cmd)
            # if result == 0:
            if result.succeeded:
                success = True
                log.logger.info('%s:rsync传送文件成功' % (uuid))
            else:
                success = False
                # msg = 'rsync传送文件失败'
                msg = result.stderr or result.stdout
    except Exception as e:
        msg = str(e)
        success = False
        log.logger.error('%s-%s' % (uuid, msg))
    finally:
        # 回调CMDB接口让cmdb执行热更新命令
        log.logger.info('%s开始回调cmdb接口' % (uuid))
        cmdb_callback(msg, success, update_type, content_object_id, uuid)


@app.task(ignore_result=True)
def file_push_test_cc(project_name_en, **kwagrs):
    """通过rsync模块将本地要同步的文件同步到相应的地方
    为了谨慎起见，在通过的过程中，需要如果方法
    1 首先检测同步的文件是否存在
    2 删除本地不包含在update_file_list中的文件，然后同步整个目录

    update_file_list的格式是[{'file_name': 'xxx', 'file_md5': 'xxxx'}, {}]的格式

    relative_path 是基于update_file_list的文件绝对路径的前缀
    比如update_file_list的一个文件是assets/1.txt
    relative_path为/data/hot_backup/hot_client/ssss/cn/fbb69580-5f0d-44dd-b6bd-1809dfd8ed85/003501000
    那么，完整的路径就是/data/hot_backup/hot_client/ssss/cn/fbb69580-5f0d-44dd-b6bd-1809dfd8ed85/003501000/assets/1.txt
    原来的参数是
    update_file_list, relative_path, version, port, pass_file, user, ip, module, uuid, update_type, content_object_id
    """

    msg = ''
    success = False

    log = RsyncLog()

    try:
        # 这里根据不同的项目来做推送方式
        if project_name_en in ('mjfz',):
            # 将本地的relative_path下面的所有文件转为list
            native_file_list = []

            # 检查必要的参数
            need_params = ('update_file_list relative_path version port pass_file '
                           'user ip module uuid update_type content_object_id').split()

            for param in need_params:
                if param not in kwagrs:
                    raise Exception('%s: 获取文件没有%s 参数' % (project_name_en, param))

            # 获取必要的参数
            update_file_list = kwagrs.get('update_file_list')
            relative_path = kwagrs.get('relative_path')
            version = kwagrs.get('version')
            port = kwagrs.get('port')
            pass_file = kwagrs.get('pass_file')
            user = kwagrs.get('user')
            ip = kwagrs.get('ip')
            module = kwagrs.get('module')
            uuid = kwagrs.get('uuid')
            update_type = kwagrs.get('update_type')
            content_object_id = kwagrs.get('content_object_id')

            if not os.path.isdir(relative_path):
                raise Exception('找不到要同步的目录:%s' % (relative_path))

            for root, dirs, files in os.walk(relative_path):
                for name in files:
                    native_file_list.append(os.path.join(root, name))

            # 转化update_file_list的格式为list绝对路径
            relative_path_with_version = os.path.join(relative_path, version)
            update_file_list = [os.path.join(relative_path_with_version, x['file_name']) for x in update_file_list]

            # 循环本地的文件，如果该文件不在update_file_list当中，则删除
            for x in native_file_list:
                if x not in update_file_list:
                    os.remove(x)

            # 循环要更新的文件，如果该文件不在本地，报错
            for x in update_file_list:
                if x not in native_file_list:
                    raise Exception('%s文件没有找到' % (x))

            # 执行rsync的命令
            cmd = """rsync --port=%d -aqz  --password-file=%s \
                    --delete %s %s@%s::%s/""" % (port, pass_file, relative_path, user, ip, module)
            log.logger.info('rsync命令:%s' % (cmd))
            # result = os.system(cmd)
            result = local(cmd)
            # if result == 0:
            if result.succeeded:
                success = True
                log.logger.info('%s:rsync传送文件成功' % (uuid))
            else:
                success = False
                # msg = 'rsync传送文件失败'
                msg = result.stderr or result.stdout
    except Exception as e:
        msg = str(e)
        success = False
        log.logger.error('%s-%s' % (uuid, msg))
    finally:
        # 回调CMDB接口让cmdb执行热更新命令
        log.logger.info('%s开始回调cmdb接口' % (uuid))
        cmdb_callback(msg, success, update_type, content_object_id, uuid)


@app.task(ignore_result=True)
def file_push_test_slqy3d_cn(project_name_en, **kwagrs):
    """通过rsync模块将本地要同步的文件同步到相应的地方
    为了谨慎起见，在通过的过程中，需要如果方法
    1 首先检测同步的文件是否存在
    2 删除本地不包含在update_file_list中的文件，然后同步整个目录

    update_file_list的格式是[{'file_name': 'xxx', 'file_md5': 'xxxx'}, {}]的格式

    relative_path 是基于update_file_list的文件绝对路径的前缀
    比如update_file_list的一个文件是assets/1.txt
    relative_path为/data/hot_backup/hot_client/ssss/cn/fbb69580-5f0d-44dd-b6bd-1809dfd8ed85/003501000
    那么，完整的路径就是/data/hot_backup/hot_client/ssss/cn/fbb69580-5f0d-44dd-b6bd-1809dfd8ed85/003501000/assets/1.txt
    原来的参数是
    update_file_list, relative_path, version, port, pass_file, user, ip, module, uuid, update_type, content_object_id
    """

    msg = ''
    success = False

    log = RsyncLog()

    try:
        # 这里根据不同的项目来做推送方式
        if project_name_en in ('mjfz',):
            # 将本地的relative_path下面的所有文件转为list
            native_file_list = []

            # 检查必要的参数
            need_params = ('update_file_list relative_path version port pass_file '
                           'user ip module uuid update_type content_object_id').split()

            for param in need_params:
                if param not in kwagrs:
                    raise Exception('%s: 获取文件没有%s 参数' % (project_name_en, param))

            # 获取必要的参数
            update_file_list = kwagrs.get('update_file_list')
            relative_path = kwagrs.get('relative_path')
            version = kwagrs.get('version')
            port = kwagrs.get('port')
            pass_file = kwagrs.get('pass_file')
            user = kwagrs.get('user')
            ip = kwagrs.get('ip')
            module = kwagrs.get('module')
            uuid = kwagrs.get('uuid')
            update_type = kwagrs.get('update_type')
            content_object_id = kwagrs.get('content_object_id')

            if not os.path.isdir(relative_path):
                raise Exception('找不到要同步的目录:%s' % (relative_path))

            for root, dirs, files in os.walk(relative_path):
                for name in files:
                    native_file_list.append(os.path.join(root, name))

            # 转化update_file_list的格式为list绝对路径
            relative_path_with_version = os.path.join(relative_path, version)
            update_file_list = [os.path.join(relative_path_with_version, x['file_name']) for x in update_file_list]

            # 循环本地的文件，如果该文件不在update_file_list当中，则删除
            for x in native_file_list:
                if x not in update_file_list:
                    os.remove(x)

            # 循环要更新的文件，如果该文件不在本地，报错
            for x in update_file_list:
                if x not in native_file_list:
                    raise Exception('%s文件没有找到' % (x))

            # 执行rsync的命令
            cmd = """rsync --port=%d -aqz  --password-file=%s \
                    --delete %s %s@%s::%s/""" % (port, pass_file, relative_path, user, ip, module)
            log.logger.info('rsync命令:%s' % (cmd))
            # result = os.system(cmd)
            result = local(cmd)
            # if result == 0:
            if result.succeeded:
                success = True
                log.logger.info('%s:rsync传送文件成功' % (uuid))
            else:
                success = False
                # msg = 'rsync传送文件失败'
                msg = result.stderr or result.stdout
    except Exception as e:
        msg = str(e)
        success = False
        log.logger.error('%s-%s' % (uuid, msg))
    finally:
        # 回调CMDB接口让cmdb执行热更新命令
        log.logger.info('%s开始回调cmdb接口' % (uuid))
        cmdb_callback(msg, success, update_type, content_object_id, uuid)


def cmdb_callback(msg, success, update_type, content_object_id, uuid, ops_ip):
    try:
        log = RsyncLog()
        url = 'http://127.0.0.1:8000/api/RsyncOnFinishedCallBack/'
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Token c6e7724396561cfd9004718330fc8a6dcbaf6409'
        }
        payload = {
            'msg': msg,
            'success': success,
            'update_type': update_type,
            'content_object_id': content_object_id,
            'uuid': uuid,
            'ops_ip': ops_ip
        }

        r = requests.post(url, headers=headers, data=payload, timeout=15, verify=False)
        log.logger.info(r)
    except Exception as e:
        log.logger.error('回调cmdb失败-%s' % (str(e)))


def client_hotupdate_callback(uuid, client_version, client_task):
    success = True
    msg = 'ok'
    try:
        log = HotUpdateLog(uuid)
        content = client_task.content
        post_data = [
            {'cdn_root_url': x['cdn_root_url'], 'cdn_dir': x['cdn_dir'], 'status': True} for x in json.loads(content)
        ]
        url = 'http://127.0.0.1:8000/api/hotupdateCallBack/'
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Token 7c166721ab00350894172405c1b8bc0cce102b00'
        }
        data = {
            'update_type': 'hot_client',
            'data': post_data,
            'uuid': uuid,
            'version': client_version
        }
        data = json.dumps(data)
        res = requests.post(url, json=data, headers=headers, timeout=60, verify=False)
        if res.status_code == 200:
            r = res.json()
            if r['resp'] == 0:
                pass
            else:
                log.logger.info(r)
        else:
            log.logger.info(res)
    except Exception as e:
        msg = str(e)
        success = False
        log.logger.error('回调cmdb失败-%s' % (str(e)))
    finally:
        return JsonResponse({'success': success, 'msg': msg})


def server_hotupdate_callback(uuid, server_version, server_task):
    try:
        log = HotUpdateLog(uuid)
        update_server_list = json.loads(server_task.update_server_list)
        result_data = {}
        for x in update_server_list:
            if x['ip'] not in result_data.keys():
                update_data = {}
                ip = x['ip']
                srv_id = x['srv_id']
                update_data[srv_id] = {"data": "更新成功", "status": True}
                result_data[ip] = {'update_data': update_data}
            else:
                ip = x['ip']
                srv_id = x['srv_id']
                update_data = result_data[ip]['update_data']
                update_data[srv_id] = {"data": "更新成功", "status": True}
                result_data[ip]['update_data'] = update_data
        log.logger.info(result_data)
        url = 'http://127.0.0.1:8000/api/HotServerCallBack/'
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Token 7c166721ab00350894172405c1b8bc0cce102b00'
        }
        data = {
            'update_type': 'hot_server',
            'ip': result_data,
            'uuid': uuid,
            'version': server_version,
        }
        data = json.dumps(data)
        res = requests.post(url, json=data, headers=headers, timeout=60, verify=False)
        if res.status_code == 200:
            r = res.json()
            if r['resp'] == 0:
                pass
            else:
                log.logger.info(r)
        else:
            log.logger.info(res)
    except Exception as e:
        log.logger.error('回调cmdb失败-%s' % (str(e)))


def server_hotupdate_callback_on_finish(uuid, server_version):
    try:
        log = HotUpdateLog(uuid)
        url = 'http://127.0.0.1:8000/api/HotServerOnFinishedCallBack/'
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Token 7c166721ab00350894172405c1b8bc0cce102b00'
        }
        data = {
            "final_result": True,
            "final_data": "全部完成",
            "uuid": uuid,
            "update_type": "hot_server",
            "version": server_version,
        }
        data = json.dumps(data)
        res = requests.post(url, json=data, headers=headers, timeout=60, verify=False)
        if res.status_code == 200:
            r = res.json()
            if r['resp'] == 0:
                pass
            else:
                log.logger.info(r)
        else:
            log.logger.info(res)
    except Exception as e:
        log.logger.error('回调cmdb失败-%s' % (str(e)))


def format_hot_client_data(content, uuid, client_type, update_file_list, version):
    """构造前端热更新数据
    content的数据格式：
    [
        {
            "cdn_dir": "qq_s1", "area_name": "大陆", "cdn_root_url": "res.qxz.zhi-ming.com",
            "client_version": "008400000", "id": 44554, "project": 24
        }
    ]
    ==============>
    需要的数据格式为
    {
        'update_type': 'hot_client',
        'client_type': 0 or 1,
        'data': [
            {'cdn_root_url': 'res.ssss.chuangyunet.com', 'cdn_dir': 't1', 'version': 'axxx_13342', 'client_type': 'cn_ios'},
            {'cdn_root_url': 'res.ssss.chuangyunet.com', 'cdn_dir': 'test_r1'},
            {'cdn_root_url': 'res.ssss.chuangyunet.com', 'cdn_dir': 's1'},
            {'cdn_root_url': 'res.ssss.chuangyunet.com', 'cdn_dir': 'r1'}
        ],
        'uuid': 'xxx',
        'version': '003100000',
        'update_file_list': [
            {'file_name': 'a.txt', 'file_md5': abe347d3fdff45f1078102c4637852a5},
            {'file_name': 'b.txt', 'file_md5': 5724c05c650550ac8034129ad7a4d915}
        ]
    }
    """
    hot_client_data = {}
    hot_client_data['update_type'] = 'hot_client'
    hot_client_data['client_type'] = client_type
    hot_client_data['data'] = content
    hot_client_data['uuid'] = uuid
    hot_client_data['version'] = version
    hot_client_data['update_file_list'] = update_file_list

    return hot_client_data


@app.task(ignore_result=True)
def do_test_hot_client(content_object_id):
    """发送前端热更新请求到管理机
    走本地的celery worker
    """
    try:
        # cmdb上面的错误 用于cmdb出错以后发送邮件报警
        CMDB_ERROR = False
        content_object = ClientHotUpdate.objects.get(id=content_object_id)
        hot_update_log = HotUpdateLog(content_object.uuid)

        # 首先去检查lock项目和地区，如果lock失败，直接引发一个异常
        """2019.3修改，运维管理机通过工单子任务表RsyncTask来获取"""
        list_ops_manager_id = [x.ops_id for x in content_object.clienthotupdatersynctask_set.all()]
        """找到其他url相同的运维管理机，事实为同一台管理机，一起上锁"""
        all_list_ops_manager_id = []
        for ops_id in list_ops_manager_id:
            ops_obj = OpsManager.objects.get(pk=ops_id)
            url = ops_obj.url
            for x in OpsManager.objects.filter(url__icontains=url):
                all_list_ops_manager_id.append(x.id)
        list_ops_manager = OpsManager.objects.filter(id__in=all_list_ops_manager_id)
        list_ops_manager_status = [x.status for x in list_ops_manager]

        if not (len(list(set(list_ops_manager_status))) == 1 and '0' in list_ops_manager_status):
            content_object.status = '4'
            content_object.save()
            raise HotUpdateBlock('%s: 项目和地区已经被锁,进入待更新状态' % content_object.title)
            # hot_update_log.logger.info('%s: 项目和地区已经被锁,进入待更新状态' % (content_object.title))
        else:
            # lock
            hot_update_log.logger.info('%s: 开始执行' % content_object.title)
            update_status = {'status': '2'}
            list_ops_manager.update(**update_status)
            hot_update_log.logger.info('hot_client: %s-成功上锁' % content_object.title)

            """
            2019.3修改
            遍历热更新的子任务，依次发送对应的热更新数据到相应的运维管理机
            """
            for task in content_object.clienthotupdatersynctask_set.all():
                content = json.loads(task.content)
                update_file_list = json.loads(task.update_file_list)
                update_file_list = format_hot_update_file_list(update_file_list, 'area_dir')

                hot_client_data = format_hot_client_data(
                    content, content_object.uuid, content_object.client_type, update_file_list,
                    content_object.client_version)

                # 获取运维管理机
                ops_manager = task.ops

                # 发送前端热更新数据给运维管理机
                url = ops_manager.url + CLIENT_HOT
                token = ops_manager.token
                authorized_token = "Token " + token

                headers = {
                    'Accept': 'application/json',
                    'Authorization': authorized_token,
                    'Connection': 'keep-alive',
                }

                s = Session()
                s.mount('https://', HTTPAdapter(max_retries=Retry(total=3, status_forcelist=[408])))
                # r = s.post(url, headers=headers, json=hot_client_data, verify=False, timeout=10)
                # result = r.json()
                result = {'Accepted': True}
                if result.get('Accepted', False):
                    hot_update_log.logger.info('hot_client: %s-发送消息到管理机%s成功' % (content_object.title, ops_manager))
                else:
                    content_object.status = '2'
                    content_object.save()
                    hot_update_log.logger.error('hot_client: %s-发送消息到管理机%s失败' % (content_object.title, ops_manager))
                    raise Exception('hot_client: %s-发送消息到管理机%s失败' % (content_object.title, ops_manager))

    except OpsManager.DoesNotExist:
        msg = 'hot_client: ops manager not found'
        hot_update_log.logger.error('%s' % msg)
        content_object.status = '2'
        content_object.save()
        CMDB_ERROR = True
    except requests.exceptions.ConnectionError:
        content_object.status = '2'
        content_object.save()
        CMDB_ERROR = True
        hot_update_log.logger.error('hot_client: %s: %s time out' % (content_object.title, url))
    except GameProject.DoesNotExist:
        msg = 'hot_client: game project not found'
        hot_update_log.logger.error('%s' % msg)
        content_object.status = '2'
        content_object.save()
        CMDB_ERROR = True
    except Room.DoesNotExist:
        msg = 'hot_client: room not found'
        hot_update_log.logger.error('%s' % (msg))
        content_object.status = '2'
        content_object.save()
        CMDB_ERROR = True
    except HotUpdateBlock as e:
        msg = str(e)
        hot_update_log.logger.error('%s' % (msg))
        CMDB_ERROR = True
    except Exception as e:
        msg = str(e)
        hot_update_log.logger.error('%s' % (msg))
        content_object.status = '2'
        content_object.save()
        CMDB_ERROR = True
    finally:
        # 通知客户端刷新状态
        content_object.save()
        ws_notify()

        if CMDB_ERROR:
            pass
        for task in content_object.clienthotupdatersynctask_set.all():
            client_hotupdate_callback(uuid=content_object.uuid, client_version=content_object.client_version,
                                      client_task=task)


def format_hot_server_data(update_server_list):
    """构造热更新后端数据
    数据库中的json格式:
    [
        {'gtype': 'game', 'srv_id': '37_1', 'pf_name': '37', 'ip': '10.104.104.36', 'srv_name': 'S1'},
        {'gtype': 'game', 'srv_id': '37_2', 'pf_name': '37', 'ip': '10.135.44.1', 'srv_name': 'S2'},
        {'gtype': 'game', 'srv_id': '37_3', 'pf_name': '37', 'ip': '10.186.0.163', 'srv_name': 'S3'},
        {'gtype': 'game', 'srv_id': '360_2', 'pf_name': '360', 'ip': '10.135.185.108', 'srv_name': 'S2'},
        {'gtype': 'game', 'srv_id': '360_3', 'pf_name': '360', 'ip': '10.135.58.58', 'srv_name': 'S3'},
        {'gtype': 'cross', 'srv_id': 'sogou_1', 'pf_name': 'sogou', 'ip': '10.135.117.44', 'srv_name': 'cross_sogou_1'},
        {'gtype': 'cross', 'srv_id': 'sogou_2', 'pf_name': 'sogou', 'ip': '10.104.227.20', 'srv_name': 'cross_sogou_2'},
        {'gtype': 'cross_center', 'srv_id': 'sogou', 'pf_name': 'sogou', 'ip': '10.104.107.56', 'srv_name': 'sogou'}
    ]
    ==========================================>>
    "update_server_list": {
        "game": {
            "10.1.1.1": ['qq_1', 'qq_2'],
            "10.1.1.2": ['qq_3', 'qq_4'],
        },
        "cross": {
            "192.168.1.1": ['cross_1', 'corss_2'],
            "192.168.1.3": ['cross_3', 'corss_4'],
        },
        "cross_center": {
            "172.17.26.12": ['center_1', 'center_2'],
            "172.17.26.15": ['center_4', 'center_6'],
        }
    },
    """

    new_update_server_list = defaultdict(lambda: defaultdict(list))

    for server in update_server_list:
        game_type = server.get('gtype', 'unknow')
        ip = server.get('ip', 'unknow')
        srv_id = server.get('srv_id', 'unknow')
        new_update_server_list[game_type][ip].append(srv_id)

    return new_update_server_list


@app.task(ignore_result=True)
def do_test_hot_server(content_object_id):
    """执行热更新后端
    """
    content_object = ServerHotUpdate.objects.get(id=content_object_id)
    hot_update_log = HotUpdateLog(content_object.uuid)
    try:
        # cmdb上面的错误 用于cmdb出错以后发送邮件报警
        CMDB_ERROR = False
        # 首先去检查lock项目和地区，如果lock失败，直接引发一个异常
        """2019.3修改，运维管理机通过工单子任务表RsyncTask来获取"""
        list_ops_manager_id = [x.ops_id for x in content_object.serverhotupdatersynctask_set.all()]
        """找到其他url相同的运维管理机，事实为同一台管理机，一起上锁"""
        all_list_ops_manager_id = []
        for ops_id in list_ops_manager_id:
            ops_obj = OpsManager.objects.get(pk=ops_id)
            url = ops_obj.url
            for x in OpsManager.objects.filter(url__icontains=url):
                all_list_ops_manager_id.append(x.id)
        list_ops_manager = OpsManager.objects.filter(id__in=all_list_ops_manager_id)
        list_ops_manager_status = [x.status for x in list_ops_manager]

        if not (len(list(set(list_ops_manager_status))) == 1 and '0' in list_ops_manager_status):
            content_object.status = '4'
            content_object.save()
            task = content_object.serverhotupdatersynctask_set.all()
            task.update(**{'rsync_result': None})
            raise HotUpdateBlock('%s: 项目和地区已经被锁,进入待更新状态' % (content_object.title))
            # hot_update_log.logger.info('%s: 项目和地区已经被锁,进入待更新状态' % (content_object.title))
        else:
            # lock
            hot_update_log.logger.info('%s: 开始执行' % (content_object.title))
            update_status = {'status': '2'}
            list_ops_manager.update(**update_status)
            hot_update_log.logger.info('hot_server: %s-成功上锁' % (content_object.title))

            # 进行一次区服的数据校验（增加新服）
            revise_server_list(content_object)

            """区服数据校验后，重新更新子任务对应的区服数据"""
            update_server_list = json.loads(content_object.update_server_list)
            for update_server in update_server_list:
                game_server_id = update_server['gameserverid']
                game_server = GameServer.objects.get(pk=int(game_server_id))
                ops = game_server.host.opsmanager
                if ops:
                    """判断管理机对应的子任务是否已存在，是则更新字段，否则创建子任务"""
                    task = ServerHotUpdateRsyncTask.objects.filter(server_hot_update=content_object, ops=ops)
                    if task:
                        task_update_server_list = json.loads(task[0].update_server_list)
                        if update_server not in task_update_server_list:
                            task_update_server_list.append(update_server)
                        task_update_server_list = json.dumps(task_update_server_list)
                        task.update(**{"update_server_list": task_update_server_list})

            # 修改final_result最终结果为None
            content_object.final_result = None

            # 复制update_server_list到result_update_file_list
            result_update_file_list = content_object.update_server_list
            content_object.result_update_file_list = result_update_file_list
            content_object.save()
            hot_update_log.logger.info('hot_server: %s-复制数据成功' % (content_object.title))

            # 加载热更新区服列表到redis中
            load_to_redis(content_object)
            hot_update_log.logger.info('hot_server: %s-将数据load到redis成功' % (content_object.title))

            """
            2019.3修改，遍历热更新子任务，发送对应的更新区服数据到对应的运维管理机
            """
            for task in content_object.serverhotupdatersynctask_set.all():
                # 热更新后端数据
                update_server_list = format_hot_server_data(json.loads(task.update_server_list))

                # 获取运维管理机
                ops_manager = task.ops

                url = ops_manager.url + CLIENT_HOT
                token = ops_manager.token
                authorized_token = "Token " + token
                headers = {
                    'Accept': 'application/json',
                    'Authorization': authorized_token,
                    'Connection': 'keep-alive',
                }

                # 后端热更新需要post的数据
                hot_server_data = {}

                hot_server_data['uuid'] = content_object.uuid
                hot_server_data['update_type'] = 'hot_server'
                hot_server_data['update_server_list'] = update_server_list
                hot_server_data['version'] = content_object.server_version
                hot_server_data['hot_server_type'] = content_object.hot_server_type
                if content_object.erlang_cmd_list:
                    hot_server_data['erlang_cmd_list'] = content_object.erlang_cmd_list.split('\n')
                else:
                    hot_server_data['erlang_cmd_list'] = []

                if content_object.update_file_list:
                    hot_server_data['update_file_list'] = format_hot_update_file_list(json.loads(task.update_file_list),
                                                                                      'area_dir')
                else:
                    hot_server_data['update_file_list'] = []

                    # r = requests.post(url, headers=headers, json=hot_server_data, verify=False, timeout=30)
                s = Session()
                s.mount('https://', HTTPAdapter(max_retries=Retry(total=3, status_forcelist=[408])))
                # r = s.post(url, headers=headers, json=hot_server_data, verify=False, timeout=10)
                # result = r.json()
                result = {"Accepted": True}
                if result.get('Accepted', False):
                    hot_update_log.logger.info('hot_server: %s-发送消息到管理机%s成功' % (content_object.title, ops_manager))
                    server_hotupdate_callback(content_object.uuid, content_object.server_version, task)
                else:
                    hot_update_log.logger.error('hot_server: %s-发送消息到管理机%s失败' % (content_object.title, ops_manager))
                    raise Exception('hot_server: %s-发送消息到管理机%s失败' % (content_object.title, ops_manager))
            server_hotupdate_callback_on_finish(content_object.uuid, content_object.server_version)

    except OpsManager.DoesNotExist:
        msg = 'hot_server: 项目%s-地区%s没有找到运维管理机' % (content_object.project.project_name, content_object.area_name)
        hot_update_log.logger.error('%s' % (msg))
        content_object.status = '2'
        content_object.save()
        task = content_object.serverhotupdatersynctask_set.all()
        task.update(**{'rsync_result': None})
        CMDB_ERROR = True
    except requests.exceptions.ConnectionError:
        content_object.status = '2'
        content_object.save()
        task = content_object.serverhotupdatersynctask_set.all()
        task.update(**{'rsync_result': None})
        CMDB_ERROR = True
        hot_update_log.logger.error('hot_server: %s: %s time out' % (content_object.title, url))
    except HotUpdateBlock as e:
        msg = str(e)
        hot_update_log.logger.error('%s' % (msg))
        CMDB_ERROR = True
    except Exception as e:
        msg = 'hot_server: ' + str(e)
        hot_update_log.logger.error('%s' % (msg))
        content_object.status = '2'
        content_object.save()
        task = content_object.serverhotupdatersynctask_set.all()
        task.update(**{'rsync_result': None})
        CMDB_ERROR = True
    finally:
        ws_notify()
