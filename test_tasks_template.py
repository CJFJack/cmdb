# -*- encoding: utf-8 -*-

from celery import Celery

app = Celery()

import test_celeryconfig

app.config_from_object(test_celeryconfig)

# from myworkflows.mails import SendEmail
# from myworkflows.mails import RecieveMail

import shutil
import os
import hashlib
import logging
import subprocess
import requests
from datetime import datetime


class RsyncLog(object):
    """热更新前后端log"""

    def __init__(self):
        # create logger
        self.logger = logging.getLogger('rsync-test-log')
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
    except Exception as e:
        out = _AttributeString("do %s is error" % (cmd))
        err = _AttributeString(str(e))
        out.cmd = cmd
        out.stderr = err
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
    msg = ''
    success = False

    try:
        if project_name_en in ('snqxz', 'jyjh', 'ssss'):
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
                area_name = os.path.basename(file_path)    # /data/version_update/client/x/cn ==> cn
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
                        file_mtime = datetime.fromtimestamp(
                            os.path.getmtime(os.path.join(from_path, relative_path))).strftime('%Y-%m-%d %H:%M')
                        list_file.append({"file_name": relative_path, 'file_md5': file_md5, 'file_mtime': file_mtime})
                success = True
            else:
                success = False
                msg = '找不到该目录'
        elif project_name_en in ('csxy'):
            list_file = []
            # 需要执行一个脚本
            # sh /data/version_update/server/csxy/cn/20180404/logic/shell/upcode.sh
            # 检查必要的参数
            need_params = ('area_name_en version').split()
            for param in need_params:
                if param not in kwagrs:
                    raise Exception('%s: 获取文件没有%s 参数' % (project_name_en, param))

            # 获取必要的参数
            area_name_en = kwagrs.get('area_name_en')
            version = kwagrs.get('version')

            pre_dir = '/data/version_update/server/csxy/'
            script_path = os.path.join(pre_dir, area_name_en, version, 'logic/shell/upcode.sh')
            file_md5 = md5Checksum(script_path)
            file_mtime = datetime.fromtimestamp(os.path.getmtime(script_path)).strftime('%Y-%m-%d %H:%M')

            cmd = "sh %s" % (script_path)
            result = local(cmd)

            if result.succeeded:
                success = True
            else:
                success = False

            file_name = result.stdout or result.stderr
            list_file.append({'file_name': file_name, 'file_md5': file_md5, 'file_mtime': file_mtime})
        else:
            raise Exception('没有配置获取热更新文件项目')
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
        # 这里根据不同的项目来做推送方式
        if project_name_en in ('snqxz', 'jyjh', 'ssss'):
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
        else:
            raise Exception('沒有配置热更新项目推送')
    except Exception as e:
        msg = str(e)
        success = False
        log.logger.error('%s-%s' % (uuid, msg))
    finally:
        # 回调CMDB接口让cmdb执行热更新命令
        log.logger.info('%s开始回调cmdb接口' % (uuid))
        cmdb_callback(msg, success, update_type, content_object_id, uuid)


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
        if project_name_en in ('snqxz', 'jyjh', 'ssss'):
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
        else:
            raise Exception('沒有配置热更新项目推送')
    except Exception as e:
        msg = str(e)
        success = False
        log.logger.error('%s-%s' % (uuid, msg))
    finally:
        # 回调CMDB接口让cmdb执行热更新命令
        log.logger.info('%s开始回调cmdb接口' % (uuid))
        cmdb_callback(msg, success, update_type, content_object_id, uuid)


def cmdb_callback(msg, success, update_type, content_object_id, uuid):

    try:
        log = RsyncLog()
        url = 'http://192.168.90.181:8089/api/RsyncOnFinishedCallBack/'
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Token c6e7724396561cfd9004718330fc8a6dcbaf6409'
        }
        payload = {
            'msg': msg,
            'success': success,
            'update_type': update_type,
            'content_object_id': content_object_id,
            'uuid': uuid
        }

        requests.post(url, headers=headers, data=payload, timeout=15, verify=False)
    except Exception as e:
        log.logger.error('回调cmdb失败-%s' % (str(e)))
