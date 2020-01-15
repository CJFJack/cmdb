"""前后端热更新rsync的配置
"""

import os

from myworkflows.models import ClientHotUpdate
from myworkflows.models import ServerHotUpdate

from myworkflows.rsync_conf import RSYNC_MANAGERS


def get_rsync_path(content_object, rsync_task):
    """
    根据热更新类型，运维管理机来确定需要同步的rsync目录
    """

    PREFIX = '/data/hot_backup'

    if isinstance(content_object, ClientHotUpdate):
        type_path = 'hot_client'
    elif isinstance(content_object, ServerHotUpdate):
        type_path = 'hot_server'
    else:
        raise Exception('未知的热更新类型')

    project_name_en = content_object.project.project_name_en
    rsync_area_name = rsync_task.ops.room.area.short_name
    if not rsync_area_name:
        raise Exception('%s 没有配置rsync路径' % rsync_task.ops)
    uuid = content_object.uuid
    return os.path.join(PREFIX, type_path, project_name_en, rsync_area_name, uuid)


def get_rsync_config(project, area):
    """根据项目英文名和地区
    获取rsync的配置
    """

    for index, x in enumerate(RSYNC_MANAGERS):
        if project == x['project'] and area == x['area']:
            return RSYNC_MANAGERS[index]

    return None
