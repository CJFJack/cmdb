# -*- encoding: utf-8 -*-

# import models
from assets.models import *

# Re url to title
url2title = {
    'game_project_list': '项目列表',
    'duty_schedule': '值班表',
    'room': '机房信息',
    'business': '业务类型',
    'host': '主机列表',
    'workflow_list': '工单列表',
    'project_group_list': '项目分组',
    'ops_manager_list': '运维管理机',
}

# Re url to model objects
url2obj = {
    'cmdb_duty_schedule': DutySchedule,
    'cmdb_fullcalendar': FullCalendar,
    'game_project_list': GameProject,
    'room': Room,
    'business': Business,
    'host': Host,
    'project_group_list': ProjectGroup,
    'ops_manager_list': OpsManager,
}

# Re url to permissions

# url到查看权限的映射
url2view_perm = {
    'game_project_list': 'view_game_project_obj',
    'project_group_list': 'view_game_project_obj',
    'duty_schedule': 'view_duty_schedule_obj',
    'room': 'view_room_obj',
    'business': 'view_business_obj',
    'host': 'view_host_obj',
    'ops_manager_list': 'view_host_obj',
}

# url到编辑权限的映射
url2edit_perm = {
    'game_project_list': 'edit_game_project_obj',
    'project_group_list': 'edit_game_project_obj',
    'duty_schedule': 'edit_duty_schedule_obj',
    'room': 'edit_room_obj',
    'business': 'edit_business_obj',
    'host': 'edit_host_obj',
    'ops_manager_list': 'edit_host_obj',
}

# url到删除权限的映射
url2del_perm = {
    'game_project_list': 'del_game_project_obj',
    'project_group_list': 'del_game_project_obj',
    'duty_schedule': 'del_duty_schedule_obj',
    'room': 'del_room_obj',
    'business': 'del_business_obj',
    'host': 'del_host_obj',
    'ops_manager_list': 'del_host_obj',
}
