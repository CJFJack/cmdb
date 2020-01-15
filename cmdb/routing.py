from channels.routing import route
from mychannels.consumers import *
from mychannels.log_consumers import log_connect
from mychannels.log_consumers import log_disconnect
from mychannels.log_consumers import log_receive
from mychannels.log_consumers import hotupdate_cmdb_log_connect
from mychannels.log_consumers import hotupdate_cmdb_log_disconnect
from mychannels.log_consumers import hotupdate_cmdb_log_receive

from mychannels.game_install_consumers import game_install_connect
from mychannels.game_install_consumers import game_install_disconnect
from mychannels.game_install_consumers import game_install_receive
from mychannels.game_install_consumers import game_install_update

from mychannels.game_server_off_consumers import game_server_off_list_connect
from mychannels.game_server_off_consumers import game_server_off_list_disconnect
from mychannels.game_server_off_consumers import update_game_server_off_list
from mychannels.game_server_off_consumers import game_server_off_detail_connect
from mychannels.game_server_off_consumers import game_server_off_detail_disconnect
from mychannels.game_server_off_consumers import update_game_server_off_detail
from mychannels.game_server_off_consumers import game_server_off_log_connect
from mychannels.game_server_off_consumers import game_server_off_log_disconnect
from mychannels.game_server_off_consumers import update_game_server_off_log

from mychannels.host_initialize_log_consumers import host_initialize_list_connect
from mychannels.host_initialize_log_consumers import host_initialize_list_disconnect
from mychannels.host_initialize_log_consumers import update_host_initialize_list
from mychannels.host_initialize_log_consumers import host_initialize_log_connect
from mychannels.host_initialize_log_consumers import host_initialize_log_disconnect
from mychannels.host_initialize_log_consumers import update_host_initialize_log

from mychannels.mysql_consumers import mysql_list_connect
from mychannels.mysql_consumers import update_mysql_list
from mychannels.mysql_consumers import mysql_list_disconnect

from mychannels.host_compression_consumers import *
from mychannels.modify_srv_open_time_schedule_consumers import *


channel_routing = [
    route("websocket.connect", ws_connect, path=r"^/ws/hot_update/(?P<update_type>[a-zA-Z0-9_]+)"),
    route("websocket.receive", ws_message, path=r"^/ws/hot_update/(?P<update_type>[a-zA-Z0-9_]+)"),
    route("websocket.disconnect", ws_disconnect, path=r"^/ws/hot_update/(?P<update_type>[a-zA-Z0-9_]+)"),

    route("websocket.connect", ws_hot_server_connect, path=r"^/ws/hot_server_detail/(?P<hot_server_id>[0-9]+)"),
    route("websocket.receive", ws_hot_server_on_message, path=r"^/ws/hot_server_detail/(?P<hot_server_id>[0-9]+)"),
    route("websocket.disconnect", ws_hot_server_disconnect, path=r"^/ws/hot_server_detail/(?P<hot_server_id>[0-9]+)"),

    route("websocket.connect", ws_clean_user_connect, path=r"^/ws/clean_user/(?P<user_id>[0-9]+)"),
    route("websocket.disconnect", ws_clean_user_disconnect, path=r"^/ws/clean_user/(?P<user_id>[0-9]+)"),
    route("update_clean_user", update_clean_user),
    # route("websocket.receive", ws_clean_user_message, path=r"^/ws/clean_user/(?P<user_id>[0-9]+)"),
    route("myupdate", update_msg),
    route("hot_detail_update", hot_detail_update),

    route("websocket.connect", log_connect, path=r"^/ws/real_time_log/"),  # 实时log初始化链接
    route("websocket.disconnect", log_disconnect, path=r"^/ws/real_time_log/"),  # 实时log断开连接
    route("websocket.receive", log_receive, path=r"^/ws/real_time_log/"),  # 实时log发送数据

    route("websocket.connect", hotupdate_cmdb_log_connect, path=r"^/ws/hotupdate_cmdb_log/(?P<uuid>[a-zA-Z0-9-]+)"),
    route("websocket.disconnect", hotupdate_cmdb_log_disconnect, path=r"^/ws/hotupdate_cmdb_log/(?P<uuid>[a-zA-Z0-9-]+)"),
    route("websocket.receive", hotupdate_cmdb_log_receive, path=r"^/ws/hotupdate_cmdb_log/(?P<uuid>[a-zA-Z0-9-]+)"),

    route("websocket.connect", game_install_connect, path=r"^/ws/game_install/"),  # 装服初始化连接
    route("websocket.disconnect", game_install_disconnect, path=r"^/ws/game_install/"),  # 装服断开连接
    route("websocket.receive", game_install_receive, path=r"^/ws/game_install/"),  # 装服发送数据
    route("game_install_receive", game_install_update),

    route("websocket.connect", execute_salt_task_connect, path=r"^/ws/execute_salt_task/"),   # 执行salt任务初始化链接
    route("websocket.disconnect", execute_salt_task_disconnect, path=r"^/ws/execute_salt_task/"),  # 执行salt任务断开连接
    route("update_execute_salt_task", update_execute_salt_task),  # 更新执行salt任务结果

    route("websocket.connect", game_server_action_connect, path=r"^/ws/game_server_action/"),  # 区服操作初始化链接
    route("websocket.disconnect", game_server_action_disconnect, path=r"^/ws/game_server_action/"),  # 区服操作断开连接
    route("update_game_server_action", update_game_server_action),  # 更新区服操作结果

    route("websocket.connect", game_server_off_list_connect, path=r"^/ws/game_server_off_list/"),  # 区服下线任务列表初始化链接
    route("websocket.disconnect", game_server_off_list_disconnect, path=r"^/ws/game_server_off_list/"),  # 区服下线任务列表断开连接
    route("update_game_server_off_list", update_game_server_off_list),  # 更新区服下线任务列表

    route("websocket.connect", game_server_off_detail_connect, path=r"^/ws/game_server_off_detail/(?P<id>[0-9]+)/"),  # 区服下线详情初始化链接
    route("websocket.disconnect", game_server_off_detail_disconnect, path=r"^/ws/game_server_off_detail/(?P<id>[0-9]+)/"),  # 区服下线详情断开连接
    route("update_game_server_off_detail", update_game_server_off_detail),  # 更新区服下线详情

    route("websocket.connect", game_server_off_log_connect, path=r"^/ws/game_server_off_log/(?P<id>[0-9]+)/"),  # 区服下线日志初始化链接
    route("websocket.disconnect", game_server_off_log_disconnect, path=r"^/ws/game_server_off_log/(?P<id>[0-9]+)/"), # 区服下线日志断开连接
    route("update_game_server_off_log", update_game_server_off_log),  # 更新区服下线日志

    route("websocket.connect", host_compression_list_connect, path=r"^/ws/host_compression_list/"),  # 机器回收任务列表初始化链接
    route("websocket.disconnect", host_compression_list_disconnect, path=r"^/ws/host_compression_list/"),  # 机器回收任务列表断开连接
    route("update_host_compression_list", update_host_compression_list),  # 更新机器回收任务列表

    route("websocket.connect", host_compression_log_connect, path=r"^/ws/host_compression_log/(?P<id>[0-9]+)/"),  # 机器回收任务日志初始化链接
    route("websocket.disconnect", host_compression_log_disconnect, path=r"^/ws/host_compression_log/(?P<id>[0-9]+)/"),  # 机器回收任务日志断开连接
    route("update_host_compression_log", update_host_compression_log),  # 更新机器回收任务日志

    route("websocket.connect", host_compression_detail_connect, path=r"^/ws/host_compression_detail/(?P<id>[0-9]+)/"),   # 机器回收任务日志初始化链接
    route("websocket.disconnect", host_compression_detail_disconnect, path=r"^/ws/host_compression_detail/(?P<id>[0-9]+)/"),   # 机器回收任务日志断开连接
    route("update_host_compression_detail", update_host_compression_detail),  # 更新机器回收任务日志

    route("websocket.connect", modify_srv_open_time_schedule_list_connect, path=r"^/ws/modify_srv_open_time_schedule_list/"),  # 修改开服时间计划列表初始化链接
    route("websocket.disconnect", modify_srv_open_time_schedule_list_disconnect, path=r"^/ws/modify_srv_open_time_schedule_list/"),  # 修改开服时间计划列表断开连接
    route("update_modify_srv_open_time_schedule_list", update_modify_srv_open_time_schedule_list),  # 更新修改开服时间计划列表

    route("websocket.connect", modify_srv_open_time_schedule_detail_connect, path=r"^/ws/modify_srv_open_time_schedule_detail/(?P<id>[0-9]+)/"),  # 修改开服时间计划详情初始化链接
    route("websocket.disconnect", modify_srv_open_time_schedule_detail_disconnect, path=r"^/ws/modify_srv_open_time_schedule_detail/(?P<id>[0-9]+)/"),  # 修改开服时间计划详情断开连接
    route("update_modify_srv_open_time_schedule_detail", update_modify_srv_open_time_schedule_detail),  # 更新修改开服时间计划详情

    route("websocket.connect", modify_srv_open_time_schedule_log_connect, path=r"^/ws/modify_srv_open_time_schedule_log/(?P<id>[0-9]+)/"),  # 修改开服时间计划日志初始化链接
    route("websocket.disconnect", modify_srv_open_time_schedule_log_disconnect, path=r"^/ws/modify_srv_open_time_schedule_log/(?P<id>[0-9]+)/"),  # 修改开服时间计划日志断开连接
    route("update_modify_srv_open_time_schedule_log", update_modify_srv_open_time_schedule_log),  # 更新修改开服时间计划日志

    route("websocket.connect", game_server_action_record_connect, path=r"^/ws/game_server_action_record/"),         # 区服操作记录初始化链接
    route("websocket.disconnect", game_server_action_record_disconnect, path=r"^/ws/game_server_action_record/"),   # 区服操作记录断开连接
    route("update_game_server_action_record", update_game_server_action_record),  # 刷新区服操作记录表

    route("websocket.connect", execute_salt_command_connect, path=r"^/ws/execute_salt_command/(?P<uuid>[a-zA-Z0-9-]+)/"), # 执行salt命令connect
    route("websocket.disconnect", execute_salt_command_disconnect, path=r"^/ws/execute_salt_command/(?P<uuid>[a-zA-Z0-9-]+)/"), # 执行salt命令disconnect
    route("update_execute_salt_command", update_execute_salt_command),  # 刷新执行salt命令结果

    route("websocket.connect", host_initialize_list_connect, path=r"^/ws/host_initialize_list/"),  # 主机初始化列表初始化链接
    route("websocket.disconnect", host_initialize_list_disconnect, path=r"^/ws/host_initialize_list/"),  # 主机初始化列表断开连接
    route("update_host_initialize_list", update_host_initialize_list),  # 更新主机初始化列表

    route("websocket.connect", host_initialize_log_connect, path=r"^/ws/host_initialize_log/(?P<id>[0-9]+)/"),  # 主机初始化日志初始化链接
    route("websocket.disconnect", host_initialize_log_disconnect, path=r"^/ws/host_initialize_log/(?P<id>[0-9]+)/"), # 主机初始化日志断开连接
    route("update_host_initialize_log", update_host_initialize_log),  # 更新主机初始化日志

    route("websocket.connect", mysql_list_connect, path=r"^/ws/mysql_list/"),  # 数据库实例列表初始化链接
    route("websocket.disconnect", mysql_list_disconnect, path=r"^/ws/mysql_list/"),  # 数据库实例列表断开连接
    route("update_mysql_list", update_mysql_list),  # 更新数据库实例列表
]

