"""后端热更新校验数据
"""

import json

from cmdb.logs import HotUpdateLog

from myworkflows.models import GameServer


def get_update_gtype(hot_server):
    """获取后端热更新的更新游戏类型
    """

    list_update_gtype = set()

    for server in json.loads(hot_server.update_server_list):
        gtype = server.get('gtype')
        if gtype not in list_update_gtype:
            list_update_gtype.add(gtype)

    return list_update_gtype


def drop_game_server(server, project, area_name, uuid):
    """对于那些找不到的区服或者被合服的区服
    直接过滤掉
    """
    log = HotUpdateLog(uuid)

    srv_id = server['srv_id']

    try:
        s = GameServer.objects.get(project=project, area_name=area_name, srv_id=srv_id, srv_status=0)
    except GameServer.DoesNotExist:
        log.logger.info('区服:%s 没有找到,删除' % (srv_id))
        return False
    else:
        # 如果这个服被合服
        if s.merge_id:
            log.logger.info('区服%s被合服,删除' % (srv_id))
            return False

        return True


def modify_game_server(update_server_list, project, area_name, uuid):
    """清理区服数据
    """
    log = HotUpdateLog(uuid)

    for server in update_server_list:
        gameserverid = server['gameserverid']
        ip = server['ip']
        try:
            s = GameServer.objects.get(pk=gameserverid)
        except GameServer.DoesNotExist:
            log.logger.info('区服:%s 没有找到,删除' % (s.srv_id))
            continue
        else:
            # 如果这个服被合服
            if s.merge_id:
                log.logger.info('区服%s被合服,删除' % (s.srv_id))
                continue

            if s.ip != ip:
                log.logger.info('区服%s:%s更正ip为:%s' % (s.srv_id, ip, s.ip))
                server['ip'] = s.ip

            yield server


def revise_server_list(hot_server):
    """校正后端热更新区服数据
    1 如果有新服，并且勾选了热更新服，增加新服
    2 如果合服了，自动删掉合服的区服
    3 如果迁服，修改迁服的ip
    4 如果是关平台删服，自动删除该服
    """

    log = HotUpdateLog(hot_server.uuid)

    hot_server_replication = hot_server.serverhotupdatereplication

    # 找到当前项目地区
    project = hot_server.project
    area_name = hot_server.area_name

    # 原来的热更新要更新的区服列表
    update_server_list = json.loads(hot_server.update_server_list)
    update_server_srv_id_list = [server.get('srv_id') for server in update_server_list]

    # 校验新服
    if hot_server_replication.on_new_server:
        log.logger.info('%s: 开始校验新服' % (hot_server.title))

        # 提交热更新时候的区服的副本数据
        replication_server_list = json.loads(hot_server_replication.replication_server_list)
        replication_server_srv_id_list = [server.get('srv_id') for server in replication_server_list]

        # 根据游戏服的类型来判断新服
        list_update_gtype = get_update_gtype(hot_server)
        for gtype in list_update_gtype:
            current_project_area_gtype_server_list = GameServer.objects.select_related('host').filter(
                project=project, host__belongs_to_room__area__chinese_name=area_name, server_version=hot_server.server_version,
                game_type__game_type_text=gtype, srv_status=0)
            for current_project_area_gtype_server in current_project_area_gtype_server_list:
                srv_id = current_project_area_gtype_server.srv_id
                if srv_id not in replication_server_srv_id_list and srv_id not in update_server_srv_id_list:
                    log.logger.info('发现新服srv_id:%s,添加到原来的热更新区服列表中' % (srv_id))
                    new_server_info = {}
                    new_server_info['srv_id'] = srv_id
                    new_server_info['pf_name'] = current_project_area_gtype_server.pf_name
                    new_server_info['srv_name'] = current_project_area_gtype_server.srv_name
                    new_server_info['gtype'] = gtype
                    new_server_info['ip'] = current_project_area_gtype_server.ip
                    update_server_list.append(new_server_info)
    else:
        log.logger.info('%s: 不需要新服校验' % (hot_server.title))

    # new = filter(lambda server: drop_game_server(server, project, area_name, hot_server.uuid), update_server_list)
    log.logger.info('%s: 开始合服迁服删服校验' % (hot_server.title))

    hot_server.update_server_list = json.dumps(list(
        modify_game_server(update_server_list, project, area_name, hot_server.uuid)))
    hot_server.save()
